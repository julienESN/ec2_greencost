"""
Test léger : on exécute analyse_ec2 sur un CSV simulé
et on vérifie que les images sont créées sans lever d’exception.
"""
import subprocess
import sys
from ec2_greencost.simulate_ec2 import generate_instances, export_to_csv

def test_analyse_ec2_runs(tmp_path):
    csv_file = tmp_path / "data.csv"
    export_to_csv(generate_instances(30), csv_file)

    out_dir = tmp_path / "plots"
    out_dir.mkdir()

    proc = subprocess.run(
        [
         sys.executable,
            "-m", "ec2_greencost.analyse_ec2",
            "-i", str(csv_file),
            "-d", str(out_dir),
            "--no-display",
            "--layout", "unified",
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    # L’exécution en mode unified crée « ec2_overview.png »
    assert (out_dir / "ec2_overview.png").exists()
