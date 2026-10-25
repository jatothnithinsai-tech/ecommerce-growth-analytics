from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def config():
    path = ROOT / "config.json"
    if not path.exists():
        raise SystemExit("Copy config.example.json to config.json and fill in your account values.")
    return json.loads(path.read_text())
