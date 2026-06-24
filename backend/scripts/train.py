"""
Train (fit) the Apriori model and save association rules to JSON.

Run from project root:
  python backend/scripts/train.py

Optional flags:
  --support 0.02 --confidence 0.30 --lift 1.0
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.apriori_service import train_apriori  # noqa: E402
from app.data_loader import DEFAULT_CSV, eda_summary, load_csv_path  # noqa: E402

MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "rules.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Train Apriori on coffee-shop ledger")
    parser.add_argument("--support", type=float, default=0.02)
    parser.add_argument("--confidence", type=float, default=0.30)
    parser.add_argument("--lift", type=float, default=1.0)
    args = parser.parse_args()

    if not DEFAULT_CSV.exists():
        print(f"Missing dataset: {DEFAULT_CSV}")
        sys.exit(1)

    transactions, _, _, df = load_csv_path(DEFAULT_CSV)
    eda = eda_summary(df, transactions)
    model = train_apriori(
        transactions,
        min_support=args.support,
        min_confidence=args.confidence,
        min_lift=args.lift,
    )

    MODEL_PATH.parent.mkdir(exist_ok=True)
    payload = {
        "source": DEFAULT_CSV.name,
        "eda": eda,
        "model": model,
    }
    MODEL_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("=== MODEL TRAINED ===")
    print(f"Rules found:        {model['metrics']['rule_count']}")
    print(f"Frequent itemsets:  {model['metrics']['frequent_itemset_count']}")
    print(f"Top lift:           {model['metrics']['top_lift']}")
    print(f"Saved to:           {MODEL_PATH}")

    if model["rules"][:3]:
        print("\nSample rules (top 3 by lift):")
        for rule in model["rules"][:3]:
            ant = ", ".join(rule["antecedent"])
            cons = ", ".join(rule["consequent"])
            print(f"  {ant}  =>  {cons}  (lift={rule['lift']:.2f})")


if __name__ == "__main__":
    main()
