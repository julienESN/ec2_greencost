import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
print(matplotlib.__version__)
import numpy as np
import os

# 1. Charger les données
df = pd.read_csv("data/simulated_ec2.csv")

# 2. Afficher un aperçu rapide
print("🔍 Aperçu des données :")
print(df.head())

# 2. bis Vérifier la présence de co2_cost
if 'co2_cost' not in df.columns:
    print("\n⚠️ La colonne 'co2_cost' n'existe pas dans le CSV. Assure-toi d'avoir mis à jour ton script de simulation.")
else:
    print("\n🔎 Aperçu de la colonne 'co2_cost':")
    print(df['co2_cost'].describe())

# 3. Quelques stats basées sur le 'pricing_model'
model_counts = df['pricing_model'].value_counts()
print("\n📊 Instances par pricing model :")
print(model_counts)

avg_cost_by_model = df.groupby('pricing_model')['total_cost'].mean()
print("\n💰 Coût moyen ($) par pricing model :")
print(avg_cost_by_model)

avg_co2_by_model = df.groupby('pricing_model')['co2_kg'].mean()
print("\n🌱 Émissions CO₂ moyennes (kg) par pricing model :")
print(avg_co2_by_model)

# 3. Bis. Si co2_cost est disponible, affichons des stats dessus
if 'co2_cost' in df.columns:
    avg_co2cost_by_model = df.groupby('pricing_model')['co2_cost'].mean()
    print("\n💲 Coût carbone moyen ($) par pricing model :")
    print(avg_co2cost_by_model)

dir_path = "plots"

if os.path.isdir(dir_path):
    print(f"{dir_path} exists")
else:
    os.makedirs(dir_path)
    print(f"Created {dir_path} directory")

# ------------------------------------------------------------------
# 🎨 Partie Visualisation 1: Coût vs Émission CO₂
# ------------------------------------------------------------------
regions = df['region'].unique()
colors = ["red", "blue", "green", "orange"]
region_color_map = dict(zip(regions, colors))

pricing_shapes = {
    'on_demand': 'o',  # cercle
    'reserved': 's',   # carré
    'spot': 'X'        # croix (ou x)
}

plt.figure(figsize=(12, 7))

for _, row in df.iterrows():
    region_color = region_color_map[row['region']]
    shape = pricing_shapes[row['pricing_model']]
    plt.scatter(
        row['total_cost'],
        row['co2_kg'],
        color=region_color,
        marker=shape,
        s=100,
        edgecolor='black',
        alpha=0.8
    )
    # Annotation facultative
    plt.text(
        row['total_cost'] + 1,
        row['co2_kg'],
        row['instance_id'],
        fontsize=8,
        color='black'
    )

plt.title("Analyse Coût vs Émission CO₂ des instances EC2\n(couleur=Région, forme=Pricing Model)",
          fontsize=14, weight='bold')
plt.xlabel("Coût total ($)", fontsize=12)
plt.ylabel("Émission CO₂ (kg)", fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)
plt.gca().set_facecolor("#f9f9f9")

# Légendes
region_handles = [
    plt.Line2D([0], [0],
               marker='o', color='w',
               markerfacecolor=color,
               markeredgecolor='black',
               markersize=10, label=region)
    for region, color in region_color_map.items()
]
model_handles = [
    plt.Line2D([0], [0],
               marker=pricing_shapes[m], color='w',
               markerfacecolor='gray',
               markeredgecolor='black',
               markersize=10,
               label=m)
    for m in pricing_shapes
]

legend1 = plt.legend(handles=region_handles, title="Régions", loc="upper left")
plt.gca().add_artist(legend1)
plt.legend(handles=model_handles, title="Pricing Model", loc="upper right")

# Top 3 instances les plus polluantes
top_co2 = df.sort_values(by='co2_kg', ascending=False).head(3)
top_text = "Top CO₂ :\n"
for _, row_ in top_co2.iterrows():
    top_text += f"- {row_['instance_id']} : {row_['co2_kg']} kg\n"

plt.text(
    x=df['total_cost'].max() * 0.60,
    y=df['co2_kg'].max() * 0.80,
    s=top_text,
    fontsize=10,
    bbox=dict(boxstyle="round,pad=0.5", fc="#f0f0f0", ec="gray", lw=1),
    ha='left'
)
plt.tight_layout()
plt.xscale('log')  # échelle log si gros écarts
plt.savefig("plots/plot_cost_vs_co2.png", dpi=300)
plt.show()

