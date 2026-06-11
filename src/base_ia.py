# estruturas de busca - Problem, Node e os algoritmos
#(BFS, DFS, A*, Greedy)

class Problem:
    def __init__(self, initial, goal=None):
        self.initial = initial
        self.goal = goal

    def actions(self, state):
        raise NotImplementedError

    def result(self, state, action):
        raise NotImplementedError

    def goal_test(self, state):
        return state == self.goal

    def path_cost(self, c, state1, action, state2):
        return c + 1


class Node:
    def __init__(self, state, parent=None, action=None, path_cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.depth = 0 if parent is None else parent.depth + 1

    def __repr__(self):
        return '<Node {}>'.format(self.state)

    def __lt__(self, node):
        return self.state < node.state

    def expand(self, problem):
        return [self.child_node(problem, action) for action in problem.actions(self.state)]

    def child_node(self, problem, action):
        next_state = problem.result(self.state, action)
        return Node(
            next_state,
            self,
            action,
            problem.path_cost(self.path_cost, self.state, action, next_state),
        )

    def solution(self):
        return [node.action for node in self.path()[1:]]

    def path(self):
        node = self
        path_back = []
        while node is not None:
            path_back.append(node)
            node = node.parent
        path_back.reverse()
        return path_back

    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

    def __hash__(self):
        return hash(self.state)


class SimpleProblemSolvingAgentProgram:
    def __init__(self, initial_state=None):
        self.state = initial_state
        self.seq = []

    def __call__(self, percept):
        self.state = self.update_state(self.state, percept)
        if not self.seq:
            goal = self.formulate_goal(self.state)
            problem = self.formulate_problem(self.state, goal)
            self.seq = self.search(problem)
            if not self.seq:
                return None
        return self.seq.pop(0)

    def update_state(self, state, percept):
        raise NotImplementedError

    def formulate_goal(self, state):
        raise NotImplementedError

    def formulate_problem(self, state, goal):
        raise NotImplementedError

    def search(self, problem):
        raise NotImplementedError


def breadth_first_graph_search(problem):
    node = Node(problem.initial)
    if problem.goal_test(node.state):
        return node
    frontier = [node]
    visited = set()
    while frontier:
        node = frontier.pop(0)
        visited.add(node.state)
        for child in node.expand(problem):
            if child.state not in visited and child not in frontier:
                if problem.goal_test(child.state):
                    return child
                frontier.append(child)
    return None


def depth_first_graph_search(problem):
    frontier = [Node(problem.initial)]
    visited = set()
    while frontier:
        node = frontier.pop()
        if problem.goal_test(node.state):
            return node
        visited.add(node.state)
        for child in node.expand(problem):
            if child.state not in visited and child not in frontier:
                frontier.append(child)
    return None


def greedy_best_first_search(problem, h):
    frontier = []
    visited = set()
    best_h = {}
    initial_node = Node(problem.initial)
    frontier.append(initial_node)
    best_h[initial_node.state] = h(initial_node)
    while frontier:
        frontier.sort(key=lambda node: (h(node), str(node.state)))
        node = frontier.pop(0)
        if node.state in visited:
            continue
        if h(node) > best_h.get(node.state, float('inf')):
            continue
        if problem.goal_test(node.state):
            return node
        visited.add(node.state)
        for child in node.expand(problem):
            child_h = h(child)
            if child.state not in visited and child_h < best_h.get(child.state, float('inf')):
                best_h[child.state] = child_h
                frontier.append(child)
    return None


def astar_search(problem, h):
    frontier = []
    visited = set()
    best_f = {}
    initial_node = Node(problem.initial)
    frontier.append(initial_node)
    best_f[initial_node.state] = initial_node.path_cost + h(initial_node)
    while frontier:
        frontier.sort(key=lambda node: (node.path_cost + h(node), str(node.state)))
        node = frontier.pop(0)
        f_value = node.path_cost + h(node)
        if node.state in visited:
            continue
        if f_value > best_f.get(node.state, float('inf')):
            continue
        if problem.goal_test(node.state):
            return node
        visited.add(node.state)
        for child in node.expand(problem):
            child_f = child.path_cost + h(child)
            if child.state not in visited and child_f < best_f.get(child.state, float('inf')):
                best_f[child.state] = child_f
                frontier.append(child)
    return None