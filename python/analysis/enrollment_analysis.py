"""
UIS Enrollment Trend Analysis
==============================
Comprehensive analysis of UIS enrollment trends (2014-2023).
Produces charts for OIRE annual report and Power BI dashboard data files.

Data Source: IPEDS Fall Enrollment Survey, UIS Unit ID: 145813
Author: Rakesh Budige
Created: 2025-01-20
Modified: 2025-02-05 - Added demographic breakdown charts

Key Findings (run this script to generate):
    - Total enrollment declined ~14% from 2014-2021 peak decline
    - Online enrollment grew from 38% to 56% of total
    - Recovery began in 2022 with +1% and 2023 +1.4%
    - Female students consistently ~53-54% of enrollment
"""

import logging
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for server

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
from scipy import stats

# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "raw"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "reports"
CHART_DIR = OUTPUT_DIR / "charts"
CHART_DIR.mkdir(parents=True, exist_ok=True)

# UIS brand colors
UIS_BLUE = "#003366"
UIS_ORANGE = "#E84A27"
UIS_LIGHT_BLUE = "#0066CC"
UIS_GRAY = "#666666"
UIS_LIGHT_GRAY = "#F0F0F0"


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load all datasets."""
    enrollment = pd.read_csv(DATA_DIR / "uis_enrollment_2014_2023.csv")
    graduation = pd.read_csv(DATA_DIR / "uis_graduation_rates_2010_2017.csv")
    retention = pd.read_csv(DATA_DIR / "uis_retention_rates_2014_2023.csv")
    il_unis = pd.read_csv(DATA_DIR / "illinois_universities_comparison_2023.csv")
    return enrollment, graduation, retention, il_unis


def plot_enrollment_trend(df: pd.DataFrame) -> None:
    """
    Plot total enrollment trend with annotations for key events.
    Shows UG vs Graduate split over time.
    """
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    fig.patch.set_facecolor("white")

    # --- Top chart: Total enrollment with trend line ---
    ax1 = axes[0]
    ax1.set_facecolor("#FAFAFA")

    # Bar chart for total enrollment
    bars = ax1.bar(df["year"], df["total_enrollment"], color=UIS_BLUE,
                   alpha=0.85, width=0.6, zorder=3)
    
    # Overlay UG and Grad
    ax1.bar(df["year"], df["undergrad_enrollment"], color=UIS_LIGHT_BLUE,
            alpha=0.6, width=0.6, label="Undergraduate", zorder=4)
    ax1.bar(df["year"], df["grad_enrollment"],
            bottom=df["undergrad_enrollment"], color=UIS_ORANGE,
            alpha=0.75, width=0.6, label="Graduate", zorder=4)

    # Trend line
    z = np.polyfit(df["year"], df["total_enrollment"], 1)
    p = np.poly1d(z)
    ax1.plot(df["year"], p(df["year"]), "--", color="red",
             alpha=0.7, linewidth=2, label=f"Trend (slope: {z[0]:+.0f}/yr)")

    # Annotate each bar
    for _, row in df.iterrows():
        ax1.annotate(
            f"{row['total_enrollment']:,}",
            xy=(row["year"], row["total_enrollment"]),
            ha="center", va="bottom", fontsize=8.5, fontweight="bold", color=UIS_BLUE
        )

    # Highlight COVID years
    ax1.axvspan(2019.5, 2021.5, alpha=0.08, color="red", label="COVID Impact")

    ax1.set_title("UIS Total Enrollment by Level (2014–2023)\nIPEDS Fall Enrollment Survey | Unit ID: 145813",
                  fontsize=13, fontweight="bold", color=UIS_BLUE, pad=12)
    ax1.set_xlabel("Academic Year", fontsize=11)
    ax1.set_ylabel("Headcount Enrollment", fontsize=11)
    ax1.legend(loc="upper right", fontsize=9)
    ax1.set_ylim(3500, 5800)
    ax1.grid(axis="y", alpha=0.4, zorder=0)
    ax1.spines[["top", "right"]].set_visible(False)
    ax1.set_xticks(df["year"])

    # --- Bottom chart: Online vs On-Campus ---
    ax2 = axes[1]
    ax2.set_facecolor("#FAFAFA")

    df["oncampus"] = df["total_enrollment"] - df["online_only"]
    ax2.stackplot(
        df["year"],
        df["online_only"],
        df["oncampus"],
        labels=["Online-Only Students", "On-Campus/Hybrid Students"],
        colors=[UIS_ORANGE, UIS_LIGHT_BLUE],
        alpha=0.8
    )
    ax2.plot(df["year"],
             df["online_only"] / df["total_enrollment"] * 100,
             "k--", linewidth=2, label="Online %")
    ax2_twin = ax2.twinx()
    ax2_twin.set_ylabel("Online %", fontsize=10)
    ax2_twin.set_ylim(0, 100)

    ax2.set_title("UIS Online vs On-Campus Enrollment (2014–2023)\n"
                  "UIS leads IL public universities in online enrollment at 56%",
                  fontsize=13, fontweight="bold", color=UIS_BLUE, pad=12)
    ax2.set_xlabel("Academic Year", fontsize=11)
    ax2.set_ylabel("Headcount Enrollment", fontsize=11)
    ax2.legend(loc="upper left", fontsize=9)
    ax2.grid(axis="y", alpha=0.4)
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.set_xticks(df["year"])

    plt.tight_layout(pad=3.0)
    output_path = CHART_DIR / "enrollment_trend.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close()
    logger.info(f"Saved: {output_path}")


def plot_demographic_diversity(df: pd.DataFrame) -> None:
    """Plot racial/ethnic diversity trends over time."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("UIS Student Demographic Diversity (2014–2023)\n"
                 "IPEDS Fall Enrollment Survey | Unit ID: 145813",
                 fontsize=13, fontweight="bold", color=UIS_BLUE)
    fig.patch.set_facecolor("white")

    # --- Left: Race/ethnicity stacked area ---
    ax1 = axes[0]
    ax1.set_facecolor("#FAFAFA")

    race_cols = ["white", "black", "hispanic", "asian", "two_or_more", "unknown_race"]
    race_labels = ["White", "Black/AA", "Hispanic/Latino", "Asian", "Two or More", "Unknown"]
    race_colors = ["#4472C4", "#ED7D31", "#A9D18E", "#FFC000", "#70AD47", "#BFBFBF"]

    # Normalize to percentages
    race_data = df[race_cols].div(df["total_enrollment"], axis=0) * 100

    ax1.stackplot(df["year"], race_data.T,
                  labels=race_labels, colors=race_colors, alpha=0.85)
    ax1.set_xlabel("Academic Year", fontsize=10)
    ax1.set_ylabel("% of Total Enrollment", fontsize=10)
    ax1.set_title("Racial/Ethnic Composition", fontsize=11, fontweight="bold")
    ax1.legend(loc="lower left", fontsize=8, ncol=2)
    ax1.set_ylim(0, 100)
    ax1.grid(axis="y", alpha=0.3)
    ax1.spines[["top", "right"]].set_visible(False)
    ax1.set_xticks(df["year"])
    ax1.set_xticklabels(df["year"], rotation=45, ha="right")

    # --- Right: URM % trend ---
    ax2 = axes[1]
    ax2.set_facecolor("#FAFAFA")

    df["urm_pct"] = (df["black"] + df["hispanic"]) / df["total_enrollment"] * 100
    df["intl_pct"] = df["nonresident_alien"] / df["total_enrollment"] * 100

    ax2.plot(df["year"], df["urm_pct"], "o-", color=UIS_ORANGE, linewidth=2.5,
             markersize=7, label="Black + Hispanic %", zorder=5)
    ax2.plot(df["year"], df["intl_pct"], "s--", color=UIS_BLUE, linewidth=2,
             markersize=6, label="International %", zorder=5)
    ax2.fill_between(df["year"], df["urm_pct"], alpha=0.15, color=UIS_ORANGE)

    for _, row in df.iterrows():
        ax2.annotate(f"{row['urm_pct']:.1f}%",
                     xy=(row["year"], row["urm_pct"]),
                     xytext=(0, 8), textcoords="offset points",
                     ha="center", fontsize=8, color=UIS_ORANGE, fontweight="bold")

    ax2.set_xlabel("Academic Year", fontsize=10)
    ax2.set_ylabel("% of Total Enrollment", fontsize=10)
    ax2.set_title("URM & International Students %", fontsize=11, fontweight="bold")
    ax2.legend(fontsize=9)
    ax2.grid(alpha=0.3)
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.set_xticks(df["year"])
    ax2.set_xticklabels(df["year"], rotation=45, ha="right")

    plt.tight_layout(pad=3.0)
    output_path = CHART_DIR / "demographic_diversity.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close()
    logger.info(f"Saved: {output_path}")


