import streamlit as st
import pandas as pd
import numpy as np

# Configuración de la página
st.set_page_config(page_title="Dashboard Académico-Agronómico de Suelos", layout="wide")

# ==========================================
# 1. BASE DE DATOS DE CULTIVOS FIDEDIGNOS (BOLIVIA)
# ==========================================
# Datos recopilados en base a guías técnicas de INIAF, CIP, CIAT Bolivia y MDRyT.
cultivos_db = {
    "Papa (Solanum tuberosum)": {
        "Nombre Científico": "Solanum tuberosum",
        "Ecorregión": "Altiplano / Valles",
        "Ciclo Total": "120 - 150 días",
        "Fases": "Emergencia (0-25d) -> Des. Vegetativo (25-50d) -> Estolonización/Floración (50-80d) -> Tubenización (80-120d) -> Maduración (120-150d)",
        "Demanda N": 120, "Demanda P2O5": 140, "Demanda K2O": 180,
        "pH_optimo": "5.5 - 6.5", "CE_limite": 2.0
    },
    "Quinua (Chenopodium quinoa)": {
        "Nombre Científico": "Chenopodium quinoa",
        "Ecorregión": "Altiplano",
        "Ciclo Total": "140 - 160 días",
        "Fases": "Germinación (0-10d) -> Ramificación (10-45d) -> Panojamientio (45-75d) -> Floración (75-100d) -> Grano Lechoso/Pastoso (100-140d) -> Madurez (140-160d)",
        "Demanda N": 80, "Demanda P2O5": 60, "Demanda K2O": 90,
        "pH_optimo": "6.0 - 8.5", "CE_limite": 8.0
    },
    "Soya (Glycine max)": {
        "Nombre Científico": "Glycine max",
        "Ecorregión": "Trópico (Tierras Bajas)",
        "Ciclo Total": "100 - 115 días",
        "Fases": "Emergencia (V1-V3) -> Floración (R1-R2) -> Des. Vainas (R3-R4) -> Llenado de Grano (R5-R6) -> Madurez (R7-R8)",
        "Demanda N": 0, # Fijación simbiótica (se asume 0 para fertilización química básica)
        "Demanda P2O5": 60, "Demanda K2O": 80,
        "pH_optimo": "6.0 - 6.8", "CE_limite": 2.0
    },
    "Maíz Sostenibilidad (Zea mays)": {
        "Nombre Científico": "Zea mays",
        "Ecorregión": "Valles / Chaco / Trópico",
        "Ciclo Total": "110 - 130 días",
        "Fases": "Emergencia (V1) -> Crecimiento Vegetativo (V6-V12) -> Floración/Panojaminto (VT-R1) -> Estado Lechoso/Masoso (R2-R4) -> Madurez (R6)",
        "Demanda N": 140, "Demanda P2O5": 60, "Demanda K2O": 100,
        "pH_optimo": "5.8 - 7.0", "CE_limite": 1.7
    },
    "Trigo Soberanía (Triticum aestivum)": {
        "Nombre Científico": "Triticum aestivum",
        "Ecorregión": "Valles / Tierras Bajas",
        "Ciclo Total": "105 - 120 días",
        "Fases": "Plántula -> Macollamiento -> Encañado -> Espigado -> Antesis -> Madurez de Grano",
        "Demanda N": 90, "Demanda P2O5": 40, "Demanda K2O": 60,
        "pH_optimo": "6.0 - 7.0", "CE_limite": 6.0
    }
}

# ==========================================
# INTERFAZ DE USUARIO - SIDEBAR
# ==========================================
st.sidebar.header("🔬 Parámetros de Control y Laboratorio")

# Selector de Cultivo
cultivo_sel = st.sidebar.selectbox("Seleccione Cultivo Estratégico:", list(cultivos_db.keys()))

# Parámetros físicos del suelo
profundidad = st.sidebar.slider("Profundidad de la Capa Arable (cm):", 10, 50, 20)
da = st.sidebar.number_input("Densidad Aparente (g/cm³):", min_value=0.5, max_value=2.0, value=1.35, step=0.05)

# Datos Químicos de Entrada
st.sidebar.subheader("Resultados de Laboratorio")
ph = st.sidebar.number_input("pH del Suelo:", 3.0, 10.0, 6.5, 0.1)
ce = st.sidebar.number_input("Conductividad Eléctrica (mS/cm):", 0.0, 20.0, 1.2, 0.1)
mo = st.sidebar.number_input("Materia Orgánica (%):", 0.0, 10.0, 2.5, 0.1)
p_ppm = st.sidebar.number_input("Fósforo Disponible (Olsen - ppm):", 0.0, 100.0, 12.0, 0.1)

