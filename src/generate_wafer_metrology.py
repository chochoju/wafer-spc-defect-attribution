import numpy as np
import pandas as pd

# Set seed for full reproducibility
np.random.seed(42)


def generate_vendor_data(vendor_id: str, n_lots: int = 15, wafers_per_lot: int = 4000) -> pd.DataFrame:
    total_wafers = n_lots * wafers_per_lot
    
    # 1. Time log & Lot IDs (sequential production timestamps)
    start_time = pd.Timestamp("2026-01-05 06:00:00") if vendor_id == "A" else pd.Timestamp("2026-01-05 06:00:15")
    # ~1.5 seconds per wafer inspection throughput
    time_offsets = pd.to_timedelta(np.arange(total_wafers) * 1.5, unit="s")
    time_logs = start_time + time_offsets
    lot_ids = np.repeat([f"LOT_{vendor_id}_{i:02d}" for i in range(1, n_lots + 1)], wafers_per_lot)

    # Revised gentler wear curve for Vendor A (Lots 9-12 peak at 1.85x instead of 2.7x -> ~96.0% overall yield)
    lot_wear_a = np.ones(n_lots)
    lot_wear_a[8:12] = [1.25, 1.45, 1.65, 1.85]
    wear_a = np.repeat(lot_wear_a, wafers_per_lot)

    # 2. Geometric Outer Dimensions (Kept strictly within M10 A-Grade Spec)
    # Spec: Side Length 182.0 +/- 0.25 mm | Diagonal 247.0 +/- 0.50 mm | Corner Angle 90.0 +/- 0.3 deg
    data = {
        "Time_Log": time_logs,
        "Vendor_ID": vendor_id,
        "Lot_ID": lot_ids,
        "Side_Length_Top": np.clip(np.random.normal(182.00, 0.05, total_wafers), 181.80, 182.20),
        "Side_Length_Bottom": np.clip(np.random.normal(182.00, 0.05, total_wafers), 181.80, 182.20),
        "Side_Length_Left": np.clip(np.random.normal(182.00, 0.05, total_wafers), 181.80, 182.20),
        "Side_Length_Right": np.clip(np.random.normal(182.00, 0.05, total_wafers), 181.80, 182.20),
        "Diagonal_1": np.clip(np.random.normal(247.00, 0.10, total_wafers), 246.60, 247.40),
        "Diagonal_2": np.clip(np.random.normal(247.00, 0.10, total_wafers), 246.60, 247.40),
        "Chamfer_Length_TL": np.clip(np.random.normal(14.50, 0.15, total_wafers), 14.00, 15.00),
        "Chamfer_Length_TR": np.clip(np.random.normal(14.50, 0.15, total_wafers), 14.00, 15.00),
        "Chamfer_Length_BL": np.clip(np.random.normal(14.50, 0.15, total_wafers), 14.00, 15.00),
        "Chamfer_Length_BR": np.clip(np.random.normal(14.50, 0.15, total_wafers), 14.00, 15.00),
        "Corner_Angle_TL": np.clip(np.random.normal(90.00, 0.06, total_wafers), 89.75, 90.25),
        "Corner_Angle_TR": np.clip(np.random.normal(90.00, 0.06, total_wafers), 89.75, 90.25),
        "Corner_Angle_BL": np.clip(np.random.normal(90.00, 0.06, total_wafers), 89.75, 90.25),
        "Corner_Angle_BR": np.clip(np.random.normal(90.00, 0.06, total_wafers), 89.75, 90.25),
    }
    df = pd.DataFrame(data)

    # 3. Thickness, Resistivity, & Flatness Metrology
    # Scenario A for Boxplot: Outliers > Defects (Tight IQR with statistical outliers still inside the specification limits)
    # Thickness Spec: 145 - 165 um | Resistivity Spec: 0.5 - 2.0 ohm-cm
    thick_mean = np.random.normal(155.0, 1.2, total_wafers)
    outlier_idx = np.random.choice(total_wafers, size=int(total_wafers * 0.035), replace=False)
    thick_mean[outlier_idx] += np.random.choice([-6.5, 6.5], size=len(outlier_idx))
    df["Thickness_Mean"] = np.clip(thick_mean, 146.0, 164.0)

    res_mean = np.random.normal(1.25, 0.08, total_wafers)
    res_out_idx = np.random.choice(total_wafers, size=int(total_wafers * 0.03), replace=False)
    res_mean[res_out_idx] += np.random.choice([-0.45, 0.45], size=len(res_out_idx))
    df["Resistivity_Mean"] = np.clip(res_mean, 0.55, 1.95)
    df["Resistivity_Min"] = df["Resistivity_Mean"] - np.random.uniform(0.05, 0.12, total_wafers)
    df["Resistivity_Max"] = df["Resistivity_Mean"] + np.random.uniform(0.05, 0.12, total_wafers)

    # Scenario B: More specification breaches than outliers on Vendor B
    # Specs: TTV <= 20 um | Warp <= 40 um | |Bow| <= 30 um | Saw_Mark_Depth <= 12 um
    if vendor_id == "A":
        # Vendor A: Tight slicing/geometry (almost zero geometry OOS)
        df["TTV"] = np.clip(np.random.normal(10.5, 2.2, total_wafers), 3.0, 19.2)
        df["Warp"] = np.clip(np.random.normal(18.0, 4.5, total_wafers), 4.0, 38.5)
        df["Bow"] = np.clip(np.random.normal(0.0, 7.5, total_wafers), -28.0, 28.0)
        df["Saw_Mark_Depth"] = np.clip(np.random.normal(5.5, 1.4, total_wafers), 1.5, 11.5)
    else:
        # Calibrated lot wear curve for Vendor B (Lots 7-11 ramp up to 1.8x, reset in Lot 12)
        lot_wear_b = np.ones(n_lots)
        lot_wear_b[6:11] = [1.15, 1.30, 1.45, 1.65, 1.80]
        wear_b = np.repeat(lot_wear_b, wafers_per_lot)

        # Calibrated means & stds so TTV, Warp, Bow, and Saw_Mark combine to ~7.2% OOS (~92.6% total yield)
        df["TTV"] = np.clip(np.random.normal(14.0, 2.9, total_wafers) * (0.96 + 0.04 * wear_b), 4.0, 27.0)
        df["Warp"] = np.clip(np.random.normal(26.5, 6.2, total_wafers) * (0.96 + 0.04 * wear_b), 5.0, 52.0)
        bow_raw = np.random.normal(0.0, 12.2, total_wafers) * (0.96 + 0.04 * wear_b)
        df["Bow"] = np.clip(bow_raw, -42.0, 42.0)
        df["Saw_Mark_Depth"] = np.clip(np.random.normal(7.8, 1.9, total_wafers) * (0.96 + 0.04 * wear_b), 2.0, 16.5)

    # Derive Thickness_Min and Thickness_Max consistently from Thickness_Mean and TTV
    df["Thickness_Min"] = df["Thickness_Mean"] - (df["TTV"] / 2.0)
    df["Thickness_Max"] = df["Thickness_Mean"] + (df["TTV"] / 2.0)

    # 4. Discrete Defect Counts (Vendor A heavy on Chips & Micro-Cracks; Vendor B minimal)
    if vendor_id == "A":
        p_crack = 0.0085 * wear_a
        p_edge_fail = 0.0155 * wear_a
        p_surf_chip = 0.0055 * wear_a
        p_stain = 0.0025
        p_pinhole = 0.0015
    else:
        p_crack = 0.0020
        p_edge_fail = 0.0030
        p_surf_chip = 0.0015
        p_stain = 0.0020
        p_pinhole = 0.0010

    df["Micro_Crack_Count"] = (np.random.rand(total_wafers) < p_crack).astype(int)
    
    # Edge_Chip spec allows up to 2 minor chips; >2 triggers Edge_Chip defect
    edge_base = np.random.choice([0, 1, 2], size=total_wafers, p=[0.88, 0.09, 0.03])
    edge_fail_mask = np.random.rand(total_wafers) < p_edge_fail
    edge_base[edge_fail_mask] = np.random.choice([3, 4, 5], size=edge_fail_mask.sum(), p=[0.6, 0.3, 0.1])
    df["Edge_Chip_Count"] = edge_base

    df["Surface_Chip_Count"] = (np.random.rand(total_wafers) < p_surf_chip).astype(int)
    df["Stain_Count"] = (np.random.rand(total_wafers) < p_stain).astype(int)
    df["Pinhole_Count"] = (np.random.rand(total_wafers) < p_pinhole).astype(int)

    # 5. Assign the A-grade result from complete synthetic inspection data.
    # Keep this result when simulating missing readings in the inspection export.
    # Priority: Micro_Crack > Edge_Chip > Surface_Chip > TTV_OOS > Warp_OOS > Bow_OOS > Saw_Mark > Stain > Pinhole > PASS
    conditions = [
        df["Micro_Crack_Count"] >= 1,
        df["Edge_Chip_Count"] > 2,
        df["Surface_Chip_Count"] >= 1,
        df["TTV"] > 20.0,
        df["Warp"] > 40.0,
        df["Bow"].abs() > 30.0,
        df["Saw_Mark_Depth"] > 12.0,
        df["Stain_Count"] >= 1,
        df["Pinhole_Count"] >= 1,
    ]
    choices = [
        "Micro_Crack",
        "Edge_Chip",
        "Surface_Chip",
        "TTV_OOS",
        "Warp_OOS",
        "Bow_OOS",
        "Saw_Mark",
        "Stain",
        "Pinhole",
    ]
    # These characteristics are generated within bounds in the baseline scenario.
    # Check them explicitly so a future scenario cannot pass an out-of-spec wafer.
    side_cols = [f"Side_Length_{side}" for side in ("Top", "Bottom", "Left", "Right")]
    corner_cols = [f"Corner_Angle_{corner}" for corner in ("TL", "TR", "BL", "BR")]
    conditions.extend([
        ~df["Thickness_Mean"].between(145.0, 165.0),
        ~df["Resistivity_Mean"].between(0.50, 2.00),
        ((df[side_cols] < 181.75) | (df[side_cols] > 182.25)).any(axis=1),
        ((df[["Diagonal_1", "Diagonal_2"]] < 246.50)
         | (df[["Diagonal_1", "Diagonal_2"]] > 247.50)).any(axis=1),
        ((df[corner_cols] < 89.70) | (df[corner_cols] > 90.30)).any(axis=1),
    ])
    choices.extend([
        "Thickness_OOS", "Resistivity_OOS", "Side_Length_OOS",
        "Diagonal_OOS", "Corner_Angle_OOS",
    ])
    df["Sorting_Result"] = np.select(conditions, choices, default="PASS")

    # Round float columns to realistic metrology precision
    float_cols = [
        "Side_Length_Top", "Side_Length_Bottom", "Side_Length_Left", "Side_Length_Right",
        "Diagonal_1", "Diagonal_2", "Chamfer_Length_TL", "Chamfer_Length_TR",
        "Chamfer_Length_BL", "Chamfer_Length_BR", "Corner_Angle_TL", "Corner_Angle_TR",
        "Corner_Angle_BL", "Corner_Angle_BR", "Thickness_Min", "Thickness_Max",
        "Thickness_Mean", "TTV", "Resistivity_Min", "Resistivity_Max", "Resistivity_Mean",
        "Bow", "Warp", "Saw_Mark_Depth"
    ]
    df[float_cols] = df[float_cols].round(3)

    return df


