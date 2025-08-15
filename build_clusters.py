"""Utility to cluster LCs by program using funnel metrics."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Iterable, List, Optional, Tuple

import pandas as pd
from pandas import DataFrame

# Third party imports (scikit-learn). May require installation.
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

# ---------------------------------------------------------------------------
# Configuration (edit these variables to customize behaviour)
# ---------------------------------------------------------------------------
INPUT_PATH: str = os.path.join("data", "data_latest.csv")
INPUT_SHEET: str = "funnel"  # Used only if INPUT_PATH ends with .xlsx
OUTPUT_PATH: str = "clusters.csv"
DATE_FROM: Optional[str] = None  # e.g. "2023-01-01"
DATE_TO: Optional[str] = None  # e.g. "2023-12-31"
K_MIN: int = 2
K_MAX: int = 8
RANDOM_STATE: int = 42
MIN_LCS_PER_PROGRAM: int = 5
PROGRAMS: Optional[List[str]] = None  # e.g. ["IGTa", "IGTe"]

FEATURES: List[str] = [
    "ApplicantRate",
    "AcceptanceRate",
    "ApprovalRate",
    "RealizationRate",
    "CompletionRate",
    "SignupsVol",
    "RealizedVol",
]

METRIC_COLS: List[str] = [
    "Signups",
    "Applicants",
    "Accepted",
    "Approved",
    "Realized",
    "Finished",
    "Completed",
]

REQUIRED_COLS: List[str] = [
    "Country_Name",
    "Country_Region",
    "LC_name",
    "Program",
    *METRIC_COLS,
    "Date",
    "DateTime",
]


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def load_data(path: str, sheet: str) -> DataFrame:
    """Load a CSV or Excel file into a DataFrame."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Input file not found: {path}")

    _, ext = os.path.splitext(path.lower())
    if ext == ".csv":
        df = pd.read_csv(path, sep=",|;", engine="python")
    elif ext in {".xls", ".xlsx"}:
        df = pd.read_excel(path, sheet_name=sheet)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    return df


def filter_by_date(df: DataFrame, date_from: Optional[str], date_to: Optional[str]) -> DataFrame:
    """Filter rows by DATE_FROM/DATE_TO using DateTime if available."""
    if date_from is None and date_to is None:
        return df

    date_col = "DateTime" if "DateTime" in df.columns else "Date"
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    if date_from:
        df = df[df[date_col] >= pd.to_datetime(date_from)]
    if date_to:
        df = df[df[date_col] <= pd.to_datetime(date_to)]
    return df


def aggregate_funnel(df: DataFrame) -> DataFrame:
    """Aggregate funnel metrics by LC and Program."""
    df = df.copy()
    # Remove rows with negative metrics
    neg_mask = (df[METRIC_COLS] < 0).any(axis=1)
    df = df[~neg_mask]
    grouped = df.groupby(["LC_name", "Program"], as_index=False)[METRIC_COLS].sum()
    grouped[METRIC_COLS] = grouped[METRIC_COLS].fillna(0)
    return grouped


def safe_div(a: float, b: float) -> float:
    """Division helper returning 0.0 when denominator <= 0."""
    return float(a) / float(b) if b and b > 0 else 0.0


def compute_features(df: DataFrame) -> DataFrame:
    """Compute conversion rates and volume features."""
    df = df.copy()
    df["ApplicantRate"] = df.apply(lambda r: safe_div(r["Applicants"], r["Signups"]), axis=1)
    df["AcceptanceRate"] = df.apply(lambda r: safe_div(r["Accepted"], r["Applicants"]), axis=1)
    df["ApprovalRate"] = df.apply(lambda r: safe_div(r["Approved"], r["Accepted"]), axis=1)
    df["RealizationRate"] = df.apply(lambda r: safe_div(r["Realized"], r["Approved"]), axis=1)
    df["CompletionRate"] = df.apply(lambda r: safe_div(r["Completed"], r["Realized"]), axis=1)
    df["SignupsVol"] = df["Signups"]
    df["RealizedVol"] = df["Realized"]
    df[FEATURES] = df[FEATURES].fillna(0.0)
    return df


def _kmeans(n_clusters: int, random_state: int) -> KMeans:
    """Create a KMeans instance handling scikit-learn version differences."""
    try:
        return KMeans(n_clusters=n_clusters, n_init="auto", random_state=random_state)
    except TypeError:  # Older scikit-learn
        return KMeans(n_clusters=n_clusters, n_init=25, random_state=random_state)


