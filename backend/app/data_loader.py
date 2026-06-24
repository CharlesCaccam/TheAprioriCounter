"""Load coffee-shop CSV ledgers into transaction lists for Apriori."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DEFAULT_CSV = DATA_DIR / "CoffeeBeanAndTeaLeafCoffeeShopData1.csv"


def parse_transactions_from_dataframe(df: pd.DataFrame) -> tuple[list[list[str]], list[str], list[list[str]]]:
    """Convert wide CSV rows into market-basket transactions."""
    headers = [str(c).strip() for c in df.columns.tolist()]
    rows: list[list[str]] = []

    for _, record in df.iterrows():
        row = ["" if pd.isna(v) else str(v).strip() for v in record.tolist()]
        rows.append(row)

    transactions: list[list[str]] = []
    for row in rows:
        items: list[str] = []
        for col, raw in zip(headers, row):
            if not raw:
                continue
            if "addon" in col.lower():
                for part in raw.split(","):
                    token = part.strip()
                    if token:
                        items.append(token)
            else:
                items.append(raw)
        if items:
            transactions.append(items)

    return transactions, headers, rows


def load_csv_path(path: Path) -> tuple[list[list[str]], list[str], list[list[str]], pd.DataFrame]:
    df = pd.read_csv(path, encoding="utf-8")
    transactions, headers, rows = parse_transactions_from_dataframe(df)
    return transactions, headers, rows, df


def load_csv_text(text: str) -> tuple[list[list[str]], list[str], list[list[str]], pd.DataFrame]:
    from io import StringIO

    df = pd.read_csv(StringIO(text))
    transactions, headers, rows = parse_transactions_from_dataframe(df)
    return transactions, headers, rows, df


def eda_summary(df: pd.DataFrame, transactions: list[list[str]]) -> dict[str, Any]:
    """Exploratory stats used in project defense / dashboard."""
    item_counts: dict[str, int] = {}
    for basket in transactions:
        for item in basket:
            item_counts[item] = item_counts.get(item, 0) + 1

    top_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)[:15]
    basket_sizes = [len(t) for t in transactions]

    return {
        "transaction_count": len(transactions),
        "unique_items": len(item_counts),
        "avg_items_per_order": round(sum(basket_sizes) / len(basket_sizes), 2) if basket_sizes else 0,
        "column_count": len(df.columns),
        "columns": list(df.columns),
        "missing_cells": int(df.isna().sum().sum()),
        "top_items": [{"name": name, "count": count} for name, count in top_items],
        "preview_rows": df.fillna("").astype(str).head(50).values.tolist(),
    }