st.sidebar.subheader("Cationes Cambiables (meq/100g)")
ca_meq = st.sidebar.number_input("Calcio (Ca²⁺):", 0.0, 40.0, 8.5)
mg_meq = st.sidebar.number_input("Magnesio (Mg²⁺):", 0.0, 15.0, 1.8)
k_meq = st.sidebar.number_input("Potasio (K⁺):", 0.0, 5.0, 0.45)
na_meq = st.sidebar.number_input("Sodio (Na⁺):", 0.0, 10.0, 0.15)
al_meq = st.sidebar.number_input("Aluminio Intercambiable (Al³⁺):", 0.0, 10.0, 0.0)

# ==========================================
# MEMORIA DE CÁLCULO INTERNA
# ==========================================
# Peso de la Capa Arable (PCA)
pca = 10000 * (profundidad / 100) * da  # t/ha

# Conversiones a kg/ha
# Fósforo disponible elemental y P2O5
p_kg_ha = (p_ppm * pca) / 1000
p2o5_oferta = p_kg_ha * 2.29  # Fómula de Chilón (2014)

# Cationes cambiables a kg/ha usando pesos equivalentes (PE)
k_kg_ha = k_meq * 39.1 * 10 * (pca / 2000)
k2o_oferta = k_kg_ha * 1.2  # De K puro a K2O

ca_kg_ha = ca_meq * 20.0 * 10 * (pca / 2000)
mg_kg_ha = mg_meq * 12.1 * 10 * (pca / 2000)

# Nitrógeno total estimado a partir de la MO según práctica de la UMSA
nt_porcentaje = mo * 0.05  # MO * 0.05 = %N
nt_kg_ha = (nt_porcentaje / 100) * pca * 1000

# Coeficiente de mineralización dinámico según pH (Ácido = 1%, Neutro/Alcalino = 2%)[cite: 1]
coef_min = 1.0 if ph < 5.5 else 2.0
n_disponible = nt_kg_ha * (coef_min / 100)  

# Cálculo de la CIC
cic_mineral = ca_meq + mg_meq + k_meq + na_meq
cic_mo = 40.0 if ph < 5.5 else 200.0  # Retención según condición de acidez
cic_total_calculada = cic_mineral + (mo * (cic_mo / 100))  # meq/100g aproximado

# Relaciones Catiónicas
rel_ca_mg = ca_meq / mg_meq if mg_meq > 0 else 0
rel_ca_k = ca_meq / k_meq if k_meq > 0 else 0
rel_mg_k = mg_meq / k_meq if k_meq > 0 else 0

# Saturación de Aluminio y Sodio
sat_al = (al_meq / cic_total_calculada) * 100 if cic_total_calculada > 0 else 0
psi_na = (na_meq / cic_total_calculada) * 100 if cic_total_calculada > 0 else 0

# ==========================================
# INTERFAZ DEL CUERPO PRINCIPAL
# ==========================================
st.title("Dashboard Académico de Fertilidad de Suelos - Bolivia")
st.markdown("---")

# PESTAÑAS DEL DASHBOARD
tab1, tab2, tab3 = st.tabs([" Ficha de Cultivo y Diagnóstico", "Índice de Storie & Aptitud", "Planificación de Fertilización"])

with tab1:
    st.subheader(f"Ficha Agronómica Fidedigna: {cultivo_sel}")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Nombre Científico", cultivos_db[cultivo_sel]["Nombre Científico"])
        st.metric("Ciclo Fenológico", cultivos_db[cultivo_sel]["Ciclo Total"])
    with col2:
        st.metric("Ecorregión Recomendada", cultivos_db[cultivo_sel]["Ecorregión"])
        st.metric("pH Óptimo", cultivos_db[cultivo_sel]["pH_optimo"])
    with col3:
        st.write("**Fases de Desarrollo:**")
        st.info(cultivos_db[cultivo_sel]["Fases"])
        
    st.markdown("---")
    st.subheader("iagnóstico Automatizado de Limitantes Nutricionales")
    
    # Sistema Experto de Alertas Basadas en Chilón y CETABOL
    alertas = []
    if ph < 5.5:
        alertas.append(f"**Suelo Ácido (pH {ph}):** Riesgo severo de toxicidad por Aluminio ($Al^{{3+}}$). Baja disponibilidad de bases ($Ca, Mg, K$).")
    elif ph > 7.8:
        alertas.append(f"**Suelo Alcalino (pH {ph}):** Puede ocurrir precipitación química de Fósforo debido al exceso de Calcio libre.")
        
    if ce > 2.0:
        alertas.append(f"**Problema de Salinidad (CE {ce} mS/cm):** El suelo califica como salino, afectando la absorción osmótica radicular.")
        
    if rel_ca_mg > 8.0:
        alertas.append(f"**Antagonismo Ca/Mg ({rel_ca_mg:.1f}):** El exceso relativo de Calcio bloquea e impide la absorción del Magnesio.")
    if rel_mg_k < 1.8:
        alertas.append(f"**Desbalance Mg/K ({rel_mg_k:.1f}):** Proporción fuera del rango ideal (1.8 - 2.5), induciendo posibles deficiencias.")
        
    if sat_al > 65.0:
        alertas.append(f"**Nivel Crítico de Aluminio ({sat_al:.1f}%):** Saturación extremadamente perjudicial para el crecimiento radicular. Encalado obligatorio.")

    if alertas:
        for al in alertas:
            st.markdown(al)
    else:
        st.success("El complejo de cambio del suelo no muestra desbalances ni toxicidades críticas latentes.")

