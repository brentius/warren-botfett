"""Config loading: config/default.yaml <- config/local.yaml <- environment (.env)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

CONFIG_DIR = Path(__file__).resolve().parents[2] / "config"


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_config(path: Path | None = None) -> dict[str, Any]:
    load_dotenv()
    cfg: dict[str, Any] = yaml.safe_load((CONFIG_DIR / "default.yaml").read_text()) or {}
    local = path or CONFIG_DIR / "local.yaml"
    if local.exists():
        cfg = _deep_merge(cfg, yaml.safe_load(local.read_text()) or {})
    return cfg
