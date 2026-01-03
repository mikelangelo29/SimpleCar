# app/storage/data_store.py
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from kivymd.app import MDApp


def seed_path() -> Path:
    """
    File JSON del progetto (SEED): non va mai riscritto.
    È relativo alla cartella 'app/'.
    """
    app_dir = Path(__file__).resolve().parent.parent  # .../app
    return app_dir / "data" / "autos.json"


def live_path() -> Path:
    """
    File JSON VIVO (scrivibile): sta nella cartella dati dell'app (user_data_dir).
    """
    app = MDApp.get_running_app()
    # user_data_dir esiste sia su desktop che su Android (è la cartella dati dell'app)
    return Path(app.user_data_dir) / "autos.json"


def ensure_live_file() -> Path:
    """
    Garantisce che il file VIVO esista.
    Se non esiste, lo crea copiando il SEED (se presente), altrimenti crea struttura base.
    """
    lp = live_path()
    lp.parent.mkdir(parents=True, exist_ok=True)

    if lp.exists():
        return lp

    sp = seed_path()
    if sp.exists():
        shutil.copyfile(sp, lp)
    else:
        # fallback minimo: non deve mai crashare
        with open(lp, "w", encoding="utf-8") as f:
            json.dump({"autos": []}, f, indent=4, ensure_ascii=False)

    return lp


def load_data() -> dict:
    """
    Legge SEMPRE dal file VIVO.
    """
    lp = ensure_live_file()
    try:
        with open(lp, "r", encoding="utf-8") as f:
            return json.load(f) or {"autos": []}
    except Exception:
        return {"autos": []}


def save_data(data: dict) -> None:
    """
    Scrive SEMPRE sul file VIVO.
    """
    lp = ensure_live_file()
    with open(lp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_autos_list() -> list:
    return load_data().get("autos", []) or []


def save_autos_list(autos_lista: list) -> None:
    save_data({"autos": autos_lista})
