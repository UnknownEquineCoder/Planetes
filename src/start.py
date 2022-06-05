from __future__ import annotations

from datetime import date

from .database import Database
from .save import Save


# Start a global database instance
def setup() -> Database:
    db = Database()
    current_save = Save(
        name="first",
        score=0,
        level=1,
        map=[line.strip() for line in open("src/graphics/level_0.txt")],
        created_at=f"{date.today()}",
    )

    db.set("current", current_save.to_json())

    return db
