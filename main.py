"""
Hospital Resource Allocation Optimization — CLI entry point.

Usage:
    uv run main.py --step audit
    uv run main.py --step preprocess
    uv run main.py --step eda
    uv run main.py --step optimize
    uv run main.py --step report
    uv run main.py --all
"""
from __future__ import annotations

import argparse


def run_audit() -> None:
    from rao.data.audit import run_full_audit
    print("=" * 60)
    print("STEP: Data Quality Audit")
    print("=" * 60)
    run_full_audit()


def run_preprocess() -> None:
    from rao.data.preprocessing import preprocess_all
    print("=" * 60)
    print("STEP: Preprocessing")
    print("=" * 60)
    preprocess_all()


def run_eda() -> None:
    from rao.data.loader import load_all_processed
    from rao.data.eda import run_full_eda
    from rao.visualization.plots import save_all_eda_plots
    from rao.config import FIGURES_DIR

    print("=" * 60)
    print("STEP: EDA & Feature Engineering")
    print("=" * 60)
    dfs = load_all_processed()
    eda_result = run_full_eda(dfs)
    save_all_eda_plots(eda_result, figures_dir=FIGURES_DIR)


def run_optimize() -> None:
    from rao.data.loader import load_all_processed
    from rao.data.eda import run_full_eda
    from rao.problem.formulation import build_problem_from_inputs
    from rao.experiments.runner import run_experiment, save_results
    from rao.experiments.stats import print_summary
    from rao.visualization.plots import (
        plot_convergence_curves,
        plot_fitness_boxplot,
        plot_allocation_heatmap,
    )
    from rao.config import FIGURES_DIR, MAX_ITER, N_RUNS, POP_SIZE, RANDOM_SEED

    print("=" * 60)
    print("STEP: Optimization Experiment (GWO vs PSO)")
    print("=" * 60)

    dfs = load_all_processed()
    eda_result = run_full_eda(dfs)
    inputs = eda_result["optimization_inputs"]

    problem = build_problem_from_inputs(inputs)
    print(f"Problem dimension: {problem.dim}")

    gwo_results, pso_results = run_experiment(
        problem, n_runs=N_RUNS, pop_size=POP_SIZE, max_iter=MAX_ITER, base_seed=RANDOM_SEED
    )
    save_results(gwo_results, pso_results)
    print_summary(gwo_results, pso_results)

    gwo_histories = [r.history for r in gwo_results]
    pso_histories = [r.history for r in pso_results]
    gwo_fitnesses = [r.best_fitness for r in gwo_results]
    pso_fitnesses = [r.best_fitness for r in pso_results]

    plot_convergence_curves(gwo_histories, pso_histories,
                            save_path=FIGURES_DIR / "convergence_curves.png")
    plot_fitness_boxplot(gwo_fitnesses, pso_fitnesses,
                         save_path=FIGURES_DIR / "fitness_boxplot.png")

    best_gwo = min(gwo_results, key=lambda r: r.best_fitness)
    staff_matrix, _ = problem.decode(best_gwo.best_x)
    plot_allocation_heatmap(
        staff_matrix,
        row_labels=[str(d) for d in inputs.get("shift_dates", list(range(staff_matrix.shape[0])))],
        col_labels=inputs.get("staff_types", ["Surgeon", "Nurse", "Technician"]),
        title="Best GWO Staff Allocation (Shifts × Staff Types)",
        save_path=FIGURES_DIR / "best_allocation_heatmap.png",
    )
    print(f"[optimize] Plots saved to {FIGURES_DIR}")


def run_report() -> None:
    from rao.experiments.runner import load_results
    from rao.experiments.stats import summary_table, convergence_comparison
    from rao.report.generate import build_report_notebook
    from rao.config import FIGURES_DIR

    print("=" * 60)
    print("STEP: Report Generation")
    print("=" * 60)

    gwo_results, pso_results = load_results()
    s_df = summary_table(gwo_results, pso_results)
    gwo_histories = [r.history for r in gwo_results]
    pso_histories = [r.history for r in pso_results]
    c_df = convergence_comparison(gwo_histories, pso_histories)

    path = build_report_notebook(s_df, c_df, figures_dir=FIGURES_DIR)
    print(f"[report] Open with: uv run jupyter notebook {path}")


_STEPS = {
    "audit": run_audit,
    "preprocess": run_preprocess,
    "eda": run_eda,
    "optimize": run_optimize,
    "report": run_report,
}

_PIPELINE = ["audit", "preprocess", "eda", "optimize", "report"]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Hospital Resource Allocation Optimization Pipeline"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--step",
        choices=list(_STEPS.keys()),
        help="Run a single pipeline step",
    )
    group.add_argument(
        "--all",
        action="store_true",
        help="Run the full pipeline end-to-end",
    )
    args = parser.parse_args()

    if args.all:
        for step in _PIPELINE:
            print(f"\n{'#'*60}")
            print(f"#  Running step: {step.upper()}")
            print(f"{'#'*60}\n")
            _STEPS[step]()
    else:
        _STEPS[args.step]()


if __name__ == "__main__":
    main()
