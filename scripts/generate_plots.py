import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# -----------------------------
# Load data
# -----------------------------
df = pd.read_csv("master_summary.csv")

# Clean method names
df["Method"] = df["Method"].str.strip()

# Rename Simple Average to Mean
df["Method"] = df["Method"].replace({
    "Simple Average": "Mean"
})

# Preserve method order from master_summary.csv
method_order = df["Method"].drop_duplicates().tolist()

# Create output folder
output_dir = "generated_graphs"
os.makedirs(output_dir, exist_ok=True)

# Style
sns.set_theme(style="whitegrid", font_scale=1.1)
plt.rcParams["figure.dpi"] = 300

# ============================================================
# FIGURE 1: Boxplot of BetP(e) by Method
# ============================================================

plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x="Method", y="BetP", order=method_order)
plt.xticks(rotation=30, ha="right")
plt.title("Distribution of BetP(e) Across Methods")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "fig1_boxplot_betp.png"), bbox_inches="tight")
plt.close()


# ============================================================
# FIGURE 2: Average Uncertainty Mass m(50-50)
# ============================================================

unc = (
    df.groupby("Method", sort=False)["fused m(50-50)"]
    .mean()
    .reindex(method_order)
    .reset_index()
)

plt.figure(figsize=(10, 6))
sns.barplot(data=unc, x="Method", y="fused m(50-50)", order=method_order)
plt.xticks(rotation=30, ha="right")
plt.title("Average Uncertainty Mass by Method")
plt.ylabel("Mean fused m(50-50)")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "fig2_uncertainty_bar.png"), bbox_inches="tight")
plt.close()


# ============================================================
# FIGURE 3: Heatmap of Mean Metrics by Method
# ============================================================

metrics = (
    df.groupby("Method", sort=False)[["Bel (e)", "Pl (e)", "BetP"]]
    .mean()
    .reindex(method_order)
)

plt.figure(figsize=(8, 6))
sns.heatmap(metrics, annot=True, fmt=".3f", cmap="viridis")
plt.title("Average Belief Measures by Method")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "fig3_metric_heatmap.png"), bbox_inches="tight")
plt.close()


# ============================================================
# FIGURE 4: Correlation Matrix Between Methods using BetP
# ============================================================

pivot = df.pivot(index="Edge", columns="Method", values="BetP")
pivot = pivot.reindex(columns=method_order)
corr = pivot.corr()

plt.figure(figsize=(8, 6))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1)
plt.title("Correlation of Methods (BetP across Edges)")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "fig4_method_correlation.png"), bbox_inches="tight")
plt.close()


# ============================================================
# FIGURE 5: Heatmap of BetP(e) Across Edges × Methods
# Top 30 most variable edges only for readability
# ============================================================

pivot2 = df.pivot(index="Edge", columns="Method", values="BetP")
pivot2 = pivot2.reindex(columns=method_order)

var_edges = pivot2.var(axis=1).sort_values(ascending=False).head(30).index
heat = pivot2.loc[var_edges]

plt.figure(figsize=(10, 10))
sns.heatmap(heat, cmap="YlGnBu")
plt.title("BetP(e) Heatmap Across Methods (Top Variable Edges)")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "fig5_edge_heatmap.png"), bbox_inches="tight")
plt.close()


# ============================================================
# FIGURE 6: Top Supported Edges
# ============================================================

avg_edges = (
    df.groupby("Edge")["BetP"]
    .mean()
    .sort_values(ascending=False)
    .head(15)
)

plt.figure(figsize=(10, 7))
sns.barplot(x=avg_edges.values, y=avg_edges.index)
plt.title("Top 15 Supported Edges (Mean BetP)")
plt.xlabel("Mean BetP")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "fig6_top_edges.png"), bbox_inches="tight")
plt.close()


print(f"All figures saved successfully in: {output_dir}")