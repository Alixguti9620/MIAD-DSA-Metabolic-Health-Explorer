"""Carga del modelo y lógica de inferencia (sin dependencias de FastAPI)."""
import numpy as np
import pandas as pd

from src import entrenar_modelos as em


class Servicio:
    def __init__(self):
        self.modelos, self.meta = em.cargar_o_entrenar()

    @property
    def version(self) -> str:
        return f"{self.meta['version_codigo']}@{self.meta['fecha']}"

    def predecir(self, escenario: str, perfil: dict) -> dict:
        modelo, info = self.modelos[escenario], self.meta[escenario]
        variables = info["variables"]
        fila = pd.DataFrame([{v: perfil[v] for v in variables}])

        probabilidad = float(modelo.predict_proba(fila)[0, 1])

        # aporte de cada variable en log-odds, respecto a una persona promedio
        escalador = modelo.named_steps["escalar"]
        coef = modelo.named_steps["modelo"].coef_[0]
        z = (fila.values[0] - escalador.mean_) / escalador.scale_
        aportes = dict(zip(variables, (coef * z).tolist()))

        advertencias = [
            f"{v}={perfil[v]:g} está fuera del rango habitual de entrenamiento "
            f"({info['rangos'][v]['p1']:g} a {info['rangos'][v]['p99']:g}); la estimación es menos fiable."
            for v in variables
            if not info["rangos"][v]["p1"] <= perfil[v] <= info["rangos"][v]["p99"]
        ]

        return {
            "escenario": escenario,
            "probabilidad": probabilidad,
            "umbral": info["umbral"],
            "prioriza": probabilidad >= info["umbral"],
            "aportes": aportes,
            "advertencias": advertencias,
            "version_modelo": self.version,
        }

    def info(self) -> dict:
        """Metadatos del modelo sin la curva de captura (que es voluminosa)."""
        salida = {k: v for k, v in self.meta.items() if k not in em.ESCENARIOS}
        for esc in em.ESCENARIOS:
            salida[esc] = {k: v for k, v in self.meta[esc].items() if k != "curva_captura"}
        return salida
