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
