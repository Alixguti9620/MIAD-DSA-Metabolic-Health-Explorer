"""Experimentos de modelado registrados en MLflow, con búsqueda de hiperparámetros.

Uso, desde la raíz del repositorio:
    MLFLOW_TRACKING_URI=http://<IP_EC2>:5000 python src/experimentos_mlflow.py
Si no se define MLFLOW_TRACKING_URI se registra en una base SQLite local (mlflow.db).

Diseño (responde a la retroalimentación de la entrega 2):
  * Partición estratificada 60 / 20 / 20: entrenamiento, validación y prueba (semilla 7).
  * Los hiperparámetros se buscan SOLO con validación cruzada de 5 pliegues dentro del
    entrenamiento, optimizando recall@40 % (la métrica del proyecto).
  * Cada modelo se evalúa en entrenamiento, validación y prueba. La prueba no se usa para elegir.
  * Cada corrida registra: espacio de búsqueda, mejores parámetros, tabla completa de la
    búsqueda (cv_results.csv), métricas de los 3 conjuntos y el modelo.
  * Se corre para los dos escenarios (sin y con laboratorio).
"""
import os
import subprocess
import tempfile
from pathlib import Path

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from scipy.stats import loguniform, randint
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, make_scorer, roc_auc_score
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures, SplineTransformer, StandardScaler

import entrenar_modelos as em

SEMILLA = em.SEMILLA
EXPERIMENTO = os.environ.get("MLFLOW_EXPERIMENT", "MIAD-Metabolic-Health-Explorer-final")
recall_40 = em.recall_al_k
scorer_r40 = make_scorer(recall_40, response_method="predict_proba")


def pipeline_logistica(C=1.0):
    return Pipeline([("imputar", SimpleImputer(strategy="median")), ("escalar", StandardScaler()),
                     ("modelo", LogisticRegression(class_weight="balanced", C=C, max_iter=1000))])


def pipeline_splines(columnas, C=1.0, n_knots=5):
    """Splines en edad y cintura + interacción edad x cintura (cuaderno 07/08)."""
    spl = ["Edad", "Cintura_cm"]
    lineales = [c for c in columnas if c not in spl]
    return Pipeline([
        ("preparar", ColumnTransformer([
            ("splines", Pipeline([("imputar", SimpleImputer(strategy="median")),
                                  ("spline", SplineTransformer(n_knots=n_knots, degree=3))]), spl),
            ("lineales", Pipeline([("imputar", SimpleImputer(strategy="median")),
                                   ("escalar", StandardScaler())]), lineales),
            ("interaccion", Pipeline([("imputar", SimpleImputer(strategy="median")), ("escalar", StandardScaler()),
                                      ("producto", PolynomialFeatures(degree=2, interaction_only=True,
                                                                      include_bias=False))]), spl),
        ])),
        ("modelo", LogisticRegression(class_weight="balanced", C=C, max_iter=2000)),
    ])


def definir_modelos(variables):
    """Devuelve {nombre: (estimador, búsqueda o None, espacio de búsqueda)}."""
    return {
        "Referencia_solo_edad": (None, None, {}),
        "Logistica": (pipeline_logistica(), "grid", {"modelo__C": [0.01, 0.1, 1, 10]}),
        "Logistica_splines_interaccion": (
            pipeline_splines(variables), "grid",
            {"modelo__C": [0.01, 0.1, 1, 10], "preparar__splines__spline__n_knots": [3, 4, 5, 7]}),
        "HistGradientBoosting": (
            HistGradientBoostingClassifier(class_weight="balanced", random_state=SEMILLA), "random",
            {"learning_rate": loguniform(0.01, 0.3), "max_iter": randint(50, 400), "max_depth": [2, 3, 4, None],
             "min_samples_leaf": randint(20, 200), "l2_regularization": loguniform(1e-3, 10)}),
    }


