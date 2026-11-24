"""Verifica que los CSV de ejemplo del manual de usuario funcionan contra la API."""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import app

EJEMPLOS = Path(__file__).resolve().parents[1] / "docs" / "ejemplos"


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.mark.parametrize("archivo, escenario", [
    ("lote_sin_laboratorio.csv", "sin_lab"),
    ("lote_con_laboratorio.csv", "con_lab"),
])
def test_ejemplo_del_manual(client, archivo, escenario):
    with open(EJEMPLOS / archivo, "rb") as f:
        r = client.post("/predict/batch/csv", files={"archivo": (archivo, f, "text/csv")})
    assert r.status_code == 200
    datos = r.json()
    assert datos["escenario"] == escenario
    assert datos["n"] == 5
    assert datos["n_priorizados_lote"] == 2          # 40 % de 5, redondeado hacia arriba
    probs = [x["probabilidad"] for x in datos["resultados"]]
    assert probs == sorted(probs, reverse=True)      # ranking de mayor a menor


def test_ejemplo_con_lab_forzado_sin_lab(client):
    """Con escenario=sin_lab el archivo con colesterol también se acepta."""
    with open(EJEMPLOS / "lote_con_laboratorio.csv", "rb") as f:
        r = client.post("/predict/batch/csv", params={"escenario": "sin_lab"},
                        files={"archivo": ("l.csv", f, "text/csv")})
    assert r.status_code == 200
    assert r.json()["escenario"] == "sin_lab"