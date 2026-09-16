#!/usr/bin/env python3
"""
Prompting-strategy statistical analysis for the QUS-13 experiment.

Preserved inputs are in results/rq1/metrics/.
Generated outputs default to replication_runs/latest/results/rq2/statistical_analysis/.
Set TOSEM_OUTPUT_ROOT to choose another reproduction root.

What this script does
---------------------
1. Reads the regenerated results/rq1/metrics/effectiveness_by_run.csv below the output root.
2. Keeps only LLM rows at level == "project_criterion".
3. Excludes project x criterion partitions with no positive Ground-Truth instances
   (TP + FN == 0), because positive-class F1 is not informative there.
4. Aggregates the five repeated runs within each:
      model  x  project  x  criterion  x  prompt
   using the mean of the selected metric.
5. Keeps only matched units with all three prompting strategies:
      zero_shot, one_shot, few_shot
6. Runs:
   - Friedman omnibus test;
   - Kendall's W as omnibus effect size;
   - pairwise two-sided Wilcoxon signed-rank tests;
   - Holm correction for the three pairwise comparisons;
   - matched-pairs rank-biserial correlation as pairwise effect size.
7. Produces analyses:
   - overall;
   - by model;
   - by QUS criterion.
8. Saves CSV outputs under results/rq2/statistical_analysis/ below the output root.

Dependencies
------------
    pip install pandas scipy

Usage
-----
From the project root:

    python -m scripts.rq2.analyze_prompting_statistics

Optional:

    python -m scripts.rq2.analyze_prompting_statistics --metric F1
    python -m scripts.rq2.analyze_prompting_statistics --metric MCC
    python -m scripts.rq2.analyze_prompting_statistics \
        --input results/rq1/metrics/effectiveness_by_run.csv \
        --output-dir replication_runs/prompting/results/rq2/statistical_analysis

Notes
-----
- The five repeated executions are NOT treated as independent observations.
- AQUSA is excluded because RQ2 concerns Zero-shot, One-shot, and Few-shot LLM prompting.
- Undefined metric values are never replaced by zero.
"""

from __future__ import annotations

import argparse
import math
import sys
from itertools import combinations
from pathlib import Path
from scripts.shared.paths import generated_path

try:
    import numpy as np
    import pandas as pd
    from scipy.stats import friedmanchisquare, rankdata, wilcoxon
except ImportError as exc:
    raise SystemExit(
        "Missing dependency. Install the required packages with:\n"
        "    pip install pandas scipy\n"
        f"\nOriginal import error: {exc}"
    )


PROMPTS = ["zero_shot", "one_shot", "few_shot"]
EXPECTED_RUNS = 5

QUS_DIMENSION = {
    "Well-formed": "syntactic",
    "Atomic": "syntactic",
    "Minimal": "syntactic",
    "Conceptually sound": "semantic",
    "Problem-oriented": "semantic",
    "Unambiguous": "semantic",
    "Conflict-free": "semantic",
    "Full sentence": "pragmatic",
    "Estimatable": "pragmatic",
    "Unique": "pragmatic",
    "Uniform": "pragmatic",
    "Independent": "pragmatic",
    "Complete": "pragmatic",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Statistical comparison of Zero-shot, One-shot and Few-shot prompting."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=generated_path("results/rq1/metrics/effectiveness_by_run.csv"),
        help="Path to effectiveness_by_run.csv",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=generated_path("results/rq2/statistical_analysis"),
        help="Directory for generated CSV files",
    )
    parser.add_argument(
        "--metric",
        type=str,
        default="F1",
        help="Effectiveness metric to analyze (default: F1). Example: MCC",
    )
    return parser.parse_args()


def holm_adjust(p_values: list[float]) -> list[float]:
    """Holm step-down adjusted p-values, returned in original order."""
    m = len(p_values)
    if m == 0:
        return []

    order = np.argsort(p_values)
    adjusted_sorted = np.empty(m, dtype=float)

    running_max = 0.0
    for rank, idx in enumerate(order):
        raw_p = float(p_values[idx])
        adj = min(1.0, (m - rank) * raw_p)
        running_max = max(running_max, adj)
        adjusted_sorted[rank] = running_max

    result = np.empty(m, dtype=float)
    for rank, idx in enumerate(order):
        result[idx] = adjusted_sorted[rank]

    return result.tolist()