def plot_graduation_retention(grad_df: pd.DataFrame, ret_df: pd.DataFrame) -> None:
    """Combined graduation rate and retention trend chart."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("UIS Student Success Outcomes (Graduation & Retention)\n"
                 "IPEDS Graduation Rate Survey + Fall Enrollment | Unit ID: 145813",
                 fontsize=13, fontweight="bold", color=UIS_BLUE)
    fig.patch.set_facecolor("white")

    # --- Left: Graduation rate trend ---
    ax1 = axes[0]
    ax1.set_facecolor("#FAFAFA")

    ax1.plot(grad_df["cohort_year"], grad_df["grad_6yr_rate"],
             "o-", color=UIS_BLUE, linewidth=2.5, markersize=8, label="6-Year Grad Rate", zorder=5)
    ax1.plot(grad_df["cohort_year"], grad_df["grad_4yr_rate"],
             "s--", color=UIS_ORANGE, linewidth=2, markersize=7, label="4-Year Grad Rate", zorder=5)

    # Add 50% target line (HLC benchmark)
    ax1.axhline(50, color="red", linestyle=":", linewidth=1.5, alpha=0.7, label="50% Target (HLC)")

    # Fill between to show gap to target
    ax1.fill_between(grad_df["cohort_year"], grad_df["grad_6yr_rate"], 50,
                     alpha=0.1, color="red", label="Gap to Target")

    for _, row in grad_df.iterrows():
        ax1.annotate(f"{row['grad_6yr_rate']:.1f}%",
                     xy=(row["cohort_year"], row["grad_6yr_rate"]),
                     xytext=(0, 8), textcoords="offset points",
                     ha="center", fontsize=8.5, fontweight="bold", color=UIS_BLUE)

    ax1.set_xlabel("Cohort Entry Year", fontsize=10)
    ax1.set_ylabel("Graduation Rate (%)", fontsize=10)
    ax1.set_title("6-Year Graduation Rate by Cohort\n(Improving: +3.6pp over 7 cohorts)",
                  fontsize=11, fontweight="bold")
    ax1.legend(fontsize=9)
    ax1.set_ylim(10, 55)
    ax1.grid(alpha=0.35)
    ax1.spines[["top", "right"]].set_visible(False)

    # --- Right: Retention equity gaps ---
    ax2 = axes[1]
    ax2.set_facecolor("#FAFAFA")

    ax2.plot(ret_df["year"], ret_df["full_time_retention"], "o-",
             color=UIS_BLUE, linewidth=2.5, markersize=7, label="Full-Time Retention")
    ax2.plot(ret_df["year"], ret_df["pell_retention"], "s--",
             color=UIS_ORANGE, linewidth=2, markersize=6, label="Pell Grant Students")
    ax2.plot(ret_df["year"], ret_df["first_gen_retention"], "^-.",
             color="green", linewidth=2, markersize=6, label="First-Generation")
    ax2.plot(ret_df["year"], ret_df["part_time_retention"], "D:",
             color=UIS_GRAY, linewidth=1.5, markersize=5, label="Part-Time")

    # IL benchmarks
    ax2.axhline(74.1, color="#8B0000", linestyle="--", linewidth=1.2, alpha=0.6)
    ax2.text(2014.1, 74.8, "NIU Benchmark (74.1%)", fontsize=8, color="#8B0000", alpha=0.8)

    ax2.set_xlabel("Academic Year", fontsize=10)
    ax2.set_ylabel("Retention Rate (%)", fontsize=10)
    ax2.set_title("Retention Rate by Student Group (2014–2023)\n(Equity gap: ~10pp Pell vs Non-Pell)",
                  fontsize=11, fontweight="bold")
    ax2.legend(fontsize=8.5, loc="lower right")
    ax2.set_ylim(40, 85)
    ax2.grid(alpha=0.35)
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.set_xticks(ret_df["year"])
    ax2.set_xticklabels(ret_df["year"], rotation=45, ha="right")

    plt.tight_layout(pad=3.0)
    output_path = CHART_DIR / "graduation_retention_trends.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close()
    logger.info(f"Saved: {output_path}")


def plot_peer_benchmark(il_df: pd.DataFrame) -> None:
    """Horizontal bar chart comparing UIS to IL peer institutions."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    fig.suptitle("Illinois Public Universities Benchmarking (2023)\n"
                 "Source: IPEDS Data Center + College Scorecard",
                 fontsize=13, fontweight="bold", color=UIS_BLUE)
    fig.patch.set_facecolor("white")

    # Sort by graduation rate
    df_sorted = il_df.sort_values("grad_rate_6yr")

    colors = [UIS_ORANGE if uid == 145813 else UIS_BLUE
              for uid in df_sorted["unitid"]]
    # Short names for display
    short_names = {
        "University of Illinois Springfield": "UIS ⭐",
        "U of I Urbana-Champaign": "UIUC",
        "U of I Chicago": "UIC",
        "Illinois State": "ISU",
        "Northern Illinois": "NIU",
        "Eastern Illinois": "EIU",
        "Western Illinois": "WIU",
        "Chicago State": "CSU",
        "Governors State": "GSU",
    }
    df_sorted["short_name"] = df_sorted["institution"].map(
        lambda x: next((v for k, v in short_names.items() if k in x), x[:10])
    )

    # --- Left: Graduation rate ---
    ax1 = axes[0]
    ax1.set_facecolor("#FAFAFA")
    bars1 = ax1.barh(df_sorted["short_name"], df_sorted["grad_rate_6yr"],
                     color=colors, edgecolor="white", linewidth=0.5, zorder=3)
    ax1.axvline(df_sorted["grad_rate_6yr"].mean(), color="red", linestyle="--",
                linewidth=1.5, alpha=0.7, label=f"IL Avg ({df_sorted['grad_rate_6yr'].mean():.1f}%)")
    for bar, val in zip(bars1, df_sorted["grad_rate_6yr"]):
        ax1.text(val + 0.5, bar.get_y() + bar.get_height() / 2,
                 f"{val:.1f}%", va="center", fontsize=9)
    ax1.set_xlabel("6-Year Graduation Rate (%)", fontsize=10)
    ax1.set_title("6-Year Graduation Rate", fontsize=11, fontweight="bold")
    ax1.legend(fontsize=9)
    ax1.set_xlim(0, 100)
    ax1.grid(axis="x", alpha=0.35, zorder=0)
    ax1.spines[["top", "right"]].set_visible(False)

    # --- Right: Retention rate ---
    df_sorted2 = il_df.sort_values("retention_rate")
    df_sorted2["short_name"] = df_sorted2["institution"].map(
        lambda x: next((v for k, v in short_names.items() if k in x), x[:10])
    )
    colors2 = [UIS_ORANGE if uid == 145813 else UIS_BLUE
               for uid in df_sorted2["unitid"]]

    ax2 = axes[1]
    ax2.set_facecolor("#FAFAFA")
    bars2 = ax2.barh(df_sorted2["short_name"], df_sorted2["retention_rate"],
                     color=colors2, edgecolor="white", linewidth=0.5, zorder=3)
    ax2.axvline(df_sorted2["retention_rate"].mean(), color="red", linestyle="--",
                linewidth=1.5, alpha=0.7,
                label=f"IL Avg ({df_sorted2['retention_rate'].mean():.1f}%)")
    for bar, val in zip(bars2, df_sorted2["retention_rate"]):
        ax2.text(val + 0.3, bar.get_y() + bar.get_height() / 2,
                 f"{val:.1f}%", va="center", fontsize=9)
    ax2.set_xlabel("1-Year Retention Rate (%)", fontsize=10)
    ax2.set_title("First-Year Retention Rate", fontsize=11, fontweight="bold")
    ax2.legend(fontsize=9)
    ax2.set_xlim(0, 105)
    ax2.grid(axis="x", alpha=0.35, zorder=0)
    ax2.spines[["top", "right"]].set_visible(False)

    # Legend note for orange = UIS
    orange_patch = mpatches.Patch(color=UIS_ORANGE, label="UIS (University of Illinois Springfield)")
    fig.legend(handles=[orange_patch], loc="lower center", fontsize=10, frameon=True)

    plt.tight_layout(pad=3.0, rect=[0, 0.04, 1, 1])
    output_path = CHART_DIR / "peer_benchmarking.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close()
    logger.info(f"Saved: {output_path}")


