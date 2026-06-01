# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**resourceAllocationOptimization** — Hospital resource allocation optimization comparing Grey Wolf Optimizer (GWO) vs Particle Swarm Optimization (PSO). Python 3.14, scaffolded with `uv`.

## Environment

- Python version: 3.14 (pinned in `.python-version`)
- Package manager: `uv`
- Package name: `rao` (module root: `src/`)
- Virtual environment: `.venv/` (excluded from git)
- Key dependencies: numpy, pandas, matplotlib, seaborn, scipy, jupyter, openpyxl

## Common Commands

```powershell
# Install dependencies
uv sync

# Run a single pipeline step
uv run main.py --step audit
uv run main.py --step preprocess
uv run main.py --step eda
uv run main.py --step optimize
uv run main.py --step report

# Run the full pipeline end-to-end
uv run main.py --all

# Add a dependency
uv add <package>
```

## Project Structure

```
main.py                  # CLI entry point — orchestrates pipeline steps
src/rao/
  config.py              # Paths, hyperparameters (POP_SIZE, MAX_ITER, N_RUNS, RANDOM_SEED)
  data/
    loader.py            # load_all_processed()
    audit.py             # run_full_audit()
    preprocessing.py     # preprocess_all()
    eda.py               # run_full_eda() → returns dict with "optimization_inputs"
  problem/
    formulation.py       # build_problem_from_inputs() → Problem object with .dim, .decode()
    objective.py         # Objective function(s)
  algorithms/
    base.py              # Abstract optimizer base class
    gwo.py               # Grey Wolf Optimizer
    pso.py               # Particle Swarm Optimization
  experiments/
    runner.py            # run_experiment(), save_results(), load_results()
    stats.py             # print_summary(), summary_table(), convergence_comparison()
  visualization/
    plots.py             # save_all_eda_plots(), plot_convergence_curves(), plot_fitness_boxplot(), plot_allocation_heatmap()
  report/
    generate.py          # build_report_notebook() → returns notebook path
data/                    # Raw and processed datasets
reports/                 # Generated report notebooks and outputs
```

## Git Conventions

### Branch Naming

Use `type/short-description` (kebab-case, lowercase):

```
feat/gwo-convergence-plot
fix/pso-velocity-clamp
chore/update-deps
docs/readme-update
refactor/objective-function
```

Types mirror conventional commit prefixes: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`.

### Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <short imperative summary>
```

| Type | When to use |
|---|---|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `chore` | Maintenance, deps, tooling |
| `docs` | Documentation only |
| `refactor` | Code restructure, no behavior change |
| `test` | Tests only |

Examples:
```
feat: add GWO convergence plot
fix: correct PSO velocity clamp
chore: update numpy to 2.x
docs: add pipeline step table to README
refactor: extract objective function to separate module
```

## Pipeline Steps

| Step | Entry point | Description |
|---|---|---|
| `audit` | `rao.data.audit.run_full_audit` | Data quality checks |
| `preprocess` | `rao.data.preprocessing.preprocess_all` | Clean and transform raw data |
| `eda` | `rao.data.eda.run_full_eda` | Exploratory analysis + feature engineering + EDA plots |
| `optimize` | `rao.experiments.runner.run_experiment` | Run GWO vs PSO, save results, generate comparison plots |
| `report` | `rao.report.generate.build_report_notebook` | Build Jupyter report notebook from saved results |