from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Entry(BaseModel):
    date: str  # YYYY-MM-DD
    text: str

ENTRIES_FILE = "entries.json"

def load_entries() -> List[Entry]:
    if not os.path.exists(ENTRIES_FILE):
        return []
    with open(ENTRIES_FILE, "r") as f:
        try:
            data = json.load(f)
            return [Entry(**item) for item in data]
        except json.JSONDecodeError:
            return []

def save_entries(entries: List[Entry]):
    with open(ENTRIES_FILE, "w") as f:
        json.dump([entry.dict() for entry in entries], f, indent=2)

entries: List[Entry] = load_entries()

@app.get("/")
def read_root():
    return {"message": "One Line a Day API is working!"}

@app.post("/entries")
def add_entry(entry: Entry):
    for e in entries:
        if e.date == entry.date:
            raise HTTPException(status_code=400, detail="Entry for this date already exists.")
    entries.append(entry)
    save_entries(entries)
    return {"message": "Entry added."}

@app.get("/entries", response_model=List[Entry])
def get_entries():
    return entries