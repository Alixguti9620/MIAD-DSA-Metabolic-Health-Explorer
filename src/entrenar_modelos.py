"""Entrenamiento de los modelos del simulador (escenarios sin y con laboratorio).

Uso, desde la raíz del repositorio:

    python src/entrenar_modelos.py

Guarda en models/ los modelos (.joblib) y un archivo metadatos.json con las
métricas, el umbral y los datos que usa el tablero. Los .joblib están en el
.gitignore, así que no se suben al repo: se regeneran con este script, o el
tablero los entrena solo la primera vez que se abre.

Modelo: regresión logística SIN pesos de clase. Con pesos las probabilidades
salen infladas, y el simulador muestra una probabilidad. Ordena casi igual que
la versión con pesos de los cuadernos 07 y 08.
"""
import json
import subprocess
from datetime import date
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

RAIZ = Path(__file__).resolve().parents[1]
RUTA_DATOS = RAIZ / "data" / "raw" / "NHANES_consolidado.csv"
RUTA_MODELOS = RAIZ / "models"

SEMILLA = 7          # la misma de los cuadernos 07 y 08
FRACCION = 0.40      # se prioriza al 40 % de los adultos con mayor probabilidad
META = 0.75          # recall que se busca con esa fracción
C_REGULARIZACION = 0.1

VARS_SIN_LAB = ["Edad", "Mujer", "IMC", "Cintura_cm", "Presion_Sistolica", "Presion_Diastolica"]
VARS_CON_LAB = VARS_SIN_LAB + ["Colesterol_Total", "Colesterol_HDL"]
ESCENARIOS = {"sin_lab": VARS_SIN_LAB, "con_lab": VARS_CON_LAB}


def cargar_adultos():
    """Adultos de la base consolidada, con la misma limpieza del cuaderno 06."""
    df = pd.read_csv(RUTA_DATOS)
    adultos = df[df["Edad"] >= 18].copy()
    # presión diastólica casi 0: lectura inválida, se pasa a nulo
    adultos.loc[adultos["Presion_Diastolica"] < 1, "Presion_Diastolica"] = np.nan
    adultos["Mujer"] = (adultos["Genero"] == 2).astype(int)
    return adultos.reset_index(drop=True)


def recall_al_k(y_real, puntaje, fraccion=FRACCION):
    """De todos los casos, qué fracción queda dentro del `fraccion` con mayor puntaje."""
    y_real = np.asarray(y_real)
    n = int(np.ceil(fraccion * len(y_real)))
    orden = np.argsort(-np.asarray(puntaje), kind="stable")
    return float(y_real[orden[:n]].sum() / y_real.sum())


def curva_captura(y_real, puntaje, puntos=101):
    """Fracción de casos capturados según la fracción de población revisada."""
    y_real = np.asarray(y_real)
    orden = np.argsort(-np.asarray(puntaje), kind="stable")
    acumulado = np.cumsum(y_real[orden]) / y_real.sum()
    fracciones = np.linspace(0, 1, puntos)
    capturado = []
    for f in fracciones:
        k = int(round(f * len(y_real)))
        capturado.append(0.0 if k == 0 else float(acumulado[k - 1]))
    return fracciones.tolist(), capturado


def crear_pipeline():
    return Pipeline([
        ("imputar", SimpleImputer(strategy="median")),
        ("escalar", StandardScaler()),
        ("modelo", LogisticRegression(C=C_REGULARIZACION, max_iter=1000)),
    ])


def _codigo_version():
    try:
        salida = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ,
                                capture_output=True, text=True, timeout=5)
        return salida.stdout.strip() or "sin_git"
    except Exception:
        return "sin_git"


