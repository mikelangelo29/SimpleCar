import json
from pathlib import Path

from app.storage.data_store import live_path


LICENSE_FILENAME = "license.json"


def license_path() -> Path:
    # stessa directory del file autos.json vivo
    return live_path().parent / LICENSE_FILENAME


def ensure_license_file() -> Path:
    lp = license_path()
    lp.parent.mkdir(parents=True, exist_ok=True)

    if lp.exists():
        return lp

    # default FREE
    with open(lp, "w", encoding="utf-8") as f:
        json.dump({"pro": False}, f, indent=4, ensure_ascii=False)

    return lp


def load_license() -> dict:
    lp = ensure_license_file()
    try:
        with open(lp, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {"pro": False}
        data.setdefault("pro", False)
        return data
    except Exception:
        return {"pro": False}


def save_license(data: dict) -> None:
    lp = ensure_license_file()
    with open(lp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def is_pro() -> bool:
    return bool(load_license().get("pro", False))


def max_cars() -> int:
    """
    FREE = 1 auto
    PRO  = 10 auto
    """
    return 10 if is_pro() else 1


def set_pro(value: bool) -> None:
    data = load_license()
    data["pro"] = bool(value)
    save_license(data)
