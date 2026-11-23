"""Capa de predicción del tablero.

Todo lo que el tablero necesita del modelo pasa por `predecir()` y `priorizar_lote()`.
Si existe la variable de entorno API_URL (por ejemplo http://api:8000), las
predicciones se piden a la API REST. Si no existe, se usa el mismo servicio de la API
cargado en el proceso, para poder abrir el tablero sin levantar la API (desarrollo).
"""
import io
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
import entrenar_modelos as em  # noqa: E402

NOMBRES_VARIABLES = {
    "Edad": "Edad", "Mujer": "Sexo (mujer)", "IMC": "IMC", "Cintura_cm": "Cintura",
    "Presion_Sistolica": "Presión sistólica", "Presion_Diastolica": "Presión diastólica",
    "Colesterol_Total": "Colesterol total", "Colesterol_HDL": "Colesterol HDL",
}


@st.cache_resource(show_spinner="Preparando los modelos...")
def cargar_modelos():
    """Devuelve (modelos, metadatos). Entrena la primera vez si faltan los archivos."""
    return em.cargar_o_entrenar()


API_URL = os.environ.get("API_URL", "").rstrip("/")
TIEMPO_ESPERA = 60


@st.cache_resource(show_spinner=False)
def _servicio_local():
    sys.path.insert(0, str(RAIZ))
    from api.servicio import Servicio  # noqa: E402
    return Servicio()


def modo_prediccion():
    """Texto que se muestra al usuario sobre de dónde salen las predicciones."""
    return f"API en {API_URL}" if API_URL else "modelo local (sin API)"


def _post(ruta, **kwargs):
    import requests
    r = requests.post(f"{API_URL}{ruta}", timeout=TIEMPO_ESPERA, **kwargs)
    if r.status_code == 422:
        detalle = r.json().get("detail")
        raise ValueError(detalle["errores"] if isinstance(detalle, dict) else detalle)
    r.raise_for_status()
    return r.json()


def predecir(escenario, perfil):
    """Probabilidad de un perfil y explicación de qué variables pesaron.

    escenario: "sin_lab" o "con_lab".
    perfil: diccionario {variable: valor} con las variables del escenario.
    """
    if API_URL:
        return _post("/predict", json={k: (int(v) if k == "Mujer" else float(v)) for k, v in perfil.items()})
    return _servicio_local().predecir(escenario, perfil)


def priorizar_lote(df, escenario="auto"):
    """Ranking de una tabla de personas (una fila por persona).

    Devuelve el diccionario de la API (`resultados` ordenados de mayor a menor probabilidad).
    Lanza ValueError con el detalle si alguna fila no es válida.
    """
    if API_URL:
        csv = df.to_csv(index=False).encode("utf-8")
        return _post("/predict/batch/csv", params={"escenario": escenario},
                     files={"archivo": ("lista.csv", io.BytesIO(csv), "text/csv")})
    sys.path.insert(0, str(RAIZ))
    from api.schemas import PerfilLote
    from pydantic import ValidationError
    perfiles, errores = [], []
    for i, fila in enumerate(df.to_dict("records"), start=1):
        fila = {k: (None if pd.isna(v) else v) for k, v in fila.items()}
        if fila.get("Id") is not None:
            fila["Id"] = str(fila["Id"])
        try:
            perfiles.append(PerfilLote(**fila))
        except ValidationError as e:
            errores.append(f"fila {i}: " + "; ".join(f"{x['loc'][0]}: {x['msg']}" for x in e.errors()))
    if errores:
        raise ValueError(errores[:20])
    con_lab = sum(p.Colesterol_Total is not None for p in perfiles)
    if escenario == "auto":
        if con_lab not in (0, len(perfiles)):
            raise ValueError("Hay filas con y sin colesterol. Completa el laboratorio en todas o elige 'sin_lab'.")
        escenario = "con_lab" if con_lab else "sin_lab"
    return _servicio_local().predecir_lote(escenario, [p.model_dump() for p in perfiles])
