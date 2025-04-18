#!/usr/bin/env python3
"""analyse_ec2.py
Analyse un fichier CSV d’instances EC2 : statistiques et visualisations.

Améliorations (Issue #5)
========================
- **Subplots unifiés** : possibilité de regrouper toutes les visualisations dans une même figure à l’aide de sous‑graphiques.
- **Mode d’affichage sélectionnable** : `--layout unified` (par défaut) ou `--layout separate` pour revenir au comportement précédent.
- **Lisibilité** : styles cohérents, titres clairs, tailles de police homogènes, légende compacte.
"""


from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

###############################################################################
# CLI
###############################################################################
parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description="Analyse un CSV d’instances EC2 et génère des statistiques visuelles.",
)
parser.add_argument("-i", "--input", type=Path, help="CSV à analyser")
parser.add_argument("-d", "--outdir", type=Path, help="Dossier de sortie des graphes")
parser.add_argument("--no-display", action="store_true", help="Pas d’affichage graphique (backend Agg)")
parser.add_argument(
    "--layout",
    choices=["unified", "separate"],
    default="unified",
    help="Organisation des graphes : figure unique avec sous-graphiques ou figures séparées",
)
args = parser.parse_args()

###############################################################################
# Interaction en mode CLI simple (aucun argument fourni)
###############################################################################
interactive = len(sys.argv) == 1 and sys.stdin.isatty()
if interactive: # pragma: no cover
    args.input = Path(input("CSV à analyser [data/simulated_ec2.csv]: ").strip() or "data/simulated_ec2.csv")
    args.outdir = Path(input("Dossier des graphes [plots]: ").strip() or "plots")
    ans_layout = input("Disposition unifiée (u) ou séparée (s) ? [u]: ").strip().lower()
    args.layout = "separate" if ans_layout == "s" else "unified"
    ans_display = input("Afficher les graphiques ? [O/n]: ").strip().lower()
    args.no_display = ans_display == "n"
else:
    args.input = args.input or Path("../../data/simulated_ec2.csv")
    args.outdir = args.outdir or Path("../../plots")

###############################################################################
# Backend Matplotlib
###############################################################################
if args.no_display:
    matplotlib.use("Agg")

plt.style.use("ggplot")  # thème simple et lisible

###############################################################################
# Lecture des données
###############################################################################
df = pd.read_csv(args.input)

print("\nAperçu du jeu de données :")
print(df.head())

args.outdir.mkdir(parents=True, exist_ok=True)

###############################################################################
# Mapping couleurs / formes
###############################################################################
regions = sorted(df["region"].unique())
# Palette cohérente (cyclique si >4 régions)
base_colors = ["tab:red", "tab:blue", "tab:green", "tab:orange", "tab:purple", "tab:brown"]
region_color_map = {r: base_colors[i % len(base_colors)] for i, r in enumerate(regions)}
marker_map = {"on_demand": "o", "reserved": "s", "spot": "X"}

###############################################################################
# Fonctions de visualisation (ajoutez-en librement)
###############################################################################

# Liste de tuples : (nom_fichier, fonction_dessin)
PLOTS: list[tuple[str, callable]] = []

def plot_cost_vs_co2(ax: plt.Axes) -> None:
    """Dispersion coût total vs émissions de CO₂."""
    for pricing_model, group in df.groupby("pricing_model"):
        ax.scatter(
            group["total_cost"],
            group["co2_kg"],
            label=pricing_model,
            marker=marker_map.get(pricing_model, "o"),
            s=50,
            alpha=0.7,
        )
    ax.set_xscale("log")
    ax.set_xlabel("Coût (US$)")
    ax.set_ylabel("CO₂ (kg)")
    ax.set_title("Coût vs CO₂ (échelle logarithmique sur x)")
    ax.legend(title="Modèle tarifaire", fontsize="small")

PLOTS.append(("cost_vs_co2.png", plot_cost_vs_co2))

def plot_avg_cost_by_region(ax: plt.Axes) -> None:
    """Coût moyen par région (bar chart)."""
    means = df.groupby("region")["total_cost"].mean().sort_values()
    ax.bar(means.index, means.values, color=[region_color_map[r] for r in means.index])
    ax.set_xlabel("Région")
    ax.set_ylabel("Coût moyen (US$)")
    ax.set_title("Coût moyen par région")
    ax.tick_params(axis="x", rotation=45)

PLOTS.append(("avg_cost_by_region.png", plot_avg_cost_by_region))

###############################################################################
# Génération des graphes
###############################################################################

if args.layout == "unified":
    n = len(PLOTS)
    ncols = 2 if n > 1 else 1
    nrows = math.ceil(n / ncols)
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(6 * ncols, 4 * nrows))
    # axes peut être un seul Axes ou un array 2D → normalisons
    if not isinstance(axes, np.ndarray):
        axes = np.array([[axes]])
    axes_flat = axes.flatten()

    for i, (fname, plot_func) in enumerate(PLOTS):
        plot_func(axes_flat[i])

    # Retirer axes inutilisés si n n'est pas un multiple de ncols
    for j in range(n, nrows * ncols):
        fig.delaxes(axes_flat[j])

    fig.tight_layout()
    outfile = args.outdir / "ec2_overview.png"
    fig.savefig(outfile, dpi=300)
    print(f"Figure unifiée enregistrée sous {outfile}")

    if not args.no_display:
        plt.show()
    plt.close(fig)

else:  # layout == "separate"
    for fname, plot_func in PLOTS:
        fig, ax = plt.subplots(figsize=(8, 5))
        plot_func(ax)
        fig.tight_layout()
        outfile = args.outdir / fname
        fig.savefig(outfile, dpi=300)
        print(f"Graphique enregistré sous {outfile}")
        if not args.no_display:
            plt.show()
        plt.close(fig)
