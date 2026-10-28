"""API MaintAI : expose le modèle de prédiction de panne.

Lancement : uvicorn maintai.api.main:app --reload
"""
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, HTTPException

from maintai import __version__
from maintai.api.schemas import HealthOut, PredictionOut, SensorReading
from maintai.config import get_settings
from maintai.predict import Predictor

state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Le modèle est chargé une seule fois, au démarrage, et non à chaque requête
    try:
        state["predictor"] = Predictor.load(get_settings())
    except FileNotFoundError:
        state["predictor"] = None  # l'API démarre quand même ; /health le signale
    yield
    state.clear()


app = FastAPI(
    title="MaintAI API",
    version=__version__,
    description="Prédiction de panne à partir de relevés de capteurs.",
    lifespan=lifespan,
)

router = APIRouter(prefix="/v1")


@app.get("/health", response_model=HealthOut)
def health() -> HealthOut:
    return HealthOut(status="ok", model_loaded=state.get("predictor") is not None)


@router.post("/predict", response_model=PredictionOut)
def predict(reading: SensorReading) -> PredictionOut:
    predictor = state.get("predictor")
    if predictor is None:
        raise HTTPException(status_code=503, detail="Modèle non chargé")
    return predictor.predict(reading.model_dump())


app.include_router(router)