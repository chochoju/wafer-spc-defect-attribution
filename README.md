# A Two-Stage Method for Diagnosing Yield Loss in U.S. Solar Wafer Manufacturing

**Metrology and Lot-Level Defect Analysis on a 120,000-Wafer Synthetic Benchmark**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Domain: Photovoltaic Manufacturing](https://img.shields.io/badge/Domain-PV%20Wafer%20SPC-orange.svg)](#governing-metrology-standards)

---

## Overview

This repository contains the reproducible synthetic metrology benchmark, Statistical Process Control (SPC) diagnostic pipeline, and publication figures accompanying the white paper *"A Two-Stage Method for Diagnosing Yield Loss in U.S. Solar Wafer Manufacturing: Metrology and Lot-Level Defect Analysis on a Synthetic Benchmark."*

In high-throughput monocrystalline silicon wafering, a 2% to 4% baseline yield gap between parallel equipment lines translates into millions of dollars in annual silicon scrap. Standard single-layer SPC dashboards frequently misdiagnose these losses by conflating benign statistical outliers with hard engineering specification breaches (`LCL`/`UCL`), or by masking discrete mechanical handling damage behind stable dimensional averages.

Evaluated across **120,000 unique M10 ($182\text{ mm} \times 182\text{ mm}$) monocrystalline silicon wafers** spanning 30 sequential production lots (15 lots per vendor), this two-stage diagnostic pipeline isolates two structurally distinct failure regimes:

* **Vendor A (96.09% Mean Yield):** Zero continuous dimensional breaches (`0.00%` OOS across all geometry channels), with **90.06%** of rejects driven by discrete mechanical handling damage (`Edge_Chip`, `Micro_Crack`, `Surface_Chip`).
* **Vendor B (92.68% Mean Yield):** High mechanical handling integrity, with **87.04%** of rejects driven by diamond-wire tension relaxation and thermal slicing drift (`TTV_OOS`, `Warp_OOS`, `Saw_Mark`, `Bow_OOS`).

---

## Repository Structure

```text
wafer-spc-defect-attribution/
├── data/
│   └── wafer_metrology_120k.csv          # 120,480 raw records (120,000 unique wafers + 480 MES duplicates)
├── figures/
│   ├── fig1_iqr_vs_spec_boxplots.png     # Stage 1: IQR statistical outliers vs. LCL/UCL limits
│   ├── fig2_longitudinal_lot_yield.png   # Stage 2A: Sequential 15-lot yield trajectories
│   ├── fig3_defect_pareto_comparison.png # Stage 2B: Defect Pareto concentration by vendor
│   └── fig4_lot_defect_heatmaps.png      # Stage 2B: Lot-level defect clustering heatmaps
├── src/
│   ├── generate_wafer_metrology.py       # Reproducible synthetic data generator (seed=42)
│   └── analyze_wafer_spc.py              # MES cleaning, SPC calculations, and chart generation
├── requirements.txt
└── README.md
```

---

## Diagnostic Architecture

```text
Raw MES Inspection Logs (120,480 rows)
        │
        ▼
[MES Telemetry Hygiene Gate]
  ├── Deduplicate conveyor re-scan / retry logs (-480 exact duplicates -> 120,000 unique wafers)
  └── Preserve pairwise sensor evaluation across intermittent optical dropouts (4.73% row-wise nulls)
        │
        ├──► [Stage 1: Parametric Dispersion & Spec Audit]
        │      • Decouples nonparametric 1.5 × IQR fences from engineering LCL/UCL limits
        │      • Separates benign statistical outliers (Outliers > Defects) from true OOS drift (Defects > Outliers)
        │
        └──► [Stage 2: Longitudinal & Categorical Forensics]
               • Tracks sequential lot-by-lot yield trajectories across 15 lots/vendor (4,000 wafers/lot)
               • Isolates equipment wear windows and maintenance resets via Pareto & lot-level heatmaps
```

---

## Dataset Schema & Acceptance Standards (`wafer_metrology_120k.csv`)

The benchmark models 33 telemetry columns across 15 sequential lots per vendor (`LOT_A_01`–`LOT_A_15` and `LOT_B_01`–`LOT_B_15`), evaluated against **SEMI PV22 / MF1530 / PV17** tolerances. Multi-defect wafers are classified into `Sorting_Result` via a deterministic severity hierarchy:

`Micro_Crack > Edge_Chip > Surface_Chip > TTV_OOS > Warp_OOS > Bow_OOS > Saw_Mark > Stain > Pinhole > PASS`

| Feature Group | Key Columns | A-Grade Spec (LCL–UCL) | Off-Grade Failure Label |
| :--- | :--- | :--- | :--- |
| **Identifiers & Logs** | `Time_Log`, `Vendor_ID`, `Lot_ID`, `Sorting_Result` | — | `PASS` or Primary Defect |
| **Outer Geometry** | `Side_Length_*`, `Diagonal_*`, `Chamfer_*`, `Corner_Angle_*` | $182.0 \pm 0.25\text{ mm}$ / $247.0 \pm 0.50\text{ mm}$ / $90.0^\circ \pm 0.3^\circ$ | Kept strictly within spec |
| **Center Thickness** | `Thickness_Mean`, `Thickness_Min`, `Thickness_Max` | $145.0\text{ – }165.0\ \mu\text{m}$ | `Outliers > Defects` ($0.00\%$ OOS) |
| **Bulk Resistivity** | `Resistivity_Mean`, `Resistivity_Min`, `Resistivity_Max` | $0.50\text{ – }2.00\ \Omega\cdot\text{cm}$ | `Outliers > Defects` ($0.00\%$ OOS) |
| **Flatness & Slicing** | `TTV`, `Warp`, `Bow`, `Saw_Mark_Depth` | $\text{TTV} \le 20\ \mu\text{m}$; $\text{Warp} \le 40\ \mu\text{m}$; $\|\text{Bow}\| \le 30\ \mu\text{m}$; $\text{Saw Mark} \le 12\ \mu\text{m}$ | `TTV_OOS`, `Warp_OOS`, `Bow_OOS`, `Saw_Mark` |
| **Discrete AOI Counts** | `Micro_Crack_Count`, `Edge_Chip_Count`, `Surface_Chip_Count`, `Stain_Count`, `Pinhole_Count` | `Edge_Chip` $\le 2$; all other defect counts $= 0$ | `Micro_Crack`, `Edge_Chip`, `Surface_Chip`, `Stain`, `Pinhole` |

---

## Summary of Empirical Results & Visual Findings

| Diagnostic Metric | Vendor A | Vendor B | Engineering Interpretation |
| :--- | :---: | :---: | :--- |
| **Clean Unique Wafers** | 60,000 | 60,000 | 15 lots × 4,000 wafers/lot |
| **Mean A-Grade Yield** | **96.09%** | **92.68%** | 3.41 percentage-point baseline yield gap |
| **Min / Max Lot Yield** | 93.67% (`LOT_A_12`) / 96.90% (`LOT_A_07`) | 89.95% (`LOT_B_11`) / 93.85% (`LOT_B_14`) | Progressive equipment wear & maintenance reset |
| **Total Rejected Wafers** | 2,343 | 4,390 | Vendor B generates 1.87× more scrap volume |
| **Primary Failure Regime** | Mechanical Handling (**90.06%**) | Slicing & Thermal Geometry (**87.04%**) | Distinct physical mechanisms requiring targeted PM |

### Key Diagnostic Visuals (`figures/`)

* **`fig1_iqr_vs_spec_boxplots.png`:** Demonstrates why `Thickness_Mean` (~3.9% outliers, 0.00% OOS) and `Resistivity_Mean` (~3.5% outliers, 0.00% OOS) should not trigger line stops, whereas Vendor B's `TTV` (2.11% OOS vs. 0.70% outliers) and `Warp` (1.58% OOS vs. 0.72% outliers) breach `UCL` while remaining inside boxplot whiskers.
* **`fig2_longitudinal_lot_yield.png`:** Captures progressive mechanical gripper degradation on Vendor A (`LOT_A_09`–`LOT_A_12`) and diamond-wire tension drift on Vendor B (`LOT_B_07`–`LOT_B_11`), followed by immediate post-maintenance yield recovery.
* **`fig3_defect_pareto_comparison.png` & `fig4_lot_defect_heatmaps.png`:** Pinpoints the exact defect concentration (`Edge_Chip` 45.41%, `Micro_Crack` 27.66%, `Surface_Chip` 16.99% on Vendor A vs. `TTV_OOS` 28.88%, `Warp_OOS` 20.98%, `Saw_Mark` 19.32%, `Bow_OOS` 17.86% on Vendor B) and lot-level escalation windows.

---

## Actionable Engineering Troubleshooting Matrix

| Equipment Line | Dominant Failure Signature | Root-Cause Physical Mechanism | Recommended Preventive Maintenance (PM) Action |
| :--- | :--- | :--- | :--- |
| **Vendor A** | `Edge_Chip` (45.4%), `Micro_Crack` (27.7%), `Surface_Chip` (17.0%) | Cassette slot misalignment, vacuum chuck shock, and gripper elastomer wear | Implement 8-lot ($\approx 32,000$-wafer) preventive gripper-pad replacement cycle; recalibrate transfer robot Z-axis deceleration profiles. |
| **Vendor B** | `TTV_OOS` (28.9%), `Warp_OOS` (21.0%), `Saw_Mark` (19.3%), `Bow_OOS` (17.9%) | Diamond-wire tension loss, guide-wheel wear, and cutting-fluid thermal gradient | Tighten closed-loop wire-tension feedback thresholds; schedule guide-wheel dressing every 6 lots ($\approx 24,000$ wafers); stabilize coolant chiller PID loop. |

---

## Quickstart & Reproducibility

### 1. Clone the Repository & Install Dependencies

```bash
git clone https://github.com/jenny6449/wafer-spc-defect-attribution.git
cd wafer-spc-defect-attribution
pip install -r requirements.txt
```

### 2. Regenerate the Synthetic Metrology Dataset *(Optional)*

```bash
python src/generate_wafer_metrology.py
```

### 3. Run the Two-Stage SPC & Defect Attribution Pipeline

```bash
python src/analyze_wafer_spc.py
```

---

## Governing Metrology Standards

* **SEMI PV22 / PV42:** Dimensional and geometric tolerances for M10 pseudo-square monocrystalline silicon wafers.
* **SEMI MF1530 / PV68:** Automated non-contact metrology specifications for center thickness, Total Thickness Variation (`TTV`), `Bow`, and `Warp`.
* **SEMI MF84 / PV66:** Four-point probe and eddy-current bulk electrical resistivity tolerances.
* **SEMI PV17:** Inline Automated Optical Inspection (AOI) classification for mechanical chips, wire-saw step marks, stains, pinholes, and micro-cracks.

---

## Author & Citation

**Author:** Juyeon Cho (Jenny), M.S. in Business Analytics (Duke University) — *Manufacturing Data & Analytics Engineer*

If you reference this benchmark dataset or two-stage SPC pipeline in academic or industrial work, please cite:

```bibtex
@misc{wafer_spc_benchmark_2026,
  author       = {Cho, Juyeon},
  title        = {A Two-Stage Method for Diagnosing Yield Loss in U.S. Solar Wafer Manufacturing: Metrology and Lot-Level Defect Analysis on a Synthetic Benchmark},
  year         = {2026},
  publisher    = {GitHub / Zenodo},
  url          = {https://github.com/chochoju/wafer-spc-defect-attribution}
}
```