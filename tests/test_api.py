import pytest
from fastapi.testclient import TestClient

from api.main import app

SIN_LAB = {"Edad": 55, "Mujer": 1, "IMC": 31.2, "Cintura_cm": 104,
           "Presion_Sistolica": 132, "Presion_Diastolica": 82}
CON_LAB = {**SIN_LAB, "Colesterol_Total": 205, "Colesterol_HDL": 48}


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:  # el `with` dispara el lifespan (carga del modelo)
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["escenarios"] == ["sin_lab", "con_lab"]


def test_predict_sin_lab(client):
    r = client.post("/predict", json=SIN_LAB)
    assert r.status_code == 200
    d = r.json()
    assert d["escenario"] == "sin_lab"
    assert 0 <= d["probabilidad"] <= 1
    assert d["prioriza"] == (d["probabilidad"] >= d["umbral"])
    assert set(d["aportes"]) == set(SIN_LAB)


def test_predict_con_lab(client):
    d = client.post("/predict", json=CON_LAB).json()
    assert d["escenario"] == "con_lab"
    assert {"Colesterol_Total", "Colesterol_HDL"} <= set(d["aportes"])


def test_mayor_edad_mayor_probabilidad(client):
    joven = client.post("/predict", json={**SIN_LAB, "Edad": 25}).json()["probabilidad"]
    mayor = client.post("/predict", json={**SIN_LAB, "Edad": 70}).json()["probabilidad"]
    assert mayor > joven


def test_aportes_coherentes_con_probabilidad(client):
    """intercepto + suma de aportes = log-odds de la probabilidad."""
    import math
    s = app.state.servicio
    d = client.post("/predict", json=SIN_LAB).json()
    # los aportes se miden frente a una persona promedio: con z=0 queda el intercepto
    interc = s.modelos["sin_lab"].named_steps["modelo"].intercept_[0]
    logit = interc + sum(d["aportes"].values())
    assert math.isclose(1 / (1 + math.exp(-logit)), d["probabilidad"], rel_tol=1e-6)


def test_laboratorio_incompleto_422(client):
    assert client.post("/predict", json={**SIN_LAB, "Colesterol_Total": 200}).status_code == 422


def test_menor_de_edad_422(client):
    assert client.post("/predict", json={**SIN_LAB, "Edad": 15}).status_code == 422


def test_campo_faltante_422(client):
    faltante = {k: v for k, v in SIN_LAB.items() if k != "IMC"}
    assert client.post("/predict", json=faltante).status_code == 422


def test_campo_desconocido_422(client):
    assert client.post("/predict", json={**SIN_LAB, "Colesterol_total": 200}).status_code == 422


def test_advertencia_fuera_de_rango(client):
    d = client.post("/predict", json={**SIN_LAB, "IMC": 75}).json()
    assert any("IMC" in a for a in d["advertencias"])


def test_model_info(client):
    d = client.get("/model/info").json()
    assert "curva_captura" not in d["sin_lab"]
    assert d["sin_lab"]["metricas_prueba"]["recall_40"] > 0


# ---------------------------------------------------------------- lotes (Alix)
def _lote(n=10, con_lab=False):
    base = CON_LAB if con_lab else SIN_LAB
    return [{**base, "Edad": 20 + 6 * i, "Id": f"p{i}"} for i in range(n)]


def test_batch_ranking_y_recorte_40(client):
    r = client.post("/predict/batch", json={"perfiles": _lote(10)})
    assert r.status_code == 200
    d = r.json()
    assert d["n"] == 10 and d["n_priorizados_lote"] == 4
    probs = [x["probabilidad"] for x in d["resultados"]]
    assert probs == sorted(probs, reverse=True)
    assert [x["posicion"] for x in d["resultados"]] == list(range(1, 11))
    assert sum(x["prioriza_lote"] for x in d["resultados"]) == 4
    assert d["resultados"][0]["id"] == "p9"  # el de mayor edad queda primero


def test_batch_coincide_con_predict_individual(client):
    d = client.post("/predict/batch", json={"perfiles": _lote(3)}).json()
    for x in d["resultados"]:
        individual = client.post("/predict", json={k: v for k, v in _lote(3)[x["fila"] - 1].items() if k != "Id"}).json()
        assert abs(individual["probabilidad"] - x["probabilidad"]) < 1e-9


def test_batch_con_lab_auto(client):
    assert client.post("/predict/batch", json={"perfiles": _lote(5, True)}).json()["escenario"] == "con_lab"


def test_batch_mezcla_lab_422(client):
    perfiles = _lote(4) + _lote(2, True)
    assert client.post("/predict/batch", json={"perfiles": perfiles}).status_code == 422


def test_batch_vacio_422(client):
    assert client.post("/predict/batch", json={"perfiles": []}).status_code == 422


def test_batch_csv(client):
    import io
    import pandas as pd
    csv = pd.DataFrame(_lote(10)).drop(columns=["Id"]).assign(Id=range(100, 110)).to_csv(index=False)
    r = client.post("/predict/batch/csv", files={"archivo": ("lista.csv", io.BytesIO(csv.encode()), "text/csv")})
    assert r.status_code == 200
    assert r.json()["resultados"][0]["id"] == "109"


def test_batch_csv_fila_invalida(client):
    import io
    import pandas as pd
    df = pd.DataFrame(_lote(3)).drop(columns=["Id"])
    df.loc[1, "Edad"] = 10
    r = client.post("/predict/batch/csv", files={"archivo": ("l.csv", io.BytesIO(df.to_csv(index=False).encode()), "text/csv")})
    assert r.status_code == 422
    assert "fila 2" in str(r.json())
