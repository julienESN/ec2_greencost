#!/usr/bin/env python3
"""simulate_ec2.py
Simule un parc d'instances EC2 et exporte les coûts financiers et carbone
vers un fichier CSV configurable.

Usage:
  python simulate_ec2.py [-n 100] [-o my_ec2.csv] [-c 0.1]

Options:
  -n, --num-instances INT   Nombre d'instances à générer (défaut : 50)
  -o, --output FILE         Chemin du fichier CSV de sortie (défaut : data/simulated_ec2.csv)
  -c, --co2-price FLOAT     Prix du CO₂ en dollars par kg (défaut : 0.08)
"""

import argparse
import csv
import os
import random
from typing import List, Dict

# 1. Type d’instances EC2 et leur coût horaire (USD)
INSTANCE_TYPES = {
    "t3.micro": 0.0116,
    "t3.small": 0.023,
    "m5.large": 0.096,
    "c6a.xlarge": 0.153,
    "r5.2xlarge": 0.504,
}

# 2. Régions AWS et leur facteur d’émission CO₂ (en gCO₂ par kWh)
REGION_EMISSIONS = {
    "eu-west-3": 19,  # Paris
    "us-east-1": 393,  # Virginie
    "ap-southeast-1": 520,  # Singapour
    "eu-central-1": 401,  # Francfort
}

# 3. Modèles de tarification (rapport multiplicatif sur le prix On‑Demand)
PRICING_MODELS = {
    "on_demand": 1.0,
    "reserved": 0.7,
    "spot": 0.4,
}

# 4. Puissance de base estimée par type d’instance (W)
BASE_POWER_MAP = {
    "t3.micro": 30,
    "t3.small": 40,
    "m5.large": 60,
    "c6a.xlarge": 80,
    "r5.2xlarge": 120,
}

def generate_instances(n: int = 10, co2_price_per_kg: float = 0.08) -> List[Dict[str, float]]:
    """Génère *n* instances EC2 simulées avec coût AWS et coût carbone.

    Args:
        n: Nombre d'instances à générer.
        co2_price_per_kg: Coût du CO₂ en $/kg.
    Returns:
        Liste de dictionnaires représentant chaque instance simulée.
    """

    instances = []
    for i in range(n):
        # Choix aléatoire du type, de la région et du modèle de pricing
        instance_type = random.choice(list(INSTANCE_TYPES.keys()))
        region = random.choice(list(REGION_EMISSIONS.keys()))
        model = random.choice(list(PRICING_MODELS.keys()))

        uptime_hours = random.randint(20, 300)  # nombre d'heures de fonctionnement
        cpu_util = round(random.uniform(5, 90), 2)  # % d'utilisation CPU moyen

        # 1) Calcul du coût AWS selon le modèle de pricing
        base_price = INSTANCE_TYPES[instance_type]
        price_per_hour = round(base_price * PRICING_MODELS[model], 4)
        total_cost = round(price_per_hour * uptime_hours, 2)

        # 2) Estimation énergie consommée
        cpu_factor = 0.3  # 0.3 W supplémentaires par % CPU
        base_power = BASE_POWER_MAP[instance_type]
        power_watts = round(base_power + cpu_util * cpu_factor, 2)
        energy_kwh = round((power_watts * uptime_hours) / 1000, 2)

        # 3) Calcul CO₂
        emission_factor = REGION_EMISSIONS[region]
        co2_grams = round(energy_kwh * emission_factor, 2)
        co2_kg = round(co2_grams / 1000, 2)

        # 4) Coût carbone (GreenOps)
        co2_cost = round(co2_kg * co2_price_per_kg, 2)

        # 5) Ajout à la liste
        instances.append(
            {
                "instance_id": f"i-sim-{i + 1:03d}",
                "type": instance_type,
                "region": region,
                "pricing_model": model,
                "uptime_hours": uptime_hours,
                "cpu_avg": cpu_util,
                "price_per_hour": price_per_hour,
                "total_cost": total_cost,
                "energy_kwh": energy_kwh,
                "co2_kg": co2_kg,
                "co2_cost": co2_cost,
            }
        )
    return instances

def export_to_csv(instances: List[Dict[str, float]], filename: str = "data/simulated_ec2.csv") -> None:
    """Exporte la liste d'instances vers un fichier CSV.

    Args:
        instances: Liste de dictionnaires d'instances simulées.
        filename: Chemin du fichier CSV de sortie.
    """

    # S'assure que le dossier cible existe
    output_dir = os.path.dirname(filename) or "."
    os.makedirs(output_dir, exist_ok=True)

    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=instances[0].keys())
        writer.writeheader()
        writer.writerows(instances)


def parse_args() -> argparse.Namespace:
    """Analyse les arguments de ligne de commande."""

    parser = argparse.ArgumentParser(
        description="Simule un parc d'instances EC2 et exporte les coûts financiers et carbone.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-n",
        "--num-instances",
        type=int,
        default=50,
        help="Nombre d'instances EC2 à simuler.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="data/simulated_ec2.csv",
        help="Chemin du fichier CSV de sortie.",
    )
    parser.add_argument(
        "-c",
        "--co2-price",
        type=float,
        default=0.08,
        help="Prix du CO₂ en dollars par kg.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    data = generate_instances(n=args.num_instances, co2_price_per_kg=args.co2_price)
    export_to_csv(data, filename=args.output)

    print(
        f"✅ {args.num_instances} instances simulées et exportées dans '{args.output}' (CO₂ : ${args.co2_price}/kg)"
    )


if __name__ == "__main__":
    main()
