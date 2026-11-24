import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set publication-grade visual theme
plt.rcParams["figure.dpi"] = 150
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
sns.set_style("whitegrid")

# ==============================================================================
# 1. DATA INGESTION & MES TELEMETRY HYGIENE AUDIT
# ==============================================================================
FILE_PATH = "wafer_metrology_120k.csv"
raw_df = pd.read_csv(FILE_PATH)

total_raw = len(raw_df)
# Audit missing readings on unique wafers, after removing exact retry rows.
df = raw_df.drop_duplicates().copy()
dup_count = total_raw - len(df)
raw_null_rows = raw_df.isna().any(axis=1).sum()
null_rows = df.isna().any(axis=1).sum()
null_by_col = df.isna().sum()
null_by_col = null_by_col[null_by_col > 0]

print("=" * 70)
print("1. MES TELEMETRY HYGIENE SUMMARY")
print("=" * 70)
print(f"Raw Records Ingested     : {total_raw:,}")
print(f"Exact Duplicate Rows     : {dup_count:,} ({dup_count / total_raw * 100:.2f}%) -> Removed")
print(f"Clean Unique Wafers      : {len(df):,}")
print(f"Raw Rows with Missing Readings: {raw_null_rows:,}")
print(f"Unique Wafers with Missing Readings: {null_rows:,} ({null_rows / len(df) * 100:.2f}%)")
print("\nMissing Readings by Metrology Channel (Unique Wafers):")
print(null_by_col.to_string())

# ==============================================================================
# 2. STAGE 1: METROLOGY SCREENING (IQR OUTLIERS VS. LSL/USL DEFECTS)
# ==============================================================================
# M10 benchmark acceptance limits
spec_limits = pd.DataFrame({
    "Feature": ["Thickness_Mean", "Resistivity_Mean", "TTV", "Warp", "Bow", "Saw_Mark_Depth"],
    "Unit": ["µm", "Ω·cm", "µm", "µm", "µm", "µm"],
    "LSL": [145.0, 0.50, 0.0, 0.0, -30.0, 0.0],
    "USL": [165.0, 2.00, 20.0, 40.0, 30.0, 12.0],
}).set_index("Feature")

features = spec_limits.index.tolist()
spc_records = []

for vendor in ["A", "B"]:
    v_df = df[df["Vendor_ID"] == vendor]
    for feat in features:
        series = v_df[feat].dropna()
        q1, median, q3 = series.quantile([0.25, 0.50, 0.75])
        iqr = q3 - q1
        lower_fence = q1 - 1.5 * iqr
        upper_fence = q3 + 1.5 * iqr

        lsl = spec_limits.loc[feat, "LSL"]
        usl = spec_limits.loc[feat, "USL"]

        outlier = (series < lower_fence) | (series > upper_fence)
        out_of_spec = (series < lsl) | (series > usl)
        outlier_pct = outlier.mean() * 100
        oos_pct = out_of_spec.mean() * 100

        spc_records.append({
            "Vendor": f"Vendor {vendor}",
            "Feature": feat,
            "Median": round(median, 3),
            "IQR": round(iqr, 3),
            "LSL": lsl,
            "USL": usl,
            "Outlier_Rate(%)": round(outlier_pct, 2),
            "Spec_Breach_Rate(%)": round(oos_pct, 2),
            "Readings": len(series),
            "Outlier_Only": (outlier & ~out_of_spec).sum(),
            "Out_of_Spec_Only": (~outlier & out_of_spec).sum(),
            "Both": (outlier & out_of_spec).sum(),
            "Neither": (~outlier & ~out_of_spec).sum(),
        })

spc_summary_df = pd.DataFrame(spc_records)
print("\n" + "=" * 70)
print("2. STAGE 1 SCREENING SUMMARY: STATISTICAL OUTLIERS VS. SPEC BREACHES")
print("=" * 70)
print(spc_summary_df.to_string(index=False))

# Figure 1: Side-by-Side Boxplots with LSL/USL Overlays (Vendor A vs. Vendor B)
fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(16, 10))
axes = axes.flatten()
palette = {"A": "#4C78A8", "B": "#F58518"}

