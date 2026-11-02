import json
from pathlib import Path
from typing import Any, Dict
import yaml


class ConfigLoader:

    @staticmethod
    def load_from_json(file_path: str) -> Dict[str, Any]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Archivo JSON no encontrado: {file_path}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def load_from_yaml(file_path: str) -> Dict[str, Any]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Archivo YAML no encontrado: {file_path}")
        with open(path, "r", encoding="utf-8") as f:
            raw_yaml = yaml.safe_load(f)

        status_mapping = {}
        for canonical, aliases in raw_yaml.get("estados_equivalentes", {}).items():
            for alias in aliases:
                status_mapping[alias.lower()] = canonical

        type_mapping = {}
        for canonical, aliases in raw_yaml.get("tipos_movimiento", {}).items():
            for alias in aliases:
                type_mapping[alias.lower()] = canonical

        return {
            "supported_currencies": raw_yaml.get("monedas_permitidas", []),
            "default_currency": raw_yaml.get("moneda_por_defecto", "USD"),
            "status_mapping": status_mapping,
            "type_mapping": type_mapping,
            "date_formats": raw_yaml.get("formatos_fecha_admitidos", []),
        }

    @classmethod
    def load(cls, file_path: str) -> Dict[str, Any]:
        if file_path.endswith(".yaml") or file_path.endswith(".yml"):
            return cls.load_from_yaml(file_path)
        elif file_path.endswith(".json"):
            return cls.load_from_json(file_path)
        raise ValueError("Formato no soportado (se requiere .json o .yaml/.yml)")
