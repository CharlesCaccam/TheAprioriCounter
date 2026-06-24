"""
Exploratory Data Analysis (EDA) for Coffee Bean & Tea Leaf market-basket data.

Run from project root:
  python backend/scripts/eda.py

Outputs charts to backend/reports/ for your project defense slides.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.data_loader import DEFAULT_CSV, eda_summary, load_csv_path  # noqa: E402

REPORTS = Path(__file__).resolve().parents[1] / "reports"
REPORTS.mkdir(exist_ok=True)


def main() -> None:
    if not DEFAULT_CSV.exists():
        print(f"Missing dataset: {DEFAULT_CSV}")
        print("Copy CoffeeBeanAndTeaLeafCoffeeShopData1.csv into the data/ folder.")
        sys.exit(1)

    transactions, _, _, df = load_csv_path(DEFAULT_CSV)
    summary = eda_summary(df, transactions)

    print("=== EDA SUMMARY ===")
    print(f"Transactions (orders):     {summary['transaction_count']}")
    print(f"Unique menu items:       {summary['unique_items']}")
    print(f"Avg items per order:     {summary['avg_items_per_order']}")
    print(f"Columns:                 {summary['columns']}")
    print(f"Missing cells:           {summary['missing_cells']}")
    print("\nTop 10 items:")
    for item in summary["top_items"][:10]:
        print(f"  {item['name']:40} {item['count']:4}")

    # --- Chart 1: top item frequencies ---
    top = pd.DataFrame(summary["top_items"][:12])
    plt.figure(figsize=(10, 5))
    sns.barplot(data=top, x="count", y="name", hue="name", palette="YlOrBr", legend=False)
    plt.title("Top 12 Most Ordered Items")
    plt.xlabel("Order count")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(REPORTS / "top_items.png", dpi=150)
    plt.close()

    # --- Chart 2: basket size distribution ---
    sizes = pd.Series([len(t) for t in transactions], name="items_per_order")
    plt.figure(figsize=(8, 4))
    sns.histplot(sizes, bins=range(1, sizes.max() + 2), color="#C1672B")
    plt.title("Items per Order (Basket Size)")
    plt.xlabel("Number of items in one transaction")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(REPORTS / "basket_sizes.png", dpi=150)
    plt.close()

    # --- Chart 3: missing values per column ---
    missing = df.isna().sum()
    plt.figure(figsize=(8, 4))
    missing.plot(kind="bar", color="#4A3728")
    plt.title("Missing Values per Column")
    plt.ylabel("Count")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(REPORTS / "missing_values.png", dpi=150)
    plt.close()

    print(f"\nCharts saved to: {REPORTS}")


if __name__ == "__main__":
    main()
