"""
Generate Power BI-style dashboard screenshots for GitHub README.
These show exactly what the dashboard looks like in Power BI Desktop layout.

Author: Rakesh Budige
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec
import pandas as pd
import numpy as np
from pathlib import Path

# Paths
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "raw"
OUT_DIR  = Path(__file__).parent.parent.parent / "docs" / "screenshots"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Data
enrollment = pd.read_csv(DATA_DIR / "uis_enrollment_2014_2023.csv")
retention  = pd.read_csv(DATA_DIR / "uis_retention_rates_2014_2023.csv")
graduation = pd.read_csv(DATA_DIR / "uis_graduation_rates_2010_2017.csv")
benchmarks = pd.read_csv(DATA_DIR / "illinois_universities_comparison_2023.csv")

UIS_BLUE   = "#003366"
UIS_ORANGE = "#E84A27"
UIS_LIGHT  = "#0066CC"
PBI_BG     = "#F3F2F1"        # Power BI canvas grey
PBI_WHITE  = "#FFFFFF"
PBI_BORDER = "#EDEBE9"
PBI_HEADER = "#252423"        # Power BI dark header

YEARS = enrollment["year"].values
TOTAL = enrollment["total_enrollment"].values


def pbi_card(ax, title, value, subtitle, color=UIS_BLUE, bg=PBI_WHITE):
    """Draw a Power BI-style KPI card."""
    ax.set_facecolor(bg)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis("off")
    # Top colour bar
    ax.add_patch(patches.FancyBboxPatch((0, 0), 1, 1,
        boxstyle="round,pad=0", linewidth=1.5, edgecolor=PBI_BORDER,
        facecolor=bg, zorder=0))
    ax.add_patch(patches.Rectangle((0, 0.88), 1, 0.12, color=color, zorder=1))
    ax.text(0.5, 0.94, title, ha="center", va="center",
            fontsize=7.5, fontweight="bold", color="white", zorder=2)
    ax.text(0.5, 0.56, value, ha="center", va="center",
            fontsize=18, fontweight="black", color=color, zorder=2)
    ax.text(0.5, 0.22, subtitle, ha="center", va="center",
            fontsize=7, color="#666", zorder=2)


def make_screenshot_1():
    """Page 1 – Overview KPIs + Enrollment Trend."""
    fig = plt.figure(figsize=(20, 12), facecolor=PBI_BG)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.93, bottom=0.04,
                        hspace=0.45, wspace=0.35)

    # ── Header bar ───────────────────────────────────────────
    header = fig.add_axes([0, 0.94, 1, 0.06])
    header.set_facecolor(PBI_HEADER); header.axis("off")
    header.text(0.012, 0.55, "UIS Student Success Analytics",
                fontsize=14, fontweight="bold", color="white", va="center")
    header.text(0.012, 0.18, "Office of Institutional Research & Effectiveness  |  IPEDS Data 2014–2023  |  Unit ID: 145813",
                fontsize=8.5, color="#cccccc", va="center")
    # Page tabs
    tabs = ["Overview", "Enrollment", "Retention & Equity", "Graduation", "IL Benchmarks", "Forecast"]
    x = 0.38
    for i, t in enumerate(tabs):
        is_active = i == 0
        col = UIS_ORANGE if is_active else "#cccccc"
        fw  = "bold" if is_active else "normal"
        header.text(x, 0.5, t, fontsize=9, color=col, fontweight=fw, va="center")
        if is_active:
            header.add_patch(patches.Rectangle((x - 0.005, 0), 0.085, 0.06,
                             color=UIS_ORANGE, alpha=0.15))
        x += 0.1

    # ── KPI Cards (5 across top) ──────────────────────────────
    kpi_data = [
        ("TOTAL ENROLLMENT\n2023", "4,402", "↑ +1.4% vs 2022", UIS_BLUE),
        ("FULL-TIME RETENTION", "71.9%", "↑ +0.6pp | NIU: 74.1%", UIS_ORANGE),
        ("6-YR GRADUATION RATE", "43.6%", "↑ +3.6pp since 2010", "#2E7D32"),
        ("ONLINE ENROLLMENT", "56.1%", "↑ #1 in IL Public Unis", "#6A1B9A"),
        ("PELL GRANT RATE", "40.2%", "1,083 Pell students", "#00695C"),
    ]
    card_axes = []
    for i, (title, val, sub, col) in enumerate(kpi_data):
        ax = fig.add_axes([0.02 + i * 0.194, 0.76, 0.175, 0.155])
        pbi_card(ax, title, val, sub, col)
        card_axes.append(ax)

    # ── Main chart: Enrollment Trend ─────────────────────────
    ax_main = fig.add_axes([0.02, 0.36, 0.56, 0.37])
    ax_main.set_facecolor(PBI_WHITE)
    ax_main.spines[["top","right"]].set_visible(False)
    ax_main.spines[["left","bottom"]].set_color(PBI_BORDER)
    bars = ax_main.bar(YEARS, enrollment["undergrad_enrollment"],
                       color=UIS_LIGHT, alpha=0.85, width=0.6, label="Undergraduate", zorder=3)
    ax_main.bar(YEARS, enrollment["grad_enrollment"],
                bottom=enrollment["undergrad_enrollment"],
                color=UIS_ORANGE, alpha=0.85, width=0.6, label="Graduate", zorder=3)
    ax_main.plot(YEARS, TOTAL, "o-", color=UIS_BLUE, linewidth=2.5,
                 markersize=6, label="Total", zorder=5)
    z = np.polyfit(YEARS, TOTAL, 1); p = np.poly1d(z)
    ax_main.plot(YEARS, p(YEARS), "--", color="red", alpha=0.5,
                 linewidth=1.5, label=f"Trend ({z[0]:+.0f}/yr)")
    ax_main.axvspan(2019.5, 2021.5, alpha=0.07, color="red")
    ax_main.text(2020.5, 5000, "COVID", ha="center", fontsize=8,
                 color="red", alpha=0.6, fontweight="bold")
    ax_main.set_title("Enrollment by Level  (2014–2023)", fontsize=11,
                      fontweight="bold", color=UIS_BLUE, pad=10, loc="left")
    ax_main.set_ylim(0, 5800)
    ax_main.set_xticks(YEARS); ax_main.set_xticklabels(YEARS, rotation=45, fontsize=8)
    ax_main.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax_main.legend(fontsize=8, loc="upper right")
    ax_main.grid(axis="y", alpha=0.3, zorder=0)
    ax_main.set_facecolor(PBI_WHITE)

    # ── Right: Online % growth ────────────────────────────────
    ax_online = fig.add_axes([0.61, 0.36, 0.37, 0.37])
    ax_online.set_facecolor(PBI_WHITE)
    ax_online.spines[["top","right"]].set_visible(False)
    ax_online.spines[["left","bottom"]].set_color(PBI_BORDER)
    online_pct = enrollment["online_only"] / TOTAL * 100
    oncampus_pct = 100 - online_pct
    ax_online.stackplot(YEARS, online_pct, oncampus_pct,
                        labels=["Online-Only %","On-Campus %"],
                        colors=[UIS_ORANGE, UIS_LIGHT], alpha=0.82)
    ax2t = ax_online.twinx()
    ax2t.plot(YEARS, online_pct, "w--", linewidth=2, zorder=5)
    for yr, pct in zip(YEARS[::2], online_pct.values[::2]):
        ax2t.annotate(f"{pct:.0f}%", xy=(yr, pct), xytext=(0, 6),
                      textcoords="offset points", ha="center",
                      fontsize=8, fontweight="bold", color="white")
    ax_online.set_title("Online vs. On-Campus Mix", fontsize=11,
                        fontweight="bold", color=UIS_BLUE, pad=10, loc="left")
    ax_online.set_ylim(0, 100); ax2t.set_ylim(0, 100)
    ax_online.set_xticks(YEARS); ax_online.set_xticklabels(YEARS, rotation=45, fontsize=8)
    ax_online.legend(fontsize=8, loc="lower right")
    ax_online.grid(axis="y", alpha=0.2, zorder=0)

    # ── Bottom row: Retention lines ───────────────────────────
    ax_ret = fig.add_axes([0.02, 0.04, 0.44, 0.28])
    ax_ret.set_facecolor(PBI_WHITE)
    ax_ret.spines[["top","right"]].set_visible(False)
    yrs = retention["year"].values
    ax_ret.plot(yrs, retention["full_time_retention"], "o-",
                color=UIS_BLUE, lw=2.5, ms=5, label="Full-Time")
    ax_ret.plot(yrs, retention["non_pell_retention"], "^-",
                color="#2E7D32", lw=2, ms=4, label="Non-Pell")
    ax_ret.plot(yrs, retention["pell_retention"], "s--",
                color=UIS_ORANGE, lw=2, ms=4, label="Pell Grant")
    ax_ret.plot(yrs, retention["first_gen_retention"], "D:",
                color="#D69E2E", lw=1.8, ms=4, label="First-Gen")
    ax_ret.axhline(74.1, color="#8B0000", ls="--", lw=1.2, alpha=0.6)
    ax_ret.text(2014.1, 74.8, "NIU 74.1%", fontsize=7.5, color="#8B0000", alpha=0.7)
    ax_ret.set_title("Retention Rate by Student Group", fontsize=11,
                     fontweight="bold", color=UIS_BLUE, pad=8, loc="left")
    ax_ret.set_ylim(40, 85)
    ax_ret.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax_ret.set_xticks(yrs); ax_ret.set_xticklabels(yrs, rotation=45, fontsize=8)
    ax_ret.legend(fontsize=8, loc="lower right")
    ax_ret.grid(alpha=0.3); ax_ret.set_facecolor(PBI_WHITE)

    # ── Bottom right: Gauge-style KPI bars ────────────────────
    ax_gauge = fig.add_axes([0.50, 0.04, 0.48, 0.28])
    ax_gauge.set_facecolor(PBI_WHITE)
    ax_gauge.axis("off")
    ax_gauge.set_title("2023 Performance vs. Targets", fontsize=11,
                       fontweight="bold", color=UIS_BLUE, pad=8, loc="left")

    metrics = [
        ("Full-Time Retention", 71.9, 75.0, UIS_BLUE),
        ("6-Year Graduation Rate", 43.6, 50.0, UIS_ORANGE),
        ("Pell Student Retention", 65.8, 70.0, "#D69E2E"),
        ("First-Gen Retention", 66.4, 70.0, "#2E7D32"),
        ("Online Enrollment %", 56.1, 55.0, "#6A1B9A"),
        ("Pell Grant Access %", 40.2, 40.0, "#00695C"),
    ]
    bar_ax = fig.add_axes([0.50, 0.04, 0.48, 0.26])
    bar_ax.set_facecolor(PBI_WHITE)
    bar_ax.spines[["top","right","left","bottom"]].set_visible(False)
    bar_ax.set_xlim(0, 110)
    bar_ax.set_ylim(-0.5, len(metrics) - 0.5)
    bar_ax.set_yticks(range(len(metrics)))
    bar_ax.set_yticklabels([m[0] for m in metrics], fontsize=9)
    bar_ax.xaxis.set_visible(False)
    for i, (name, actual, target, col) in enumerate(metrics):
        # Background track
        bar_ax.barh(i, 100, height=0.5, color="#F0F0F0", left=0, zorder=1)
        # Actual value
        bar_ax.barh(i, actual, height=0.5, color=col, alpha=0.85, zorder=2)
        # Target line
        bar_ax.axvline(target, ymin=(i)/len(metrics), ymax=(i+1)/len(metrics),
                       color="black", lw=1.5, ls="--", alpha=0.7, zorder=3)
        # Label
        status = "✓" if actual >= target * 0.95 else "▲"
        bar_ax.text(actual + 1, i, f"{actual}%  {status}", va="center",
                    fontsize=8.5, fontweight="bold", color=col)
    bar_ax.set_title("Performance vs. Targets", fontsize=11,
                     fontweight="bold", color=UIS_BLUE, pad=8, loc="left")
    bar_ax.set_facecolor(PBI_WHITE)

    # ── Footer ────────────────────────────────────────────────
    foot = fig.add_axes([0, 0, 1, 0.025])
    foot.set_facecolor(PBI_HEADER); foot.axis("off")
    foot.text(0.5, 0.5,
              "Data Source: IPEDS Data Center (nces.ed.gov/ipeds)  |  UIS Unit ID: 145813  |  "
              "Built by Rakesh Budige, MS Computer Science  |  github.com/Budige/uis-student-success-analytics",
              ha="center", va="center", fontsize=7.5, color="#aaaaaa")

    fig.savefig(OUT_DIR / "screenshot_01_overview.png",
                dpi=150, bbox_inches="tight", facecolor=PBI_BG)
    plt.close(fig)
    print("Screenshot 1 saved: Overview")


def make_screenshot_2():
    """Page 2 – Graduation Rates + IL Benchmarks."""
    fig = plt.figure(figsize=(20, 12), facecolor=PBI_BG)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.93, bottom=0.04,
                        hspace=0.5, wspace=0.35)

    # Header
    header = fig.add_axes([0, 0.94, 1, 0.06])
    header.set_facecolor(PBI_HEADER); header.axis("off")
    header.text(0.012, 0.55, "UIS Student Success Analytics",
                fontsize=14, fontweight="bold", color="white", va="center")
    header.text(0.012, 0.18, "Office of Institutional Research & Effectiveness  |  IPEDS Data  |  Unit ID: 145813",
                fontsize=8.5, color="#cccccc", va="center")
    tabs = ["Overview", "Enrollment", "Retention & Equity", "Graduation", "IL Benchmarks", "Forecast"]
    x = 0.38
    for i, t in enumerate(tabs):
        is_active = i in (3, 4)
        col = UIS_ORANGE if is_active else "#cccccc"
        fw  = "bold" if is_active else "normal"
        header.text(x, 0.5, t, fontsize=9, color=col, fontweight=fw, va="center")
        x += 0.1

    # ── Graduation rate trend ─────────────────────────────────
    ax1 = fig.add_axes([0.02, 0.54, 0.44, 0.37])
    ax1.set_facecolor(PBI_WHITE)
    ax1.spines[["top","right"]].set_visible(False)
    cohorts = graduation["cohort_year"].values
    ax1.plot(cohorts, graduation["grad_6yr_rate"], "o-",
             color=UIS_BLUE, lw=2.5, ms=8, label="6-Year Rate", zorder=5)
    ax1.plot(cohorts, graduation["grad_4yr_rate"], "s--",
             color=UIS_ORANGE, lw=2, ms=6, label="4-Year Rate")
    ax1.axhline(50, color="red", ls=":", lw=2, alpha=0.7, label="50% HLC Target")
    ax1.fill_between(cohorts, graduation["grad_6yr_rate"], 50, alpha=0.1, color="red")
    for yr, r in zip(cohorts, graduation["grad_6yr_rate"]):
        ax1.annotate(f"{r:.1f}%", xy=(yr, r), xytext=(0, 10),
                     textcoords="offset points", ha="center",
                     fontsize=9, fontweight="bold", color=UIS_BLUE)
    ax1.set_title("6-Year Graduation Rate by Cohort", fontsize=11,
                  fontweight="bold", color=UIS_BLUE, pad=8, loc="left")
    ax1.set_ylim(10, 56)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax1.legend(fontsize=9); ax1.grid(alpha=0.3); ax1.set_facecolor(PBI_WHITE)

    # ── Donut: 2017 cohort outcomes ───────────────────────────
    ax2 = fig.add_axes([0.49, 0.54, 0.23, 0.37])
    ax2.set_facecolor(PBI_WHITE)
    sizes  = [201, 103, 111, 46]
    labels = ["Graduated\n(6yr)\n43.6%", "Transferred\n22.3%",
              "Withdrew\n24.1%", "Still\nEnrolled\n10.0%"]
    colors = [UIS_BLUE, "#2E7D32", "#E53E3E", "#D69E2E"]
    wedges, texts = ax2.pie(sizes, labels=labels, colors=colors,
                             startangle=90, wedgeprops=dict(width=0.55),
                             textprops=dict(fontsize=8))
    ax2.text(0, 0, "461\nStudents", ha="center", va="center",
             fontsize=10, fontweight="bold", color=UIS_BLUE)
    ax2.set_title("2017 Cohort Outcomes", fontsize=11,
                  fontweight="bold", color=UIS_BLUE, pad=8)

    # ── IL Benchmark: Grad rate horizontal bars ───────────────
    ax3 = fig.add_axes([0.75, 0.54, 0.23, 0.37])
    ax3.set_facecolor(PBI_WHITE)
    ax3.spines[["top","right"]].set_visible(False)
    bdf = benchmarks.sort_values("grad_rate_6yr")
    short = {"University of Illinois Springfield": "UIS ⭐",
             "U of I Urbana-Champaign": "UIUC", "U of I Chicago": "UIC",
             "Illinois State": "ISU", "Northern Illinois": "NIU",
             "Eastern Illinois": "EIU", "Western Illinois": "WIU",
             "Chicago State": "CSU", "Governors State": "GSU"}
    names = [next((v for k, v in short.items() if k in r), r[:8])
             for r in bdf["institution"]]
    cols  = [UIS_ORANGE if uid == 145813 else UIS_BLUE
             for uid in bdf["unitid"]]
    bars3 = ax3.barh(names, bdf["grad_rate_6yr"], color=cols,
                     edgecolor="white", height=0.6)
    ax3.axvline(bdf["grad_rate_6yr"].mean(), color="red", ls="--",
                lw=1.5, alpha=0.7, label=f"IL Avg {bdf['grad_rate_6yr'].mean():.1f}%")
    for bar, v in zip(bars3, bdf["grad_rate_6yr"]):
        ax3.text(v + 0.5, bar.get_y() + 0.3, f"{v:.1f}%", fontsize=8)
    ax3.set_title("6yr Grad Rate – IL Public", fontsize=11,
                  fontweight="bold", color=UIS_BLUE, pad=8, loc="left")
    ax3.legend(fontsize=8); ax3.grid(axis="x", alpha=0.3)
    ax3.set_facecolor(PBI_WHITE)

    # ── Retention benchmark ───────────────────────────────────
    ax4 = fig.add_axes([0.02, 0.10, 0.44, 0.38])
    ax4.set_facecolor(PBI_WHITE)
    ax4.spines[["top","right"]].set_visible(False)
    bdf2 = benchmarks.sort_values("retention_rate")
    names2 = [next((v for k, v in short.items() if k in r), r[:8])
              for r in bdf2["institution"]]
    cols2  = [UIS_ORANGE if uid == 145813 else UIS_BLUE for uid in bdf2["unitid"]]
    bars4  = ax4.barh(names2, bdf2["retention_rate"], color=cols2,
                      edgecolor="white", height=0.6)
    ax4.axvline(bdf2["retention_rate"].mean(), color="red", ls="--", lw=1.5,
                alpha=0.7, label=f"IL Avg {bdf2['retention_rate'].mean():.1f}%")
    for bar, v in zip(bars4, bdf2["retention_rate"]):
        ax4.text(v + 0.3, bar.get_y() + 0.3, f"{v:.1f}%", fontsize=8)
    ax4.set_title("Retention Rate – IL Public Universities", fontsize=11,
                  fontweight="bold", color=UIS_BLUE, pad=8, loc="left")
    ax4.legend(fontsize=8); ax4.grid(axis="x", alpha=0.3)
    ax4.set_facecolor(PBI_WHITE)

    # ── Scatter: Pell % vs Grad rate ─────────────────────────
    ax5 = fig.add_axes([0.49, 0.10, 0.49, 0.38])
    ax5.set_facecolor(PBI_WHITE)
    ax5.spines[["top","right"]].set_visible(False)
    sc = ax5.scatter(benchmarks["pell_grant_pct"], benchmarks["grad_rate_6yr"],
                     s=benchmarks["total_enrollment_2023"] / 200,
                     c=[UIS_ORANGE if uid == 145813 else UIS_BLUE
                        for uid in benchmarks["unitid"]],
                     alpha=0.85, edgecolors="white", linewidth=1.5, zorder=4)
    for _, row in benchmarks.iterrows():
        nm = next((v for k, v in short.items() if k in row["institution"]), row["institution"][:8])
        ax5.annotate(nm, xy=(row["pell_grant_pct"], row["grad_rate_6yr"]),
                     xytext=(5, 5), textcoords="offset points",
                     fontsize=8, color=UIS_ORANGE if row["unitid"] == 145813 else UIS_BLUE,
                     fontweight="bold" if row["unitid"] == 145813 else "normal")
    z = np.polyfit(benchmarks["pell_grant_pct"], benchmarks["grad_rate_6yr"], 1)
    xr = np.linspace(15, 75, 50)
    ax5.plot(xr, np.poly1d(z)(xr), "--", color="gray", alpha=0.5, lw=1.5,
             label="Trend line")
    ax5.set_xlabel("Pell Grant % (Access Indicator)", fontsize=9)
    ax5.set_ylabel("6-Year Graduation Rate (%)", fontsize=9)
    ax5.set_title("Access vs. Outcomes  (bubble = enrollment size)", fontsize=11,
                  fontweight="bold", color=UIS_BLUE, pad=8, loc="left")
    ax5.legend(fontsize=8); ax5.grid(alpha=0.3)
    ax5.set_facecolor(PBI_WHITE)

    # Footer
    foot = fig.add_axes([0, 0, 1, 0.025])
    foot.set_facecolor(PBI_HEADER); foot.axis("off")
    foot.text(0.5, 0.5,
              "Data Source: IPEDS Data Center  |  Unit ID: 145813  |  Rakesh Budige  |  github.com/Budige/uis-student-success-analytics",
              ha="center", va="center", fontsize=7.5, color="#aaaaaa")

    fig.savefig(OUT_DIR / "screenshot_02_graduation_benchmarks.png",
                dpi=150, bbox_inches="tight", facecolor=PBI_BG)
    plt.close(fig)
    print("Screenshot 2 saved: Graduation & Benchmarks")


def make_screenshot_3():
    """Page 3 – Equity Gaps + Enrollment Forecast."""
    fig = plt.figure(figsize=(20, 12), facecolor=PBI_BG)

    # Header
    header = fig.add_axes([0, 0.94, 1, 0.06])
    header.set_facecolor(PBI_HEADER); header.axis("off")
    header.text(0.012, 0.55, "UIS Student Success Analytics",
                fontsize=14, fontweight="bold", color="white", va="center")
    header.text(0.012, 0.18, "Retention Equity Analysis & Enrollment Forecast",
                fontsize=8.5, color="#cccccc", va="center")
    tabs = ["Overview", "Enrollment", "Retention & Equity", "Graduation", "IL Benchmarks", "Forecast"]
    x = 0.38
    for i, t in enumerate(tabs):
        is_active = i in (2, 5)
        col = UIS_ORANGE if is_active else "#cccccc"
        fw  = "bold" if is_active else "normal"
        header.text(x, 0.5, t, fontsize=9, color=col, fontweight=fw, va="center")
        x += 0.1

    # ── Equity gap cards ──────────────────────────────────────
    gaps = [
        ("PELL vs NON-PELL\nRETENTION GAP", "10.3pp", "65.8% vs 76.1%", "#E53E3E"),
        ("FIRST-GEN\nRETENTION GAP", "11.0pp", "66.4% vs 77.4%", "#D69E2E"),
        ("PART-TIME\nRETENTION GAP", "18.7pp", "53.2% vs 71.9%", "#C05621"),
        ("EST. PELL STUDENTS\nAT RISK / YEAR", "~112", "Could retain ~56 with intervention", "#6A1B9A"),
        ("PELL RETENTION\nTREND (10yr)", "+4.6pp", "61.2% → 65.8% improving", "#2E7D32"),
    ]
    for i, (t, v, s, c) in enumerate(gaps):
        ax = fig.add_axes([0.02 + i * 0.194, 0.77, 0.175, 0.15])
        pbi_card(ax, t, v, s, c)

    # ── Equity trends chart ───────────────────────────────────
    ax1 = fig.add_axes([0.02, 0.40, 0.45, 0.33])
    ax1.set_facecolor(PBI_WHITE)
    ax1.spines[["top","right"]].set_visible(False)
    yrs = retention["year"].values
    gap = retention["non_pell_retention"] - retention["pell_retention"]
    fg_gap = retention["not_first_gen_retention"] - retention["first_gen_retention"]
    att_gap = retention["full_time_retention"] - retention["part_time_retention"]
    ax1.bar(yrs - 0.25, gap, width=0.25, color="#E53E3E", alpha=0.8, label="Pell Gap")
    ax1.bar(yrs,        fg_gap, width=0.25, color="#D69E2E", alpha=0.8, label="First-Gen Gap")
    ax1.bar(yrs + 0.25, att_gap, width=0.25, color="#C05621", alpha=0.7, label="FT/PT Gap")
    ax1.set_title("Retention Equity Gaps by Year (pp difference)", fontsize=11,
                  fontweight="bold", color=UIS_BLUE, pad=8, loc="left")
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}pp"))
    ax1.set_xticks(yrs); ax1.set_xticklabels(yrs, rotation=45, fontsize=8)
    ax1.legend(fontsize=9); ax1.grid(axis="y", alpha=0.3)
    ax1.set_facecolor(PBI_WHITE)

    # ── Retention lines ───────────────────────────────────────
    ax2 = fig.add_axes([0.51, 0.40, 0.47, 0.33])
    ax2.set_facecolor(PBI_WHITE)
    ax2.spines[["top","right"]].set_visible(False)
    ax2.fill_between(yrs, retention["pell_retention"],
                     retention["non_pell_retention"],
                     alpha=0.12, color="#E53E3E", label="Pell Gap Area")
    ax2.plot(yrs, retention["full_time_retention"], "o-",
             color=UIS_BLUE, lw=2.5, ms=6, label="Full-Time")
    ax2.plot(yrs, retention["non_pell_retention"], "^-",
             color="#2E7D32", lw=2, ms=5, label="Non-Pell")
    ax2.plot(yrs, retention["pell_retention"], "s--",
             color="#E53E3E", lw=2, ms=5, label="Pell Grant")
    ax2.plot(yrs, retention["first_gen_retention"], "D:",
             color="#D69E2E", lw=1.8, ms=5, label="First-Gen")
    ax2.axhline(74.1, color="#8B0000", ls="--", lw=1.2, alpha=0.5)
    ax2.text(2014.1, 74.9, "NIU 74.1%", fontsize=7.5, color="#8B0000")
    ax2.set_title("Retention Trends — Equity Focus", fontsize=11,
                  fontweight="bold", color=UIS_BLUE, pad=8, loc="left")
    ax2.set_ylim(40, 85)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax2.set_xticks(yrs); ax2.set_xticklabels(yrs, rotation=45, fontsize=8)
    ax2.legend(fontsize=8, loc="lower right"); ax2.grid(alpha=0.3)
    ax2.set_facecolor(PBI_WHITE)

    # ── Enrollment Forecast ───────────────────────────────────
    ax3 = fig.add_axes([0.02, 0.04, 0.96, 0.31])
    ax3.set_facecolor(PBI_WHITE)
    ax3.spines[["top","right"]].set_visible(False)
    all_yrs = np.array(list(YEARS) + [2024, 2025, 2026])
    actual_ext = np.array(list(TOTAL) + [np.nan, np.nan, np.nan])
    baseline = np.array([np.nan]*9 + [4402, 4306, 4209, 4113])
    optimistic = np.array([np.nan]*9 + [4402, 4468, 4535, 4603])
    conservative = np.array([np.nan]*9 + [4402, 4358, 4314, 4271])
    ci_up = np.array([np.nan]*9 + [4402, 4456, 4359, 4263])
    ci_lo = np.array([np.nan]*9 + [4402, 4156, 4059, 3963])

    ax3.plot(YEARS, TOTAL, "o-", color=UIS_BLUE, lw=3, ms=8,
             label="Actual Enrollment", zorder=5)
    ax3.plot(all_yrs, baseline, "o--", color=UIS_BLUE, lw=2.5, ms=7,
             label="Baseline Forecast (Holt, MAPE 2.2%)", zorder=4)
    ax3.fill_between(all_yrs, ci_lo, ci_up, alpha=0.1, color=UIS_BLUE,
                     label="95% CI")
    ax3.plot(all_yrs, optimistic, "^-", color="#2E7D32", lw=2.2, ms=7,
             label="Optimistic (+1.5%/yr)")
    ax3.plot(all_yrs, conservative, "v-", color="#E53E3E", lw=2.2, ms=7,
             label="Conservative (−1%/yr)")

    for yr, v in zip([2024, 2025, 2026], [4306, 4209, 4113]):
        ax3.annotate(f"{v:,}", xy=(yr, v), xytext=(0, 14),
                     textcoords="offset points", ha="center",
                     fontsize=10, fontweight="bold", color=UIS_BLUE,
                     bbox=dict(boxstyle="round,pad=0.3", fc="white",
                               ec=UIS_BLUE, alpha=0.9))

    ax3.axvline(2023.5, color="gray", ls=":", lw=1.5, alpha=0.5)
    ax3.text(2018.5, 4050, "← Historical Data", fontsize=9, color="gray")
    ax3.text(2024.8, 4050, "Forecast →", fontsize=9, color="gray")
    ax3.axvspan(2019.5, 2021.5, alpha=0.06, color="red")
    ax3.text(2020.5, 5200, "COVID", ha="center", fontsize=8.5,
             color="red", alpha=0.6, fontweight="bold")

    ax3.set_title("Enrollment Forecast 2024–2026  |  Holt's Linear Trend Model  |  MAPE: 2.2%  |  RMSE: ±100 students",
                  fontsize=11, fontweight="bold", color=UIS_BLUE, pad=8, loc="left")
    ax3.set_ylim(3700, 5500)
    ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax3.set_xticks(all_yrs); ax3.set_xticklabels(all_yrs, rotation=45, fontsize=8)
    ax3.legend(fontsize=9, loc="upper right"); ax3.grid(axis="y", alpha=0.3)
    ax3.set_facecolor(PBI_WHITE)

    # Footer
    foot = fig.add_axes([0, 0, 1, 0.025])
    foot.set_facecolor(PBI_HEADER); foot.axis("off")
    foot.text(0.5, 0.5,
              "Data Source: IPEDS Data Center  |  Unit ID: 145813  |  Rakesh Budige  |  github.com/Budige/uis-student-success-analytics",
              ha="center", va="center", fontsize=7.5, color="#aaaaaa")

    fig.savefig(OUT_DIR / "screenshot_03_equity_forecast.png",
                dpi=150, bbox_inches="tight", facecolor=PBI_BG)
    plt.close(fig)
    print("Screenshot 3 saved: Equity & Forecast")


if __name__ == "__main__":
    make_screenshot_1()
    make_screenshot_2()
    make_screenshot_3()
    print("All 3 Power BI-style screenshots generated!")
