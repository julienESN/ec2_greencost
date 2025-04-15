import random
import csv

# 1. Type d’instances EC2 et leur coût horaire (USD)
instance_types = {
    't3.micro': 0.0116,
    't3.small': 0.023,
    'm5.large': 0.096,
    'c6a.xlarge': 0.153,
    'r5.2xlarge': 0.504
}

# 2. Régions AWS et leur facteur d’émission CO₂ (en gCO2 par kWh)
region_emissions = {
    'eu-west-3': 19,       # Paris
    'us-east-1': 393,      # Virginie
    'ap-southeast-1': 520, # Singapour
    'eu-central-1': 401    # Francfort
}

# 2.bis. Ajout d'un pricing model
# On-Demand = coût de base, Reserved = ~30% moins cher, Spot = ~60% moins cher
pricing_models = {
    'on_demand': 1.0,
    'reserved': 0.7,
    'spot': 0.4
}

# 2. ter. Puissance de base estimée par type d’instance (W)
base_power_map = {
    't3.micro': 30,
    't3.small': 40,
    'm5.large': 60,
    'c6a.xlarge': 80,
    'r5.2xlarge': 120
}

def generate_instances(n=10):
    """
    Génère n instances EC2 simulées avec coût AWS + coût carbone.
    """
    # -- Hypothèse : 80$/tonne de CO2 => 0.08$/kg
    co2_price_per_kg = 0.08

    instances = []
    for i in range(n):
        # Choix aléatoire du type, de la région, du pricing
        instance_type = random.choice(list(instance_types.keys()))
        region = random.choice(list(region_emissions.keys()))
        model = random.choice(list(pricing_models.keys()))

        uptime_hours = random.randint(20, 300)  # nombre d'heures où l'instance tourne
        cpu_util = round(random.uniform(5, 90), 2)  # % d'utilisation CPU moyen

        # 1) Calcul du coût AWS selon le pricing model
        base_price = instance_types[instance_type]
        price_per_hour = round(base_price * pricing_models[model], 4)
        total_cost = round(price_per_hour * uptime_hours, 2)

        # 2) Estimation énergie consommée
        cpu_factor = 0.3  # ex: 0.3 W supplémentaires par % CPU
        base_power = base_power_map[instance_type]
        power_watts = round(base_power + cpu_util * cpu_factor, 2)
        energy_kwh = round((power_watts * uptime_hours) / 1000, 2)

        # 3) Calcul CO₂
        emission_factor = region_emissions[region]
        co2_grams = round(energy_kwh * emission_factor, 2)
        co2_kg = round(co2_grams / 1000, 2)

        # 4) Coût carbone (GreenOps)
        co2_cost = round(co2_kg * co2_price_per_kg, 2)

        # 5) Ajout à la liste
        instances.append({
            'instance_id': f"i-sim-{i+1:03d}",
            'type': instance_type,
            'region': region,
            'pricing_model': model,
            'uptime_hours': uptime_hours,
            'cpu_avg': cpu_util,
            'price_per_hour': price_per_hour,
            'total_cost': total_cost,
            'energy_kwh': energy_kwh,
            'co2_kg': co2_kg,
            'co2_cost': co2_cost
        })
    return instances

def export_to_csv(instances, filename='simulated_ec2.csv'):
    """
    Exporte la liste de dictionnaires en un fichier CSV.
    """
    with open(filename, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=instances[0].keys())
        writer.writeheader()
        writer.writerows(instances)

# Exécution principale
if __name__ == "__main__":
    data = generate_instances(50)
    export_to_csv(data)
    print("✅ Données simulées exportées dans simulated_ec2.csv")
