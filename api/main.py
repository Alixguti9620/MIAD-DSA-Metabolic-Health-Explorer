"""API de inferencia de Metabolic Health Explorer.

Desde la raíz del repositorio:

    uvicorn api.main:app --reload

Documentación interactiva en http://127.0.0.1:8000/docs
"""
from contextlib import asynccontextmanager

import io

import pandas as pd
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from .schemas import Lote, Perfil, PerfilLote, Prediccion, PrediccionLote
from .servicio import Servicio


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.servicio = Servicio()  # si el modelo no carga, la API no arranca
    yield


app = FastAPI(
    title="Metabolic Health Explorer API",
    description="Prioriza adultos para tamizaje de diabetes/prediabetes con regresión logística (con splines e interacción en el escenario sin laboratorio). "
                "No es un dispositivo de diagnóstico.",
    version="0.5.0",
    lifespan=lifespan,
)


app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET", "POST"], allow_headers=["*"])


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


# ---------------------------------------------------------------- lotes (Alix)
def _escenario_lote(perfiles: list[PerfilLote], pedido: str) -> str:
    con_lab = sum(p.Colesterol_Total is not None for p in perfiles)
    if pedido == "con_lab" and con_lab != len(perfiles):
        raise HTTPException(422, "Escenario con_lab: todas las filas necesitan Colesterol_Total y Colesterol_HDL.")
    if pedido != "auto":
        return pedido
    if con_lab in (0, len(perfiles)):
        return "con_lab" if con_lab else "sin_lab"
    raise HTTPException(422, "Hay filas con y sin colesterol. Completa el laboratorio en todas, o pide "
                             "escenario=sin_lab para ignorarlo.")


def _ranking(request: Request, perfiles: list[PerfilLote], pedido: str):
    esc = _escenario_lote(perfiles, pedido)
    return request.app.state.servicio.predecir_lote(esc, [p.model_dump() for p in perfiles])


@app.post("/predict/batch", response_model=PrediccionLote)
def predict_batch(lote: Lote, request: Request):
    """Ranking de una lista de perfiles en JSON."""
    return _ranking(request, lote.perfiles, lote.escenario)


@app.post("/predict/batch/csv", response_model=PrediccionLote)
async def predict_batch_csv(request: Request, archivo: UploadFile = File(...), escenario: str = "auto"):
    """Ranking de una lista cargada como CSV. Columnas: las del perfil y, opcional, Id."""
    if escenario not in ("auto", "sin_lab", "con_lab"):
        raise HTTPException(422, "escenario debe ser auto, sin_lab o con_lab")
    try:
        df = pd.read_csv(io.BytesIO(await archivo.read()))
    except Exception:
        raise HTTPException(422, "No se pudo leer el archivo como CSV.")
    if df.empty:
        raise HTTPException(422, "El CSV no tiene filas.")
    if len(df) > 20000:
        raise HTTPException(422, "Máximo 20.000 filas por archivo.")
    perfiles, errores = [], []
    for i, fila in enumerate(df.to_dict("records"), start=1):
        fila = {k: (None if pd.isna(v) else v) for k, v in fila.items()}
        if fila.get("Id") is not None:
            fila["Id"] = str(fila["Id"])
        try:
            perfiles.append(PerfilLote(**fila))
        except ValidationError as e:
            errores.append(f"fila {i}: " + "; ".join(f"{'.'.join(map(str, x['loc']))}: {x['msg']}" for x in e.errors()))
    if errores:
        raise HTTPException(422, {"mensaje": f"{len(errores)} fila(s) inválidas", "errores": errores[:20]})
    return _ranking(request, perfiles, escenario)
