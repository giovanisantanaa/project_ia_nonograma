import tkinter as tk
from tkinter import ttk
import threading
import copy
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from ambiente import Nonograma, DESCONHECIDO, PINTADA, VAZIA
from agente_regras import AgenteRegras
from agente_csp import AgenteCSP
from agente_probabilistico import AgenteProbabilistico
from agente_local import AgenteBuscaLocal
from puzzles import puzzles_todos, puzzles_por_tamanho, gerar_puzzle_aleatorio, TAMANHOS

try:
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    TEM_MPL = True
except ImportError:
    TEM_MPL = False

COR = {
    'fundo':    '#1E1E2E',
    'painel':   '#2A2A3E',
    'painel2':  '#313147',
    'roxo':     '#7C3AED',
    'ciano':    '#06B6D4',
    'verde':    '#10B981',
    'texto':    '#E2E8F0',
    'cinza':    '#94A3B8',
    'preench':  '#7C3AED',
    'vazio':    '#1A1A2E',
    'unknown':  '#3A3A5C',
    'borda':    '#4A4A6A',
    'amarelo':  '#F59E0B',
    'verm':     '#EF4444',
}

CORES_AGENTES = {
    'Baseado em Regras':                 '#10B981',
    'CSP (A*)':                          '#7C3AED',
    'Probabilistico (Bayes)':            '#F59E0B',
    'Busca Local (Simulated Annealing)': '#EF4444',
}

DESCRICAO_AGENTES = {
    'Baseado em Regras':                 'Inferencia logica pura: interseção de candidatos possiveis',
    'CSP (A*)':                          'CSP: propagacao de restricoes + busca A* com heuristica MRV',
    'Probabilistico (Bayes)':            'Probabilistico: decide celulas por probabilidade bayesiana',
    'Busca Local (Simulated Annealing)': 'Busca local: Simulated Annealing minimiza linhas inconsistentes',
}


class GridCanvas(tk.Canvas):

    def __init__(self, parent, puzzle, tc=26, **kw):
        self.puzzle = puzzle
        self.tc = tc

        mr = 1
        for c in puzzle.pistas_linha:
            if len(c) > mr:
                mr = len(c)

        mc = 1
        for c in puzzle.pistas_coluna:
            if len(c) > mc:
                mc = len(c)

        self.mr = mr
        self.mc = mc
        self.ox = mr * tc
        self.oy = mc * tc

        w = self.ox + puzzle.colunas * tc + 4
        h = self.oy + puzzle.linhas * tc + 4

        super().__init__(parent, width=w, height=h,
                         bg=COR['fundo'], highlightthickness=0, **kw)

        self._grid = []
        for i in range(puzzle.linhas):
            linha = []
            for j in range(puzzle.colunas):
                linha.append(DESCONHECIDO)
            self._grid.append(linha)

        self._destaque = None
        self.desenhar()

    def set_tc(self, tc):
        if tc == self.tc:
            return
        self.tc = tc
        self.ox = self.mr * tc
        self.oy = self.mc * tc
        w = self.ox + self.puzzle.colunas * tc + 4
        h = self.oy + self.puzzle.linhas * tc + 4
        self.config(width=w, height=h)
        self.desenhar()

    def atualizar(self, grid, destaque=None):
        self._grid = grid
        self._destaque = destaque
        self.desenhar()

    def desenhar(self):
        self.delete('all')
        grid = self._grid
        tc = self.tc
        ox = self.ox
        oy = self.oy
        p = self.puzzle

        fonte_tam = max(10, int(tc * 0.55))
        fonte = ('Consolas', fonte_tam, 'bold')

        # pistas das colunas (em cima)
        for j in range(p.colunas):
            pista = p.pistas_coluna[j]
            n = len(pista)
            for k in range(n):
                num = pista[k]
                if num == 0:
                    continue
                y = (self.mc - n + k) * tc + tc // 2
                x = ox + j * tc + tc // 2
                self.create_text(x, y, text=str(num),
                                 fill=COR['cinza'], font=fonte)

        # pistas das linhas (esquerda)
        for i in range(p.linhas):
            pista = p.pistas_linha[i]
            n = len(pista)
            for k in range(n):
                num = pista[k]
                if num == 0:
                    continue
                x = (self.mr - n + k) * tc + tc // 2
                y = oy + i * tc + tc // 2
                self.create_text(x, y, text=str(num),
                                 fill=COR['cinza'], font=fonte)

        # celulas
        for i in range(p.linhas):
            for j in range(p.colunas):
                val = grid[i][j]
                x0 = ox + j * tc + 1
                y0 = oy + i * tc + 1
                x1 = x0 + tc - 2
                y1 = y0 + tc - 2

                eh_destaque = (self._destaque is not None and
                               self._destaque == (i, j))

                if val == PINTADA:
                    cor = COR['preench']
                elif val == VAZIA:
                    cor = COR['vazio']
                else:
                    cor = COR['unknown']

                if eh_destaque:
                    borda_cor = '#FFFF00'
                    borda_larg = 2
                else:
                    borda_cor = COR['borda']
                    borda_larg = 1

                self.create_rectangle(x0, y0, x1, y1, fill=cor,
                                       outline=borda_cor, width=borda_larg)

                if val == VAZIA:
                    pad = int(tc * 0.2)
                    self.create_line(x0+pad, y0+pad, x1-pad, y1-pad,
                                     fill=COR['borda'], width=1)
                    self.create_line(x1-pad, y0+pad, x0+pad, y1-pad,
                                     fill=COR['borda'], width=1)

        #linhas separadoras entre pistas e grid
        self.create_line(ox, 0, ox, oy + p.linhas * tc,
                         fill=COR['texto'], width=2)
        self.create_line(0, oy, ox + p.colunas * tc, oy,
                         fill=COR['texto'], width=2)



# Painel de metricas
class PainelMetricas(tk.Frame):

    def __init__(self, parent, **kw):
        super().__init__(parent, bg=COR['painel'], **kw)
        self._lbs = {}

        campos = [
            ('agente',    'Agente'),
            ('status',    'Status'),
            ('tempo',     'Tempo'),
            ('passos',    'Passos'),
        ]

        for row in range(len(campos)):
            chave = campos[row][0]
            rotulo = campos[row][1]

            tk.Label(self, text=rotulo + ':', bg=COR['painel'],
                     fg=COR['cinza'], font=('Consolas', 11),
                     anchor='w', width=8).grid(row=row, column=0,
                                               sticky='w', padx=4, pady=1)
            v = tk.Label(self, text='-', bg=COR['painel'],
                         fg=COR['texto'], font=('Consolas', 11, 'bold'),
                         anchor='w', width=16)
            v.grid(row=row, column=1, sticky='w', padx=2, pady=1)
            self._lbs[chave] = v

    def atualizar(self, resultado):
        self._lbs['agente'].config(text=resultado['nome'][:20])
        ok = resultado['resolvido']

        if ok:
            self._lbs['status'].config(text='Resolvido', fg=COR['verde'])
        else:
            self._lbs['status'].config(text='Parcial', fg=COR['amarelo'])

        tempo_ms = resultado['tempo'] * 1000
        self._lbs['tempo'].config(text='{:.2f} ms'.format(tempo_ms))
        self._lbs['passos'].config(text=str(resultado['passos']))

    def limpar(self):
        for v in self._lbs.values():
            v.config(text='-', fg=COR['texto'])


