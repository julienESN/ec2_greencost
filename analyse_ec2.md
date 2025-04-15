
---



# Analyse et Visualisation des Instances EC2 (analyse_ec2.py)

Ce script lit le fichier `simulated_ec2.csv` généré par le simulateur et propose différentes analyses et visualisations :

1. **Statistiques agrégées** (coût moyen, émissions moyennes, etc.)  
2. **Scatter plots** (Coût vs CO₂, Coût vs Coût carbone)  
3. **Bar Chart** (Comparaison coût moyen vs CO₂ moyen par région)  
4. **Heatmap** (coût carbone moyen par région et pricing model)  
5. **Boxplot** (distribution du coût total par région)

---

## 📁 Structure Principale

```bash
analyse_ec2.py
├── Import des bibliothèques (pandas, matplotlib, numpy)
├── Lecture du CSV (simulated_ec2.csv)
├── Statistiques descriptives (groupby, describe, etc.)
├── Visualisation 1 : Coût vs Émissions CO₂ (scatter)
├── Visualisation 2 : Coût vs Coût Carbone (scatter)
├── Visualisation 3 : Bar Chart (Coût moyen vs CO₂ moyen par région)
├── Visualisation 4 : Heatmap (région vs pricing_model, co2_cost)
└── Visualisation 5 : Boxplot (distribution du coût total par région)
