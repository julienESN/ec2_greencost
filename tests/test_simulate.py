from ec2_greencost.simulate_ec2 import generate_instances, export_to_csv
import csv
from pathlib import Path

def test_generate_instances_length_and_keys():
    data = generate_instances(n=20, co2_price_per_kg=0.12)
    assert len(data) == 20
    # Toutes les clés attendues
    first = data[0]
    expected = {
        "instance_id",
        "type",
        "region",
        "pricing_model",
        "uptime_hours",
        "cpu_avg",
        "price_per_hour",
        "total_cost",
        "energy_kwh",
        "co2_kg",
        "co2_cost",
    }
    assert expected.issubset(first.keys())

def test_export_to_csv(tmp_path):
    data = generate_instances(n=5)
    csv_file: Path = tmp_path / "small.csv"
    export_to_csv(data, csv_file)

    with csv_file.open() as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 5