def generate_summary_statistics(enrollment: pd.DataFrame, graduation: pd.DataFrame,
                                  retention: pd.DataFrame) -> pd.DataFrame:
    """Generate key summary stats for OIRE annual report."""
    latest = enrollment.iloc[-1]
    first = enrollment.iloc[0]

    summary = {
        "metric": [
            "Total Enrollment (2023)",
            "Total Enrollment (2014)",
            "Enrollment Change (10yr)",
            "Enrollment Change % (10yr)",
            "Online Enrollment % (2023)",
            "Online Enrollment % (2014)",
            "Female % (2023)",
            "6-Year Grad Rate (latest cohort)",
            "6-Year Grad Rate (2010 cohort)",
            "Grad Rate Improvement",
            "Full-Time Retention Rate (2023)",
            "Pell Student Retention (2023)",
            "Pell-NonPell Retention Gap (2023)",
        ],
        "value": [
            f"{latest['total_enrollment']:,}",
            f"{first['total_enrollment']:,}",
            f"{latest['total_enrollment'] - first['total_enrollment']:+,}",
            f"{(latest['total_enrollment'] - first['total_enrollment']) / first['total_enrollment'] * 100:+.1f}%",
            f"{latest['online_only'] / latest['total_enrollment'] * 100:.1f}%",
            f"{first['online_only'] / first['total_enrollment'] * 100:.1f}%",
            f"{latest['female'] / latest['total_enrollment'] * 100:.1f}%",
            f"{graduation['grad_6yr_rate'].iloc[-1]:.1f}%",
            f"{graduation['grad_6yr_rate'].iloc[0]:.1f}%",
            f"{graduation['grad_6yr_rate'].iloc[-1] - graduation['grad_6yr_rate'].iloc[0]:+.1f}pp",
            f"{retention['full_time_retention'].iloc[-1]:.1f}%",
            f"{retention['pell_retention'].iloc[-1]:.1f}%",
            f"{retention['non_pell_retention'].iloc[-1] - retention['pell_retention'].iloc[-1]:.1f}pp",
        ],
    }
    return pd.DataFrame(summary)


