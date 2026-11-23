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
        # (sirve para la logística simple y para la de splines; ver src/entrenar_modelos.py)
        aportes = em.aportes(modelo, info, fila)

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
            "tipo_modelo": info["tipo_modelo"],
        }

    def predecir_lote(self, escenario: str, perfiles: list[dict]) -> dict:
        """Ranking de una lista de personas. Marca al 40 % con mayor probabilidad del lote
        y, aparte, a quienes superan el umbral poblacional del modelo."""
        modelo, info = self.modelos[escenario], self.meta[escenario]
        variables = info["variables"]
        X = pd.DataFrame([{v: p[v] for v in variables} for p in perfiles])
        prob = modelo.predict_proba(X)[:, 1]
        n = len(prob)
        n_top = int(np.ceil(self.meta["fraccion_priorizada"] * n))
        orden = np.argsort(-prob, kind="stable")
        filas = []
        for pos, i in enumerate(orden, start=1):
            p = perfiles[i]
            filas.append({
                "posicion": pos, "fila": int(i) + 1, "id": p.get("Id"),
                "probabilidad": float(prob[i]),
                "prioriza_lote": pos <= n_top,
                "prioriza_umbral": bool(prob[i] >= info["umbral"]),
                "advertencias": [
                    f"{v}={p[v]:g} fuera de rango de entrenamiento ({info['rangos'][v]['p1']:g} a {info['rangos'][v]['p99']:g})"
                    for v in variables if not info["rangos"][v]["p1"] <= p[v] <= info["rangos"][v]["p99"]],
            })
        return {
            "escenario": escenario, "n": n, "fraccion": self.meta["fraccion_priorizada"],
            "n_priorizados_lote": n_top,
            "n_priorizados_umbral": int((prob >= info["umbral"]).sum()),
            "umbral": info["umbral"], "version_modelo": self.version, "resultados": filas,
        }

    def info(self) -> dict:
        """Metadatos del modelo sin la curva de captura (que es voluminosa)."""
        salida = {k: v for k, v in self.meta.items() if k not in em.ESCENARIOS}
        for esc in em.ESCENARIOS:
            salida[esc] = {k: v for k, v in self.meta[esc].items() if k not in ("curva_captura", "explicacion")}
        return salida