def cluster_by_program(
    df_features: DataFrame,
    kmin: int,
    kmax: int,
    random_state: int,
    min_lcs: int,
    programs: Optional[Iterable[str]] = None,
) -> Tuple[DataFrame, DataFrame]:
    """Cluster LCs by program using KMeans and silhouette selection."""
    clusters = []
    diagnostics = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    df_iter = df_features
    if programs is not None:
        df_iter = df_iter[df_iter["Program"].isin(programs)]

    for program, subdf in df_iter.groupby("Program"):
        n_lcs = len(subdf)
        if n_lcs < min_lcs:
            print(f"Program {program}: skipped (only {n_lcs} LCs)")
            diagnostics.append(
                {
                    "Program": program,
                    "n_LCs": n_lcs,
                    "k_opt": None,
                    "silhouette": None,
                    "generated_at": now,
                    "features": ",".join(FEATURES),
                }
            )
            continue

        if n_lcs == 1:
            subdf = subdf.copy()
            subdf["cluster_id"] = 0
            subdf["n_in_program"] = n_lcs
            subdf["k_opt_program"] = 1
            subdf["generated_at"] = now
            clusters.append(subdf[["LC_name", "Program", "cluster_id", "n_in_program", "k_opt_program", "generated_at"]])
            diagnostics.append(
                {
                    "Program": program,
                    "n_LCs": n_lcs,
                    "k_opt": 1,
                    "silhouette": float("nan"),
                    "generated_at": now,
                    "features": ",".join(FEATURES),
                }
            )
            print(f"Program {program}: only one LC, assigned cluster 0")
            continue

        scaler = StandardScaler()
        X = scaler.fit_transform(subdf[FEATURES])
        candidate_ks = [k for k in range(kmin, min(kmax, n_lcs - 1) + 1) if k < n_lcs]
        best_k = None
        best_score = -1.0

        for k in candidate_ks:
            try:
                model = _kmeans(k, random_state)
                labels = model.fit_predict(X)
                if len(set(labels)) > 1:
                    score = silhouette_score(X, labels)
                    if score > best_score:
                        best_k, best_score = k, score
            except Exception:
                continue

        if best_k is None:
            best_k = 2 if n_lcs >= 2 else 1
            best_score = float("nan")

        model = _kmeans(best_k, random_state)
        labels = model.fit_predict(X)
        subdf = subdf.copy()
        subdf["cluster_id"] = labels
        subdf["n_in_program"] = n_lcs
        subdf["k_opt_program"] = best_k
        subdf["generated_at"] = now
        clusters.append(subdf[["LC_name", "Program", "cluster_id", "n_in_program", "k_opt_program", "generated_at"]])
        diagnostics.append(
            {
                "Program": program,
                "n_LCs": n_lcs,
                "k_opt": best_k,
                "silhouette": best_score,
                "generated_at": now,
                "features": ",".join(FEATURES),
            }
        )
        print(f"Program {program}: n_LCs={n_lcs}, k_opt={best_k}, silhouette={best_score:.4f}")

    clusters_df = pd.concat(clusters, ignore_index=True) if clusters else pd.DataFrame()
    diag_df = pd.DataFrame(diagnostics)
    return clusters_df, diag_df


def save_clusters_csv(df: DataFrame, output_path: str) -> None:
    """Save clusters DataFrame to CSV sorted as required."""
    df_sorted = df.sort_values(["Program", "cluster_id", "LC_name"]).reset_index(drop=True)
    df_sorted.to_csv(output_path, index=False)


# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------
def main() -> None:
    print(f"Loading data from: {os.path.abspath(INPUT_PATH)}")
    df = load_data(INPUT_PATH, INPUT_SHEET)
    print(f"Rows loaded: {len(df)}")

    df_filtered = filter_by_date(df, DATE_FROM, DATE_TO)
    print(f"Rows after date filter: {len(df_filtered)}")

    agg_df = aggregate_funnel(df_filtered)
    features_df = compute_features(agg_df)

    clusters_df, diag_df = cluster_by_program(
        features_df,
        kmin=K_MIN,
        kmax=K_MAX,
        random_state=RANDOM_STATE,
        min_lcs=MIN_LCS_PER_PROGRAM,
        programs=PROGRAMS,
    )

    if not clusters_df.empty:
        save_clusters_csv(clusters_df, OUTPUT_PATH)
        print(f"Clusters saved to: {os.path.abspath(OUTPUT_PATH)}")
    else:
        print("No clusters generated.")

    if not diag_df.empty:
        diag_path = OUTPUT_PATH.replace(".csv", "_diag.csv")
        diag_df.to_csv(diag_path, index=False)


if __name__ == "__main__":
    main()