for idx, feat in enumerate(features):
    ax = axes[idx]
    unit = spec_limits.loc[feat, "Unit"]
    lsl = spec_limits.loc[feat, "LSL"]
    usl = spec_limits.loc[feat, "USL"]

    sns.boxplot(
        data=df, x="Vendor_ID", y=feat, hue="Vendor_ID",
        palette=palette, ax=ax, width=0.45, fliersize=2, legend=False
    )

    # Plot Specification Limits (USL always shown; LSL shown where non-zero)
    ax.axhline(usl, color="#D62728", linestyle="--", linewidth=1.6, label=f"USL ({usl})")
    if lsl != 0.0:
        ax.axhline(lsl, color="#2CA02C", linestyle="--", linewidth=1.6, label=f"LSL ({lsl})")

    # Annotate Outlier % vs. OOS Defect % for both vendors
    row_a = spc_summary_df[(spc_summary_df["Vendor"] == "Vendor A") & (spc_summary_df["Feature"] == feat)].iloc[0]
    row_b = spc_summary_df[(spc_summary_df["Vendor"] == "Vendor B") & (spc_summary_df["Feature"] == feat)].iloc[0]

    info_text = (
        f"Vendor A | Outliers: {row_a['Outlier_Rate(%)']:.2f}% | OOS: {row_a['Spec_Breach_Rate(%)']:.2f}%\n"
        f"Vendor B | Outliers: {row_b['Outlier_Rate(%)']:.2f}% | OOS: {row_b['Spec_Breach_Rate(%)']:.2f}%"
    )
    ax.text(
        0.5, 0.96, info_text, transform=ax.transAxes, fontsize=8.5,
        ha="center", va="top", bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.88, edgecolor="#CCCCCC")
    )

    ax.set_title(f"{feat} ({unit})", fontsize=12, fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel(unit, fontsize=10)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Vendor A", "Vendor B"], fontsize=10)
    # Expand y-axis slightly at top to prevent annotation box overlap
    ymin, ymax = ax.get_ylim()
    ax.set_ylim(ymin, ymax + (ymax - ymin) * 0.18)
    ax.legend(loc="lower right", fontsize=8.5)

fig.suptitle("Stage 1 Metrology Dispersion: Statistical Outliers (IQR) vs. Engineering Spec Limits (LSL/USL)", fontsize=14, fontweight="bold", y=0.99)
plt.tight_layout()
plt.savefig("fig1_iqr_vs_spec_boxplots.png", bbox_inches="tight")
plt.close()

# ==============================================================================
# 3. STAGE 2A: LONGITUDINAL LOT-BY-LOT YIELD TRAJECTORY
# ==============================================================================
# Grade labels come from complete synthetic records before measurement loss.
# A missing exported reading does not change the stored benchmark result.
df["Lot_Num"] = df["Lot_ID"].str.extract(r"_(\d+)$").astype(int)
df["Is_Pass"] = (df["Sorting_Result"] == "PASS").astype(int)

lot_yield = (
    df.groupby(["Vendor_ID", "Lot_Num", "Lot_ID"], as_index=False)
    .agg(Total_Wafers=("Is_Pass", "count"), Pass_Count=("Is_Pass", "sum"))
)
lot_yield["Yield_Pct"] = (lot_yield["Pass_Count"] / lot_yield["Total_Wafers"]) * 100

print("\n" + "=" * 70)
print("3. LOT-BY-LOT YIELD SUMMARY (MIN / MAX / MEAN ACROSS 15 LOTS)")
print("=" * 70)
for v in ["A", "B"]:
    sub_y = lot_yield[lot_yield["Vendor_ID"] == v]
    min_row = sub_y.loc[sub_y["Yield_Pct"].idxmin()]
    max_row = sub_y.loc[sub_y["Yield_Pct"].idxmax()]
    print(
        f"Vendor {v} -> Mean Yield: {sub_y['Yield_Pct'].mean():.2f}% | "
        f"Min: {min_row['Yield_Pct']:.2f}% ({min_row['Lot_ID']}) | "
        f"Max: {max_row['Yield_Pct']:.2f}% ({max_row['Lot_ID']})"
    )

# Figure 2: Dual-Panel Longitudinal Lot Yield Trend
fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(16, 5.5), sharey=True)
vendor_titles = {
    "A": "Vendor A: Simulated Handling Defects (Lots 09–12), Reset at Lot 13",
    "B": "Vendor B: Simulated Geometry Drift (Lots 07–11), Reset at Lot 12"
}

for idx, v in enumerate(["A", "B"]):
    ax = axes[idx]
    sub_y = lot_yield[lot_yield["Vendor_ID"] == v].sort_values("Lot_Num")
    mean_y = sub_y["Yield_Pct"].mean()

    ax.plot(
        sub_y["Lot_Num"], sub_y["Yield_Pct"], marker="o", linewidth=2.4,
        color=palette[v], label=f"Lot Yield (%)"
    )
    ax.axhline(mean_y, color="#333333", linestyle="--", linewidth=1.4, label=f"Mean Yield ({mean_y:.2f}%)")

    for _, r in sub_y.iterrows():
        ax.annotate(
            f"{r['Yield_Pct']:.1f}%", (r["Lot_Num"], r["Yield_Pct"]),
            textcoords="offset points", xytext=(0, 8), ha="center", fontsize=8
        )

    ax.set_title(vendor_titles[v], fontsize=11.5, fontweight="bold")
    ax.set_xlabel("Sequential Production Lot (Lot 01 – Lot 15)", fontsize=10.5)
    ax.set_xticks(range(1, 16))
    ax.set_xticklabels([f"L{i:02d}" for i in range(1, 16)])
    ax.set_ylim(84, 99)
    if idx == 0:
        ax.set_ylabel("A-Grade Production Yield (%)", fontsize=10.5)
    ax.legend(loc="lower left", fontsize=9.5)