# Generate both vendors (60k each = 120k rows)
df_a = generate_vendor_data("A", n_lots=15, wafers_per_lot=4000)
df_b = generate_vendor_data("B", n_lots=15, wafers_per_lot=4000)
combined_df = pd.concat([df_a, df_b], ignore_index=True)

# 6. Simulate missing inspection readings after grading (~0.6% per channel).
# The random loss represents possible sensor or data-transfer failures. IDs and
# Sorting_Result survive in this scenario, even when an exported reading is blank.
metrology_cols = [
    "Thickness_Mean", "TTV", "Resistivity_Mean", "Bow", "Warp", "Saw_Mark_Depth",
    "Side_Length_Top", "Diagonal_1"
]
for col in metrology_cols:
    null_indices = np.random.choice(combined_df.index, size=int(len(combined_df) * 0.006), replace=False)
    combined_df.loc[null_indices, col] = np.nan

# 7. Inject Exact Duplicate Rows (~0.4% from conveyor re-scans / MES retry logs)
dup_indices = np.random.choice(combined_df.index, size=int(len(combined_df) * 0.004), replace=False)
duplicates = combined_df.loc[dup_indices].copy()
combined_df = pd.concat([combined_df, duplicates], ignore_index=True)

# Sort by Vendor_ID and Time_Log
combined_df = combined_df.sort_values(by=["Vendor_ID", "Time_Log"]).reset_index(drop=True)

# Save to single combined CSV matching analyze_wafer_spc.py
output_filename = "wafer_metrology_120k.csv"
combined_df.to_csv(output_filename, index=False)

# Verification Summary
print(f"Saved {len(combined_df):,} total rows to '{output_filename}'")
for v in ["A", "B"]:
    sub = combined_df[combined_df["Vendor_ID"] == v].drop_duplicates()
    yield_pct = (sub["Sorting_Result"] == "PASS").mean() * 100
    print(f"\n--- Vendor {v} (Clean Unique Rows: {len(sub):,}) | Overall Yield: {yield_pct:.2f}% ---")
    print(sub["Sorting_Result"].value_counts())