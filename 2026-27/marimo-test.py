import marimo

__generated_with = "0.24.0"
app = marimo.App()


@app.cell
def _(mo):
    mo.md(r"""
    Copyright © 2026 [Giovanni Squillero](https://squillero.github.io/) / [Politecnico di Torino](https://www.polito.it)
    [`https://github.com/squillero/computational-intelligence`](https://github.com/squillero/computational-intelligence)
    Free under certain conditions — see the [`license`](https://github.com/squillero/computational-intelligence/blob/master/LICENSE) for details.
    """)
    return


@app.cell
def _():
    1+1
    return


if __name__ == "__main__":
    app.run()
