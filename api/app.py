# app.py

# TODO: importer FastAPI
from fastapi import FastAPI

# TODO: créer une instance FastAPI
app = FastAPII()

# TODO: définir une route GET /health
@app.get("/health")
def health():
    return {"status": "ok"}
