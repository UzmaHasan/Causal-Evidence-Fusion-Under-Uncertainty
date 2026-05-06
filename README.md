# A Benchmark for Fusing Expert-Elicited Causal Beliefs under Uncertainty

This repository accompanies the paper:

**Beyond Binary Edges: A Benchmark for Fusing Expert-Elicited Causal Beliefs under Uncertainty**

This repository provides the data, code, fusion outputs, benchmark metrics, and figures used to evaluate uncertainty aware fusion methods for causal edge beliefs. The benchmark focuses on expert elicited beliefs over candidate directed causal edges, where each expert assigns belief masses to three hypotheses: edge existence, edge non-existence, and explicit uncertainty.

## Repository Structure

```text
A-Benchmark-for-Fusing-Expert-Elicited-Causal-Beliefs-under-Uncertainty/
│
├── README.md
├── croissant_metadata.json
│
├── data/
│   ├── raw_expert_spreadsheets/
│   ├── edge_level_expert_beliefs/
│   └── all_experts_rows_combined.csv
│
├── scripts/
│   ├── end_to_end_edge_fusion.py
│   └── generate_plots.py
│
├── results/
│   ├── master_summary.csv
│   ├── aggregate_benchmark_metrics.csv
│   └── edge_fusion_outputs/
│
├── figures/
│
└── docs/
    └── variable_descriptions.txt
```

## Data Description

The benchmark is constructed from structured expert probability assignments over candidate directed causal edges.

For each candidate edge, each expert provides three belief masses:

- `m(e)`: belief that the causal edge exists
- `m(not e)`: belief that the causal edge does not exist
- `m(Theta)`: explicit uncertainty 

These three masses sum to 1 for each expert-edge pair.

## Data Folder

### `data/raw_expert_spreadsheets/`

This folder contains the original expert-provided spreadsheet files. Each spreadsheet corresponds to one expert and contains belief assignments for the same set of candidate directed edges.

### `data/edge_level_expert_beliefs/`

This folder contains edge-level expert belief tables. Each file corresponds to a candidate edge and includes the belief assignments provided by all experts for that edge.

### `data/all_experts_rows_combined.csv`

This file contains the combined machine-readable dataset, where each row corresponds to an expert-edge belief assignment.

## Scripts

### `scripts/end_to_end_edge_fusion.py`

This script performs the complete edge-level belief fusion pipeline. It reads expert belief assignments, applies multiple uncertainty fusion methods, and saves edge-level fused outputs and summary results.

### `scripts/generate_plots.py`

This script generates publication-style plots from the benchmark summary outputs.

## Results

### `results/master_summary.csv`

This file contains the main edge-level fusion summary across methods. It includes fused belief masses and derived uncertainty-aware quantities such as belief, plausibility, and pignistic probability.

### `results/aggregate_benchmark_metrics.csv`

This file contains aggregate benchmark metrics comparing fusion methods across all evaluated edges.

### `results/edge_fusion_outputs/`

This folder contains detailed fusion outputs for each candidate edge.

## Figures

The `figures/` folder contains PNG figures generated from the benchmark outputs and used for analysis, visualization, and paper reporting.

## Documentation

### `docs/variable_descriptions.txt`

This file describes the variables used in the causal edge benchmark.

## Fusion Methods

The benchmark supports comparison of multiple evidence fusion methods, including Dempster-Shafer rule, Yager's rule, Murphy's rule, PCR5 and Dubois-Prade rule. The outputs are reported using edge level fused masses and derived quantities such as:

- `Bel(e)`: belief in edge existence
- `Pl(e)`: plausibility of edge existence
- `BetP(e)`: pignistic probability of edge existence

## Installation

Clone the repository:

```bash
git clone https://github.com/noname31157/A-Benchmark-for-Fusing-Expert-Elicited-Causal-Beliefs-under-Uncertainty.git
cd A-Benchmark-for-Fusing-Expert-Elicited-Causal-Beliefs-under-Uncertainty
```

Create and activate a virtual environment:

```bash
python -m venv venv
```

On Windows:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

## Requirements

The code requires Python 3.9 or later.

The main Python dependencies are:

```text
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
openpyxl>=3.1.0
scikit-learn>=1.3.0
```

These dependencies support reading CSV and Excel files, processing expert belief assignments, computing fusion outputs, calculating benchmark metrics, and generating figures.

## Usage

Run the fusion pipeline:

```bash
python scripts/end_to_end_edge_fusion.py
```

Generate plots:

```bash
python scripts/generate_plots.py
```

Depending on the local directory setup, the scripts may require updating input and output paths.

## License

This repository is released under the CC BY-NC 4.0 License.

## Notes

This repository is intended to support reproducible evaluation of uncertainty aware causal belief fusion methods. The provided data, scripts, results, and figures are organized to facilitate transparent benchmark construction, method comparison, and future extensions.

For anonymized review, author information has been omitted or replaced with anonymous placeholders where appropriate.