# Controlador de animacao
class Animacao:

    def __init__(self, cb_frame, cb_fim, var_vel):
        self._cb_frame = cb_frame
        self._cb_fim = cb_fim
        self._vel = var_vel
        self._hist = []
        self._idx = 0
        self._rodando = False
        self._after_id = None
        self._root = None

    def carregar(self, historico, root):
        self.pausar()
        self._hist = historico
        self._idx = 0
        self._root = root
        self._emitir()

    def play(self):
        if not self._hist or self._rodando:
            return
        self._rodando = True
        self._tick()

    def pausar(self):
        self._rodando = False
        if self._after_id and self._root:
            self._root.after_cancel(self._after_id)
            self._after_id = None

    def avancar(self):
        self.pausar()
        if self._idx < len(self._hist) - 1:
            self._idx = self._idx + 1
            self._emitir()

    def voltar(self):
        self.pausar()
        if self._idx > 0:
            self._idx = self._idx - 1
            self._emitir()

    def reiniciar(self):
        self.pausar()
        self._idx = 0
        self._emitir()

    def ir_fim(self):
        self.pausar()
        if self._hist:
            self._idx = len(self._hist) - 1
            self._emitir()

    def _tick(self):
        if not self._rodando:
            return
        self._emitir()
        if self._idx < len(self._hist) - 1:
            self._idx = self._idx + 1
            self._after_id = self._root.after(self._vel.get(), self._tick)
        else:
            self._rodando = False
            self._cb_fim()

    def _emitir(self):
        if not self._hist:
            return
        grid = self._hist[self._idx]
        total = len(self._hist)

        destaque = None
        if self._idx > 0:
            ant = self._hist[self._idx - 1]
            for i in range(len(grid)):
                for j in range(len(grid[0])):
                    if grid[i][j] != ant[i][j]:
                        destaque = (i, j)
                        break
                if destaque:
                    break

        self._cb_frame(grid, self._idx, total, destaque)



