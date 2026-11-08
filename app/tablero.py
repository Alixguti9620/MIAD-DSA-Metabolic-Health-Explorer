"""Metabolic Health Explorer: tablero de exploración y priorización para tamizaje.

Ejecutar desde la raíz del repositorio:

    streamlit run app/tablero.py

Pantallas: Exploración, Simulador y Modelo y datos (maqueta del doc 04, opción A).
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
from predictor import NOMBRES_VARIABLES, cargar_modelos, em, predecir  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]

TEAL, CORAL, AZUL, GRIS = "#0E7C86", "#E4572E", "#2E86AB", "#64748B"
COLOR_CLASE = {"Con diabetes o prediabetes": CORAL, "Sin diabetes ni prediabetes": AZUL}

st.set_page_config(page_title="Metabolic Health Explorer", page_icon="🩺", layout="wide")

st.markdown("""
<style>
.hero {background: linear-gradient(120deg, #0E7C86 0%, #14A3B0 55%, #5BC0BE 100%); color: white;
       padding: 1.5rem 2rem; border-radius: 18px; margin-bottom: 1.3rem;}
.hero h1 {margin: 0; font-size: 2.05rem; color: white; padding: 0;}
.hero p {margin: .35rem 0 0 0; opacity: .93; font-size: 1.02rem;}
.kpi {background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; padding: 1rem 1.2rem; min-height: 132px;
      box-shadow: 0 2px 10px rgba(15,23,42,.05); height: 100%;}
.kpi .etiqueta {color: #64748B; font-size: .78rem; text-transform: uppercase; letter-spacing: .05em;}
.kpi .valor {font-size: 1.95rem; font-weight: 700; color: #0F172A; line-height: 1.25;}
.kpi .nota {color: #64748B; font-size: .84rem;}
.badge {display: inline-block; padding: .55rem 1.1rem; border-radius: 999px; font-weight: 700; font-size: 1.02rem;}
.badge-si {background: #FDE3D9; color: #B4381A;}
.badge-no {background: #DDF1EF; color: #0A5C64;}
.aviso {background: #F1F6F8; border-left: 4px solid #0E7C86; padding: .8rem 1rem; border-radius: 8px;
        color: #334155; font-size: .92rem;}
section[data-testid="stSidebar"] {border-right: 1px solid #E2E8F0;}
.tabla {width: 100%; border-collapse: collapse; font-size: .92rem; margin: .3rem 0 .8rem 0;}
.tabla th {background: #F1F6F8; color: #334155; text-align: right; padding: .55rem .8rem; border-bottom: 2px solid #CBD5E1;}
.tabla th:first-child, .tabla td:first-child {text-align: left;}
.tabla td {padding: .5rem .8rem; border-bottom: 1px solid #E2E8F0; text-align: right;}
.tabla tr:hover td {background: #F8FAFC;}
</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------------------------------- utilidades
def num(x, decimales=1):
    """Número con formato en español: miles con punto y decimales con coma."""
    texto = f"{x:,.{decimales}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def kpi(etiqueta, valor, nota=""):
    return (f'<div class="kpi"><div class="etiqueta">{etiqueta}</div>'
            f'<div class="valor">{valor}</div><div class="nota">{nota}</div></div>')


def mostrar_tabla(df, decimales=1):
    """Tabla en HTML. No usa st.dataframe para no depender de pyarrow."""
    texto = df.copy()
    def dar_formato(v):
        if isinstance(v, (int, np.integer)):
            return num(v, 0)
        if isinstance(v, (float, np.floating)) and pd.notna(v):
            return num(v, decimales)
        return v
    for col in texto.columns:
        texto[col] = texto[col].map(dar_formato)
    st.markdown(texto.to_html(border=0, classes="tabla"), unsafe_allow_html=True)


def encabezado(titulo, subtitulo):
    st.markdown(f'<div class="hero"><h1>{titulo}</h1><p>{subtitulo}</p></div>', unsafe_allow_html=True)


def diseno(fig, alto=380):
    fig.update_layout(template="plotly_white", height=alto, margin=dict(l=10, r=10, t=50, b=10),
                      font=dict(size=13), legend_title_text="", separators=",.")
    if fig.layout.title.text:
        fig.update_layout(title_font=dict(size=16))
    else:
        fig.update_layout(title_text="")   # evita que Plotly escriba 'undefined'
    return fig


@st.cache_data(show_spinner="Cargando los datos...")
def cargar_datos():
    d = em.cargar_adultos()
    d["Sexo"] = np.where(d["Mujer"] == 1, "Mujer", "Hombre")
    d["Clase"] = np.where(d["Diabetes"] == 1, "Con diabetes o prediabetes", "Sin diabetes ni prediabetes")
    d["Grupo_Edad"] = pd.cut(d["Edad"], [17, 29, 39, 49, 59, 69, 80],
                             labels=["18-29", "30-39", "40-49", "50-59", "60-69", "70-80"])
    d["Categoria_IMC"] = pd.cut(d["IMC"], [0, 18.5, 25, 30, 35, 100], right=False,
                                labels=["Bajo peso", "Normal", "Sobrepeso", "Obesidad I", "Obesidad II o más"])
    d["Edad_3"] = pd.cut(d["Edad"], [17, 39, 59, 80], labels=["18-39", "40-59", "60-80"])
    d["Raza_Etnia"] = d["Raza_Etnia"].map({1: "Mexicano-americano", 2: "Otro hispano", 3: "Blanco no hispano",
                                           4: "Negro no hispano", 6: "Asiático no hispano", 7: "Otra / multirracial"})
    return d


# ----------------------------------------------------------------------------- pantalla 1
def pagina_exploracion(datos):
    encabezado("Exploración de los datos",
               "¿Quiénes tienen más casos de diabetes o prediabetes? Explora los 6.110 adultos de NHANES 2013-2014.")

    st.sidebar.markdown("### Filtros")
    rango = st.sidebar.slider("Edad", 18, 80, (18, 80))
    sexos = st.sidebar.multiselect("Sexo", ["Mujer", "Hombre"], default=["Mujer", "Hombre"])
    sel = datos[datos["Edad"].between(*rango) & datos["Sexo"].isin(sexos)]
    if sel.empty:
        st.warning("Con estos filtros no queda nadie. Amplía el rango de edad o el sexo.")
        return

    tasa_global = datos["Diabetes"].mean()
    tasa_sel = sel["Diabetes"].mean()
    casos = int(sel["Diabetes"].sum())
    dif = (tasa_sel - tasa_global) * 100

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("Adultos en la selección", num(len(sel), 0), f"de {num(len(datos), 0)} en total"), unsafe_allow_html=True)
    c2.markdown(kpi("Con diabetes o prediabetes", num(casos, 0), "casos reportados"), unsafe_allow_html=True)
    c3.markdown(kpi("Porcentaje de casos", f"{num(tasa_sel * 100)} %",
                    f"{'+' if dif >= 0 else ''}{num(dif)} puntos frente al promedio ({num(tasa_global * 100)} %)"),
                unsafe_allow_html=True)
    c4.markdown(kpi("Edad mediana", f"{num(sel['Edad'].median(), 0)} años", "de la selección"), unsafe_allow_html=True)
    if casos < 30:
        st.warning(f"Hay solo {casos} casos en esta selección: los porcentajes son poco confiables.")

    st.markdown("&nbsp;")
    izq, der = st.columns(2)

    def barras_tasa(col, titulo):
        g = sel.groupby(col, observed=True)["Diabetes"].agg(["mean", "size"]).reset_index()
        g["pct"] = g["mean"] * 100
        fig = px.bar(g, x=col, y="pct", text=g["pct"].map(lambda v: f"{v:.0f}%"), color="pct",
                     color_continuous_scale=["#BFE6E3", "#F4A582", CORAL], hover_data={"size": True, "pct": ":.1f"})
        fig.add_hline(y=tasa_global * 100, line_dash="dash", line_color=GRIS,
                      annotation_text=f"Promedio {num(tasa_global * 100)} %", annotation_position="top left")
        fig.update_traces(textposition="outside")
        fig.update_layout(coloraxis_showscale=False, title=titulo, xaxis_title="", yaxis_title="% con diabetes o prediabetes")
        fig.update_yaxes(range=[0, max(g["pct"].max(), tasa_global * 100) * 1.22])
        return diseno(fig)

    izq.plotly_chart(barras_tasa("Grupo_Edad", "El riesgo sube con la edad"), use_container_width=True)
    der.plotly_chart(barras_tasa("Categoria_IMC", "Y también con el IMC"), use_container_width=True)

    st.markdown("### ¿En qué se diferencian quienes tienen y quienes no tienen el diagnóstico?")
    opciones = {"Edad": "Edad", "IMC": "IMC", "Cintura (cm)": "Cintura_cm", "Presión sistólica": "Presion_Sistolica",
                "Presión diastólica": "Presion_Diastolica", "Colesterol total": "Colesterol_Total", "Colesterol HDL": "Colesterol_HDL"}
    a, b = st.columns([1, 1])
    nombre = a.selectbox("Variable", list(opciones))
    tipo = b.radio("Gráfico", ["Violín", "Histograma"], horizontal=True)
    var = opciones[nombre]
    if tipo == "Violín":
        fig = px.violin(sel, x="Clase", y=var, color="Clase", box=True, color_discrete_map=COLOR_CLASE)
        fig.update_layout(xaxis_title="", yaxis_title=nombre, showlegend=False)
    else:
        fig = px.histogram(sel, x=var, color="Clase", barmode="overlay", opacity=0.65, nbins=40,
                           histnorm="probability density", color_discrete_map=COLOR_CLASE)
        fig.update_layout(xaxis_title=nombre, yaxis_title="Densidad")
    st.plotly_chart(diseno(fig, 400), use_container_width=True)

    st.markdown("### Edad e IMC se refuerzan")
    tasa = sel.pivot_table(index="Edad_3", columns="Categoria_IMC", values="Diabetes", aggfunc="mean", observed=True) * 100
    cant = sel.pivot_table(index="Edad_3", columns="Categoria_IMC", values="Diabetes", aggfunc="size", observed=True)
    if tasa.shape[0] > 0 and tasa.shape[1] > 0:
        texto = tasa.round(0).astype("Int64").astype(str) + "%<br>n=" + cant.astype(str)
        fig = go.Figure(go.Heatmap(z=tasa.values, x=list(tasa.columns), y=list(tasa.index), text=texto.values,
                                   texttemplate="%{text}", colorscale="YlOrRd", colorbar=dict(title="% casos")))
        fig.update_layout(title="Porcentaje de casos según edad e IMC", xaxis_title="Categoría de IMC", yaxis_title="Edad")
        st.plotly_chart(diseno(fig, 330), use_container_width=True)
        st.caption("Las celdas con pocas personas (n pequeño) se leen con cuidado.")

    st.markdown("### Tabla comparativa")
    cols = {"Edad": "Edad", "IMC": "IMC", "Cintura_cm": "Cintura (cm)", "Presion_Sistolica": "Sistólica",
            "Presion_Diastolica": "Diastólica", "Colesterol_Total": "Colesterol total", "Colesterol_HDL": "HDL"}
    tabla = sel.groupby("Clase")[list(cols)].median().rename(columns=cols).round(1).T
    tabla["Diferencia"] = (tabla["Con diabetes o prediabetes"] - tabla["Sin diabetes ni prediabetes"]).round(1)
    tabla.columns.name = "Mediana de"
    mostrar_tabla(tabla)
    st.download_button("Descargar tabla (CSV)", tabla.to_csv().encode("utf-8"), "comparacion_medianas.csv", "text/csv")

    with st.expander("Raza/etnia e ingreso (solo descripción)"):
        st.write("Estas variables se muestran para describir a la población. **No se usan** para decidir a quién "
                 "priorizar, por equidad y porque pueden reflejar el acceso a un diagnóstico y no solo el riesgo.")
        g = sel.groupby("Raza_Etnia")["Diabetes"].agg(["mean", "size"]).reset_index()
        g["pct"] = g["mean"] * 100
        fig = px.bar(g.sort_values("pct"), x="pct", y="Raza_Etnia", orientation="h", text=g.sort_values("pct")["pct"].map(lambda v: f"{v:.0f}%"),
                     color_discrete_sequence=[TEAL], hover_data={"size": True, "pct": ":.1f"})
        fig.update_layout(xaxis_title="% con diabetes o prediabetes", yaxis_title="")
        st.plotly_chart(diseno(fig, 320), use_container_width=True)


# ----------------------------------------------------------------------------- pantalla 2
EJEMPLOS = {
    "Adulta joven": dict(in_edad=28, in_sexo="Mujer", in_imc=22.0, in_cin=78.0, in_sis=110, in_dia=68, in_col=170, in_hdl=62),
    "Adulto de mediana edad": dict(in_edad=48, in_sexo="Hombre", in_imc=29.0, in_cin=100.0, in_sis=128, in_dia=82, in_col=200, in_hdl=45),
    "Adulto mayor con obesidad": dict(in_edad=66, in_sexo="Hombre", in_imc=34.0, in_cin=115.0, in_sis=145, in_dia=80, in_col=175, in_hdl=38),
}
VALORES_INICIALES = EJEMPLOS["Adulto de mediana edad"]


def aplicar_ejemplo(nombre):
    for clave, valor in EJEMPLOS[nombre].items():
        st.session_state[clave] = valor


def pagina_simulador(datos):
    encabezado("Simulador de priorización",
               "Ingresa un perfil y mira si quedaría dentro del grupo que se priorizaría para la prueba de laboratorio.")
    modelos, meta = cargar_modelos()
    for clave, valor in VALORES_INICIALES.items():
        st.session_state.setdefault(clave, valor)

    escenario_txt = st.radio("Escenario", ["Sin laboratorio", "Con laboratorio"], horizontal=True,
                             help="Con laboratorio se suman el colesterol total y el HDL, que requieren una muestra de sangre.")
    esc = "sin_lab" if escenario_txt == "Sin laboratorio" else "con_lab"
    info = meta[esc]
    if esc == "sin_lab":
        st.caption("Usa solo medidas de una consulta básica: edad, sexo, IMC, cintura y presión arterial.")
    else:
        st.caption("Suma colesterol total y HDL, que necesitan sangre. Rinde un poco mejor, pero no es una medida sencilla.")

    izq, der = st.columns([1, 1.2], gap="large")
    with izq:
        st.markdown("#### Perfil")
        st.caption("Perfiles de ejemplo:")
        botones = st.columns(3)
        for col, nombre in zip(botones, EJEMPLOS):
            col.button(nombre, on_click=aplicar_ejemplo, args=(nombre,), use_container_width=True)

        a, b = st.columns(2)
        edad = a.number_input("Edad (años)", 18, 90, step=1, key="in_edad")
        sexo = b.radio("Sexo", ["Mujer", "Hombre"], horizontal=True, key="in_sexo")
        a, b = st.columns(2)
        imc = a.number_input("IMC (kg/m²)", 12.0, 70.0, step=0.1, key="in_imc")
        cintura = b.number_input("Cintura (cm)", 50.0, 180.0, step=0.5, key="in_cin")
        a, b = st.columns(2)
        sis = a.number_input("Presión sistólica (mmHg)", 70, 230, step=1, key="in_sis")
        dia = b.number_input("Presión diastólica (mmHg)", 30, 130, step=1, key="in_dia")
        perfil = {"Edad": edad, "Mujer": 1 if sexo == "Mujer" else 0, "IMC": imc, "Cintura_cm": cintura,
                  "Presion_Sistolica": sis, "Presion_Diastolica": dia}
        # los campos de laboratorio se muestran siempre (así no se pierde su valor al cambiar
        # de escenario) y quedan deshabilitados cuando el escenario no los usa
        sin_lab = esc == "sin_lab"
        a, b = st.columns(2)
        col_total = a.number_input("Colesterol total (mg/dL)", 70, 400, step=1, key="in_col", disabled=sin_lab,
                                   help="Requiere una muestra de sangre. Solo se usa en el escenario con laboratorio.")
        col_hdl = b.number_input("Colesterol HDL (mg/dL)", 15, 130, step=1, key="in_hdl", disabled=sin_lab,
                                 help="Requiere una muestra de sangre. Solo se usa en el escenario con laboratorio.")
        if not sin_lab:
            perfil["Colesterol_Total"] = col_total
            perfil["Colesterol_HDL"] = col_hdl

        fuera = [NOMBRES_VARIABLES[v] for v in info["variables"] if v != "Mujer"
                 and not (info["rangos"][v]["p1"] <= perfil[v] <= info["rangos"][v]["p99"])]
        if fuera:
            st.warning("Valores fuera del rango habitual de los datos (percentiles 1 a 99): " + ", ".join(fuera) +
                       ". El modelo casi no tiene personas así, así que el resultado es menos confiable.")

    res = predecir(esc, perfil)
    prob, umbral = res["probabilidad"], res["umbral"]
    with der:
        st.markdown("#### Resultado")
        maximo = 100 if prob * 100 > 75 else 80
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=prob * 100, number=dict(suffix=" %", valueformat=".1f"),
            title=dict(text="Probabilidad estimada"),
            gauge=dict(axis=dict(range=[0, maximo]), bar=dict(color=CORAL if res["prioriza"] else TEAL),
                       steps=[dict(range=[0, umbral * 100], color="#E3F4EF"), dict(range=[umbral * 100, maximo], color="#FDE3D9")],
                       threshold=dict(line=dict(color="#0F172A", width=4), thickness=0.85, value=umbral * 100))))
        st.plotly_chart(diseno(fig, 290), use_container_width=True)
        if res["prioriza"]:
            st.markdown('<span class="badge badge-si">Dentro del 40 % priorizado</span>', unsafe_allow_html=True)
            st.write("Este perfil está entre el 40 % de adultos con mayor probabilidad. En una campaña de tamizaje "
                     "se le ofrecería la prueba de laboratorio.")
        else:
            st.markdown('<span class="badge badge-no">Fuera del 40 % priorizado</span>', unsafe_allow_html=True)
            st.write("Este perfil queda entre el 60 % de adultos con menor probabilidad, así que no entraría en el grupo "
                     "al que se prioriza para la prueba.")
        st.caption(f"La línea negra es el umbral ({num(umbral * 100)} %): la probabilidad que deja al 40 % de los adultos por encima.")

    st.markdown("---")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("#### ¿Qué empuja el resultado?")
        aportes = pd.Series(res["aportes"])
        etiquetas = {v: (f"Sexo: {'mujer' if perfil[v] == 1 else 'hombre'}" if v == "Mujer"
                         else f"{NOMBRES_VARIABLES[v]} = {num(perfil[v], 0 if v in ('Edad', 'Presion_Sistolica', 'Presion_Diastolica', 'Colesterol_Total', 'Colesterol_HDL') else 1)}")
                     for v in aportes.index}
        orden = aportes.sort_values()
        fig = go.Figure(go.Bar(x=orden.values, y=[etiquetas[v] for v in orden.index], orientation="h",
                               marker_color=[CORAL if x > 0 else TEAL for x in orden.values]))
        fig.add_vline(x=0, line_color="#0F172A", line_width=1)
        fig.update_layout(xaxis_title="Aporte al resultado (log-odds)", yaxis_title="")
        st.plotly_chart(diseno(fig, 340), use_container_width=True)
        st.caption("A la derecha: sube la probabilidad. A la izquierda: la baja. Se compara con una persona promedio.")
    with c2:
        st.markdown("#### Tu perfil frente a los adultos de la base")
        columnas = [v for v in info["variables"] if v != "Mujer"]
        percentiles = [(NOMBRES_VARIABLES[v], float((datos[v].dropna() < perfil[v]).mean() * 100)) for v in columnas]
        dfp = pd.DataFrame(percentiles, columns=["Variable", "Percentil"]).iloc[::-1]
        fig = go.Figure(go.Bar(x=dfp["Percentil"], y=dfp["Variable"], orientation="h", marker_color=TEAL,
                               text=dfp["Percentil"].map(lambda p: f"{p:.0f}"), textposition="outside"))
        fig.add_vline(x=50, line_dash="dash", line_color=GRIS)
        fig.update_layout(xaxis=dict(range=[0, 108], title="Percentil (0 a 100)"), yaxis_title="")
        st.plotly_chart(diseno(fig, 340), use_container_width=True)
        st.caption("Un percentil de 80 significa que el 80 % de los adultos tiene un valor menor.")

    st.markdown('<div class="aviso"><b>Importante:</b> esto es una herramienta para planear campañas de tamizaje, '
                'no un diagnóstico ni una recomendación médica. El modelo aprende el perfil de quienes ya reportaron '
                'un diagnóstico; no detecta diabetes que nadie ha diagnosticado.</div>', unsafe_allow_html=True)


# ----------------------------------------------------------------------------- pantalla 3
def veredicto_meta(m, meta_recall):
    r, (bajo, alto) = m["recall_40"], m["ic95_recall_40"]
    if r >= meta_recall and bajo >= meta_recall:
        return "Cumple la meta en esta partición."
    if r >= meta_recall + 0.01:
        return "Supera la meta en esta partición, pero el intervalo baja del 75 %: no es seguro."
    if r >= meta_recall:
        return "Cae justo en la meta, y el intervalo baja del 75 %: no se puede asegurar que la cumpla."
    return "No alcanza la meta en esta partición."


def pagina_modelo(datos):
    encabezado("Modelo y datos", "De dónde salen los datos, qué tan bien funciona el modelo y qué límites tiene.")
    modelos, meta = cargar_modelos()
    meta_recall = meta["meta_recall"]

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("Adultos", num(meta["n_adultos"], 0), "NHANES 2013-2014 (6 tablas)"), unsafe_allow_html=True)
    c2.markdown(kpi("Casos", num(meta["n_positivos"], 0), f"{num(meta['n_positivos'] / meta['n_adultos'] * 100)} % con diabetes o prediabetes"),
                unsafe_allow_html=True)
    c3.markdown(kpi("Meta del proyecto", "75 % de casos", "revisando como máximo al 40 % de la población"), unsafe_allow_html=True)
    c4.markdown(kpi("Versión", meta["version_codigo"], f"semilla {meta['semilla']} · {meta['fecha']}"), unsafe_allow_html=True)
    st.markdown("&nbsp;")

    t1, t2, t3, t4, t5 = st.tabs(["Resultados", "Curva de captura", "Estabilidad (20 semillas)",
                                  "Qué pesa en el modelo", "Evidencia MLflow"])

    with t1:
        st.caption("Evaluación en el 20 % de adultos que el modelo no vio al entrenar (1.222 personas, 180 con el diagnóstico).")
        izq, der = st.columns(2, gap="large")
        for col, (clave, titulo) in zip((izq, der), (("sin_lab", "Sin laboratorio"), ("con_lab", "Con laboratorio"))):
            m = meta[clave]["metricas_prueba"]
            with col:
                st.markdown(f"#### {titulo}")
                dif = (m["recall_40"] - m["recall_40_edad_sola"]) * 100
                st.markdown(kpi("Casos capturados revisando al 40 %", f"{num(m['recall_40'] * 100)} %",
                                f"{'+' if dif >= 0 else ''}{num(dif)} puntos frente a usar solo la edad ({num(m['recall_40_edad_sola'] * 100)} %)"),
                            unsafe_allow_html=True)
                st.write(f"Intervalo del 95 %: {num(m['ic95_recall_40'][0] * 100)} % a {num(m['ic95_recall_40'][1] * 100)} %. "
                         + veredicto_meta(m, meta_recall))
                a, b, c = st.columns(3)
                a.metric("ROC-AUC", num(m["roc_auc"], 3))
                b.metric("PR-AUC", num(m["pr_auc"], 3))
                c.metric("Priorizados", f"{num(m['pct_priorizado'] * 100)} %")
                matriz = pd.DataFrame([[m["tp"], m["fn"]], [m["fp"], m["tn"]]],
                                      index=["Con el diagnóstico", "Sin el diagnóstico"], columns=["Priorizados", "No priorizados"])
                mostrar_tabla(matriz, 0)
        st.info("El resultado de una sola partición varía varios puntos. Mira la pestaña **Estabilidad** para ver el "
                "promedio con 20 particiones distintas.")

    with t2:
        fig = go.Figure()
        for clave, titulo, color in (("sin_lab", "Sin laboratorio", TEAL), ("con_lab", "Con laboratorio", CORAL)):
            curva = meta[clave]["curva_captura"]
            fig.add_trace(go.Scatter(x=np.array(curva["fraccion"]) * 100, y=np.array(curva["modelo"]) * 100,
                                     name=titulo, line=dict(color=color, width=3)))
        edad = meta["sin_lab"]["curva_captura"]
        fig.add_trace(go.Scatter(x=np.array(edad["fraccion"]) * 100, y=np.array(edad["edad_sola"]) * 100,
                                 name="Solo la edad", line=dict(color=GRIS, width=2, dash="dot")))
        fig.add_trace(go.Scatter(x=[0, 100], y=[0, 100], name="Al azar", line=dict(color="#CBD5E1", dash="dash")))
        fig.add_vline(x=40, line_color="#0F172A", line_width=1)
        fig.add_hline(y=75, line_color="#0F172A", line_width=1)
        fig.add_annotation(x=40, y=75, text="Meta: 75 % de los casos<br>revisando al 40 %", showarrow=True,
                           ax=70, ay=60, bgcolor="white", bordercolor="#0F172A")
        fig.update_layout(title="Casos capturados según el porcentaje de adultos revisados",
                          xaxis_title="% de adultos revisados (los de mayor probabilidad primero)",
                          yaxis_title="% de los casos que se encuentran")
        st.plotly_chart(diseno(fig, 470), use_container_width=True)
        st.caption("Cuanto más arriba de la línea punteada gris (solo la edad), más aporta combinar las variables.")

    with t3:
        ruta = RAIZ / "reports" / "figures" / "supuestos_escenarios_recall_semillas.csv"
        if ruta.exists():
            sem = pd.read_csv(ruta)
            st.write("Mismo cálculo repetido con 20 particiones distintas de entrenamiento y prueba "
                     "(modelos de los cuadernos 07 y 08, con pesos de clase).")
            orden = sem.groupby("modelo")["recall_40"].mean().sort_values().index.tolist()
            fig = px.box(sem, y="modelo", x="recall_40", category_orders={"modelo": orden}, color_discrete_sequence=[TEAL], points="all")
            fig.add_vline(x=0.75, line_dash="dash", line_color=CORAL, annotation_text="Meta 75 %")
            fig.update_layout(xaxis_title="Casos capturados revisando al 40 % (al azar sería 0,40)", yaxis_title="")
            fig.update_xaxes(range=[0.64, 0.9])
            st.plotly_chart(diseno(fig, 420), use_container_width=True)
            resumen = sem.groupby("modelo")["recall_40"].agg(["mean", "min", "max", lambda s: int((s >= 0.75).sum())])
            resumen.columns = ["Promedio", "Mínimo", "Máximo", "Particiones sobre la meta (de 20)"]
            resumen = resumen.sort_values("Promedio", ascending=False)
            resumen.index.name = None
            resumen["Particiones sobre la meta (de 20)"] = resumen["Particiones sobre la meta (de 20)"].astype(int)
            mostrar_tabla(resumen, 3)
            st.caption("La meta se cumple en promedio, con poco margen: algunas particiones quedan por debajo del 75 %.")
        else:
            st.info("No se encontró reports/figures/supuestos_escenarios_recall_semillas.csv.")

    with t4:
        st.write("Cuánto cambian los 'odds' de tener el diagnóstico al subir una desviación estándar de cada variable "
                 "(1 = sin efecto). Son asociaciones, no causas.")
        filas = []
        for clave, titulo in (("sin_lab", "Sin laboratorio"), ("con_lab", "Con laboratorio")):
            for v, o in meta[clave]["odds_ratio"].items():
                filas.append({"Escenario": titulo, "Variable": NOMBRES_VARIABLES[v], "Odds ratio": o})
        dfo = pd.DataFrame(filas)
        fig = px.bar(dfo, y="Variable", x="Odds ratio", color="Escenario", barmode="group", orientation="h",
                     color_discrete_map={"Sin laboratorio": TEAL, "Con laboratorio": CORAL})
        fig.add_vline(x=1, line_color="#0F172A", line_width=1)
        st.plotly_chart(diseno(fig, 430), use_container_width=True)
        st.caption("El colesterol total sale con efecto contrario al que uno esperaría. Probablemente refleja que muchas "
                   "personas ya diagnosticadas toman medicamentos que bajan el colesterol.")

    with t5:
        carpeta = RAIZ / "docs" / "evidencias_mlflow"
        imagenes = sorted(carpeta.glob("*.jp*g")) + sorted(carpeta.glob("*.png")) if carpeta.exists() else []
        if imagenes:
            st.write("Experimentos registrados en MLflow, en un servidor de AWS EC2.")
            for ruta in imagenes:
                pie = re.sub(r"^mlflow_ec2_\d+_", "", ruta.stem).replace("_", " ").capitalize()
                st.image(str(ruta), caption=pie, use_container_width=True)
        else:
            st.info("Aún no hay capturas en docs/evidencias_mlflow.")

    with st.expander("Límites que hay que tener presentes"):
        st.markdown("""
- El diagnóstico es **autorreportado**: el modelo aprende el perfil de quienes ya les dijeron que tienen diabetes o prediabetes.
- Se mezclan diabetes y prediabetes en una sola clase.
- Los valores de laboratorio pueden estar alterados por los medicamentos.
- No se usaron los ponderadores de NHANES, así que los porcentajes no representan a toda la población de Estados Unidos.
- Raza/etnia e ingreso no entran al modelo, por equidad.
- La herramienta sirve para **planear campañas de tamizaje**, no para diagnosticar.
""")


# ----------------------------------------------------------------------------- navegación
datos = cargar_datos()
st.sidebar.markdown("## 🩺 Metabolic Health Explorer")
PANTALLAS = ["Exploración", "Simulador", "Modelo y datos"]
# se puede abrir una pantalla directo con ?pantalla=Simulador en la URL
inicial = st.query_params.get("pantalla", PANTALLAS[0])
pantalla = st.sidebar.radio("Pantalla", PANTALLAS, index=PANTALLAS.index(inicial) if inicial in PANTALLAS else 0,
                            label_visibility="collapsed")
st.sidebar.markdown("---")

if pantalla == "Exploración":
    pagina_exploracion(datos)
elif pantalla == "Simulador":
    pagina_simulador(datos)
else:
    pagina_modelo(datos)

st.sidebar.caption("Prototipo académico · MIAD · Despliegue de soluciones analíticas. No es un dispositivo de diagnóstico.")
