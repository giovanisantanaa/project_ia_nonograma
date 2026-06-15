import sys

sys.path.append("src")


if __name__ == "__main__":
    from interface import App

    app = App()
    app.mainloop()