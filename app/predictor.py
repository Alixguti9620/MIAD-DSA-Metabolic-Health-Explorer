"""Capa de predicción del tablero.

Todo lo que el tablero necesita del modelo pasa por `predecir()`. Cuando exista la
API (entrega siguiente), solo hay que cambiar el cuerpo de esta función por una
llamada HTTP; el resto del tablero no se toca.
"""
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


def predecir(escenario, perfil):
    """Probabilidad de un perfil y explicación de qué variables pesaron.

    escenario: "sin_lab" o "con_lab".
    perfil: diccionario {variable: valor} con las variables del escenario.
    """
    modelos, meta = cargar_modelos()
    modelo, info = modelos[escenario], meta[escenario]
    variables = info["variables"]

    fila = pd.DataFrame([{v: perfil[v] for v in variables}])
    probabilidad = float(modelo.predict_proba(fila)[0, 1])

    # aporte de cada variable al resultado (en escala log-odds), respecto a una persona promedio
    escalador = modelo.named_steps["escalar"]
    coef = modelo.named_steps["modelo"].coef_[0]
    z = (fila.values[0] - escalador.mean_) / escalador.scale_
    aportes = dict(zip(variables, (coef * z).tolist()))

    return {
        "probabilidad": probabilidad,
        "umbral": info["umbral"],
        "prioriza": probabilidad >= info["umbral"],
        "aportes": aportes,
    }
