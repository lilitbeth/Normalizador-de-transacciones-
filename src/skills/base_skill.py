from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseSkill(ABC):
    """Contrato estándar para el desarrollo de skills del agente."""

    def __init__(self, name: str, description: str, version: str = "1.0.0"):
        self.name = name
        self.description = description
        self.version = version

    @abstractmethod
    def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """Lógica ejecutable de la habilidad."""
        pass

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
        }