def metricas(y, p, prefijo):
    return {f"{prefijo}_recall_40": float(recall_40(y, p)), f"{prefijo}_roc_auc": float(roc_auc_score(y, p)),
            f"{prefijo}_pr_auc": float(average_precision_score(y, p))}


def commit():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=em.RAIZ, capture_output=True,
                              text=True, timeout=5).stdout.strip() or "sin_git"
    except Exception:
        return "sin_git"


def correr():
    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", f"sqlite:///{em.RAIZ / 'mlflow.db'}"))
    mlflow.set_experiment(EXPERIMENTO)
    adultos = em.cargar_adultos()
    y = adultos["Diabetes"]
    cv = StratifiedKFold(5, shuffle=True, random_state=SEMILLA)
    sha = commit()
    resumen = []
    for escenario, variables in em.ESCENARIOS.items():
        X = adultos[variables]
        X_tmp, X_te, y_tmp, y_te = train_test_split(X, y, test_size=0.20, stratify=y, random_state=SEMILLA)
        X_tr, X_va, y_tr, y_va = train_test_split(X_tmp, y_tmp, test_size=0.25, stratify=y_tmp, random_state=SEMILLA)
        for nombre, (est, tipo, espacio) in definir_modelos(variables).items():
            with mlflow.start_run(run_name=f"{nombre}__{escenario}"):
                params = {"modelo": nombre, "escenario": escenario, "variables": ",".join(variables),
                          "semilla": SEMILLA, "particion": "60/20/20", "n_train": len(X_tr),
                          "n_validacion": len(X_va), "n_prueba": len(X_te), "metrica_busqueda": "recall@40%"}
                if est is None:  # referencia: la edad como puntaje
                    puntajes = {k: X_k["Edad"].values for k, X_k in (("train", X_tr), ("val", X_va), ("test", X_te))}
                    modelo = None
                else:
                    params["tipo_busqueda"] = {"grid": "GridSearchCV", "random": "RandomizedSearchCV (30 iter)"}[tipo]
                    params["espacio_busqueda"] = str({k: (v if isinstance(v, list) else type(v.dist).__name__)
                                                      for k, v in espacio.items()})
                    busqueda = (GridSearchCV(est, espacio, scoring=scorer_r40, cv=cv, n_jobs=-1) if tipo == "grid" else
                                RandomizedSearchCV(est, espacio, n_iter=30, scoring=scorer_r40, cv=cv,
                                                   random_state=SEMILLA, n_jobs=-1))
                    busqueda.fit(X_tr, y_tr)
                    modelo = busqueda.best_estimator_
                    params.update({f"mejor_{k}": v for k, v in busqueda.best_params_.items()})
                    with tempfile.TemporaryDirectory() as d:
                        ruta = Path(d) / "cv_results.csv"
                        pd.DataFrame(busqueda.cv_results_).sort_values("rank_test_score").to_csv(ruta, index=False)
                        mlflow.log_artifact(str(ruta))
                    mlflow.log_metric("cv_recall_40", float(busqueda.best_score_))
                    puntajes = {k: modelo.predict_proba(X_k)[:, 1] for k, X_k in (("train", X_tr), ("val", X_va), ("test", X_te))}
                mlflow.log_params(params)
                m = {}
                for k, y_k in (("train", y_tr), ("val", y_va), ("test", y_te)):
                    m.update(metricas(y_k, puntajes[k], k))
                mlflow.log_metrics(m)
                mlflow.set_tags({"dataset": "NHANES_2013_2014_consolidado", "git_commit": sha,
                                 "origen": "src/experimentos_mlflow.py"})
                if modelo is not None:
                    mlflow.sklearn.log_model(modelo, "modelo", serialization_format="cloudpickle")
                resumen.append({"escenario": escenario, "modelo": nombre, **{k: round(v, 3) for k, v in m.items() if "recall" in k}})
                print(resumen[-1])
    print("\n" + pd.DataFrame(resumen).to_string(index=False))


if __name__ == "__main__":
    correr()
