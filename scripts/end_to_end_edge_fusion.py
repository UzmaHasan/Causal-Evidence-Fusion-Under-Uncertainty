#!/usr/bin/env python3
"""
Robust end-to-end pipeline:
1. Read multiple expert Excel sheets from a folder
2. Build edge-wise Table 1 inputs internally
3. Optionally save intermediate Table 1 CSV files
4. Compute Table 2 outputs using:
      - Simple Average
      - DST
      - Yager
      - Murphy
      - Dubois-Prade
      - PCR5
5. Write:
      - one Table 2 CSV per edge
      - one master_summary.csv
      - all_expert_rows_combined.csv
      - edge_processing_status.csv
      - benchmark_metrics.csv
      - inter_method_correlation_matrix.csv
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


@dataclass
class MassBinary:
    e: float
    ne: float
    omega: float

    def total(self) -> float:
        return self.e + self.ne + self.omega


def check_mass(m: MassBinary, tol: float = 1e-8) -> None:
    if m.e < 0 or m.ne < 0 or m.omega < 0:
        raise ValueError(f"Masses must be non-negative. Got {m}")
    s = m.total()
    if abs(s - 1.0) > tol:
        raise ValueError(f"Masses must sum to 1 (±{tol}). Got sum={s:.12f} for {m}")


def normalize(m: MassBinary) -> MassBinary:
    s = m.total()
    if s <= 0:
        raise ValueError(f"Cannot normalize masses with sum={s}. Got {m}")
    return MassBinary(e=m.e / s, ne=m.ne / s, omega=m.omega / s)


def smooth_and_normalize(
    m: MassBinary,
    eps: float = 1e-6,
    mode: str = "zeros_only",
    enforce_omega_min: bool = True,
) -> MassBinary:
    def bump(x: float) -> float:
        if mode == "zeros_only":
            return eps if x == 0.0 else x
        if mode == "clip_small":
            return max(x, eps)
        raise ValueError("mode must be 'zeros_only' or 'clip_small'")

    e = bump(m.e)
    ne = bump(m.ne)
    omega = bump(m.omega)

    if enforce_omega_min:
        omega = max(omega, eps)

    return normalize(MassBinary(e=e, ne=ne, omega=omega))


def bel_pl_betp(m: MassBinary) -> Tuple[float, float, float]:
    bel = m.e
    pl = m.e + m.omega
    betp = m.e + 0.5 * m.omega
    return bel, pl, betp


def conjunctive_components(m1: MassBinary, m2: MassBinary) -> Tuple[MassBinary, float]:
    check_mass(m1)
    check_mass(m2)

    m_prime_e = m1.e * m2.e + m1.e * m2.omega + m1.omega * m2.e
    m_prime_ne = m1.ne * m2.ne + m1.ne * m2.omega + m1.omega * m2.ne
    m_prime_omega = m1.omega * m2.omega
    K = m1.e * m2.ne + m1.ne * m2.e

    return MassBinary(m_prime_e, m_prime_ne, m_prime_omega), K


def combine_two_dst(m1: MassBinary, m2: MassBinary) -> Tuple[MassBinary, float]:
    m_prime, K = conjunctive_components(m1, m2)
    denom = 1.0 - K

    if denom <= 0:
        raise ValueError(f"Total conflict for DST: K={K:.12f}, so 1-K <= 0.")

    return MassBinary(
        e=m_prime.e / denom,
        ne=m_prime.ne / denom,
        omega=m_prime.omega / denom,
    ), K


def combine_two_yager(m1: MassBinary, m2: MassBinary) -> Tuple[MassBinary, float]:
    m_prime, K = conjunctive_components(m1, m2)

    return MassBinary(
        e=m_prime.e,
        ne=m_prime.ne,
        omega=m_prime.omega + K,
    ), K


def combine_two_dubois_prade(m1: MassBinary, m2: MassBinary) -> Tuple[MassBinary, float]:
    """
    Dubois-Prade rule for binary frame {e, not e}.

    In this binary case, conflict between e and not e is moved to omega={e,not e}.
    Therefore, it behaves similarly to Yager for this specific frame.
    """
    m_prime, K = conjunctive_components(m1, m2)

    return MassBinary(
        e=m_prime.e,
        ne=m_prime.ne,
        omega=m_prime.omega + K,
    ), K


def combine_two_pcr5(m1: MassBinary, m2: MassBinary) -> Tuple[MassBinary, float]:
    check_mass(m1)
    check_mass(m2)

    m_prime, K = conjunctive_components(m1, m2)

    c1 = m1.e * m2.ne
    c2 = m1.ne * m2.e

    add_to_e = 0.0
    add_to_ne = 0.0

    denom1 = m1.e + m2.ne
    if c1 > 0 and denom1 > 0:
        add_to_e += (m1.e ** 2 * m2.ne) / denom1
        add_to_ne += (m2.ne ** 2 * m1.e) / denom1

    denom2 = m1.ne + m2.e
    if c2 > 0 and denom2 > 0:
        add_to_ne += (m1.ne ** 2 * m2.e) / denom2
        add_to_e += (m2.e ** 2 * m1.ne) / denom2

    return normalize(
        MassBinary(
            e=m_prime.e + add_to_e,
            ne=m_prime.ne + add_to_ne,
            omega=m_prime.omega,
        )
    ), K


def combine_sequential(
    sources: List[MassBinary],
    pairwise_func: Callable[[MassBinary, MassBinary], Tuple[MassBinary, float]],
) -> Tuple[MassBinary, float]:
    if len(sources) < 2:
        raise ValueError("Need at least 2 sources.")

    combined = sources[0]
    last_conflict = 0.0

    for i in range(1, len(sources)):
        combined, last_conflict = pairwise_func(combined, sources[i])

    return combined, last_conflict


def simple_average(sources: List[MassBinary]) -> MassBinary:
    if not sources:
        raise ValueError("No sources found.")

    n = len(sources)
    return normalize(
        MassBinary(
            e=sum(s.e for s in sources) / n,
            ne=sum(s.ne for s in sources) / n,
            omega=sum(s.omega for s in sources) / n,
        )
    )


def combine_murphy(sources: List[MassBinary]) -> MassBinary:
    """
    Murphy's average rule:
    1. Average all source masses.
    2. Combine the averaged mass with itself n times using Dempster's rule.
    """
    if len(sources) < 2:
        raise ValueError("Need at least 2 sources.")

    avg_mass = simple_average(sources)
    combined = avg_mass

    for _ in range(len(sources) - 1):
        combined, _ = combine_two_dst(combined, avg_mass)

    return combined


def canonicalize(col: str) -> str:
    return (
        str(col)
        .strip()
        .lower()
        .replace("\n", " ")
        .replace("%", "")
        .replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace("_", "")
        .replace("’", "'")
        .replace("`", "'")
        .replace(" ", "")
    )


def find_column(df: pd.DataFrame, candidates: List[str], required: bool = True) -> Optional[str]:
    canon_map = {canonicalize(c): c for c in df.columns}

    for cand in candidates:
        key = canonicalize(cand)
        if key in canon_map:
            return canon_map[key]

    if required:
        raise ValueError(
            f"Could not find any matching column for: {candidates}\n"
            f"Available columns are: {list(df.columns)}"
        )

    return None


def clean_edge_name(edge: str) -> str:
    edge = str(edge).strip()
    edge = (
        edge.replace("-->", " to ")
        .replace("->", " to")
        .replace("=>", " to ")
        .replace("→", " to ")
    )
    edge = re.sub(r"[^\w\s]", " ", edge)
    edge = re.sub(r"\s+", "_", edge.strip())
    return edge.lower()


def to_probability_or_none(x):
    if pd.isna(x):
        return 0.0

    if isinstance(x, str):
        x = x.strip().replace("%", "")
        if x == "":
            return 0.0

    try:
        val = float(x)
    except (ValueError, TypeError):
        return None

    return val if 0.0 <= val <= 1.0 else val / 100.0


def normalize_three_probs(
    pe: float,
    pne: float,
    pomega: float,
    tol: float = 1e-8,
) -> Tuple[float, float, float]:
    total = pe + pne + pomega

    if total <= 0:
        return 0.0, 0.0, 1.0

    if abs(total - 1.0) <= tol:
        return pe, pne, pomega

    return pe / total, pne / total, pomega / total


def read_one_expert_file(
    excel_path: Path,
    sheet_name: Optional[str] = None,
) -> Tuple[pd.DataFrame, List[Dict[str, str]]]:
    df = pd.read_excel(excel_path, sheet_name=sheet_name) if sheet_name else pd.read_excel(excel_path)
    df = df.dropna(how="all").copy()

    print(f"\nColumns in file {excel_path.name}:")
    print(list(df.columns))

    col_edge = find_column(df, ["Edge"])
    col_exists = find_column(df, ["p(Exists) (in %)", "p(Exists)", "Exists"])
    col_not_exists = find_column(
        df,
        [
            "p(Doesn't exist) (in %)",
            "p(Doesnt exist) (in %)",
            "p(Doesn't exist)",
            "p(Doesnt exist)",
            "Doesn't exist",
            "Doesnt exist",
        ],
    )
    col_either = find_column(df, ["p(Either) (in %)", "p(Either)", "Either"])
    col_remarks = find_column(df, ["Remarks (Optional)", "Remarks", "Remark"], required=False)

    print(f"Detected columns in {excel_path.name}:")
    print(f"  Edge column       -> {col_edge}")
    print(f"  P(e) column       -> {col_exists}")
    print(f"  P(not e) column   -> {col_not_exists}")
    print(f"  P(50-50) column   -> {col_either}")
    print(f"  Remarks column    -> {col_remarks}")

    expert_name = excel_path.stem
    out_rows = []
    skipped_rows = []

    for row_idx, row in df.iterrows():
        edge = row[col_edge]

        if pd.isna(edge) or str(edge).strip() == "":
            continue

        edge_str = str(edge).strip()

        raw_pe = row[col_exists]
        raw_pne = row[col_not_exists]
        raw_pomega = row[col_either]

        pe = to_probability_or_none(raw_pe)
        pne = to_probability_or_none(raw_pne)
        pomega = to_probability_or_none(raw_pomega)

        invalid_fields = []
        if pe is None:
            invalid_fields.append((col_exists, raw_pe))
        if pne is None:
            invalid_fields.append((col_not_exists, raw_pne))
        if pomega is None:
            invalid_fields.append((col_either, raw_pomega))

        if invalid_fields:
            skipped_rows.append(
                {
                    "ExpertFile": expert_name,
                    "ExcelFile": excel_path.name,
                    "RowNumberInExcel": row_idx + 2,
                    "Edge": edge_str,
                    "InvalidFields": " | ".join(
                        [f"{col}={value!r}" for col, value in invalid_fields]
                    ),
                    "Reason": "Non-numeric probability cell",
                }
            )
            continue

        pe, pne, pomega = normalize_three_probs(pe, pne, pomega)

        remarks = ""
        if col_remarks is not None and not pd.isna(row[col_remarks]):
            remarks = str(row[col_remarks]).strip()

        out_rows.append(
            {
                "Edge": edge_str,
                "Sources": expert_name,
                "P(e)": pe,
                "P(not e)": pne,
                "P(50-50)": pomega,
                "Remarks": remarks,
            }
        )

    return pd.DataFrame(out_rows), skipped_rows


def read_all_expert_files(
    input_dir: str,
    sheet_name: Optional[str] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    input_path = Path(input_dir)
    excel_files = sorted(list(input_path.glob("*.xlsx")) + list(input_path.glob("*.xls")))

    if not excel_files:
        raise FileNotFoundError(f"No Excel files found in: {input_dir}")

    print(f"Found {len(excel_files)} expert Excel file(s).")

    all_frames = []
    all_skipped_rows = []

    for excel_file in excel_files:
        print(f"\nReading: {excel_file.name}")
        df_one, skipped_rows = read_one_expert_file(excel_file, sheet_name=sheet_name)
        all_frames.append(df_one)
        all_skipped_rows.extend(skipped_rows)

    combined = pd.concat(all_frames, ignore_index=True) if all_frames else pd.DataFrame()
    skipped_df = pd.DataFrame(all_skipped_rows)

    if combined.empty:
        raise ValueError("No valid expert rows found after reading the Excel files.")

    return combined, skipped_df


def success_row(
    method: str,
    m: MassBinary,
    bel: float,
    pl: float,
    betp: float,
    error: str = "",
) -> Dict[str, object]:
    return {
        "Method": method,
        "fused m(e)": m.e,
        "fused m(not e)": m.ne,
        "fused m(50-50)": m.omega,
        "Bel (e)": bel,
        "Pl (e)": pl,
        "BetP": betp,
        "Error": error,
    }


def failure_row(method: str, error: str) -> Dict[str, object]:
    return {
        "Method": method,
        "fused m(e)": float("nan"),
        "fused m(not e)": float("nan"),
        "fused m(50-50)": float("nan"),
        "Bel (e)": float("nan"),
        "Pl (e)": float("nan"),
        "BetP": float("nan"),
        "Error": error,
    }


def generate_table2_from_sources(
    df_sources: pd.DataFrame,
    do_smooth: bool = False,
    eps: float = 1e-6,
    mode: str = "zeros_only",
    enforce_omega_min: bool = True,
) -> Tuple[pd.DataFrame, bool]:
    masses: List[MassBinary] = []

    for _, row in df_sources.iterrows():
        m = MassBinary(
            e=float(row["P(e)"]),
            ne=float(row["P(not e)"]),
            omega=float(row["P(50-50)"]),
        )

        check_mass(m)

        if do_smooth:
            m = smooth_and_normalize(
                m,
                eps=eps,
                mode=mode,
                enforce_omega_min=enforce_omega_min,
            )

        masses.append(m)

    rows: List[Dict[str, object]] = []
    any_success = False

    method_jobs = [
        ("Simple Average", lambda ms: simple_average(ms), 1),
        ("DST", lambda ms: combine_sequential(ms, combine_two_dst)[0], 2),
        ("Yager", lambda ms: combine_sequential(ms, combine_two_yager)[0], 2),
        ("Murphy", lambda ms: combine_murphy(ms), 2),
        ("Dubois-Prade", lambda ms: combine_sequential(ms, combine_two_dubois_prade)[0], 2),
        ("PCR5", lambda ms: combine_sequential(ms, combine_two_pcr5)[0], 2),
    ]

    for method_name, func, min_sources in method_jobs:
        try:
            if len(masses) < min_sources:
                raise ValueError(f"Need at least {min_sources} valid source(s).")

            m_result = func(masses)
            bel, pl, betp = bel_pl_betp(m_result)
            rows.append(success_row(method_name, m_result, bel, pl, betp))
            any_success = True

        except Exception as ex:
            rows.append(failure_row(method_name, str(ex)))

    return pd.DataFrame(rows), any_success


def compute_no_label_benchmark_metrics(
    master_df: pd.DataFrame,
    output_path: Path,
    abstain_threshold: float = 0.40,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Computes no-ground-truth benchmark metrics from master_summary.csv.

    Metrics:
    1. Avg Ignorance
    2. Avg Width
    3. Decisiveness
    4. Abstention Rate
    5. Selective Risk
    6. Mean Inter-Method Correlation
    """

    required_cols = [
        "Edge",
        "Method",
        "fused m(50-50)",
        "Bel (e)",
        "Pl (e)",
        "BetP",
    ]

    missing_cols = [c for c in required_cols if c not in master_df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns for benchmark metrics: {missing_cols}")

    df = master_df.copy()

    if "Error" in df.columns:
        df = df[df["Error"].fillna("").eq("")].copy()

    numeric_cols = ["fused m(50-50)", "Bel (e)", "Pl (e)", "BetP"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=required_cols)

    results = []

    for method, group in df.groupby("Method", sort=True):
        width = group["Pl (e)"] - group["Bel (e)"]
        ignorance = group["fused m(50-50)"]
        betp = group["BetP"]

        non_abstained = ignorance <= abstain_threshold

        selective_risk = (
            width[non_abstained].mean()
            if non_abstained.any()
            else np.nan
        )

        results.append(
            {
                "Method": method,
                "Avg Ignorance": ignorance.mean(),
                "Avg Width": width.mean(),
                "Decisiveness": (betp - 0.5).abs().mean(),
                "Abstention Rate": (ignorance > abstain_threshold).mean(),
                "Selective Risk": selective_risk,
                "Edge Count": group["Edge"].nunique(),
            }
        )

    metrics_df = pd.DataFrame(results)

    pivot = df.pivot_table(
        index="Edge",
        columns="Method",
        values="BetP",
        aggfunc="mean",
    )

    corr_matrix = pivot.corr(method="spearman")

    mean_corr = {}
    for method in corr_matrix.columns:
        others = corr_matrix.loc[method].drop(method).dropna()
        mean_corr[method] = others.mean() if len(others) > 0 else np.nan

    metrics_df["Mean Inter-Method Corr"] = metrics_df["Method"].map(mean_corr)

    metrics_df.to_csv(output_path / "no_label_benchmark_metrics.csv", index=False)
    corr_matrix.to_csv(output_path / "inter_method_correlation_matrix.csv")

    return metrics_df, corr_matrix


def process_end_to_end(
    expert_input_dir: str,
    output_dir: str,
    sheet_name: Optional[str] = None,
    save_input_tables: bool = False,
    do_smooth: bool = False,
    eps: float = 1e-6,
    mode: str = "zeros_only",
    enforce_omega_min: bool = True,
    abstain_threshold: float = 0.40,
) -> None:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    input_tables_dir = output_path / "input_tables"
    table2_dir = output_path / "table2_outputs"

    if save_input_tables:
        input_tables_dir.mkdir(parents=True, exist_ok=True)

    table2_dir.mkdir(parents=True, exist_ok=True)

    combined, skipped_df = read_all_expert_files(expert_input_dir, sheet_name=sheet_name)
    combined.to_csv(output_path / "all_expert_rows_combined.csv", index=False)

    if not skipped_df.empty:
        skipped_df.to_csv(output_path / "skipped_invalid_probability_rows.csv", index=False)
        print(f"\nSkipped invalid rows written to: {output_path / 'skipped_invalid_probability_rows.csv'}")

    master_rows = []
    edge_status_rows = []

    for edge_name, df_edge in combined.groupby("Edge", sort=True):
        safe_name = clean_edge_name(edge_name)
        df_input = df_edge[["Sources", "P(e)", "P(not e)", "P(50-50)", "Remarks"]].copy()

        if save_input_tables:
            df_input.to_csv(input_tables_dir / f"{safe_name}.csv", index=False)

        df_table2, any_success = generate_table2_from_sources(
            df_sources=df_input,
            do_smooth=do_smooth,
            eps=eps,
            mode=mode,
            enforce_omega_min=enforce_omega_min,
        )

        df_table2.to_csv(table2_dir / f"{safe_name}_table2.csv", index=False)

        success_count = int(df_table2["Error"].eq("").sum())
        edge_status_rows.append(
            {
                "Edge": edge_name,
                "ValidSourceCount": len(df_input),
                "SuccessfulMethodCount": success_count,
                "AnySuccess": any_success,
            }
        )

        if any_success:
            df_master = df_table2.copy()
            df_master.insert(0, "Edge", edge_name)
            master_rows.append(df_master)

    edge_status_df = pd.DataFrame(edge_status_rows)
    edge_status_df.to_csv(output_path / "edge_processing_status.csv", index=False)

    if not master_rows:
        raise RuntimeError(
            "No edges were successfully processed. Check:\n"
            f"  - {output_path / 'skipped_invalid_probability_rows.csv'}\n"
            f"  - {output_path / 'edge_processing_status.csv'}\n"
            f"  - edge-level files under {table2_dir}"
        )

    master_df = pd.concat(master_rows, ignore_index=True)
    master_df.to_csv(output_path / "master_summary.csv", index=False)

    metrics_df, corr_matrix = compute_no_label_benchmark_metrics(
        master_df=master_df,
        output_path=output_path,
        abstain_threshold=abstain_threshold,
    )

    print("\nDone.")
    print(f"Master summary: {output_path / 'master_summary.csv'}")
    print(f"No-label benchmark metrics: {output_path / 'no_label_benchmark_metrics.csv'}")
    print(f"Inter-method correlation matrix: {output_path / 'inter_method_correlation_matrix.csv'}")
    print(f"Edge-level Table 2 files: {table2_dir}")
    print(f"Edge processing status: {output_path / 'edge_processing_status.csv'}")

    if save_input_tables:
        print(f"Intermediate Table 1 files: {input_tables_dir}")

    print("\nBenchmark metrics preview:")
    print(metrics_df)

    print("\nInter-method Spearman correlation matrix:")
    print(corr_matrix)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="End-to-end edge fusion from expert Excel sheets to Table 2 outputs and no-label benchmark metrics."
    )

    parser.add_argument("expert_input_dir", help="Folder containing expert Excel files")
    parser.add_argument("output_dir", help="Folder where outputs will be written")
    parser.add_argument("--sheet", default=None, help="Optional Excel sheet name. If omitted, first sheet is used.")
    parser.add_argument("--save-input-tables", action="store_true", help="Also save intermediate edge-wise Table 1 CSV files.")
    parser.add_argument("--smooth", action="store_true", help="Apply smoothing before fusion.")
    parser.add_argument("--eps", type=float, default=1e-6, help="Smoothing epsilon, default: 1e-6")
    parser.add_argument("--mode", choices=["zeros_only", "clip_small"], default="zeros_only", help="Smoothing mode")
    parser.add_argument("--enforce-omega-min", action="store_true", help="Ensure m(50-50) >= epsilon during smoothing")
    parser.add_argument("--abstain-threshold", type=float, default=0.40, help="Threshold for abstention based on m(50-50). Default: 0.40")

    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    process_end_to_end(
        expert_input_dir=args.expert_input_dir,
        output_dir=args.output_dir,
        sheet_name=args.sheet,
        save_input_tables=args.save_input_tables,
        do_smooth=args.smooth,
        eps=args.eps,
        mode=args.mode,
        enforce_omega_min=args.enforce_omega_min,
        abstain_threshold=args.abstain_threshold,
    )


if __name__ == "__main__":
    main()