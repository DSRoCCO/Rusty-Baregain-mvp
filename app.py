import sys
from pathlib import Path

import pandas as pd
import streamlit as st
import altair as alt

sys.path.insert(0, str(Path(__file__).parent / "src"))
from rusty_baregain_mvp.comparables import comparable_summary
from rusty_baregain_mvp.data import load_descriptive_data, load_modeling_data
from rusty_baregain_mvp.model import load_estimator, load_metadata

st.set_page_config(page_title="Rusty Bargain", page_icon="🚗", layout="wide")

@st.cache_data
def get_data():
    return load_modeling_data(), load_descriptive_data()

@st.cache_resource
def get_model():
    return load_estimator(), load_metadata()

model_data, descriptive_data = get_data()
model, metadata = get_model()
base = {"Brand":"volkswagen","Model":"golf","VehicleType":"small","Gearbox":"manual","FuelType":"gasoline","NotRepaired":"no","AgeAtCrawl":10,"PowerForModel":105,"Mileage":125000}
for key, value in base.items():
    st.session_state.setdefault(key, value)

def reset():
    for key, value in base.items():
        st.session_state[key] = value

def ordered_line_chart(series, order, title):
    chart_data = series.reindex(order).rename("EUR").reset_index()
    chart_data.columns = ["tramo", "EUR"]
    chart = alt.Chart(chart_data).mark_line(point=alt.OverlayMarkDef(size=70), color="#72B7E8").encode(
        x=alt.X("tramo:N", sort=order, title=None),
        y=alt.Y("EUR:Q", title="EUR", scale=alt.Scale(zero=True)),
        tooltip=[alt.Tooltip("tramo:N", title="Tramo"), alt.Tooltip("EUR:Q", title="Mediana", format=",.0f")],
    ).properties(title=title, height=260)
    st.altair_chart(chart, width="stretch")

def ordered_bar_chart(series, order, title):
    chart_data = series.reindex(order).rename("EUR").reset_index()
    chart_data.columns = ["tramo", "EUR"]
    chart = alt.Chart(chart_data).mark_bar(color="#72B7E8").encode(
        x=alt.X("tramo:N", sort=order, title=None),
        y=alt.Y("EUR:Q", title="EUR", scale=alt.Scale(zero=True)),
        tooltip=[alt.Tooltip("tramo:N", title="Rango"), alt.Tooltip("EUR:Q", title="MAE", format=",.0f")],
    ).properties(title=title, height=260)
    st.altair_chart(chart, width="stretch")

def fixed_coverage_chart(series):
    chart_data = series.rename("registros").reset_index()
    chart_data.columns = ["marca", "registros"]
    chart = alt.Chart(chart_data).mark_bar(color="#72B7E8").encode(
        x=alt.X("marca:N", sort=None, title=None),
        y=alt.Y("registros:Q", title="Registros", scale=alt.Scale(domain=[0, 80_000]), axis=alt.Axis(values=list(range(0, 80_001, 10_000)), format=",d")),
        tooltip=[alt.Tooltip("marca:N", title="Marca"), alt.Tooltip("registros:Q", title="Registros", format=",d")],
    ).properties(height=300)
    st.altair_chart(chart, width="stretch")

st.title("Rusty Bargain")
st.caption("Demo analítica de referencia de precio histórico para compradores")
st.warning("Referencia histórica de 2016: no es una tasación actual, una venta final confirmada ni una recomendación automática de compra.")
tab_overview, tab_predict = st.tabs(["Análisis descriptivo y diagnóstico", "Estimación predictiva y comparables"])

