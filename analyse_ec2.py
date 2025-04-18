#!/usr/bin/env python3
"""analyse_ec2.py
Analyse un fichier CSV simulant des instances EC2 : statistiques financières et carbone + visualisations.

Usage :
  python analyse_ec2.py [-i ec2.csv] [-d plots] [--no-display]

Options :
  -i, --input FILE     Chemin du CSV d'entrée. [def. : data/simulated_ec2.csv]
  -d, --outdir DIR     Dossier où sauver les graphiques. [def. : plots]
  --no-display         Génère les graphes sans les afficher (backend Agg).
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

# ────────────────────────────
# ░░ 1. Arguments CLI ░░
# ────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyse un CSV d'instances EC2 et produit des graphes/statistiques.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-i",
        "--input",
        default="data/simulated_ec2.csv",
        help="Chemin du CSV d'entrée.",
    )
    parser.add_argument(
        "-d",
        "--outdir",
        default="plots",
        help="Dossier de sortie pour les graphiques.",
    )
    parser.add_argument(
        "--no-display",
        action="store_true",
        help="N'affiche pas les graphiques (backend Agg).",
    )
    return parser.parse_args()


ARGS = parse_args()

# Placer le backend *avant* d'importer pyplot si headless
import matplotlib  # noqa: E402  # isort: skip

if ARGS.no_display:
    matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402  # isort: skip
import numpy as np  # noqa: E402  # isort: skip
import pandas as pd  # noqa: E402  # isort: skip

print(f"Matplotlib backend : {matplotlib.get_backend()}")

# ────────────────────────────
# ░░ 2. Chargement des données ░░
# ────────────────────────────

input_path = Path(ARGS.input)
if not input_path.exists():
    raise FileNotFoundError(f"Le fichier d'entrée '{input_path}' est introuvable.")

df = pd.read_csv(input_path)

# ────────────────────────────
# ░░ 3. Analyse descriptive ░░
# ────────────────────────────

print("\n🔍 Aperçu des données :")
print(df.head())

if "co2_cost" not in df.columns:
    print("\n⚠️  La colonne 'co2_cost' n'existe pas dans le CSV. Assure‑toi d'avoir mis à jour ton script de simulation.")
else:
    print("\n🔎 Aperçu de la colonne 'co2_cost' :")
    print(df["co2_cost"].describe())

model_counts = df["pricing_model"].value_counts()
print("\n📊 Instances par pricing model :")
print(model_counts)

avg_cost_by_model = df.groupby("pricing_model")["total_cost"].mean()
print("\n💰 Coût moyen ($) par pricing model :")
print(avg_cost_by_model)

avg_co2_by_model = df.groupby("pricing_model")["co2_kg"].mean()
print("\n🌱 Émissions CO₂ moyennes (kg) par pricing model :")
print(avg_co2_by_model)

if "co2_cost" in df.columns:
    avg_co2cost_by_model = df.groupby("pricing_model")["co2_cost"].mean()
    print("\n💲 Coût carbone moyen ($) par pricing model :")
    print(avg_co2cost_by_model)

# ────────────────────────────
# ░░ 4. Préparation dossier de sortie ░░
# ────────────────────────────

outdir = Path(ARGS.outdir)
outdir.mkdir(parents=True, exist_ok=True)
print(f"\n📂 Graphiques sauvegardés dans : {outdir.resolve()}")

# Palette et mappings
regions = df["region"].unique()
colors = ["red", "blue", "green", "orange"]
region_color_map = dict(zip(regions, colors))

pricing_shapes = {
    "on_demand": "o",  # cercle
    "reserved": "s",  # carré
    "spot": "X",  # croix
}

# Helper pour show/save/close

def finalize(fig_name: str):
    plt.tight_layout()
    plt.savefig(outdir / fig_name, dpi=300)
    if not ARGS.no_display:
        plt.show()
    plt.close()

# ────────────────────────────
# ░░ 5. Visualisation 1 : Coût vs CO₂ ░░
# ────────────────────────────

plt.figure(figsize=(12, 7))
for _, row in df.iterrows():
    plt.scatter(
        row["total_cost"],
        row["co2_kg"],
        color=region_color_map[row["region"]],
        marker=pricing_shapes[row["pricing_model"]],
        s=100,
        edgecolor="black",
        alpha=0.8,
    )
    plt.text(row["total_cost"] + 1, row["co2_kg"], row["instance_id"], fontsize=8)

plt.title("Coût vs Émission CO₂ (couleur : région, forme : pricing)")
plt.xlabel("Coût total ($)")
plt.ylabel("Émission CO₂ (kg)")
plt.grid(True, linestyle="--", alpha=0.5)
plt.gca().set_facecolor("#f9f9f9")

# Légendes
region_handles = [
    plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=c, markeredgecolor="black", markersize=10, label=r)
    for r, c in region_color_map.items()
]
model_handles = [
    plt.Line2D([0], [0], marker=pricing_shapes[m], color="w", markerfacecolor="gray", markeredgecolor="black", markersize=10, label=m)
    for m in pricing_shapes
]
plt.legend(handles=region_handles + model_handles, loc="best")
plt.xscale("log")
finalize("plot_cost_vs_co2.png")

# ────────────────────────────
# ░░ 5b. Coût vs Coût carbone (si dispo) ░░
# ────────────────────────────

if "co2_cost" in df.columns:
    plt.figure(figsize=(12, 7))
    for _, row in df.iterrows():
        plt.scatter(
            row["total_cost"],
            row["co2_cost"],
            color=region_color_map[row["region"]],
            marker=pricing_shapes[row["pricing_model"]],
            s=100,
            edgecolor="black",
            alpha=0.8,
        )

    plt.title("Coût vs Coût Carbone (co2_cost)")
    plt.xlabel("Coût AWS ($)")
    plt.ylabel("Coût Carbone ($)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.gca().set_facecolor("#f9f9f9")
    plt.xscale("log")
    plt.yscale("log")
    plt.legend(handles=region_handles + model_handles, loc="best")
    finalize("plot_cost_vs_co2cost.png")

# ────────────────────────────
# ░░ 6. Bar Chart coût moyen vs CO₂ moyen ░░
# ────────────────────────────

region_summary = df.groupby("region", as_index=False).agg({"total_cost": "mean", "co2_kg": "mean"})
region_summary.sort_values("total_cost", ascending=False, inplace=True)

fig, ax1 = plt.subplots(figsize=(8, 5))
positions = np.arange(len(region_summary))
bar_w = 0.4
ax1.bar(positions - bar_w / 2, region_summary["total_cost"], width=bar_w, alpha=0.7, label="Coût moyen ($)")
ax1.set_ylabel("Coût moyen ($)")
ax2 = ax1.twinx()
ax2.bar(positions + bar_w / 2, region_summary["co2_kg"], width=bar_w, alpha=0.7, label="CO₂ moyen (kg)")
ax2.set_ylabel("CO₂ moyen (kg)")
ax1.set_xticks(positions)
ax1.set_xticklabels(region_summary["region"], rotation=45)
plt.title("Coût moyen vs CO₂ moyen par région")
ax1.legend(loc="upper left")
ax2.legend(loc="upper right")
fig.tight_layout()
finalize("bar_cost_co2_by_region.png")

# ────────────────────────────
# ░░ 7. Heatmap (si co2_cost) ░░
# ────────────────────────────

if "co2_cost" in df.columns:
    pivot = df.pivot_table(values="co2_cost", index="region", columns="pricing_model", aggfunc="mean")
    plt.figure(figsize=(6, 4))
    plt.imshow(pivot.values, cmap="YlGnBu", aspect="auto")
    plt.colorbar(label="Coût carbone moyen ($)")
    plt.xticks(np.arange(len(pivot.columns)), pivot.columns, rotation=45)
    plt.yticks(np.arange(len(pivot.index)), pivot.index)
    plt.title("Heatmap : Coût carbone (region × pricing)")
    finalize("heatmap_co2_cost.png")

# ────────────────────────────
# ░░ 8. Boxplot coût total par région ░░
# ────────────────────────────

regions_order = df["region"].unique().tolist()
plt.figure(figsize=(8, 5))
plt.boxplot([df[df["region"] == r]["total_cost"] for r in regions_order], labels=regions_order, patch_artist=True)
plt.title("Distribution du Coût total par région")
plt.xlabel("Région")
plt.ylabel("Coût total ($)")
plt.grid(axis="y", linestyle="--", alpha=0.5)
finalize("boxplot_cost_by_region.png")

print("\n✅ Analyse terminée !")
