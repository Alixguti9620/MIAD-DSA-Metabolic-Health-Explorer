"""API de inferencia de Metabolic Health Explorer.

Desde la raíz del repositorio:

    uvicorn api.main:app --reload

Documentación interactiva en http://127.0.0.1:8000/docs
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from .schemas import Perfil, Prediccion
from .servicio import Servicio


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.servicio = Servicio()  # si el modelo no carga, la API no arranca
    yield


app = FastAPI(
    title="Metabolic Health Explorer API",
    description="Prioriza adultos para tamizaje de diabetes/prediabetes con regresión logística. "
                "No es un dispositivo de diagnóstico.",
    version="0.3.0",
    lifespan=lifespan,
)


@app.get("/health")
def health(request: Request):
    s: Servicio = request.app.state.servicio
    return {"status": "ok", "version_modelo": s.version, "escenarios": list(s.modelos)}


@app.post("/predict", response_model=Prediccion)
def predict(perfil: Perfil, request: Request):
    s: Servicio = request.app.state.servicio
    return s.predecir(perfil.escenario, perfil.model_dump())


@app.get("/model/info")
def model_info(request: Request):
    return request.app.state.servicio.info()