with tab_overview:
    metrics = metadata["metrics"]
    cols = st.columns(4)
    cols[0].metric("Observaciones", f"{len(descriptive_data):,}")
    cols[1].metric("Población MVP", f"{len(model_data):,}")
    cols[2].metric("MAE temporal", f"EUR {metrics['mae_eur']:,.0f}")
    cols[3].metric("Cobertura intervalo", f"{metrics['interval_coverage']:.1%}")
    st.caption("Vehículos ordinarios matriculados entre 1991 y 2016. Los autos de colección y años posteriores quedan fuera del alcance.")
    brands = model_data.groupby("Brand").Price.agg(registros="size", mediana="median").sort_values("registros", ascending=False).head(12)
    st.subheader("Marcas con mayor evidencia")
    fixed_coverage_chart(brands["registros"])
    st.dataframe(brands.style.format({"mediana":"EUR {:,.0f}"}), width="stretch")
    st.subheader("Cómo varía el precio histórico")
    age_labels = ["0–3 años", "4–7 años", "8–12 años", "13–18 años", "19–25 años"]
    mileage_labels = ["≤50 mil km", "50–100 mil km", "100–125 mil km", "125–150 mil km"]
    power_labels = ["≤60 CV", "61–90 CV", "91–120 CV", "121–160 CV", "161–220 CV", ">220 CV"]
    age_data = model_data.assign(tramo=pd.cut(model_data["AgeAtCrawl"], [-1, 3, 7, 12, 18, 25], labels=age_labels, include_lowest=True))
    mileage_data = model_data.assign(tramo=pd.cut(model_data["Mileage"], [0, 50_000, 100_000, 125_000, 150_000], labels=mileage_labels, include_lowest=True))
    power_data = model_data.assign(tramo=pd.cut(model_data["PowerForModel"], [0, 60, 90, 120, 160, 220, 1_000], labels=power_labels, include_lowest=True))
    c1, c2 = st.columns(2)
    with c1:
        age_chart = age_data.groupby("tramo", observed=True).Price.median()
        ordered_line_chart(age_chart, age_labels, "Mediana de precio por antigüedad")
        mileage_chart = mileage_data.groupby("tramo", observed=True).Price.median()
        ordered_line_chart(mileage_chart, mileage_labels, "Mediana de precio por kilometraje")
    with c2:
        power_chart = power_data.groupby("tramo", observed=True).Price.median()
        ordered_line_chart(power_chart, power_labels, "Mediana de precio por potencia")
        error = pd.DataFrame(metrics["error_by_price"]).set_index("rango")
        error_labels = ["≤ EUR 1 mil", "EUR 1–5 mil", "EUR 5–10 mil", "> EUR 10 mil"]
        error.index = error_labels
        ordered_bar_chart(error["mae_eur"], error_labels, "Error absoluto medio por rango de precio")
    st.subheader("Modelos con mayor evidencia")
    models_table = (model_data.groupby(["Brand", "Model"]).Price.agg(registros="size", mediana="median", p25=lambda x: x.quantile(.25), p75=lambda x: x.quantile(.75)).sort_values("registros", ascending=False).head(15))
    st.dataframe(models_table.style.format({"mediana":"EUR {:,.0f}","p25":"EUR {:,.0f}","p75":"EUR {:,.0f}"}), width="stretch")
    st.info("Los descuentos, promociones, equipamiento detallado y estado mecánico real no existen en la fuente. Las asociaciones no prueban causalidad.")

with tab_predict:
    left, right = st.columns(2)
    with left:
        brand = st.selectbox("Marca", sorted(model_data.Brand.dropna().unique()), key="Brand")
        models = sorted(model_data.loc[model_data.Brand.eq(brand), "Model"].dropna().unique())
        if st.session_state.Model not in models:
            st.session_state.Model = models[0]
        model_name = st.selectbox("Modelo", models, key="Model")
        vehicle = st.selectbox("Tipo de vehículo", sorted(model_data.VehicleType.dropna().unique()), key="VehicleType")
        gearbox = st.selectbox("Transmisión", sorted(model_data.Gearbox.dropna().unique()), key="Gearbox")
    with right:
        fuel = st.selectbox("Combustible", sorted(model_data.FuelType.dropna().unique()), key="FuelType")
        repair = st.selectbox("¿Reparación pendiente declarada?", sorted(model_data.NotRepaired.dropna().unique()), key="NotRepaired")
        registration_year = st.selectbox("Año de matriculación", list(range(2016, 1990, -1)))
        power = st.slider("Potencia (CV)", 20, 500, key="PowerForModel")
        mileage = st.slider("Kilometraje", 5_000, 150_000, step=5_000, key="Mileage")
    st.button("Restablecer escenario", on_click=reset)
    profile = {"Brand":brand,"Model":model_name,"VehicleType":vehicle,"Gearbox":gearbox,"FuelType":fuel,"NotRepaired":repair,"AgeAtCrawl":2016-registration_year,"PowerForModel":power,"Mileage":mileage}
    estimate = float(model.predict(pd.DataFrame([profile]))[0])
    evidence = comparable_summary(model_data, profile)
    half_width = metadata["metrics"]["interval_half_width_eur"]
    result = st.columns(3)
    result[0].metric("Estimación histórica", f"EUR {estimate:,.0f}")
    result[1].metric("Intervalo empírico", f"EUR {max(0, estimate-half_width):,.0f} – {estimate+half_width:,.0f}")
    result[2].metric("Evidencia", {"exacta":"alta","bandas":"media","sin cobertura":"baja"}[evidence["level"]])
    if evidence["level"] == "sin cobertura":
        st.info("No hay al menos 10 comparables locales. Interprete la estimación como evidencia baja.")
    else:
        st.write(f"{evidence['n']} comparables ({evidence['level']}): mediana EUR {evidence['median']:,.0f}; rango intercuartílico EUR {evidence['p25']:,.0f} – {evidence['p75']:,.0f}.")
    st.caption("El intervalo está calibrado en datos históricos de 2016. No garantiza el precio de una compra real.")
