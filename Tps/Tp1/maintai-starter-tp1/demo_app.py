
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()  # L'application


class Reading(BaseModel):  # Le schéma
    temperature_c: float = Field(ge=-40, le=150)
    vibration_mm_s: float = Field(ge=0, le=100)



@app.get("/health")  # Route GET /health
def health():
    return {"status": "ok"}


@app.post("/v1/predict")  # Route POST /v1/predict
def predict(reading: Reading):  # Données automatiquement validées
    return {"alert": reading.temperature_c > 80
                    or reading.vibration_mm_s > 6}