# ------------------------------------------------------------------
# 🎨 Partie Visualisation 2: Coût vs Coût carbone (si dispo)
# ------------------------------------------------------------------
if 'co2_cost' in df.columns:
    plt.figure(figsize=(12, 7))
    for _, row in df.iterrows():
        region_color = region_color_map[row['region']]
        shape = pricing_shapes[row['pricing_model']]
        plt.scatter(
            row['total_cost'],
            row['co2_cost'],
            color=region_color,
            marker=shape,
            s=100,
            edgecolor='black',
            alpha=0.8
        )

    plt.title("Analyse Coût vs Coût Carbone (co2_cost) des instances EC2",
              fontsize=14, weight='bold')
    plt.xlabel("Coût AWS ($)", fontsize=12)
    plt.ylabel("Coût Carbone ($)", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.gca().set_facecolor("#f9f9f9")

    legend1 = plt.legend(handles=region_handles, title="Régions", loc="upper left")
    plt.gca().add_artist(legend1)
    plt.legend(handles=model_handles, title="Pricing Model", loc="upper right")

    plt.tight_layout()
    plt.xscale('log')
    plt.yscale('log')
    plt.savefig("plots/plot_cost_vs_co2cost.png", dpi=300)
    plt.show()
else:
    print("\n⚠️ Pas de 'co2_cost' dans le dataset, impossible de tracer le 2ème graphique.")

# ------------------------------------------------------------------
# 🎨 Partie Visualisation 3: Bar Chart coût moyen vs CO₂ moyen par région
# ------------------------------------------------------------------
print("\n== Bar Chart: Coût moyen vs CO₂ moyen par région ==\n")
region_summary = df.groupby('region', as_index=False).agg({
    'total_cost': 'mean',
    'co2_kg': 'mean'
})
# Tri par coût (juste pour une lecture plus intuitive)
region_summary.sort_values(by='total_cost', ascending=False, inplace=True)

fig, ax1 = plt.subplots(figsize=(8, 5))
x_positions = np.arange(len(region_summary))
bar_width = 0.4

# Barre pour le coût moyen
ax1.bar(
    x_positions - bar_width/2,
    region_summary['total_cost'],
    width=bar_width,
    alpha=0.7,
    color='blue',
    label='Coût moyen ($)'
)
ax1.set_ylabel("Coût moyen ($)", color='blue')
ax1.set_ylim(0, region_summary['total_cost'].max() * 1.2)
ax1.set_xticks(x_positions)
ax1.set_xticklabels(region_summary['region'], rotation=45)

# Deuxième axe Y pour le CO₂
ax2 = ax1.twinx()
ax2.bar(
    x_positions + bar_width/2,
    region_summary['co2_kg'],
    width=bar_width,
    alpha=0.7,
    color='green',
    label='CO₂ moyen (kg)'
)
ax2.set_ylabel("CO₂ moyen (kg)", color='green')
ax2.set_ylim(0, region_summary['co2_kg'].max() * 1.2)

plt.title("Coût moyen vs CO₂ moyen par région")
fig.tight_layout()

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='best')
plt.savefig("plots/bar_cost_co2_by_region.png", dpi=300)
plt.show()

# ------------------------------------------------------------------
# 🎨 Partie Visualisation 4: Heatmap co2_cost (si dispo) par (region, pricing_model)
# ------------------------------------------------------------------
if 'co2_cost' in df.columns:
    print("\n== Heatmap co2_cost par (région, pricing_model) ==\n")
    pivot_co2cost = df.pivot_table(
        values='co2_cost',
        index='region',
        columns='pricing_model',
        aggfunc='mean'
    )
    print(pivot_co2cost)

    plt.figure(figsize=(6, 4))
    heat_data = pivot_co2cost.values
    plt.imshow(heat_data, cmap='YlGnBu', aspect='auto')
    plt.colorbar(label='Coût Carbone moyen ($)')

    plt.xticks(np.arange(len(pivot_co2cost.columns)), pivot_co2cost.columns, rotation=45)
    plt.yticks(np.arange(len(pivot_co2cost.index)), pivot_co2cost.index)

    plt.title("Heatmap Coût Carbone moyen\n(région vs pricing_model)")
    plt.tight_layout()
    plt.savefig("plots/heatmap_co2_cost.png", dpi=300)
    plt.show()
else:
    print("\n⚠️ Pas de 'co2_cost' dans le dataset, impossible de tracer la heatmap.")

# ------------------------------------------------------------------
# 🎨 Partie Visualisation 5: Boxplot coût total par région
# ------------------------------------------------------------------
print("\n== Boxplot: Distribution du coût total par région ==\n")

regions_ordered = df['region'].unique().tolist()  # ordre brut (ou trié si besoin)
data_by_region = [df[df['region'] == reg]['total_cost'] for reg in regions_ordered]

plt.figure(figsize=(8, 5))
#Ne met pas tick_labels
plt.boxplot(data_by_region, labels=regions_ordered, patch_artist=True)

plt.title("Distribution du Coût total par région (Boxplot)", fontsize=12)
plt.xlabel("Région")
plt.ylabel("Coût total ($)")
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.savefig("plots/boxplot_cost_by_region.png", dpi=300)
plt.show()