def kendalls_w_from_friedman(matrix: np.ndarray) -> float:
    """
    Kendall's W for n matched blocks (rows) and k conditions (columns).

    W = chi-square / (n * (k - 1))

    The scipy Friedman statistic already includes the standard tie correction.
    """
    n, k = matrix.shape
    if n == 0 or k < 2:
        return math.nan

    try:
        stat, _ = friedmanchisquare(*[matrix[:, i] for i in range(k)])
    except ValueError:
        return math.nan

    return float(stat / (n * (k - 1)))


def matched_rank_biserial(x: np.ndarray, y: np.ndarray) -> float:
    """
    Matched-pairs rank-biserial correlation.

    Difference convention: x - y.
    Positive values indicate larger values for x; negative values indicate
    larger values for y.

    Zero differences are excluded from the signed-rank sums.
    """
    d = np.asarray(x, dtype=float) - np.asarray(y, dtype=float)
    d = d[np.isfinite(d)]
    d = d[d != 0]

    if len(d) == 0:
        return 0.0

    ranks = rankdata(np.abs(d), method="average")
    w_plus = float(ranks[d > 0].sum())
    w_minus = float(ranks[d < 0].sum())
    denom = w_plus + w_minus

    if denom == 0:
        return 0.0

    return (w_plus - w_minus) / denom