fig.suptitle("Stage 2A: Simulated Yield Across 15 Sequential Lots per Line (4,000 Wafers/Lot)", fontsize=14, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("fig2_longitudinal_lot_yield.png", bbox_inches="tight")
plt.close()

# ==============================================================================
# 4. STAGE 2B: DEFECT PARETO CONCENTRATION & LOT-LEVEL HEATMAP
# ==============================================================================
defects_only = df[df["Sorting_Result"] != "PASS"].copy()

print("\n" + "=" * 70)
print("4. PRIMARY REJECT CODE PARETO (EXCLUDING PASS)")
print("=" * 70)
pareto_tables = {}
for v in ["A", "B"]:
    v_def = defects_only[defects_only["Vendor_ID"] == v]["Sorting_Result"].value_counts().reset_index()
    v_def.columns = ["Defect_Type", "Count"]
    total_rejects = v_def["Count"].sum()
    v_def["Share(%)"] = 100 * v_def["Count"] / total_rejects
    v_def["Cumulative(%)"] = 100 * v_def["Count"].cumsum() / total_rejects
    pareto_tables[v] = v_def
    print(f"\n--- Vendor {v} Total Rejects: {v_def['Count'].sum():,} ---")
    print(v_def.to_string(index=False, float_format="{:.2f}".format))

# Figure 3: Side-by-Side Defect Pareto Charts
fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(16, 5.5))
for idx, v in enumerate(["A", "B"]):
    ax = axes[idx]
    p_df = pareto_tables[v]

    sns.barplot(data=p_df, x="Defect_Type", y="Share(%)", color=palette[v], ax=ax, edgecolor="black")
    ax2 = ax.twinx()
    ax2.plot(range(len(p_df)), p_df["Cumulative(%)"], color="#D62728", marker="D", linewidth=2, label="Cumulative %")
    ax2.axhline(80, color="#7F7F7F", linestyle=":", linewidth=1.2)
    ax2.set_ylim(0, 110)
    ax2.set_ylabel("Cumulative Defect Share (%)", color="#D62728", fontsize=10)
    ax2.grid(False)

    for bar in ax.patches:
        h = bar.get_height()
        ax.annotate(f"{h:.1f}%", (bar.get_x() + bar.get_width() / 2, h), ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    ax.set_title(f"Vendor {v} Defect Pareto (N = {p_df['Count'].sum():,} Rejects)", fontsize=12, fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Share of Rejected Wafers (%)", fontsize=10)
    ax.set_ylim(0, max(p_df["Share(%)"]) * 1.2)
    ax.tick_params(axis="x", rotation=30)

fig.suptitle("Stage 2B: Primary Reject Codes by Simulated Equipment Line", fontsize=14, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("fig3_defect_pareto_comparison.png", bbox_inches="tight")
plt.close()

# Figure 4: Lot-by-Lot Defect Count Heatmaps (Vendor A vs. Vendor B)
fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(17, 6))
for idx, v in enumerate(["A", "B"]):
    ax = axes[idx]
    sub_d = defects_only[defects_only["Vendor_ID"] == v]
    piv = pd.crosstab(sub_d["Sorting_Result"], sub_d["Lot_Num"])
    # Order rows by total frequency
    row_order = piv.sum(axis=1).sort_values(ascending=False).index
    piv = piv.loc[row_order]
    piv.columns = [f"L{c:02d}" for c in piv.columns]

    sns.heatmap(piv, annot=True, fmt="d", cmap="YlOrRd", cbar=True, ax=ax, linewidths=0.5)
    ax.set_title(f"Vendor {v}: Defect Frequency per Lot", fontsize=12, fontweight="bold")
    ax.set_xlabel("Production Lot ID", fontsize=10)
    ax.set_ylabel("Primary Reject Code" if idx == 0 else "", fontsize=10)

fig.suptitle("Stage 2B: Primary Reject Counts by Lot", fontsize=14, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("fig4_lot_defect_heatmaps.png", bbox_inches="tight")
plt.close()

print("\nAll 4 publication-grade figures saved successfully:")
print(" - fig1_iqr_vs_spec_boxplots.png")
print(" - fig2_longitudinal_lot_yield.png")
print(" - fig3_defect_pareto_comparison.png")
print(" - fig4_lot_defect_heatmaps.png")