from abc import ABC, abstractmethod
from typing import Any, Dict
from src.skills.base_skill import BaseSkill


class BaseAgent(ABC):

    def __init__(self, agent_config: Dict[str, Any]):
        cfg = agent_config.get("agent", {})
        self.name = cfg.get("name", "UnnamedAgent")
        self.role = cfg.get("role", "Assistant")
        self.instructions = cfg.get("system_instructions", "")
        self.skills: Dict[str, BaseSkill] = {}

    def register_skill(self, skill: BaseSkill) -> None:
        self.skills[skill.name] = skill

    def execute_skill(self, skill_name: str, **kwargs: Any) -> Dict[str, Any]:
        if skill_name not in self.skills:
            raise KeyError(f"La skill '{skill_name}' no está registrada en {self.name}.")
        return self.skills[skill_name].execute(**kwargs)

    @abstractmethod
    def process(self, input_data: Any) -> Any:
        pass