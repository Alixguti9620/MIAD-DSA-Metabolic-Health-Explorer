"""Experimento de robustez: logística simple frente a splines con interacción, en 20 particiones.

Responde a la retroalimentación de la entrega 2: si los splines con interacción cumplen la meta
(recall@40 % >= 75 %) en más particiones que la logística simple, la evidencia los favorece.

Uso, desde la raíz del repositorio:
    MLFLOW_TRACKING_URI=http://<IP_EC2>:<puerto> python src/experimentos_robustez.py
Sin la variable se registra en una base SQLite local (mlflow.db, no se sube a git).

Diseño:
  * 20 semillas (0 a 19). En cada una: partición estratificada 80/20 (entrenamiento / prueba), igual a
    la del modelo servido.
  * Los hiperparámetros de cada modelo se buscan DENTRO del entrenamiento (validación cruzada de 5
    pliegues, métrica recall@40 %). La prueba solo se usa para evaluar.
  * Se evalúa en entrenamiento y en prueba. Se compara cada modelo con la edad sola y se hace una
    comparación pareada (misma partición) entre splines con interacción y logística simple.
  * Se prueba con y sin pesos de clase: el ranking casi no cambia, pero la probabilidad que muestra
    el simulador sí (con pesos sale inflada).
"""
import os
import tempfile
from pathlib import Path

import mlflow
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, make_scorer, roc_auc_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures, SplineTransformer, StandardScaler

import entrenar_modelos as em

N_SEMILLAS = int(os.environ.get("N_SEMILLAS", 20))
META = em.META
EXPERIMENTO = os.environ.get("MLFLOW_EXPERIMENT", "MIAD-Metabolic-Health-Explorer-robustez")
scorer_r40 = make_scorer(em.recall_al_k, response_method="predict_proba")


def logistica(pesos):
    return Pipeline([("imputar", SimpleImputer(strategy="median")), ("escalar", StandardScaler()),
                     ("modelo", LogisticRegression(class_weight=pesos, max_iter=2000))])


def splines(columnas, pesos):
    """Splines en edad y cintura, resto lineal, e interacción edad x cintura."""
    spl = ["Edad", "Cintura_cm"]
    lineales = [c for c in columnas if c not in spl]
    return Pipeline([
        ("preparar", ColumnTransformer([
            ("splines", Pipeline([("imputar", SimpleImputer(strategy="median")),
                                  ("spline", SplineTransformer(n_knots=5, degree=3))]), spl),
            ("lineales", Pipeline([("imputar", SimpleImputer(strategy="median")),
                                   ("escalar", StandardScaler())]), lineales),
            ("interaccion", Pipeline([("imputar", SimpleImputer(strategy="median")), ("escalar", StandardScaler()),
                                      ("producto", PolynomialFeatures(degree=2, interaction_only=True,
                                                                      include_bias=False))]), spl),
        ])),
        ("modelo", LogisticRegression(class_weight=pesos, max_iter=3000)),
    ])


GRID_C = {"modelo__C": [0.01, 0.1, 1, 10]}
GRID_SPL = {"modelo__C": [0.01, 0.1, 1, 10], "preparar__splines__spline__n_knots": [3, 4, 5, 7]}


def modelos(variables):
    """{nombre: (estimador, rejilla)}. La referencia (edad sola) no tiene estimador."""
    return {
        "Edad_sola": (None, None),
        "Logistica_sin_pesos": (logistica(None), GRID_C),
        "Logistica_con_pesos": (logistica("balanced"), GRID_C),
        "Splines_interaccion_sin_pesos": (splines(variables, None), GRID_SPL),
        "Splines_interaccion_con_pesos": (splines(variables, "balanced"), GRID_SPL),
    }


def una_particion(adultos, variables, semilla):
    """Devuelve {modelo: {métricas}} para una semilla."""
    X, y = adultos[variables], adultos["Diabetes"]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.20, stratify=y, random_state=semilla)
    cv = StratifiedKFold(5, shuffle=True, random_state=semilla)
    salida = {}
    for nombre, (est, rejilla) in modelos(variables).items():
        if est is None:
            p_tr, p_te, mejor = X_tr["Edad"].values, X_te["Edad"].values, {}
        else:
            g = GridSearchCV(est, rejilla, scoring=scorer_r40, cv=cv, n_jobs=-1).fit(X_tr, y_tr)
            p_tr, p_te = g.predict_proba(X_tr)[:, 1], g.predict_proba(X_te)[:, 1]
            mejor = g.best_params_
        salida[nombre] = {
            "semilla": semilla, "recall_40_train": em.recall_al_k(y_tr, p_tr),
            "recall_40_test": em.recall_al_k(y_te, p_te), "roc_auc_test": roc_auc_score(y_te, p_te),
            "pr_auc_test": average_precision_score(y_te, p_te), "mejores_parametros": str(mejor),
        }
    return salida


