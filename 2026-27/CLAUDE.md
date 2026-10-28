# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Lecture material (notebooks and small code fragments) for the *Computational Intelligence* course (01URROV / 01URRSM) at Politecnico di Torino. The git root is `../` and holds one directory per academic year (`2021-22` … `2026-27`) plus the shared `README.md` and `LICENSE`; this directory is the current year. Earlier year directories are frozen archives — use them as reference (e.g. `../2025-26/gx_utils.py`, earlier search/EA notebooks), but don't edit them unless asked.

This is teaching code: clarity and readability for students matter more than generality or performance. Notebooks are developed live during lectures and committed with their outputs. There is no test suite, no build step and no local lint config.

## Environment

Each year directory is a self-contained [uv](https://docs.astral.sh/uv/) project (`pyproject.toml`, `uv.lock`, `.venv/` here). Python is pinned to `3.14+freethreaded` (`.python-version`); notebooks use the local `.venv` kernel.

```sh
uv sync                        # create/update .venv from uv.lock
uv add <pkg>                   # add a dependency (updates pyproject.toml and uv.lock)
uv run jupyter lab             # work on notebooks
uv run python <script>.py
```

Direct dependencies: `icecream`, `jupyter`, `matplotlib`, `networkx`, `rich`, `scipy`, `tqdm`, `z3-solver` (`numpy` arrives transitively). When dependencies change, `THIRD_PARTY_LICENSES.md` must be updated to list the new package's license notice (same format as existing entries).

CI (`../.github/workflows/superlinter.yml`) runs GitHub Super-Linter only on non-master pushes and on PRs to master.

## Content

Notebooks follow the lecture order, from state-space search to single-state and population-based optimization:

- `alcuinus.ipynb` — Alcuin's river-crossing puzzle (brothers/sisters variant). Models states as `NamedTuple` with `frozenset` fields (hashable), enumerates the state space and the solution space, and draws them with `networkx` + `matplotlib`.
- `1-max.ipynb` — OneMax with a minimal hill climber (`fitness` / `tweak` on a `list[bool]`).
- `knapsack.ipynb`, `knapsack2.ipynb` — unbounded knapsack with hill climbing; solutions are `dict[object → quantity]`, overweight solutions get fitness 0. `knapsack2` adds a greedy start, a multi-move `tweak`, a no-improvement stop criterion and a fitness-history plot (`accumulate(history, max)`).
- `multiple-knapsack.ipynb` — 0-1 multi-dimensional knapsack in NumPy (seeded): Random-Mutation Hill Climber, RMHC with a stronger tweak, steepest step with restart.
- `rastrigin.ipynb` — Evolution Strategies on the (negated, i.e. maximized) Rastrigin function: vanilla (1+λ)-ES, adaptive (1+λ)-ES, adaptive (μ+λ)-ES.
- `upq/upq.py` — reusable updatable priority queue (lazy-deletion heap) for search algorithms such as Dijkstra/A*.

## Conventions

- Recurring vocabulary across optimization notebooks: `fitness` (or `evaluate`) / `tweak` functions, UPPER_CASE problem constants (`NUM_OBJECTS`, `MAX_WEIGHT`, `DIMENSION`, …), a `steps` counter, and a `history` list plotted at the end.
- Debug/progress output uses `icecream.ic`, `logging` (level `INFO`) and `tqdm.auto`. Seed randomness (`np.random.seed(42)`) when results are discussed in class.
- Reusable helpers go in small standalone modules/packages next to the notebooks (like `upq/`).
- Every source file and notebook starts with the copyright header — keep it on new files. Current form (as in `pyproject.toml`):

  ```python
  # Author: Giovanni Squillero <giovanni.squillero@polito.it>
  # Copyright © 2026 Giovanni Squillero / Politecnico di Torino
  # https://github.com/squillero/computational-intelligence
  # Free under certain conditions; see LICENSE for details.
  ```

  In notebooks it is the first markdown cell, with the same four lines as links (author `mailto`, `squillero.github.io`, `polito.it`, repo URL, and a link to `LICENSE` on GitHub), each ending with two spaces for line breaks. `LICENSE` is a symlink to `../LICENSE`.
