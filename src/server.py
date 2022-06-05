from save import Save
from fastapi import FastAPI

try:
    from .JsonFile import JsonFile
except ImportError:
    from JsonFile import JsonFile

# very simple rest api built using FAST API
app = FastAPI()

saves: dict[str, Save] = {}

# API Storage
save_file = JsonFile("../save.json")


# Get the save with the given name
@app.get("/save", response_model=Save)
async def save(name: str):
    return saves[name]


# Post a save to the API storage
@app.post("/save", response_model=Save)
async def save_post(_save: Save):
    saves[_save.name] = _save
    save_file.write(_save.to_json())
    return _save