def comparar_pareado(tabla, a, b):
    """Compara dos modelos sobre las mismas particiones: (promedio de la diferencia, victorias, empates, derrotas, p)."""
    x = tabla[tabla.modelo == a].sort_values("semilla")["recall_40_test"].values
    z = tabla[tabla.modelo == b].sort_values("semilla")["recall_40_test"].values
    d = x - z
    try:
        p = float(wilcoxon(x, z).pvalue)
    except ValueError:
        p = float("nan")
    return float(d.mean()), int((d > 1e-12).sum()), int((np.abs(d) <= 1e-12).sum()), int((d < -1e-12).sum()), p


def correr():
    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", f"sqlite:///{em.RAIZ / 'mlflow.db'}"))
    mlflow.set_experiment(EXPERIMENTO)
    adultos = em.cargar_adultos()
    sha = em._codigo_version()
    resumen, comparaciones = [], []
    for escenario, variables in em.ESCENARIOS.items():
        filas = []
        for semilla in range(N_SEMILLAS):
            for nombre, m in una_particion(adultos, variables, semilla).items():
                filas.append({"modelo": nombre, **m})
            print(f"[{escenario}] semilla {semilla} lista", flush=True)
        tabla = pd.DataFrame(filas)
        edad = tabla[tabla.modelo == "Edad_sola"].set_index("semilla")["recall_40_test"]
        for nombre, g in tabla.groupby("modelo", sort=False):
            r = g.set_index("semilla")["recall_40_test"]
            agg = {"recall_40_test_media": r.mean(), "recall_40_test_desv": r.std(), "recall_40_test_min": r.min(),
                   "recall_40_test_max": r.max(), "particiones_sobre_meta": int((r >= META).sum()),
                   "recall_40_train_media": g["recall_40_train"].mean(), "roc_auc_test_media": g["roc_auc_test"].mean(),
                   "pr_auc_test_media": g["pr_auc_test"].mean(), "ganancia_vs_edad_media": (r - edad).mean(),
                   "particiones_mejor_que_edad": int((r > edad).sum())}
            with mlflow.start_run(run_name=f"{nombre}__{escenario}__{N_SEMILLAS}semillas"):
                mlflow.log_params({"modelo": nombre, "escenario": escenario, "variables": ",".join(variables),
                                   "n_semillas": N_SEMILLAS, "particion": "80/20", "meta_recall_40": META,
                                   "metrica_busqueda": "recall@40% (CV 5 pliegues dentro del entrenamiento)"})
                mlflow.log_metrics({k: float(v) for k, v in agg.items()})
                for s, v in r.items():
                    mlflow.log_metric("recall_40_test_por_semilla", float(v), step=int(s))
                mlflow.set_tags({"dataset": "NHANES_2013_2014_consolidado", "git_commit": sha,
                                 "origen": "src/experimentos_robustez.py"})
                with tempfile.TemporaryDirectory() as d:
                    ruta = Path(d) / "resultados_por_semilla.csv"
                    g.to_csv(ruta, index=False)
                    mlflow.log_artifact(str(ruta))
            resumen.append({"escenario": escenario, "modelo": nombre, **agg})
        for a, b in (("Splines_interaccion_sin_pesos", "Logistica_sin_pesos"),
                     ("Splines_interaccion_con_pesos", "Logistica_con_pesos")):
            dif, w, e, l, p = comparar_pareado(tabla, a, b)
            comparaciones.append({"escenario": escenario, "A": a, "B": b, "dif_media": dif,
                                  "A_gana": w, "empate": e, "B_gana": l, "p_wilcoxon": p})
    res = pd.DataFrame(resumen)
    cmp_ = pd.DataFrame(comparaciones)
    with pd.option_context("display.width", 250, "display.max_columns", 30):
        print(f"\n=== Resumen (recall@40 en prueba, {N_SEMILLAS} particiones) ===")
        print(res[["escenario", "modelo", "recall_40_test_media", "recall_40_test_desv", "recall_40_test_min",
                   "particiones_sobre_meta", "roc_auc_test_media", "pr_auc_test_media", "ganancia_vs_edad_media"]]
              .round(3).to_string(index=False))
        print("\n=== Comparación pareada (A frente a B) ===")
        print(cmp_.round(4).to_string(index=False))
    with mlflow.start_run(run_name=f"Comparacion_pareada__{N_SEMILLAS}semillas"):
        with tempfile.TemporaryDirectory() as d:
            for nombre, df in (("resumen.csv", res), ("comparacion_pareada.csv", cmp_)):
                (Path(d) / nombre).write_text(df.to_csv(index=False), encoding="utf-8")
                mlflow.log_artifact(str(Path(d) / nombre))
        mlflow.set_tags({"git_commit": sha, "origen": "src/experimentos_robustez.py"})
    res.to_csv(em.RAIZ / "reports" / "figures" / "robustez_splines_vs_logistica.csv", index=False)
    cmp_.to_csv(em.RAIZ / "reports" / "figures" / "robustez_comparacion_pareada.csv", index=False)


if __name__ == "__main__":
    correr()
