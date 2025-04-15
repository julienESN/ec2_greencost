# Simulateur d’Instances EC2 (simulate_ec2.py)

Ce script génère un ensemble de données simulées sur l’utilisation et le coût d’instances EC2, en y associant une estimation de l’empreinte carbone. Il exporte ensuite ces données sous forme de fichier CSV.

---

## ✨ Fonctionnalités

1. **Génération aléatoire** d’instances EC2 :
   - Type d’instance (t3.micro, c6a.xlarge, etc.)
   - Région AWS (us-east-1, eu-west-3, etc.)
   - Modèle de pricing (On-Demand, Reserved, Spot)
   - Charge CPU moyenne (pour estimer la consommation électrique)

2. **Calcul automatique** du coût AWS :
   - Selon le type d’instance (coût horaire de base)
   - Multiplicateur propre au modèle de pricing

3. **Estimation de l’empreinte carbone** :
   - Facteur d’émission spécifique à chaque région (gCO₂/kWh)
   - Consommation énergétique basée sur la puissance (W) et le CPU
   - Conversion de l’empreinte carbone en coût carbone monétaire (co2_cost)

4. **Export en CSV** :
   - Un fichier `simulated_ec2.csv` contenant toutes les colonnes pertinentes (`total_cost`, `co2_kg`, etc.)

---

## 📁 Structure Principale

```bash
simulate_ec2.py
├── instance_types          # Dict : coût horaire de base par type d’instance
├── region_emissions        # Dict : facteur d’émission CO₂ par région
├── pricing_models          # Dict : multiplicateur de coût (on_demand, reserved, spot)
├── base_power_map          # Dict : puissance de base estimée par type d’instance
├── generate_instances()    # Fonction principale de génération
├── export_to_csv()         # Fonction d’export CSV
└── Main Section            # Appel de generate_instances() + export_to_csv()