def entrenar_escenario(adultos, variables):
    """Entrena un escenario y devuelve (modelo, metadatos)."""
    X, y = adultos[variables], adultos["Diabetes"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=SEMILLA)

    modelo = crear_pipeline().fit(X_train, y_train)

    # umbral: probabilidad que deja al 40 % de la población por arriba, calculada
    # con predicciones fuera de muestra del entrenamiento
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEMILLA)
    oof = cross_val_predict(crear_pipeline(), X_train, y_train, cv=cv, method="predict_proba")[:, 1]
    umbral = float(np.quantile(oof, 1 - FRACCION))

    # evaluación en la prueba (se usa una sola vez)
    p_test = modelo.predict_proba(X_test)[:, 1]
    prioriza = p_test >= umbral
    tp = int((prioriza & (y_test.values == 1)).sum())
    fp = int((prioriza & (y_test.values == 0)).sum())
    fn = int((~prioriza & (y_test.values == 1)).sum())
    tn = int((~prioriza & (y_test.values == 0)).sum())

    rng = np.random.default_rng(SEMILLA)
    yv = y_test.values
    boot = [recall_al_k(yv[i], p_test[i]) for i in (rng.integers(0, len(yv), len(yv)) for _ in range(1000))]
    ic = np.percentile(boot, [2.5, 97.5]).tolist()

    x_curva, y_curva = curva_captura(y_test, p_test)
    _, y_curva_edad = curva_captura(y_test, X_test["Edad"].values)

    coef = modelo.named_steps["modelo"].coef_[0]
    meta = {
        "variables": variables,
        "umbral": umbral,
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "positivos_test": int(y_test.sum()),
        "metricas_prueba": {
            "recall_40": recall_al_k(y_test, p_test),
            "recall_40_edad_sola": recall_al_k(y_test, X_test["Edad"].values),
            "ic95_recall_40": ic,
            "roc_auc": float(roc_auc_score(y_test, p_test)),
            "pr_auc": float(average_precision_score(y_test, p_test)),
            "pct_priorizado": float(prioriza.mean()),
            "recall_con_umbral": tp / (tp + fn),
            "precision_con_umbral": tp / (tp + fp),
            "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        },
        "curva_captura": {"fraccion": x_curva, "modelo": y_curva, "edad_sola": y_curva_edad},
        "coeficientes": dict(zip(variables, coef.tolist())),
        "odds_ratio": dict(zip(variables, np.exp(coef).tolist())),
        "rangos": {v: {"min": float(adultos[v].min()), "p1": float(adultos[v].quantile(0.01)),
                       "mediana": float(adultos[v].median()), "p99": float(adultos[v].quantile(0.99)),
                       "max": float(adultos[v].max())} for v in variables},
    }
    return modelo, meta


def entrenar_todo(guardar=True):
    """Entrena los dos escenarios; si `guardar`, escribe los archivos en models/."""
    adultos = cargar_adultos()
    modelos, metadatos = {}, {
        "version_codigo": _codigo_version(),
        "fecha": date.today().isoformat(),
        "semilla": SEMILLA,
        "fraccion_priorizada": FRACCION,
        "meta_recall": META,
        "n_adultos": int(len(adultos)),
        "n_positivos": int(adultos["Diabetes"].sum()),
    }
    for nombre, variables in ESCENARIOS.items():
        modelos[nombre], metadatos[nombre] = entrenar_escenario(adultos, variables)
    if guardar:
        RUTA_MODELOS.mkdir(exist_ok=True)
        for nombre, modelo in modelos.items():
            joblib.dump(modelo, RUTA_MODELOS / f"modelo_{nombre}.joblib")
        (RUTA_MODELOS / "metadatos.json").write_text(
            json.dumps(metadatos, ensure_ascii=False, indent=2), encoding="utf-8")
    return modelos, metadatos


def cargar_o_entrenar():
    """Carga los modelos guardados; si no existen, los entrena y los guarda."""
    archivos = [RUTA_MODELOS / f"modelo_{n}.joblib" for n in ESCENARIOS] + [RUTA_MODELOS / "metadatos.json"]
    if all(a.exists() for a in archivos):
        try:
            modelos = {n: joblib.load(RUTA_MODELOS / f"modelo_{n}.joblib") for n in ESCENARIOS}
            metadatos = json.loads((RUTA_MODELOS / "metadatos.json").read_text(encoding="utf-8"))
            return modelos, metadatos
        except Exception:
            pass  # archivos de otra versión de scikit-learn: se vuelven a entrenar
    return entrenar_todo(guardar=True)


if __name__ == "__main__":
    _, meta = entrenar_todo(guardar=True)
    print(f"Adultos: {meta['n_adultos']:,} | positivos: {meta['n_positivos']:,} | semilla {meta['semilla']}")
    for nombre in ESCENARIOS:
        m = meta[nombre]["metricas_prueba"]
        print(f"\n[{nombre}] {len(meta[nombre]['variables'])} variables | umbral {meta[nombre]['umbral']:.3f}")
        print(f"  recall@40 % prueba: {m['recall_40']:.3f}  (edad sola: {m['recall_40_edad_sola']:.3f})"
              f" | IC95: {m['ic95_recall_40'][0]:.3f} a {m['ic95_recall_40'][1]:.3f}")
        print(f"  ROC-AUC {m['roc_auc']:.3f} | PR-AUC {m['pr_auc']:.3f} | priorizado {m['pct_priorizado']:.1%}")
    print(f"\nGuardado en {RUTA_MODELOS}")