def load_and_prepare(path: Path, metric: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    if not path.exists():
        raise FileNotFoundError(
            f"Input file not found: {path}\n"
            "Run this script from the TOSEM-Experiment repository root, or pass --input."
        )

    df = pd.read_csv(path)

    required = {
        "level",
        "prompt_profile",
        "model",
        "project",
        "run",
        "criterion",
        "TP",
        "FN",
        metric,
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Missing required columns in {path}: {sorted(missing)}"
        )

    # RQ2 focuses on the LLM prompting conditions, not AQUSA.
    llm = df[
        (df["level"] == "project_criterion")
        & (df["prompt_profile"].isin(PROMPTS))
        & (df["model"] != "AQUSA")
    ].copy()

    if llm.empty:
        raise ValueError(
            "No LLM project_criterion rows found for zero_shot/one_shot/few_shot."
        )

    llm["gt_positive"] = llm["TP"] + llm["FN"]
    llm["dimension"] = llm["criterion"].map(QUS_DIMENSION)

    # Audit table before exclusions.
    audit_rows = []

    for keys, group in llm.groupby(
        ["model", "project", "criterion", "prompt_profile"], dropna=False
    ):
        model, project, criterion, prompt = keys
        gt_positive_values = group["gt_positive"].dropna().unique()
        gt_positive = (
            float(gt_positive_values[0]) if len(gt_positive_values) else math.nan
        )
        metric_non_missing = int(group[metric].notna().sum())
        runs_observed = int(group["run"].nunique())

        reasons = []
        if gt_positive == 0:
            reasons.append("no_positive_ground_truth")
        if runs_observed != EXPECTED_RUNS:
            reasons.append(f"expected_{EXPECTED_RUNS}_runs_found_{runs_observed}")
        if metric_non_missing == 0:
            reasons.append("metric_undefined_all_runs")
        elif metric_non_missing < runs_observed:
            reasons.append(
                f"metric_undefined_some_runs_{metric_non_missing}_of_{runs_observed}"
            )

        audit_rows.append(
            {
                "model": model,
                "project": project,
                "criterion": criterion,
                "dimension": QUS_DIMENSION.get(criterion),
                "prompt_profile": prompt,
                "runs_observed": runs_observed,
                "gt_positive": gt_positive,
                "metric": metric,
                "metric_values_available": metric_non_missing,
                "exclusion_or_warning": ";".join(reasons),
            }
        )

    audit = pd.DataFrame(audit_rows)

    # Exclude partitions with no positive GT instances for positive-class F1-style analysis.
    eligible = llm[llm["gt_positive"] > 0].copy()

    # Never impute undefined metric values.
    eligible = eligible[np.isfinite(pd.to_numeric(eligible[metric], errors="coerce"))].copy()

    # Aggregate repeated executions within the experimental condition.
    condition_means = (
        eligible.groupby(
            ["model", "project", "criterion", "dimension", "prompt_profile"],
            as_index=False,
            dropna=False,
        )
        .agg(
            metric_mean=(metric, "mean"),
            metric_sd=(metric, "std"),
            valid_runs=(metric, "count"),
            gt_positive=("gt_positive", "first"),
        )
    )

    return condition_means, audit


def make_matched_table(
    condition_means: pd.DataFrame,
    unit_cols: list[str],
) -> pd.DataFrame:
    wide = condition_means.pivot_table(
        index=unit_cols,
        columns="prompt_profile",
        values="metric_mean",
        aggfunc="first",
    ).reset_index()

    for p in PROMPTS:
        if p not in wide.columns:
            wide[p] = np.nan

    # Complete-case matching across all three prompt strategies.
    wide = wide.dropna(subset=PROMPTS).copy()
    return wide


def run_analysis(
    matched: pd.DataFrame,
    analysis_level: str,
    analysis_group: str,
    metric: str,
) -> tuple[dict | None, list[dict]]:
    n = len(matched)
    if n < 2:
        return None, []

    matrix = matched[PROMPTS].to_numpy(dtype=float)

    # If all columns are exactly identical for all blocks, scipy may return NaN.
    all_equal = np.allclose(
        matrix[:, 0], matrix[:, 1], equal_nan=False
    ) and np.allclose(
        matrix[:, 0], matrix[:, 2], equal_nan=False
    )

    if all_equal:
        friedman_stat = 0.0
        friedman_p = 1.0
        kendall_w = 0.0
    else:
        try:
            friedman_stat, friedman_p = friedmanchisquare(
                *[matrix[:, i] for i in range(len(PROMPTS))]
            )
            friedman_stat = float(friedman_stat)
            friedman_p = float(friedman_p)
            kendall_w = kendalls_w_from_friedman(matrix)
        except ValueError:
            friedman_stat = math.nan
            friedman_p = math.nan
            kendall_w = math.nan

    omnibus = {
        "analysis_level": analysis_level,
        "analysis_group": analysis_group,
        "metric": metric,
        "n_matched_units": n,
        "test": "Friedman",
        "statistic": friedman_stat,
        "df": len(PROMPTS) - 1,
        "p_value": friedman_p,
        "effect_size": kendall_w,
        "effect_size_measure": "Kendall_W",
        "zero_shot_mean": float(matched["zero_shot"].mean()),
        "one_shot_mean": float(matched["one_shot"].mean()),
        "few_shot_mean": float(matched["few_shot"].mean()),
        "zero_shot_median": float(matched["zero_shot"].median()),
        "one_shot_median": float(matched["one_shot"].median()),
        "few_shot_median": float(matched["few_shot"].median()),
    }

    pairwise = []
    raw_ps = []

    for a, b in combinations(PROMPTS, 2):
        x = matched[a].to_numpy(dtype=float)
        y = matched[b].to_numpy(dtype=float)
        diff = x - y
        nonzero = int(np.sum(diff != 0))

        if nonzero == 0:
            stat = 0.0
            p = 1.0
        else:
            # Pratt keeps zero differences in ranking logic more conservatively.
            # scipy may fail in pathological all-zero cases, already handled above.
            result = wilcoxon(
                x,
                y,
                alternative="two-sided",
                zero_method="pratt",
                correction=False,
                method="auto",
            )
            stat = float(result.statistic)
            p = float(result.pvalue)

        rbc = matched_rank_biserial(x, y)

        row = {
            "analysis_level": analysis_level,
            "analysis_group": analysis_group,
            "metric": metric,
            "comparison": f"{a}_vs_{b}",
            "prompt_a": a,
            "prompt_b": b,
            "n_matched_units": n,
            "n_nonzero_differences": nonzero,
            "test": "Wilcoxon_signed_rank_two_sided",
            "statistic": stat,
            "p_value": p,
            "p_holm": math.nan,  # filled below
            "effect_size": rbc,
            "effect_size_measure": "matched_rank_biserial",
            "effect_direction": (
                f"{a}_higher" if rbc > 0 else f"{b}_higher" if rbc < 0 else "no_difference"
            ),
            "prompt_a_mean": float(np.mean(x)),
            "prompt_b_mean": float(np.mean(y)),
            "mean_difference_a_minus_b": float(np.mean(diff)),
            "median_difference_a_minus_b": float(np.median(diff)),
        }
        pairwise.append(row)
        raw_ps.append(p)

    adjusted = holm_adjust(raw_ps)
    for row, p_adj in zip(pairwise, adjusted):
        row["p_holm"] = p_adj

    return omnibus, pairwise


def main() -> int:
    args = parse_args()
    metric = args.metric

    args.output_dir.mkdir(parents=True, exist_ok=True)

    condition_means, audit = load_and_prepare(args.input, metric)

    condition_path = args.output_dir / f"prompting_condition_means_{metric}.csv"
    audit_path = args.output_dir / f"prompting_input_audit_{metric}.csv"
    condition_means.to_csv(condition_path, index=False)
    audit.to_csv(audit_path, index=False)

    omnibus_rows: list[dict] = []
    pairwise_rows: list[dict] = []
    matched_frames: list[pd.DataFrame] = []

    # 1) Overall: each matched block is model  x  project  x  criterion.
    overall = make_matched_table(
        condition_means,
        ["model", "project", "criterion", "dimension"],
    )
    if not overall.empty:
        tagged = overall.copy()
        tagged.insert(0, "analysis_group", "all_models")
        tagged.insert(0, "analysis_level", "overall")
        matched_frames.append(tagged)

    omnibus, pairwise = run_analysis(
        overall, "overall", "all_models", metric
    )
    if omnibus:
        omnibus_rows.append(omnibus)
    pairwise_rows.extend(pairwise)

    # 2) By model: matched block is project  x  criterion.
    for model, group in condition_means.groupby("model"):
        matched = make_matched_table(
            group,
            ["project", "criterion", "dimension"],
        )
        if not matched.empty:
            tagged = matched.copy()
            tagged.insert(0, "analysis_group", model)
            tagged.insert(0, "analysis_level", "by_model")
            matched_frames.append(tagged)

        omnibus, pairwise = run_analysis(
            matched, "by_model", str(model), metric
        )
        if omnibus:
            omnibus_rows.append(omnibus)
        pairwise_rows.extend(pairwise)

    # 3) By criterion: matched block is model  x  project.
    for criterion, group in condition_means.groupby("criterion"):
        matched = make_matched_table(
            group,
            ["model", "project", "dimension"],
        )
        if not matched.empty:
            tagged = matched.copy()
            tagged.insert(0, "analysis_group", criterion)
            tagged.insert(0, "analysis_level", "by_criterion")
            matched_frames.append(tagged)

        omnibus, pairwise = run_analysis(
            matched, "by_criterion", str(criterion), metric
        )
        if omnibus:
            omnibus_rows.append(omnibus)
        pairwise_rows.extend(pairwise)

    omnibus_df = pd.DataFrame(omnibus_rows)
    pairwise_df = pd.DataFrame(pairwise_rows)
    matched_df = (
        pd.concat(matched_frames, ignore_index=True)
        if matched_frames
        else pd.DataFrame()
    )

    omnibus_path = args.output_dir / f"prompting_friedman_{metric}.csv"
    pairwise_path = args.output_dir / f"prompting_pairwise_wilcoxon_{metric}.csv"
    matched_path = args.output_dir / f"prompting_matched_units_{metric}.csv"

    omnibus_df.to_csv(omnibus_path, index=False)
    pairwise_df.to_csv(pairwise_path, index=False)
    matched_df.to_csv(matched_path, index=False)

    print("=" * 72)
    print("QUS-13 prompting statistical analysis")
    print("=" * 72)
    print(f"Input:          {args.input}")
    print(f"Metric:         {metric}")
    print(f"Output dir:     {args.output_dir}")
    print()
    print("Generated files:")
    print(f"  - {condition_path}")
    print(f"  - {audit_path}")
    print(f"  - {matched_path}")
    print(f"  - {omnibus_path}")
    print(f"  - {pairwise_path}")
    print()

    if not omnibus_df.empty:
        overall_rows = omnibus_df[omnibus_df["analysis_level"] == "overall"]
        if not overall_rows.empty:
            row = overall_rows.iloc[0]
            print("Overall Friedman result:")
            print(
                f"  n={int(row['n_matched_units'])}, "
                f"chi2={row['statistic']:.6f}, "
                f"p={row['p_value']:.6g}, "
                f"Kendall W={row['effect_size']:.6f}"
            )
            print(
                "  means: "
                f"zero_shot={row['zero_shot_mean']:.6f}, "
                f"one_shot={row['one_shot_mean']:.6f}, "
                f"few_shot={row['few_shot_mean']:.6f}"
            )
            print()

    print(
        "Important: inspect prompting_input_audit_*.csv and the matched-unit "
        "counts before reporting inferential results in the paper."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