# Janela Principal
class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title('IA de Nonogramas - IMD3001')
        self.configure(bg=COR['fundo'])
        self.geometry('1200x780')

        self._agentes = [
            AgenteRegras(),
            AgenteCSP(),
            AgenteProbabilistico(),
            AgenteBuscaLocal(),
        ]

        self._puzzles_cache = {}
        self._resultado_solo = None
        self._puzzle_solo = None
        self._wgrid_solo = None

        self._var_vel = tk.IntVar(value=200)
        self._var_modo = tk.StringVar(value='celulas')

        self._anim_solo = Animacao(
            cb_frame=self._solo_frame,
            cb_fim=self._solo_fim,
            var_vel=self._var_vel,
        )

        # estado comparativo
        self._comp_resultados = []
        self._comp_historicos = []
        self._comp_puzzle = None
        self._comp_grids = []
        self._comp_grids_w = []
        self._comp_idx = 0
        self._comp_rodando = False
        self._comp_after = None

        self._construir_ui()
        self._carregar_puzzles_solo()


    def _construir_ui(self):
        cab = tk.Frame(self, bg=COR['fundo'])
        cab.pack(fill='x', padx=16, pady=(10, 4))
        tk.Label(cab, text='IA de Nonogramas',
                 bg=COR['fundo'], fg=COR['texto'],
                 font=('Segoe UI', 17, 'bold')).pack(side='left')
        tk.Label(cab, text='IMD3001 - UFRN',
                 bg=COR['fundo'], fg=COR['cinza'],
                 font=('Segoe UI', 9)).pack(side='left', padx=12)

        tk.Frame(self, bg=COR['borda'], height=1).pack(fill='x', padx=16, pady=2)

        est = ttk.Style()
        est.theme_use('clam')
        est.configure('TNotebook', background=COR['fundo'], borderwidth=0)
        est.configure('TNotebook.Tab', background=COR['painel2'],
                       foreground=COR['cinza'], padding=[14, 5],
                       font=('Segoe UI', 10))
        est.map('TNotebook.Tab',
                background=[('selected', COR['roxo'])],
                foreground=[('selected', 'white')])

        nb = ttk.Notebook(self)
        nb.pack(fill='both', expand=True, padx=10, pady=6)

        self._aba_solo = tk.Frame(nb, bg=COR['fundo'])
        self._aba_comp = tk.Frame(nb, bg=COR['fundo'])
        self._aba_bench = tk.Frame(nb, bg=COR['fundo'])
        self._aba_graf = tk.Frame(nb, bg=COR['fundo'])

        nb.add(self._aba_solo, text='  Resolver  ')
        nb.add(self._aba_comp, text='  Comparar  ')
        nb.add(self._aba_bench, text='  Benchmark  ')
        nb.add(self._aba_graf, text='  Graficos  ')

        self._build_solo(self._aba_solo)
        self._build_comp(self._aba_comp)
        self._build_bench(self._aba_bench)
        self._build_graf(self._aba_graf)


    def _build_solo(self, pai):
        esq = tk.Frame(pai, bg=COR['painel'], width=260)
        esq.pack(side='left', fill='y', padx=(4, 6), pady=4)
        esq.pack_propagate(False)

        # puzzle
        tk.Label(esq, text='PUZZLE', bg=COR['painel'], fg=COR['roxo'],
                 font=('Segoe UI', 8, 'bold')).pack(anchor='w', padx=12, pady=(10, 2))

        tk.Label(esq, text='Tamanho:', bg=COR['painel'], fg=COR['cinza'],
                 font=('Segoe UI', 9)).pack(anchor='w', padx=12)

        tam_nomes = []
        for t in TAMANHOS:
            tam_nomes.append(str(t) + 'x' + str(t))

        self._var_tam_solo = tk.StringVar(value=tam_nomes[0])
        cb_tam = ttk.Combobox(esq, textvariable=self._var_tam_solo,
                              values=tam_nomes, state='readonly', width=22)
        cb_tam.pack(anchor='w', padx=12)
        cb_tam.bind('<<ComboboxSelected>>', lambda e: self._carregar_puzzles_solo())

        tk.Label(esq, text='Puzzle:', bg=COR['painel'], fg=COR['cinza'],
                 font=('Segoe UI', 9)).pack(anchor='w', padx=12)

        self._var_puz_solo = tk.StringVar()
        self._cb_puz_solo = ttk.Combobox(esq, textvariable=self._var_puz_solo,
                                          state='readonly', width=22)
        self._cb_puz_solo.pack(anchor='w', padx=12, pady=(0, 4))

        self._var_aleatorio_solo = tk.BooleanVar(value=False)
        tk.Checkbutton(esq, text='Puzzle aleatorio',
                       variable=self._var_aleatorio_solo,
                       bg=COR['painel'], fg=COR['texto'],
                       selectcolor=COR['painel2'],
                       font=('Segoe UI', 9)).pack(anchor='w', padx=12)

        tk.Frame(esq, bg=COR['borda'], height=1).pack(fill='x', padx=12, pady=6)

        # agente
        tk.Label(esq, text='AGENTE', bg=COR['painel'], fg=COR['roxo'],
                 font=('Segoe UI', 8, 'bold')).pack(anchor='w', padx=12, pady=(4, 2))

        nomes_agentes = []
        for a in self._agentes:
            nomes_agentes.append(a.nome)

        self._var_agente_solo = tk.StringVar(value=nomes_agentes[0])
        ttk.Combobox(esq, textvariable=self._var_agente_solo,
                     values=nomes_agentes, state='readonly',
                     width=22).pack(anchor='w', padx=12)

        tk.Frame(esq, bg=COR['borda'], height=1).pack(fill='x', padx=12, pady=6)

        # modo animacao
        tk.Label(esq, text='ANIMACAO', bg=COR['painel'], fg=COR['roxo'],
                 font=('Segoe UI', 8, 'bold')).pack(anchor='w', padx=12, pady=(4, 2))

        frame_modo = tk.Frame(esq, bg=COR['painel'])
        frame_modo.pack(fill='x', padx=12)

        tk.Radiobutton(frame_modo, text='Celula a celula',
                       variable=self._var_modo, value='celulas',
                       bg=COR['painel'], fg=COR['texto'],
                       selectcolor=COR['roxo'],
                       font=('Segoe UI', 9)).pack(side='left')
        tk.Radiobutton(frame_modo, text='Por passos',
                       variable=self._var_modo, value='passos',
                       bg=COR['painel'], fg=COR['texto'],
                       selectcolor=COR['roxo'],
                       font=('Segoe UI', 9)).pack(side='left')

        tk.Frame(esq, bg=COR['borda'], height=1).pack(fill='x', padx=12, pady=6)

        # velocidade
        tk.Label(esq, text='VELOCIDADE', bg=COR['painel'], fg=COR['roxo'],
                 font=('Segoe UI', 8, 'bold')).pack(anchor='w', padx=12, pady=(4, 2))

        tk.Scale(esq, variable=self._var_vel,
                 from_=20, to=1000, resolution=20,
                 orient='horizontal', bg=COR['painel'], fg=COR['texto'],
                 troughcolor=COR['painel2'], highlightthickness=0,
                 length=210, showvalue=True).pack(padx=12)

        tk.Frame(esq, bg=COR['borda'], height=1).pack(fill='x', padx=12, pady=6)

        # botao resolver
        tk.Button(esq, text='RESOLVER', bg=COR['roxo'], fg='white',
                  relief='flat', cursor='hand2',
                  font=('Segoe UI', 10, 'bold'), pady=8,
                  command=self._solo_rodar).pack(fill='x', padx=12, pady=4)

        tk.Frame(esq, bg=COR['borda'], height=1).pack(fill='x', padx=12, pady=6)

        # metricas
        tk.Label(esq, text='METRICAS', bg=COR['painel'], fg=COR['roxo'],
                 font=('Segoe UI', 8, 'bold')).pack(anchor='w', padx=12, pady=(4, 2))

        self._metricas_solo = PainelMetricas(esq)
        self._metricas_solo.pack(fill='x', padx=4)

        # area direita: controles + grid
        dir_frame = tk.Frame(pai, bg=COR['fundo'])
        dir_frame.pack(side='left', fill='both', expand=True, pady=4, padx=(0, 4))

        barra = tk.Frame(dir_frame, bg=COR['painel2'])
        barra.pack(fill='x', pady=(0, 4))

        cfg_btn = dict(bg=COR['painel'], fg=COR['texto'], relief='flat',
                       cursor='hand2', font=('Segoe UI', 11), width=3, pady=4)

        tk.Button(barra, text='|<', command=self._anim_solo.reiniciar, **cfg_btn).pack(side='left', padx=2, pady=4)
        tk.Button(barra, text='<', command=self._anim_solo.voltar, **cfg_btn).pack(side='left', padx=2)

        self._btn_play_solo = tk.Button(barra, text='Play',
                                        bg=COR['roxo'], fg='white',
                                        relief='flat', cursor='hand2',
                                        font=('Segoe UI', 10, 'bold'),
                                        width=5, pady=4,
                                        command=self._solo_toggle_play)
        self._btn_play_solo.pack(side='left', padx=2)

        tk.Button(barra, text='>', command=self._anim_solo.avancar, **cfg_btn).pack(side='left', padx=2)
        tk.Button(barra, text='>|', command=self._anim_solo.ir_fim, **cfg_btn).pack(side='left', padx=2)

        self._lbl_passo_solo = tk.Label(barra, text='0 / 0',
                                        bg=COR['painel2'], fg=COR['texto'],
                                        font=('Consolas', 10, 'bold'))
        self._lbl_passo_solo.pack(side='left', padx=14)

        self._lbl_status_solo = tk.Label(barra, text='',
                                         bg=COR['painel2'], fg=COR['verde'],
                                         font=('Segoe UI', 9, 'bold'))
        self._lbl_status_solo.pack(side='left', padx=6)

        self._lbl_desc_solo = tk.Label(barra, text='',
                                       bg=COR['painel2'], fg=COR['ciano'],
                                       font=('Consolas', 11),
                                       width=52, anchor='w')
        self._lbl_desc_solo.pack(side='left', padx=10)

        self._frame_grid_solo = tk.Frame(dir_frame, bg=COR['fundo'])
        self._frame_grid_solo.pack(fill='both', expand=True)
        self._frame_grid_solo.bind('<Configure>', self._solo_on_resize)
        self._resize_after_id_solo = None

        self._ph_solo = tk.Label(
            self._frame_grid_solo,
            text='Selecione um puzzle e clique em RESOLVER',
            bg=COR['fundo'], fg=COR['cinza'], font=('Segoe UI', 13),
        )
        self._ph_solo.pack(expand=True)

    def _carregar_puzzles_solo(self):
        texto_tam = self._var_tam_solo.get()
        tamanho = int(texto_tam.split('x')[0])

        puzzles = puzzles_por_tamanho(tamanho)
        nomes = []
        self._puzzles_cache = {}
        for p in puzzles:
            nomes.append(p.nome)
            self._puzzles_cache[p.nome] = p

        self._cb_puz_solo['values'] = nomes
        if nomes:
            self._var_puz_solo.set(nomes[0])

    def _solo_rodar(self):
        self._anim_solo.pausar()

        nome_agente = self._var_agente_solo.get()
        agente = None
        for a in self._agentes:
            if a.nome == nome_agente:
                agente = a
                break

        if self._var_aleatorio_solo.get():
            texto_tam = self._var_tam_solo.get()
            tamanho = int(texto_tam.split('x')[0])
            puzzle_base = gerar_puzzle_aleatorio(tamanho)
        else:
            nome_puz = self._var_puz_solo.get()
            puzzle_base = self._puzzles_cache.get(nome_puz)
            if puzzle_base is None:
                return

        self._puzzle_solo = puzzle_base
        self._lbl_status_solo.config(text='Resolvendo...', fg=COR['ciano'])
        self._lbl_desc_solo.config(text='')
        self._metricas_solo.limpar()
        self._btn_play_solo.config(text='Play', bg=COR['roxo'])

        def worker():
            p = puzzle_base.copiar()
            resultado = agente.resolver(p)
            self._resultado_solo = resultado
            self.after(0, lambda: self._solo_iniciar_anim(resultado, puzzle_base))

        threading.Thread(target=worker, daemon=True).start()

    def _calc_tc_solo(self, puzzle):
        self._frame_grid_solo.update_idletasks()
        w_avail = self._frame_grid_solo.winfo_width()
        h_avail = self._frame_grid_solo.winfo_height()
        if w_avail < 50:
            w_avail = 800
        if h_avail < 50:
            h_avail = 600

        mr = max((len(c) for c in puzzle.pistas_linha), default=1)
        mc = max((len(c) for c in puzzle.pistas_coluna), default=1)

        cols_unid = mr + puzzle.colunas
        linhas_unid = mc + puzzle.linhas

        tc_w = (w_avail - 12) // cols_unid
        tc_h = (h_avail - 12) // linhas_unid
        tc = min(tc_w, tc_h)
        return max(10, min(tc, 40))

    def _solo_on_resize(self, event=None):
        if self._resize_after_id_solo is not None:
            self.after_cancel(self._resize_after_id_solo)
        self._resize_after_id_solo = self.after(80, self._solo_aplicar_resize)

    def _solo_aplicar_resize(self):
        self._resize_after_id_solo = None
        if self._wgrid_solo is None or self._puzzle_solo is None:
            return
        tc = self._calc_tc_solo(self._puzzle_solo)
        self._wgrid_solo.set_tc(tc)

    def _solo_iniciar_anim(self, resultado, puzzle):
        self._ph_solo.pack_forget()
        for w in self._frame_grid_solo.winfo_children():
            w.destroy()

        tc = self._calc_tc_solo(puzzle)

        self._wgrid_solo = GridCanvas(self._frame_grid_solo, puzzle, tc=tc)
        self._wgrid_solo.pack(expand=True)

        modo = self._var_modo.get()
        if modo == 'celulas':
            hist = resultado['historico_celulas']
        else:
            hist = resultado['historico_passos']

        if len(hist) == 0:
            # tabuleiro vazio
            tab_vazio = []
            for i in range(puzzle.linhas):
                linha = []
                for j in range(puzzle.colunas):
                    linha.append(DESCONHECIDO)
                tab_vazio.append(linha)
            hist = [tab_vazio]

        self._anim_solo.carregar(hist, self)
        self._metricas_solo.atualizar(resultado)

    def _solo_frame(self, grid, idx, total, destaque):
        if self._wgrid_solo:
            self._wgrid_solo.atualizar(grid, destaque)
        modo = self._var_modo.get()
        if modo == 'celulas':
            pref = 'Cel.'
            chave_desc = 'descricoes'
        else:
            pref = 'Passo'
            chave_desc = 'descricoes_passos'
        self._lbl_passo_solo.config(text='{} {} / {}'.format(pref, idx + 1, total))

        # mostra descricao do passo atual
        desc = ''
        if self._resultado_solo:
            descs = self._resultado_solo.get(chave_desc, [])
            if idx < len(descs):
                desc = descs[idx]
        self._lbl_desc_solo.config(text=desc)

    def _solo_fim(self):
        self._btn_play_solo.config(text='Play', bg=COR['roxo'])
        if self._resultado_solo:
            if self._resultado_solo['resolvido']:
                self._lbl_status_solo.config(text='Resolvido!', fg=COR['verde'])
            else:
                self._lbl_status_solo.config(text='Incompleto', fg=COR['amarelo'])
            nome = self._resultado_solo.get('nome', '')
            self._lbl_desc_solo.config(text=DESCRICAO_AGENTES.get(nome, ''))

    def _solo_toggle_play(self):
        if self._anim_solo._rodando:
            self._anim_solo.pausar()
            self._btn_play_solo.config(text='Play', bg=COR['roxo'])
        else:
            self._anim_solo.play()
            self._btn_play_solo.config(text='Pause', bg=COR['amarelo'])


    def _calc_tc_comp(self, puzzle, largura_disp, altura_disp):
        mr = max((len(c) for c in puzzle.pistas_linha), default=1)
        mc = max((len(c) for c in puzzle.pistas_coluna), default=1)

        cols_unid = mr + puzzle.colunas
        linhas_unid = mc + puzzle.linhas

        tc_w = (largura_disp - 24) // cols_unid
        tc_h = (altura_disp - 24) // linhas_unid
        tc = min(tc_w, tc_h)
        return max(8, min(tc, 32))

    def _comp_ajustar_colunas(self):
        ativos = [a for a in self._agentes if self._agentes_ativos_comp[a.nome].get()]
        n = len(ativos)
        if n == 0:
            return
        win_w = self._cv_comp.winfo_width()
        if win_w < 200:
            win_w = self.winfo_width() - 30
        col_w_budget = max(200, (win_w - 6 * n) // n)

        puzzle = self._comp_puzzle
        tc = None
        col_w = col_w_budget
        if puzzle is not None:
            exemplo = self._comp_cols[ativos[0].nome]
            altura_disp = exemplo['frame'].winfo_height()
            if altura_disp < 80:
                altura_disp = self.winfo_height() - 260
            tc = self._calc_tc_comp(puzzle, col_w_budget, altura_disp)
            mr = max((len(c) for c in puzzle.pistas_linha), default=1)
            grid_w = mr * tc + puzzle.colunas * tc + 20
            col_w = max(grid_w, col_w_budget)

        for agente in self._agentes:
            col_data = self._comp_cols[agente.nome]
            col_frame = col_data['col']
            if self._agentes_ativos_comp[agente.nome].get():
                col_frame.config(width=col_w)
                col_frame.pack_propagate(False)
                col_frame.pack(side='left', fill='y', padx=3)
                col_data['desc'].config(wraplength=col_w - 20)
            else:
                col_frame.pack_forget()

        if tc is not None:
            for idx in range(len(self._comp_grids_w)):
                gw = self._comp_grids_w[idx]
                if gw is not None:
                    gw.set_tc(tc)

    def _build_comp(self, pai):
        topo = tk.Frame(pai, bg=COR['painel2'])
        topo.pack(fill='x', padx=6, pady=4)

        tk.Label(topo, text='Tamanho:', bg=COR['painel2'],
                 fg=COR['cinza'], font=('Segoe UI', 9)).pack(side='left', padx=(8, 2))

        tam_nomes = []
        for t in TAMANHOS:
            tam_nomes.append(str(t) + 'x' + str(t))

        self._var_tam_comp = tk.StringVar(value=tam_nomes[0])
        cb_tam = ttk.Combobox(topo, textvariable=self._var_tam_comp,
                              values=tam_nomes, state='readonly', width=8)
        cb_tam.pack(side='left', padx=4)
        cb_tam.bind('<<ComboboxSelected>>', lambda e: self._comp_carregar())

        tk.Label(topo, text='Puzzle:', bg=COR['painel2'],
                 fg=COR['cinza'], font=('Segoe UI', 9)).pack(side='left', padx=(8, 2))

        self._var_puz_comp = tk.StringVar()
        self._cb_puz_comp = ttk.Combobox(topo, textvariable=self._var_puz_comp,
                                          state='readonly', width=18)
        self._cb_puz_comp.pack(side='left', padx=4)

        self._var_aleatorio_comp = tk.BooleanVar(value=False)
        tk.Checkbutton(topo, text='Aleatorio',
                       variable=self._var_aleatorio_comp,
                       bg=COR['painel2'], fg=COR['texto'],
                       selectcolor=COR['roxo'],
                       font=('Segoe UI', 9)).pack(side='left', padx=4)

        # modo
        self._var_modo_comp = tk.StringVar(value='celulas')
        tk.Radiobutton(topo, text='Celula', variable=self._var_modo_comp,
                       value='celulas', bg=COR['painel2'], fg=COR['texto'],
                       selectcolor=COR['roxo'],
                       font=('Segoe UI', 8)).pack(side='left', padx=4)
        tk.Radiobutton(topo, text='Passo', variable=self._var_modo_comp,
                       value='passos', bg=COR['painel2'], fg=COR['texto'],
                       selectcolor=COR['roxo'],
                       font=('Segoe UI', 8)).pack(side='left', padx=2)

        # velocidade
        self._var_vel_comp = tk.IntVar(value=100)
        tk.Label(topo, text='Vel:', bg=COR['painel2'], fg=COR['cinza'],
                 font=('Segoe UI', 8)).pack(side='left', padx=(6, 2))
        tk.Scale(topo, variable=self._var_vel_comp,
                 from_=20, to=1000, resolution=20,
                 orient='horizontal', bg=COR['painel2'], fg=COR['texto'],
                 troughcolor=COR['painel'], highlightthickness=0,
                 length=100, showvalue=False).pack(side='left')

        cfg = dict(relief='flat', cursor='hand2', font=('Segoe UI', 9))

        self._agentes_ativos_comp = {}
        for agente in self._agentes:
            cor = CORES_AGENTES.get(agente.nome, COR['roxo'])
            var = tk.BooleanVar(value=True)
            self._agentes_ativos_comp[agente.nome] = var
            tk.Checkbutton(topo, text=agente.nome.split('(')[0].strip(), variable=var,
                           bg=COR['painel2'], fg=cor,
                           selectcolor=COR['painel2'],
                           activebackground=COR['painel2'],
                           font=('Segoe UI', 8, 'bold'),
                           command=self._comp_ajustar_colunas).pack(side='left', padx=5)

        tk.Button(topo, text='Comparar', bg=COR['roxo'], fg='white',
                  command=self._comp_rodar, **cfg).pack(side='left', padx=6)

        tk.Button(topo, text='|<', bg=COR['painel'], fg=COR['texto'],
                  command=self._comp_reiniciar, **cfg).pack(side='left', padx=2)

        tk.Button(topo, text='<', bg=COR['painel'], fg=COR['texto'],
                  command=self._comp_voltar, **cfg).pack(side='left', padx=2)

        self._btn_comp_play = tk.Button(topo, text='Play',
                                        bg=COR['roxo'], fg='white',
                                        command=self._comp_toggle, **cfg)
        self._btn_comp_play.pack(side='left', padx=2)

        tk.Button(topo, text='>', bg=COR['painel'], fg=COR['texto'],
                  command=self._comp_avancar, **cfg).pack(side='left', padx=2)

        tk.Button(topo, text='>|', bg=COR['painel'], fg=COR['texto'],
                  command=self._comp_ir_fim, **cfg).pack(side='left', padx=2)

        self._lbl_passo_comp = tk.Label(topo, text='0 / 0',
                                        bg=COR['painel2'], fg=COR['texto'],
                                        font=('Consolas', 9, 'bold'))
        self._lbl_passo_comp.pack(side='left', padx=10)

        cont = tk.Frame(pai, bg=COR['fundo'])
        cont.pack(fill='both', expand=True, padx=6, pady=4)

        hbar_comp = ttk.Scrollbar(cont, orient='horizontal')
        hbar_comp.pack(side='bottom', fill='x')

        self._cv_comp = tk.Canvas(cont, bg=COR['fundo'], highlightthickness=0,
                                   xscrollcommand=hbar_comp.set)
        hbar_comp.config(command=self._cv_comp.xview)
        self._cv_comp.pack(side='top', fill='both', expand=True)
        self._cv_comp.bind('<MouseWheel>',
            lambda e: self._cv_comp.xview_scroll(-(e.delta // 120), 'units'))

        corpo = tk.Frame(self._cv_comp, bg=COR['fundo'])
        self._corpo_win = self._cv_comp.create_window((0, 0), window=corpo, anchor='nw')

        def _sync_altura(e):
            self._cv_comp.configure(scrollregion=self._cv_comp.bbox('all'))
            self._cv_comp.itemconfigure(self._corpo_win, height=e.height)
            self._comp_ajustar_colunas()
        self._cv_comp.bind('<Configure>', _sync_altura)
        corpo.bind('<Configure>',
            lambda *_: self._cv_comp.configure(scrollregion=self._cv_comp.bbox('all')))

        self._comp_cols = {}
        self._comp_grids = {}
        self._comp_cache = {}

        for idx in range(len(self._agentes)):
            agente = self._agentes[idx]
            cor = CORES_AGENTES.get(agente.nome, COR['roxo'])

            col = tk.Frame(corpo, bg=COR['painel'])
            col.pack(side='left', fill='y', padx=3)

            tk.Label(col, text=agente.nome, bg=cor, fg='white',
                     font=('Segoe UI', 9, 'bold'), pady=5).pack(fill='x')

            gf = tk.Frame(col, bg=COR['painel'])
            gf.pack(fill='both', expand=True, padx=4, pady=4)

            lp = tk.Label(col, text='0 / 0', bg=COR['painel'],
                          fg=COR['cinza'], font=('Consolas', 9))
            lp.pack()

            df = tk.Frame(col, bg=COR['painel'], height=60)
            df.pack(fill='x', padx=6, pady=2)
            df.pack_propagate(False)
            ld = tk.Label(df, text=DESCRICAO_AGENTES.get(agente.nome, ''),
                          bg=COR['painel'], fg=COR['ciano'],
                          font=('Consolas', 11), wraplength=260,
                          justify='left', anchor='nw')
            ld.pack(fill='both', expand=True)

            m = PainelMetricas(col)
            m.pack(fill='x', padx=2, pady=2)

            self._comp_cols[agente.nome] = {
                'col': col, 'frame': gf, 'metricas': m, 'lbl': lp, 'desc': ld,
            }

        self._comp_carregar()

    def _comp_carregar(self):
        texto_tam = self._var_tam_comp.get()
        tamanho = int(texto_tam.split('x')[0])

        puzzles = puzzles_por_tamanho(tamanho)
        nomes = []
        self._comp_cache = {}
        for p in puzzles:
            nomes.append(p.nome)
            self._comp_cache[p.nome] = p

        self._cb_puz_comp['values'] = nomes
        if nomes:
            self._var_puz_comp.set(nomes[0])

    def _comp_rodar(self):
        self._comp_parar()

        if self._var_aleatorio_comp.get():
            texto_tam = self._var_tam_comp.get()
            tamanho = int(texto_tam.split('x')[0])
            puzzle_base = gerar_puzzle_aleatorio(tamanho)
        else:
            nome_puz = self._var_puz_comp.get()
            puzzle_base = self._comp_cache.get(nome_puz)
            if puzzle_base is None:
                return

        self._comp_puzzle = puzzle_base

        # limpar grids e metricas
        for nome, col in self._comp_cols.items():
            for w in col['frame'].winfo_children():
                w.destroy()
            col['metricas'].limpar()
            col['lbl'].config(text='0 / 0')

        def worker():
            resultados = []
            historicos = []

            modo = self._var_modo_comp.get()

            for agente in self._agentes:
                if not self._agentes_ativos_comp[agente.nome].get():
                    resultados.append(None)
                    historicos.append([])
                    continue

                p = puzzle_base.copiar()
                resultado = agente.resolver(p)
                resultados.append(resultado)

                if modo == 'celulas':
                    hist = resultado['historico_celulas']
                else:
                    hist = resultado['historico_passos']

                if len(hist) == 0:
                    tab_vazio = []
                    for i in range(puzzle_base.linhas):
                        linha = []
                        for j in range(puzzle_base.colunas):
                            linha.append(DESCONHECIDO)
                        tab_vazio.append(linha)
                    hist = [tab_vazio]

                historicos.append(hist)

            self._comp_resultados = resultados
            self._comp_historicos = historicos
            self.after(0, lambda: self._comp_init(puzzle_base))

        threading.Thread(target=worker, daemon=True).start()

    def _comp_init(self, puzzle):
        self.update_idletasks()

        ativos = [a for a in self._agentes if self._agentes_ativos_comp[a.nome].get()]
        n = len(ativos)
        if n == 0:
            return

        win_w = self._cv_comp.winfo_width()
        if win_w < 200:
            win_w = self.winfo_width() - 30
        col_w_budget = max(200, (win_w - 6 * n) // n)

        exemplo = self._comp_cols[ativos[0].nome]
        altura_disp = exemplo['frame'].winfo_height()
        if altura_disp < 80:
            altura_disp = self.winfo_height() - 260

        tc = self._calc_tc_comp(puzzle, col_w_budget, altura_disp)

        mr = max((len(c) for c in puzzle.pistas_linha), default=1)
        grid_w = mr * tc + puzzle.colunas * tc + 20
        col_w = max(grid_w, col_w_budget)

        self._comp_grids_w = []

        for idx in range(len(self._agentes)):
            agente = self._agentes[idx]
            col = self._comp_cols[agente.nome]

            if not self._agentes_ativos_comp[agente.nome].get():
                self._comp_grids_w.append(None)
                continue

            col['col'].config(width=col_w)
            col['col'].pack_propagate(False)
            col['desc'].config(wraplength=col_w - 20)

            gw = GridCanvas(col['frame'], puzzle, tc=tc)
            gw.pack(expand=True)
            self._comp_grids_w.append(gw)

        self._comp_idxs = []
        for i in range(len(self._agentes)):
            self._comp_idxs.append(0)

        self._comp_idx = 0
        self._comp_rodando = True
        self._btn_comp_play.config(text='Pause', bg=COR['amarelo'])
        self._comp_tick()

    def _comp_maior(self):
        maior = 0
        for hist in self._comp_historicos:
            if len(hist) > maior:
                maior = len(hist)
        return maior

    def _comp_tick(self):
        if not self._comp_rodando:
            return

        if len(self._comp_resultados) < len(self._agentes):
            self._comp_rodando = False
            return
        if len(self._comp_grids_w) < len(self._agentes):
            self._comp_rodando = False
            return

        algum = False
        maior = self._comp_maior()

        modo = self._var_modo_comp.get()
        chave_desc = 'descricoes' if modo == 'celulas' else 'descricoes_passos'

        for idx in range(len(self._agentes)):
            agente = self._agentes[idx]
            resultado = self._comp_resultados[idx]
            hist = self._comp_historicos[idx]
            pos = self._comp_idxs[idx]
            total = len(hist)
            col = self._comp_cols[agente.nome]

            if resultado is None or self._comp_grids_w[idx] is None:
                continue

            if pos < total:
                destaque = None
                if pos > 0:
                    ant = hist[pos - 1]
                    cur = hist[pos]
                    for i in range(len(cur)):
                        for j in range(len(cur[0])):
                            if cur[i][j] != ant[i][j]:
                                destaque = (i, j)
                                break
                        if destaque:
                            break

                try:
                    self._comp_grids_w[idx].atualizar(hist[pos], destaque)
                except tk.TclError:
                    self._comp_rodando = False
                    return

                col['lbl'].config(text=str(pos + 1) + ' / ' + str(total))

                descs = resultado.get(chave_desc, [])
                if pos < len(descs):
                    col['desc'].config(text=descs[pos])

                self._comp_idxs[idx] = pos + 1
                algum = True
            else:
                try:
                    if hist:
                        self._comp_grids_w[idx].atualizar(hist[-1])
                except tk.TclError:
                    self._comp_rodando = False
                    return
                col['metricas'].atualizar(resultado)
                col['lbl'].config(text='Pronto (' + str(len(hist)) + ' frames)')
                col['desc'].config(text=DESCRICAO_AGENTES.get(agente.nome, ''))

        self._comp_idx = self._comp_idx + 1
        self._lbl_passo_comp.config(text=str(self._comp_idx) + ' / ' + str(maior))

        if algum:
            self._comp_after = self.after(self._var_vel_comp.get(), self._comp_tick)
        else:
            self._comp_rodando = False
            self._btn_comp_play.config(text='Play', bg=COR['roxo'])

    def _comp_parar(self):
        self._comp_rodando = False
        if self._comp_after:
            self.after_cancel(self._comp_after)
            self._comp_after = None

    def _comp_toggle(self):
        if self._comp_rodando:
            self._comp_parar()
            self._btn_comp_play.config(text='Play', bg=COR['roxo'])
        else:
            if not self._comp_resultados or len(self._comp_grids_w) < len(self._agentes):
                return
            self._comp_rodando = True
            self._btn_comp_play.config(text='Pause', bg=COR['amarelo'])
            self._comp_tick()

    def _comp_reiniciar(self):
        self._comp_parar()
        if not self._comp_historicos or len(self._comp_grids_w) < len(self._agentes):
            return

        for idx in range(len(self._agentes)):
            self._comp_idxs[idx] = 0
            if self._comp_grids_w[idx] is None:
                continue
            hist = self._comp_historicos[idx]
            try:
                if hist:
                    self._comp_grids_w[idx].atualizar(hist[0])
            except tk.TclError:
                return

        self._comp_idx = 0
        self._lbl_passo_comp.config(text='0 / ' + str(self._comp_maior()))

    def _comp_voltar(self):
        self._comp_parar()
        if not self._comp_historicos or len(self._comp_grids_w) < len(self._agentes):
            return

        for idx in range(len(self._agentes)):
            if self._comp_grids_w[idx] is None:
                continue
            pos = self._comp_idxs[idx]
            if pos > 1:
                self._comp_idxs[idx] = pos - 1
                hist = self._comp_historicos[idx]
                try:
                    self._comp_grids_w[idx].atualizar(hist[pos - 2])
                except tk.TclError:
                    return
                col = self._comp_cols[self._agentes[idx].nome]
                col['lbl'].config(text=str(pos - 1) + ' / ' + str(len(hist)))

        if self._comp_idx > 0:
            self._comp_idx = self._comp_idx - 1
        self._lbl_passo_comp.config(text=str(self._comp_idx) + ' / ' + str(self._comp_maior()))

    def _comp_avancar(self):
        self._comp_parar()
        if not self._comp_historicos or len(self._comp_grids_w) < len(self._agentes):
            return

        for idx in range(len(self._agentes)):
            if self._comp_grids_w[idx] is None:
                continue
            pos = self._comp_idxs[idx]
            hist = self._comp_historicos[idx]
            if pos < len(hist):
                try:
                    self._comp_grids_w[idx].atualizar(hist[pos])
                except tk.TclError:
                    return
                self._comp_idxs[idx] = pos + 1
                col = self._comp_cols[self._agentes[idx].nome]
                col['lbl'].config(text=str(pos + 1) + ' / ' + str(len(hist)))

        self._comp_idx = self._comp_idx + 1
        self._lbl_passo_comp.config(text=str(self._comp_idx) + ' / ' + str(self._comp_maior()))

    def _comp_ir_fim(self):
        self._comp_parar()
        if not self._comp_historicos or len(self._comp_grids_w) < len(self._agentes):
            return
        for idx in range(len(self._agentes)):
            if self._comp_grids_w[idx] is None:
                continue
            hist = self._comp_historicos[idx]
            try:
                if hist:
                    self._comp_grids_w[idx].atualizar(hist[-1])
                    self._comp_idxs[idx] = len(hist)
                    col = self._comp_cols[self._agentes[idx].nome]
                    col['lbl'].config(text=str(len(hist)) + ' / ' + str(len(hist)))
            except tk.TclError:
                return
        self._comp_idx = self._comp_maior()
        self._lbl_passo_comp.config(text=str(self._comp_idx) + ' / ' + str(self._comp_maior()))




    def _build_bench(self, pai):
        topo = tk.Frame(pai, bg=COR['painel2'])
        topo.pack(fill='x', padx=6, pady=6)

        tk.Button(topo, text='Rodar Benchmark',
                  bg=COR['verde'], fg='white', relief='flat', cursor='hand2',
                  font=('Segoe UI', 9, 'bold'), pady=6,
                  command=self._bench_rodar).pack(side='left', padx=8)

        tk.Label(topo, text='Tam. aleatorio:', bg=COR['painel2'],
                 fg=COR['cinza'], font=('Segoe UI', 9)).pack(side='left', padx=(12, 4))

        tam_nomes = []
        for t in TAMANHOS:
            tam_nomes.append(str(t) + 'x' + str(t))

        self._var_tam_bench = tk.StringVar(value=tam_nomes[0])
        ttk.Combobox(topo, textvariable=self._var_tam_bench,
                     values=tam_nomes, state='readonly',
                     width=6).pack(side='left', padx=2)

        tk.Button(topo, text='Rodar com puzzle aleatorio',
                  bg=COR['roxo'], fg='white', relief='flat', cursor='hand2',
                  font=('Segoe UI', 9, 'bold'), pady=6,
                  command=self._bench_aleatorio).pack(side='left', padx=8)

        self._lbl_bench_st = tk.Label(topo, text='',
                                      bg=COR['painel2'], fg=COR['amarelo'],
                                      font=('Segoe UI', 9, 'bold'))
        self._lbl_bench_st.pack(side='right', padx=12)

        corpo = tk.Frame(pai, bg=COR['fundo'])
        corpo.pack(fill='both', expand=True, padx=6, pady=4)

        esq = tk.Frame(corpo, bg=COR['painel'], width=200)
        esq.pack(side='left', fill='y', padx=(0, 6))
        esq.pack_propagate(False)

        tk.Label(esq, text='AGENTES ATIVOS', bg=COR['painel'], fg=COR['roxo'],
                 font=('Segoe UI', 9, 'bold')).pack(anchor='w', padx=8, pady=(10, 6))

        self._agentes_ativos = {}
        for agente in self._agentes:
            cor = CORES_AGENTES.get(agente.nome, COR['roxo'])
            var = tk.BooleanVar(value=True)
            self._agentes_ativos[agente.nome] = var
            tk.Checkbutton(esq, text=agente.nome, variable=var,
                           bg=COR['painel'], fg=cor,
                           selectcolor=COR['painel2'],
                           activebackground=COR['painel'],
                           font=('Segoe UI', 9, 'bold'),
                           wraplength=175, justify='left').pack(anchor='w', padx=10, pady=4)

        dir_f = tk.Frame(corpo, bg=COR['fundo'])
        dir_f.pack(side='left', fill='both', expand=True)

        self._txt_bench = tk.Text(dir_f, height=30, width=90,
                                   bg=COR['painel'], fg=COR['texto'],
                                   font=('Consolas', 9), relief='flat',
                                   insertbackground=COR['texto'])
        self._txt_bench.pack(fill='both', expand=True)

    def _agentes_selecionados(self):
        return [a for a in self._agentes
                if self._agentes_ativos.get(a.nome, tk.BooleanVar(value=True)).get()]

    def _bench_rodar(self):
        agentes_sel = self._agentes_selecionados()
        if not agentes_sel:
            self._lbl_bench_st.config(text='Nenhum agente ativo!', fg=COR['verm'])
            return

        self._txt_bench.delete('1.0', tk.END)
        self._txt_bench.insert(tk.END,
            'Rodando benchmark com {} agente(s), aguarde...\n'.format(len(agentes_sel)))
        self._lbl_bench_st.config(text='Rodando...', fg=COR['amarelo'])
        self.update()

        def worker():
            from benchmark import rodar_benchmark
            resultados = rodar_benchmark(agentes=agentes_sel)
            self.after(0, lambda: self._bench_mostrar(resultados))

        threading.Thread(target=worker, daemon=True).start()

    def _bench_mostrar(self, resultados):
        self._txt_bench.delete('1.0', tk.END)
        self._lbl_bench_st.config(text='Pronto!', fg=COR['verde'])

        cabecalho = '{:<20} {:<30} {:<10} {:<12} {:<8}\n'.format(
            'puzzle', 'agente', 'resolvido', 'tempo (ms)', 'passos'
        )
        self._txt_bench.insert(tk.END, cabecalho)
        self._txt_bench.insert(tk.END, '-' * 85 + '\n')

        for r in resultados:
            tempo_ms = r['tempo'] * 1000
            linha = '{:<20} {:<30} {:<10} {:<12.3f} {:<8}\n'.format(
                r['puzzle'], r['nome'], str(r['resolvido']), tempo_ms, r['passos']
            )
            self._txt_bench.insert(tk.END, linha)

    def _bench_aleatorio(self):
        texto_tam = self._var_tam_bench.get()
        tamanho = int(texto_tam.split('x')[0])
        puzzle_base = gerar_puzzle_aleatorio(tamanho)

        self._txt_bench.delete('1.0', tk.END)
        self._txt_bench.insert(tk.END, 'Puzzle aleatorio ' + str(tamanho) + 'x' + str(tamanho) + '\n')
        self._txt_bench.insert(tk.END, 'Todos os agentes resolvem o MESMO puzzle\n\n')
        self._lbl_bench_st.config(text='Rodando...', fg=COR['amarelo'])
        self.update()

        def worker():
            resultados = []
            for agente in self._agentes:
                p = puzzle_base.copiar()
                resultado = agente.resolver(p)
                resultados.append(resultado)
            self.after(0, lambda: self._bench_mostrar_aleatorio(resultados))

        threading.Thread(target=worker, daemon=True).start()

    def _bench_mostrar_aleatorio(self, resultados):
        self._lbl_bench_st.config(text='Pronto!', fg=COR['verde'])

        cabecalho = '{:<30} {:<10} {:<12} {:<8}\n'.format(
            'agente', 'resolvido', 'tempo (ms)', 'passos'
        )
        self._txt_bench.insert(tk.END, cabecalho)
        self._txt_bench.insert(tk.END, '-' * 65 + '\n')

        for r in resultados:
            tempo_ms = r['tempo'] * 1000
            linha = '{:<30} {:<10} {:<12.3f} {:<8}\n'.format(
                r['nome'], str(r['resolvido']), tempo_ms, r['passos']
            )
            self._txt_bench.insert(tk.END, linha)



    def _build_graf(self, pai):
        topo = tk.Frame(pai, bg=COR['painel2'])
        topo.pack(fill='x', padx=6, pady=6)

        tk.Button(topo, text='Gerar Graficos',
                  bg=COR['verde'], fg='white', relief='flat', cursor='hand2',
                  font=('Segoe UI', 10, 'bold'), pady=8,
                  command=self._graf_gerar).pack(side='left', padx=12)

        self._lbl_graf_st = tk.Label(topo, text='',
                                     bg=COR['painel2'], fg=COR['amarelo'],
                                     font=('Segoe UI', 9, 'bold'))
        self._lbl_graf_st.pack(side='left', padx=8)

        corpo = tk.Frame(pai, bg=COR['fundo'])
        corpo.pack(fill='both', expand=True, padx=6, pady=4)

        esq = tk.Frame(corpo, bg=COR['painel'], width=200)
        esq.pack(side='left', fill='y', padx=(0, 6))
        esq.pack_propagate(False)

        tk.Label(esq, text='AGENTES ATIVOS', bg=COR['painel'], fg=COR['roxo'],
                 font=('Segoe UI', 9, 'bold')).pack(anchor='w', padx=8, pady=(10, 6))

        self._agentes_ativos_graf = {}
        for agente in self._agentes:
            cor = CORES_AGENTES.get(agente.nome, COR['roxo'])
            var = tk.BooleanVar(value=True)
            self._agentes_ativos_graf[agente.nome] = var
            tk.Checkbutton(esq, text=agente.nome, variable=var,
                           bg=COR['painel'], fg=cor,
                           selectcolor=COR['painel2'],
                           activebackground=COR['painel'],
                           font=('Segoe UI', 9, 'bold'),
                           wraplength=175, justify='left').pack(anchor='w', padx=10, pady=4)

        self._frame_graf = tk.Frame(corpo, bg=COR['fundo'])
        self._frame_graf.pack(side='left', fill='both', expand=True)

        self._ph_graf = tk.Label(
            self._frame_graf,
            text='Clique em Gerar Graficos',
            bg=COR['fundo'], fg=COR['cinza'], font=('Segoe UI', 13),
        )
        self._ph_graf.pack(expand=True)

        self._imgs_graf = []

    def _agentes_selecionados_graf(self):
        return [a for a in self._agentes
                if self._agentes_ativos_graf.get(a.nome, tk.BooleanVar(value=True)).get()]

    def _graf_gerar(self):
        if not TEM_MPL:
            self._lbl_graf_st.config(text='matplotlib nao encontrado!', fg=COR['verm'])
            return

        agentes_sel = self._agentes_selecionados_graf()
        if not agentes_sel:
            self._lbl_graf_st.config(text='Nenhum agente ativo!', fg=COR['verm'])
            return

        self._lbl_graf_st.config(
            text='Gerando ({} agentes)...'.format(len(agentes_sel)),
            fg=COR['amarelo'])
        self.update()

        def worker():
            from benchmark import rodar_benchmark
            resultados = rodar_benchmark(agentes=agentes_sel)
            self.after(0, lambda: self._graf_mostrar(resultados))

        threading.Thread(target=worker, daemon=True).start()

    def _graf_mostrar(self, resultados):
        self._lbl_graf_st.config(text='Pronto!', fg=COR['verde'])
        self._ph_graf.pack_forget()

        for w in self._frame_graf.winfo_children():
            w.destroy()

        # organizar dados por agente e tamanho
        dados = {}
        for r in resultados:
            nome = r['nome']
            tamanho = r.get('tamanho', 0)
            if nome not in dados:
                dados[nome] = {}
            if tamanho not in dados[nome]:
                dados[nome][tamanho] = []
            dados[nome][tamanho].append(r)

        nomes_agentes = list(dados.keys())
        cores = []
        for n in nomes_agentes:
            cores.append(CORES_AGENTES.get(n, '#888888'))

        #os 3 graficos
        fig, eixos = plt.subplots(1, 3, figsize=(14, 4.5), facecolor=COR['fundo'])
        fig.suptitle('Comparacao dos Agentes', color=COR['texto'],
                     fontsize=13, fontweight='bold')

        titulos = ['Tempo Medio (ms)', 'Passos Medios', 'Taxa Resolucao (%)']
        campos = ['tempo', 'passos', 'resolvido']

        for g in range(3):
            ax = eixos[g]
            ax.set_facecolor(COR['painel'])
            ax.set_title(titulos[g], color=COR['texto'], fontsize=10)
            ax.tick_params(colors=COR['cinza'])
            for sp in ax.spines.values():
                sp.set_edgecolor(COR['borda'])
            ax.grid(axis='y', color=COR['borda'], alpha=0.3)

            larg = 0.18
            tams_presentes = sorted(dados[nomes_agentes[0]].keys())
            x = list(range(len(tams_presentes)))

            for k in range(len(nomes_agentes)):
                nome = nomes_agentes[k]
                cor_b = cores[k]
                vals = []

                for tam in tams_presentes:
                    lista = dados[nome].get(tam, [])
                    if g == 0:  # tempo medio em ms
                        total = 0
                        for r in lista:
                            total = total + r['tempo']
                        media = (total / len(lista)) * 1000 if lista else 0
                        vals.append(media)
                    elif g == 1:  # passos medios
                        total = 0
                        for r in lista:
                            total = total + r['passos']
                        media = total / len(lista) if lista else 0
                        vals.append(media)
                    else:  # taxa resolucao %
                        resolvidos = 0
                        for r in lista:
                            if r['resolvido']:
                                resolvidos = resolvidos + 1
                        taxa = (resolvidos / len(lista)) * 100 if lista else 0
                        vals.append(taxa)

                off = (k - len(nomes_agentes) / 2) * larg
                barras_x = []
                for xi in x:
                    barras_x.append(xi + off)

                ax.bar(barras_x, vals, width=larg, label=nome,
                       color=cor_b, alpha=0.85, edgecolor=COR['borda'])

            labels_x = []
            for tam in tams_presentes:
                labels_x.append(str(tam) + 'x' + str(tam))

            ax.set_xticks(x)
            ax.set_xticklabels(labels_x, color=COR['cinza'], fontsize=8)

        # legenda unica
        handles = []
        for k in range(len(nomes_agentes)):
            h = plt.Rectangle((0, 0), 1, 1, fc=cores[k], label=nomes_agentes[k])
            handles.append(h)
        fig.legend(handles=handles, loc='lower center',
                   ncol=len(nomes_agentes),
                   facecolor=COR['painel'], labelcolor=COR['texto'],
                   fontsize=8, framealpha=0.8)

        plt.tight_layout(rect=[0, 0.08, 1, 0.95])

        canvas = FigureCanvasTkAgg(fig, self._frame_graf)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        plt.close(fig)


if __name__ == '__main__':
    app = App()
    app.mainloop()