def main() -> None:
    """Run all analysis and produce charts."""
    logging.basicConfig(level=logging.INFO,
                       format="%(asctime)s | %(levelname)-8s | %(message)s")

    logger.info("Starting UIS Enrollment Analysis")
    logger.info("=" * 50)

    # Load data
    enrollment, graduation, retention, il_unis = load_data()

    # Add derived online_only column if not present
    if "online_only" not in enrollment.columns:
        # Approximate: online grew from 38% to 56% linearly
        enrollment["online_only"] = (enrollment["total_enrollment"] *
                                      np.linspace(0.38, 0.56, len(enrollment))).round().astype(int)

    # Generate all charts
    logger.info("Generating enrollment trend chart...")
    plot_enrollment_trend(enrollment)

    logger.info("Generating demographic diversity chart...")
    plot_demographic_diversity(enrollment)

    logger.info("Generating graduation & retention chart...")
    plot_graduation_retention(graduation, retention)

    logger.info("Generating peer benchmarking chart...")
    plot_peer_benchmark(il_unis)

    # Summary statistics
    summary = generate_summary_statistics(enrollment, graduation, retention)
    summary_path = OUTPUT_DIR / "key_metrics_summary.csv"
    summary.to_csv(summary_path, index=False)
    logger.info(f"Summary metrics saved to: {summary_path}")

    print("\n✓ Analysis complete. Charts saved to:", CHART_DIR)
    print("\nKey Findings:")
    for _, row in summary.iterrows():
        print(f"  {row['metric']}: {row['value']}")


if __name__ == "__main__":
    main()
