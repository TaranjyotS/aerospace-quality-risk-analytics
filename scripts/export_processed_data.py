"""Export processed EVM and risk data as CSV files."""

from pathlib import Path

import pandas as pd

from app.evm_engine import load_evm_workbook
from app.risk_engine import default_risk_register, score_risk

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "evm_data.xlsx"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

pd.DataFrame([score_risk(risk) for risk in default_risk_register()]).to_csv(
    OUT / "risk_register_scored.csv", index=False
)
load_evm_workbook(RAW, "Sheet1").to_csv(OUT / "evm_metrics_sheet1.csv", index=False)
load_evm_workbook(RAW, "Sheet2").to_csv(OUT / "evm_metrics_sheet2.csv", index=False)
print(f"Processed files exported to {OUT}")
