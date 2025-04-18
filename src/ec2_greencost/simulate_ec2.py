#!/usr/bin/env python3
"""simulate_ec2.py
Simule un parc d'instances EC2 et exporte les coûts financiers & carbone dans un CSV.

Modes d’exécution :
  • Interactif : lancer simplement `python simulate_ec2.py` et répondre aux questions.
  • Ligne de commande : fournir tout ou partie des options, ex.:
      python simulate_ec2.py -n 100 -o data/ec2.csv -c 0.10
"""

from __future__ import annotations

import argparse
import csv
import os
import random
import sys
from pathlib import Path
from typing import Dict, List

INSTANCE_TYPES: dict[str, float] = {
    "t3.micro": 0.0116,
    "t3.small": 0.023,
    "m5.large": 0.096,
    "c6a.xlarge": 0.153,
    "r5.2xlarge": 0.504,
}

REGION_EMISSIONS: dict[str, int] = {
    "eu-west-3": 19,
    "us-east-1": 393,
    "ap-southeast-1": 520,
    "eu-central-1": 401,
}

PRICING_MODELS: dict[str, float] = {
    "on_demand": 1.0,
    "reserved": 0.7,
    "spot": 0.4,
}

BASE_POWER_MAP: dict[str, int] = {
    "t3.micro": 30,
    "t3.small": 40,
    "m5.large": 60,
    "c6a.xlarge": 80,
    "r5.2xlarge": 120,
}


def _ask_positive_int(prompt: str, default: int) -> int:
    while True:
        raw = input(f"{prompt} [{default}]: ").strip()
        if not raw:
            return default
        if raw.isdigit() and int(raw) > 0:
            return int(raw)
        print("❌ Merci d’entrer un entier positif.")


def _ask_path(prompt: str, default: Path) -> Path:
    raw = input(f"{prompt} [{default}]: ").strip()
    return Path(raw) if raw else default


def _ask_float(prompt: str, default: float) -> float:
    while True:
        raw = input(f"{prompt} [{default}]: ").replace(",", ".").strip()
        if not raw:
            return default
        try:
            val = float(raw)
            if val >= 0:
                return val
        except ValueError:
            pass
        print("❌ Merci d’entrer un nombre positif.")


def generate_instances(n: int = 10, co2_price_per_kg: float = 0.08) -> List[Dict[str, float]]:
    instances: list[dict[str, float]] = []
    for i in range(n):
        instance_type = random.choice(list(INSTANCE_TYPES))
        region = random.choice(list(REGION_EMISSIONS))
        model = random.choice(list(PRICING_MODELS))

        uptime_hours = random.randint(20, 300)
        cpu_util = round(random.uniform(5, 90), 2)

        base_price = INSTANCE_TYPES[instance_type]
        price_per_hour = round(base_price * PRICING_MODELS[model], 4)
        total_cost = round(price_per_hour * uptime_hours, 2)

        cpu_factor = 0.3
        power_watts = round(BASE_POWER_MAP[instance_type] + cpu_util * cpu_factor, 2)
        energy_kwh = round(power_watts * uptime_hours / 1000, 2)

        co2_kg = round(energy_kwh * REGION_EMISSIONS[region] / 1000, 2)
        co2_cost = round(co2_kg * co2_price_per_kg, 2)

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


def export_to_csv(instances: List[Dict[str, float]], filename: Path) -> None:
    filename.parent.mkdir(parents=True, exist_ok=True)
    with filename.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=instances[0].keys())
        writer.writeheader()
        writer.writerows(instances)


def _cli_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("-n", "--num-instances", type=int, help="Nombre d’instances à générer")
    p.add_argument("-o", "--output", type=Path, help="Chemin du CSV de sortie")
    p.add_argument("-c", "--co2-price", type=float, help="Prix du CO₂ en $/kg")
    return p


def main() -> None:
    args = _cli_parser().parse_args()
    interactive = len(sys.argv) == 1 and sys.stdin.isatty()

    if interactive:
        print("=== Mode interactif ===")
        num_instances = _ask_positive_int("Nombre d’instances", 50)
        output_csv = _ask_path("CSV de sortie", Path("../data/simulated_ec2.csv"))
        co2_price = _ask_float("Prix du CO₂ en $/kg", 0.08)
    else:
        num_instances = args.num_instances or 50
        output_csv = args.output or Path("../data/simulated_ec2.csv")
        co2_price = args.co2_price if args.co2_price is not None else 0.08

    data = generate_instances(num_instances, co2_price)
    export_to_csv(data, output_csv)
    print(f"✅ {num_instances} instances écrites → {output_csv} (CO₂: ${co2_price}/kg)")


if __name__ == "__main__":
    main()
