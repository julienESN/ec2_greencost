# Documentation technique – Package **ec2_greencost**

Ce document décrit l’architecture et l’usage des trois fichiers Python principaux :

| Fichier | Rôle principal | Exécution | API publique |
|---------|----------------|-----------|--------------|
| `src/ec2_greencost/__init__.py` | Initialise le package, expose des sous‑modules sans effets de bord | import automatique | `simulate_ec2` |
| `src/ec2_greencost/analyse_ec2.py` | Analyse et visualise un CSV d’instances EC2 | `python -m ec2_greencost.analyse_ec2` ou via `analyse_ec2.py` wrapper | `main()` |
| `src/ec2_greencost/simulate_ec2.py` | Génère un CSV de simulation EC2 | `python -m ec2_greencost.simulate_ec2` | `generate_instances`, `export_to_csv`, `main()` |

---
## 1 · `src/ec2_greencost/__init__.py`

```python
__all__: list[str] = []
__version__ = "0.1.0"
from . import simulate_ec2  # noqa: F401
__all__.append("simulate_ec2")
```

### Objectif
* Garantir qu’**importer le package n’exécute aucun parsing CLI** ni accès disque.
* Exposer uniquement le sous‑module **`simulate_ec2`** pour usage programmatique.

### À retenir
* Pas d’import d’`analyse_ec2` (effet de bord).  
* `__version__` centralisé pour un futur packaging PyPI.

---
## 2 · `src/ec2_greencost/analyse_ec2.py`

### Description générale
Analyse un fichier CSV listant des instances AWS EC2 et génère des graphiques (scatter, bar chart) au format PNG. Le script sait :

1. **Choisir un layout** : figure unique (subplots) ou images séparées.  
2. **Basculer en mode sans affichage** (`--no-display`) pour la CI / serveurs.
3. **Fonctionner en mode interactif** si aucun argument CLI n’est fourni.

### Exécution
```bash
# Recommandé (à la racine du repo)
python -m ec2_greencost.analyse_ec2 -i data/simulated_ec2.csv -d plots --layout unified
```
Un wrapper `analyse_ec2.py` à la racine permet aussi :
```bash
python analyse_ec2.py -i …
```

### Options CLI
| Option | Défaut | Description |
|--------|--------|-------------|
| `-i, --input` | `data/simulated_ec2.csv` | Chemin du CSV à analyser |
| `-d, --outdir` | `plots/` | Dossier où enregistrer les PNG |
| `--layout` | `unified` | `unified` (subplots) ou `separate` (figures multiples) |
| `--no-display` | *false* | Force le backend Matplotlib « Agg » et désactive `plt.show()` |

### Points d’implémentation clés
* **Palette auto‑extensible** pour un nombre quelconque de régions.
* **Liste `PLOTS`** : ajouter un tuple `(filename, draw_function)` suffit pour étendre les visuels.
* Blocs interactifs exclus de la couverture (`# pragma: no cover`).

### API interne
* `main()` : exécuté uniquement lorsque le module est lancé en script ou via wrapper.
* Fonctions de dessin : `plot_cost_vs_co2()`, `plot_avg_cost_by_region()`.

---
## 3 · `src/ec2_greencost/simulate_ec2.py`

### Description générale
Génère un jeu de données synthétique représentant un parc d’instances EC2, avec :
* Coût horaire, coût total, électricité consommée, émissions CO₂, etc.
* Tarification aléatoire (`on_demand`, `reserved`, `spot`).
* Facteurs d’émissions régionaux simplifiés.

### Exécution
```bash
# Mode CLI (batch)
python -m ec2_greencost.simulate_ec2 -n 100 -o data/simulated_ec2.csv -c 0.10

# Mode interactif (aucun argument)
python -m ec2_greencost.simulate_ec2
```

### Options CLI
| Option | Défaut | Description |
|--------|--------|-------------|
| `-n, --num-instances` | 50 | Nombre d’instances à simuler |
| `-o, --output` | `data/simulated_ec2.csv` | Chemin du CSV de sortie |
| `-c, --co2-price` | `0.08` | Prix du CO₂ en $/kg pour calculer `co2_cost` |

### Fonctions + API
* `generate_instances(n:int, co2_price_per_kg:float)` → `list[dict]`  
  Renvoie la simulation brute (sans I/O).
* `export_to_csv(instances, filename)`  
  Écrit un CSV en créant les dossiers au besoin.
* `_cli_parser()`  : interne, renvoie un `argparse.ArgumentParser`.
* `main()`  : gère l’interactivité et appelle les fonctions ci‑dessus.

### Détails d’implémentation
* Valeurs par défaut regroupées en dictionnaires (`INSTANCE_TYPES`, `REGION_EMISSIONS`, etc.) pour une modification aisée.
* Les trois helpers `_ask_positive_int`, `_ask_path`, `_ask_float` sont exclus de la couverture.
* Utilise `random` **sans seed** (choix assumé pour la variabilité).

---
## 4 · Tests & Couverture

* **tests/test_cli.py** : parseur CLI + génération CSV via sous‑process.
* **tests/test_simulate.py** : logique pure (`generate_instances`, `export_to_csv`).
* **tests/test_plots.py** : exécution complète d’`analyse_ec2` en subprocess contrôlé.
* Couverture actuelle : **83 %** (seuil CI 70 %). Les lignes manquantes sont quasi‑exclusivement des blocs interactifs marqués `# pragma: no cover`.
