"""FastAPI backend — serves EDA + Apriori analysis to the frontend."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .apriori_service import train_apriori
from .data_loader import DEFAULT_CSV, eda_summary, load_csv_path, load_csv_text

app = FastAPI(title="Apriori Counter API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_DIR = Path(__file__).resolve().parents[1] / "models"
MODEL_DIR.mkdir(exist_ok=True)
DEFAULT_MODEL = MODEL_DIR / "rules.json"


@app.get("/")
def root():
    return {
        "service": "Apriori Counter API",
        "health": "/api/health",
        "docs": "/docs",
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "model_exists": DEFAULT_MODEL.exists()}


@app.get("/api/sample/analyze")
def analyze_sample(
    min_support: float = 0.02,
    min_confidence: float = 0.30,
    min_lift: float = 1.0,
):
    """Run EDA + Apriori on the bundled coffee-shop dataset."""
    if not DEFAULT_CSV.exists():
        return {"error": f"Sample CSV not found at {DEFAULT_CSV}"}

    transactions, headers, rows, df = load_csv_path(DEFAULT_CSV)
    eda = eda_summary(df, transactions)
    model = train_apriori(transactions, min_support, min_confidence, min_lift)

    return {
        "source": DEFAULT_CSV.name,
        "headers": headers,
        "rows": rows,
        "eda": eda,
        "model": model,
    }


@app.post("/api/analyze")
async def analyze_upload(
    file: UploadFile = File(...),
    min_support: float = Form(0.02),
    min_confidence: float = Form(0.30),
    min_lift: float = Form(1.0),
):
    """Upload a CSV ledger and run EDA + Apriori."""
    raw = await file.read()
    text = raw.decode("utf-8", errors="replace")
    if "\ufffd" in text:
        text = raw.decode("latin-1")

    transactions, headers, rows, df = load_csv_text(text)
    eda = eda_summary(df, transactions)
    model = train_apriori(transactions, min_support, min_confidence, min_lift)

    return {
        "source": file.filename,
        "headers": headers,
        "rows": rows,
        "eda": eda,
        "model": model,
    }


@app.post("/api/train")
async def train_and_save(
    min_support: float = Form(0.02),
    min_confidence: float = Form(0.30),
    min_lift: float = Form(1.0),
    file: UploadFile | None = File(None),
):
    """Train Apriori and persist rules to backend/models/rules.json."""
    if file is not None:
        raw = await file.read()
        text = raw.decode("utf-8", errors="replace")
        transactions, _, _, df = load_csv_text(text)
        source = file.filename
    else:
        transactions, _, _, df = load_csv_path(DEFAULT_CSV)
        source = DEFAULT_CSV.name

    eda = eda_summary(df, transactions)
    model = train_apriori(transactions, min_support, min_confidence, min_lift)

    payload = {
        "source": source,
        "eda": eda,
        "model": model,
    }
    DEFAULT_MODEL.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    return {
        "message": "Model trained and saved",
        "path": str(DEFAULT_MODEL),
        "rule_count": model["metrics"]["rule_count"],
    }


@app.get("/api/model")
def get_saved_model():
    """Load the last trained model (for deployment / demo)."""
    if not DEFAULT_MODEL.exists():
        return {"error": "No trained model. POST /api/train first."}
    return json.loads(DEFAULT_MODEL.read_text(encoding="utf-8"))
