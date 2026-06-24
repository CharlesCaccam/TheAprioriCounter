"""Apriori association-rule mining (model training / inference)."""

from __future__ import annotations

from typing import Any

import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder


def train_apriori(
    transactions: list[list[str]],
    min_support: float = 0.02,
    min_confidence: float = 0.30,
    min_lift: float = 1.0,
    max_len: int = 3,
) -> dict[str, Any]:
    """
    Train (fit) Apriori on transaction data and return association rules.

    In market-basket analysis, "training" means discovering frequent itemsets
    and generating rules — there is no labeled target variable.
    """
    if not transactions:
        return {"frequent_itemsets": [], "rules": [], "metrics": {}}

    encoder = TransactionEncoder()
    encoded = encoder.fit(transactions).transform(transactions)
    df = pd.DataFrame(encoded, columns=encoder.columns_)

    frequent = apriori(df, min_support=min_support, use_colnames=True, max_len=max_len)
    if frequent.empty:
        return {
            "frequent_itemsets": [],
            "rules": [],
            "metrics": {"rule_count": 0, "top_lift": None},
        }

    rules_df = association_rules(
        frequent,
        metric="confidence",
        min_threshold=min_confidence,
    )
    rules_df = rules_df[rules_df["lift"] >= min_lift]
    rules_df = rules_df.sort_values("lift", ascending=False)

    frequent_out = [
        {
            "items": sorted(list(row["itemsets"])),
            "support": float(row["support"]),
        }
        for _, row in frequent.iterrows()
    ]

    rules_out = [
        {
            "antecedent": sorted(list(row["antecedents"])),
            "consequent": sorted(list(row["consequents"])),
            "support": float(row["support"]),
            "confidence": float(row["confidence"]),
            "lift": float(row["lift"]),
        }
        for _, row in rules_df.iterrows()
    ]

    top_lift = rules_out[0]["lift"] if rules_out else None
    return {
        "frequent_itemsets": frequent_out,
        "rules": rules_out,
        "metrics": {
            "rule_count": len(rules_out),
            "frequent_itemset_count": len(frequent_out),
            "top_lift": top_lift,
            "hyperparameters": {
                "min_support": min_support,
                "min_confidence": min_confidence,
                "min_lift": min_lift,
                "max_len": max_len,
            },
        },
    }