with tab2:
    st.subheader("Evaluación de Aptitud por el Índice de Storie")
    st.write("Cálculo paramétrico de la Práctica de Clase 1 de la UMSA.")
    
    # Asignación de puntajes automatizados basados en las tablas del PDF
    # Factor A: Perfil/Profundidad
    fact_A = 100 if profundidad >= 90 else (80 if profundidad >= 60 else (50 if profundidad >= 30 else 20))
    # Factor B: Textura (simplificado para el script base)
    fact_B = 100 # Asumiendo Franco equilibrado por defecto
    # Factor C: Pendiente (Asumiendo condición llana para ejemplo)
    fact_C = 100
    
    # Modificadores (Factor X)
    mod_ph = 100 if (6.5 <= ph <= 7.5) else 80
    mod_ce = 100 if ce < 2.0 else 50
    mod_carb = 100 # Simplificado
    
    fact_X = (mod_ph / 100) * (mod_ce / 100) * (mod_carb / 100) * 100
    
    # Ecuación Multiplicativa de Storie[cite: 1, 2]
    is_storie = (fact_A / 100) * (fact_B / 100) * (fact_C / 100) * (fact_X / 100) * 100
    
    # Calificación final[cite: 1]
    calif_storie = "Excelente" if is_storie >= 65 else ("Buena" if is_storie >= 35 else "Moderada/Pobre")
    
    st.metric(label="Índice de Storie Calculado", value=f"{is_storie:.2f} %", delta=f"Clasificación: {calif_storie}")
    
    # Tabla estructurada réplica de la práctica académica
    st.dataframe(pd.DataFrame({
        "Factor de Evaluación": ["Perfil (A)", "Textura (B)", "Pendiente (C)", "Modificador pH", "Modificador Salinidad"],
        "Puntuación Asignada (%)": [fact_A, fact_B, fact_C, mod_ph, mod_ce]
    }))

with tab3:
    st.subheader("Balance Nutricional Dinámico")
    
    # Demandas del cultivo seleccionado
    dem_n = cultivos_db[cultivo_sel]["Demanda N"]
    dem_p = cultivos_db[cultivo_sel]["Demanda P2O5"]
    dem_k = cultivos_db[cultivo_sel]["Demanda K2O"]
    
    st.write(f"**Peso calculado de tu capa arable:** `{pca:.0f} t/ha`")
    
    # Cuadro comparativo Oferta vs Demanda
    balance_df = pd.DataFrame({
        "Nutriente": ["Nitrógeno (N)", "Fósforo (P₂O₅)", "Potasio (K₂O)"],
        "Demanda Cultivo (kg/ha)": [dem_n, dem_p, dem_k],
        "Oferta Real Suelo (kg/ha)": [round(n_disponible, 1), round(p2o5_oferta, 1), round(k2o_oferta, 1)]
    })
    
    # Calcular Dosis Teórica
    balance_df["Dosis Teórica (Diferencia)"] = balance_df["Demanda Cultivo (kg/ha)"] - balance_df["Oferta Real Suelo (kg/ha)"]
    balance_df["Dosis Teórica (Diferencia)"] = balance_df["Dosis Teórica (Diferencia)"].apply(lambda x: max(0, x))
    
    st.table(balance_df)
    
    st.markdown("---")
    st.subheader("Ajuste por Efectividad de Aplicación y Selección de Fuentes")
    
    # Controles interactivos solicitados
    efectividad = st.slider("Ajustar Factor de Efectividad/Eficiencia de Aplicación (0.1 - 1.0):", 0.1, 1.0, 0.50, step=0.05)
    
    opcion_f = st.selectbox("Seleccione la fuente nitrogenada comercial:", ["Urea (46% N)", "Nitrato de Amonio (33.5% N)"])
    porcent_f = 0.46 if "Urea" in opcion_f else 0.335
    
    # Cálculo posterior automatizado ajustado por efectividad
    dosis_teor_n = balance_df.loc[0, "Dosis Teórica (Diferencia)"]
    if dosis_teor_n > 0:
        fertilizante_requerido = dosis_teor_n / (porcent_f * efectividad)
        st.warning(f"**Recomendación:** Se requiere aplicar **{fertilizante_requerido:.1f} kg/ha** de {opcion_f} para satisfacer el requerimiento neto.")
    else:
        st.success("El suelo cuenta con suficiente suministro de nitrógeno para el ciclo de este cultivo.")