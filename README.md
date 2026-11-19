# A Two-Stage Method for Diagnosing Yield Loss in U.S. Solar Wafer Manufacturing

**Metrology and Lot-Level Defect Analysis on a 120,000-Wafer Synthetic Benchmark**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

## Overview
This repository contains the reproducible synthetic dataset, Statistical Process Control (SPC) diagnostic pipeline, and publication figures accompanying the white paper *"A Two-Stage Method for Diagnosing Yield Loss in U.S. Solar Wafer Manufacturing: Metrology and Lot-Level Defect Analysis on a Synthetic Benchmark."*

The framework evaluates **120,000 M10 (182 mm × 182 mm) monocrystalline silicon wafers** across 30 sequential production lots (15 lots per vendor) to decouple benign statistical outliers from physical engineering specification breaches (`LCL`/`UCL`) and isolate equipment-specific root causes:
* **Vendor A (96.09% Mean Yield):** Zero continuous dimensional breaches (`0.00%` OOS), with **90.06%** of rejects driven by discrete mechanical handling damage (`Edge_Chip`, `Micro_Crack`, `Surface_Chip`).
* **Vendor B (92.68% Mean Yield):** High mechanical handling integrity, with **87.04%** of rejects driven by diamond-wire tension and thermal slicing drift (`TTV_OOS`, `Warp_OOS`, `Saw_Mark`, `Bow_OOS`).

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