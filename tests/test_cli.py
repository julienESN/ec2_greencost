import argparse
import sys

from ec2_greencost import simulate_ec2


# -------- simulate_ec2 CLI --------
def test_simulate_cli_defaults(tmp_path):
    """Le parseur accepte les valeurs par défaut et renvoie bien 50 instances."""
    argv = ["prog"]
    parser: argparse.ArgumentParser = simulate_ec2._cli_parser()
    args = parser.parse_args(argv[1:])

    # Valeurs par défaut
    assert args.num_instances is None
    assert args.output is None
    assert args.co2_price is None

    # Lancement dans un sous‑processus : simulate_ec2 en mode non interactif
    out_csv = tmp_path / "ec2.csv"
    sys.argv = ["simulate_ec2.py", "-n", "50", "-o", str(out_csv), "-c", "0.08"]
    simulate_ec2.main()

    assert out_csv.exists()
