from __future__ import annotations

from pydantic import BaseModel

try:
    from .type_aliases import LevelMatrix
except ImportError:
    LevelMatrix = list[str]


class Save(BaseModel):
    """
    Save class made to work with both database and API.
    Inherits from BaseModel to make it pydantic compliant.
    """
    name: str
    score: int
    level: int
    map: LevelMatrix
    created_at: str

    @property
    def pretty(self) -> str:
        return f"{self.name} {self.score} {self.level}"

    def to_json(self) -> dict:
        """
        Convert to json

        :return:
        """
        return {
            "name": self.name,
            "score": self.score,
            "level": self.level,
            "map": self.map,
            "created_at": self.created_at,
        }

    @classmethod
    def from_json(cls, json_data) -> Save:
        """
        Construct from json

        :param json_data:
        :return:
        """
        return cls(
            name=json_data["name"],
            score=json_data["score"],
            level=json_data["level"],
            map=json_data["map"],
            created_at=json_data["created_at"],
        )
