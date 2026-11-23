"""Contratos de entrada y salida de la API."""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Escenario = Literal["sin_lab", "con_lab"]


class Perfil(BaseModel):
    """Perfil de un adulto. Los nombres de campo son los mismos que usa el modelo.

    Si se envían los dos colesterol se usa el escenario `con_lab`; si no se envía
    ninguno, `sin_lab`. Enviar solo uno es un error.
    """
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={"examples": [
            {"Edad": 55, "Mujer": 1, "IMC": 31.2, "Cintura_cm": 104,
             "Presion_Sistolica": 132, "Presion_Diastolica": 82},
            {"Edad": 55, "Mujer": 1, "IMC": 31.2, "Cintura_cm": 104,
             "Presion_Sistolica": 132, "Presion_Diastolica": 82,
             "Colesterol_Total": 205, "Colesterol_HDL": 48},
        ]},
    )

    Edad: float = Field(ge=18, le=120, description="Años cumplidos (el modelo solo aplica a adultos)")
    Mujer: int = Field(ge=0, le=1, description="1 = mujer, 0 = hombre")
    IMC: float = Field(ge=10, le=80, description="kg/m²")
    Cintura_cm: float = Field(ge=40, le=200)
    Presion_Sistolica: float = Field(ge=60, le=260, description="mmHg")
    Presion_Diastolica: float = Field(ge=30, le=150, description="mmHg")
    Colesterol_Total: float | None = Field(None, ge=80, le=500, description="mg/dL")
    Colesterol_HDL: float | None = Field(None, ge=10, le=150, description="mg/dL")

    @model_validator(mode="after")
    def laboratorio_completo(self):
        if (self.Colesterol_Total is None) != (self.Colesterol_HDL is None):
            raise ValueError("Envía Colesterol_Total y Colesterol_HDL juntos, o ninguno de los dos.")
        return self

    @property
    def escenario(self) -> Escenario:
        return "sin_lab" if self.Colesterol_Total is None else "con_lab"


class Prediccion(BaseModel):
    escenario: Escenario
    probabilidad: float = Field(description="Probabilidad estimada de diabetes o prediabetes reportada")
    umbral: float = Field(description="Probabilidad que deja al 40 % de los adultos por encima")
    prioriza: bool = Field(description="True si la probabilidad >= umbral")
    aportes: dict[str, float] = Field(description="Aporte de cada variable en log-odds, frente a una persona promedio")
    advertencias: list[str] = Field(description="Valores fuera del rango p1-p99 de entrenamiento")
    version_modelo: str = Field(description="commit@fecha de entrenamiento")
    tipo_modelo: str = Field(description="logistica o splines_interaccion")


# ---------------------------------------------------------------- lotes (Alix)
# Priorización de una lista de personas. Se agrega sobre la API de Antonio sin
# modificar sus contratos anteriores.
class PerfilLote(Perfil):
    """Perfil con un identificador opcional para reconocer a la persona en el ranking."""
    Id: str | None = Field(None, max_length=60, description="Identificador opcional (se devuelve igual)")


class Lote(BaseModel):
    perfiles: list[PerfilLote] = Field(min_length=1, max_length=20000)
    escenario: Literal["auto", "sin_lab", "con_lab"] = Field(
        "auto", description="auto: con_lab si todos traen colesterol, sin_lab si ninguno lo trae")


class ResultadoLote(BaseModel):
    posicion: int = Field(description="1 = mayor probabilidad del lote")
    fila: int = Field(description="Número de fila en la lista enviada (desde 1)")
    id: str | None
    probabilidad: float
    prioriza_lote: bool = Field(description="Está dentro del 40 % con mayor probabilidad de ESTA lista")
    prioriza_umbral: bool = Field(description="Probabilidad >= umbral poblacional del modelo")
    advertencias: list[str]


class PrediccionLote(BaseModel):
    escenario: Escenario
    n: int
    fraccion: float = Field(description="Fracción de la lista que se marca como priorizada")
    n_priorizados_lote: int
    n_priorizados_umbral: int
    umbral: float
    version_modelo: str
    resultados: list[ResultadoLote] = Field(description="Ordenados de mayor a menor probabilidad")
