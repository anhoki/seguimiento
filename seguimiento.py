# dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import json

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Proyectos - Guatemala",
    page_icon="📊",
    layout="wide"
)

# Título principal
st.title("📊 Dashboard de Seguimiento de Proyectos")
st.markdown("---")

# ============================================
# CARGA DE DATOS
# ============================================
@st.cache_data
def load_data():
    """Carga los datos desde el archivo Excel"""
    df = pd.read_excel('BD encabezados.xlsx', engine='openpyxl')
    
    # Limpiar nombres de columnas
    df.columns = df.columns.str.strip()
    
    # Renombrar columnas para facilitar el manejo
    columnas_rename = {
        'No.': 'ID',
        'AÑO DE INICIO': 'ANIO_INICIO',
        'INSTITUCIÓN': 'INSTITUCION',
        'TIPO DE PROYECTO': 'TIPO_PROYECTO',
        'NOMBRE  DEL  PROYECTO': 'NOMBRE_PROYECTO',
        'MUNICIPIO': 'MUNICIPIO',
        'DEPARTAMENTO': 'DEPARTAMENTO',
        '% AVANCE FISICO REAL': 'AVANCE_FISICO',
        '% AVANCE FINANCIERO': 'AVANCE_FINANCIERO',
        'ESTATUS DEL PROYECTO': 'OBSERVACIONES',
        'SUPERVISOR INTERNO UCEE ACTUAL': 'SUPERVISOR',
        'SNIP': 'SNIP',
        'NOG': 'NOG',
        'CONTRATO': 'CONTRATO',
        'LATITUD': 'LATITUD',
        'LONGITUD': 'LONGITUD',
        'FECHA DE INICIO': 'FECHA_INICIO',
        'FECHA FINALIZACION': 'FECHA_FIN',
        'PLAZO CONTRACTUAL': 'PLAZO_CONTRACTUAL',
        'PRORROGA': 'PRORROGA',
        'EMPRESA': 'EMPRESA',
        'NIT': 'NIT',
        'MONTO DE CONTRATO ORIGINAL': 'MONTO_ORIGINAL',
        'DOCUMENTOS DE CAMBIO': 'DOCUMENTOS_CAMBIO',
        'MONTO DE CONTRATO MODIFICADO': 'MONTO_MODIFICADO',
        'MONTO PAGADO': 'MONTO_PAGADO',
        'SALDO PENDIENTE POR PAGAR': 'SALDO_PENDIENTE'
    }
    
    # Renombrar solo columnas que existen
    columnas_existentes = {k: v for k, v in columnas_rename.items() if k in df.columns}
    df.rename(columns=columnas_existentes, inplace=True)
    
    # Convertir columnas numéricas
    columnas_numericas = ['AVANCE_FISICO', 'AVANCE_FINANCIERO', 'MONTO_ORIGINAL', 
                          'MONTO_MODIFICADO', 'MONTO_PAGADO', 'SALDO_PENDIENTE', 
                          'PLAZO_CONTRACTUAL', 'LATITUD', 'LONGITUD']
    
    for col in columnas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Limpiar porcentajes (remover el signo % si existe)
    if 'AVANCE_FISICO' in df.columns:
        df['AVANCE_FISICO'] = df['AVANCE_FISICO'].astype(str).str.replace('%', '').astype(float)
    if 'AVANCE_FINANCIERO' in df.columns:
        df['AVANCE_FINANCIERO'] = df['AVANCE_FINANCIERO'].astype(str).str.replace('%', '').astype(float)
    
    # Convertir fechas
    columnas_fechas = ['FECHA_INICIO', 'FECHA_FIN']
    for col in columnas_fechas:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    return df

# Cargar datos
try:
    df = load_data()
    if df is not None and not df.empty:
        st.success(f"✅ Datos cargados correctamente: {len(df)} proyectos")
    else:
        st.error("❌ No se encontraron datos en el archivo")
        st.stop()
except Exception as e:
    st.error(f"❌ Error al cargar datos: {e}")
    st.info("📝 Asegúrate de que el archivo 'followingmatrix.xlsx' existe en el mismo directorio")
    st.stop()

# ============================================
# FILTROS JERÁRQUICOS
# ============================================
st.sidebar.header("🔍 Filtros")

# FILTRO 1: AÑO (Principal)
st.sidebar.subheader("📅 1. Seleccionar Año")
años_disponibles = sorted(df['ANIO_INICIO'].unique())
años_seleccionados = st.sidebar.multiselect(
    "Año de inicio",
    options=años_disponibles,
    default=años_disponibles
)

df_filtrado = df[df['ANIO_INICIO'].isin(años_seleccionados)]

if df_filtrado.empty:
    st.warning("⚠️ No hay proyectos en los años seleccionados.")
    st.stop()

# FILTRO 2: INSTITUCIÓN
st.sidebar.subheader("🏛️ 2. Seleccionar Institución")
instituciones_disponibles = sorted(df_filtrado['INSTITUCION'].unique())
instituciones_seleccionadas = st.sidebar.multiselect(
    "Institución",
    options=instituciones_disponibles,
    default=instituciones_disponibles
)

df_filtrado = df_filtrado[df_filtrado['INSTITUCION'].isin(instituciones_seleccionadas)]

if df_filtrado.empty:
    st.warning("⚠️ No hay proyectos para las instituciones seleccionadas.")
    st.stop()

# FILTRO 3: Tipo de Proyecto
st.sidebar.subheader("📁 3. Tipo de Proyecto")
tipos_disponibles = sorted(df_filtrado['TIPO_PROYECTO'].unique())
tipos_seleccionados = st.sidebar.multiselect(
    "Tipo de Proyecto",
    options=tipos_disponibles,
    default=tipos_disponibles
)

df_filtrado = df_filtrado[df_filtrado['TIPO_PROYECTO'].isin(tipos_seleccionados)]

# FILTRO 4: Departamento
st.sidebar.subheader("🗺️ 4. Departamento")
departamentos_disponibles = sorted(df_filtrado['DEPARTAMENTO'].unique())
departamentos_seleccionados = st.sidebar.multiselect(
    "Departamento",
    options=departamentos_disponibles,
    default=departamentos_disponibles
)

df_filtrado = df_filtrado[df_filtrado['DEPARTAMENTO'].isin(departamentos_seleccionados)]

# FILTRO 5: Estatus
st.sidebar.subheader("📌 5. Estatus")
estatus_disponibles = sorted(df_filtrado['ESTATUS'].unique())
estatus_seleccionados = st.sidebar.multiselect(
    "Estatus",
    options=estatus_disponibles,
    default=estatus_disponibles
)

df_filtrado = df_filtrado[df_filtrado['ESTATUS'].isin(estatus_seleccionados)]

# FILTRO 6: Rango de Avance
st.sidebar.subheader("📈 6. Rango de Avance Físico")
rango_avance = st.sidebar.slider(
    "Porcentaje de avance (%)",
    min_value=0,
    max_value=100,
    value=(0, 100)
)

df_filtrado = df_filtrado[
    df_filtrado['AVANCE_FISICO'].between(rango_avance[0], rango_avance[1])
]

# Resumen de filtros
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Resumen")
st.sidebar.info(f"""
**Años:** {len(años_seleccionados)}  
**Instituciones:** {len(instituciones_seleccionadas)}  
**Tipos:** {len(tipos_seleccionados)}  
**Departamentos:** {len(departamentos_seleccionados)}  
**Estatus:** {len(estatus_seleccionados)}  
**Proyectos:** {len(df_filtrado)}
""")

# ============================================
# MÉTRICAS PRINCIPALES
# ============================================
st.header("📈 Indicadores Clave")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Proyectos", len(df_filtrado))

with col2:
    avance_fisico = df_filtrado['AVANCE_FISICO'].mean()
    st.metric("Avance Físico Promedio", f"{avance_fisico:.1f}%")

with col3:
    avance_financiero = df_filtrado['AVANCE_FINANCIERO'].mean()
    st.metric("Avance Financiero Promedio", f"{avance_financiero:.1f}%")

with col4:
    monto_total = df_filtrado['MONTO_MODIFICADO'].sum()
    st.metric("Monto Total", f"Q{monto_total:,.2f}")

st.markdown("---")

# ============================================
# GRÁFICOS PRINCIPALES
# ============================================

# Gráfico 1: Evolución por año
st.subheader("📅 Evolución de Proyectos por Año")
proyectos_por_año = df_filtrado.groupby('ANIO_INICIO').size().reset_index(name='Cantidad')
fig_temporal = px.line(
    proyectos_por_año,
    x='ANIO_INICIO',
    y='Cantidad',
    markers=True,
    line_shape='linear'
)
fig_temporal.update_traces(line=dict(width=3), marker=dict(size=10))
st.plotly_chart(fig_temporal, use_container_width=True)

# Gráficos en dos columnas
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Avance por Tipo de Proyecto")
    avance_por_tipo = df_filtrado.groupby('TIPO_PROYECTO')[['AVANCE_FISICO', 'AVANCE_FINANCIERO']].mean().reset_index()
    fig_avance = px.bar(
        avance_por_tipo,
        x='TIPO_PROYECTO',
        y=['AVANCE_FISICO', 'AVANCE_FINANCIERO'],
        barmode='group',
        title="Avance Promedio por Tipo",
        labels={'value': 'Porcentaje (%)', 'variable': 'Tipo'}
    )
    st.plotly_chart(fig_avance, use_container_width=True)

with col2:
    st.subheader("💰 Montos por Institución")
    montos_inst = df_filtrado.groupby('INSTITUCION')['MONTO_MODIFICADO'].sum().reset_index()
    montos_inst = montos_inst.sort_values('MONTO_MODIFICADO', ascending=True).head(10)
    fig_montos = px.bar(
        montos_inst,
        x='MONTO_MODIFICADO',
        y='INSTITUCION',
        orientation='h',
        title="Top 10 Instituciones",
        labels={'MONTO_MODIFICADO': 'Monto (Q)'}
    )
    st.plotly_chart(fig_montos, use_container_width=True)

# Matriz de avance
st.subheader("🎯 Matriz de Avance Físico vs Financiero")
fig_scatter = px.scatter(
    df_filtrado,
    x='AVANCE_FISICO',
    y='AVANCE_FINANCIERO',
    color='ESTATUS',
    size='MONTO_MODIFICADO',
    hover_data=['NOMBRE_PROYECTO', 'INSTITUCION', 'EMPRESA'],
    title="Relación entre Avances"
)
fig_scatter.add_trace(
    go.Scatter(
        x=[0, 100],
        y=[0, 100],
        mode='lines',
        name='Línea Ideal',
        line=dict(dash='dash', color='gray')
    )
)
st.plotly_chart(fig_scatter, use_container_width=True)

# ============================================
# MAPAS
# ============================================
st.header("🗺️ Visualización Geográfica")

try:
    import folium
    from streamlit_folium import folium_static
    from folium.plugins import MarkerCluster, HeatMap
    
    # Proyectos con coordenadas
    proyectos_con_coords = df_filtrado.dropna(subset=['LATITUD', 'LONGITUD']).copy()
    
    if len(proyectos_con_coords) > 0:
        center_lat = proyectos_con_coords['LATITUD'].mean()
        center_lon = proyectos_con_coords['LONGITUD'].mean()
        
        tab1, tab2 = st.tabs(["📍 Mapa de Proyectos", "🔥 Mapa de Calor"])
        
        with tab1:
            m = folium.Map(location=[center_lat, center_lon], zoom_start=8, control_scale=True)
            marker_cluster = MarkerCluster().add_to(m)
            
            for _, row in proyectos_con_coords.iterrows():
                popup = f"""
                <b>{row['NOMBRE_PROYECTO']}</b><br>
                <b>Institución:</b> {row['INSTITUCION']}<br>
                <b>Ubicación:</b> {row['MUNICIPIO']}, {row['DEPARTAMENTO']}<br>
                <b>Avance:</b> {row['AVANCE_FISICO']:.1f}%<br>
                <b>Monto:</b> Q{row['MONTO_MODIFICADO']:,.2f}<br>
                <b>Empresa:</b> {row['EMPRESA']}
                """
                folium.Marker(
                    location=[row['LATITUD'], row['LONGITUD']],
                    popup=folium.Popup(popup, max_width=300),
                    tooltip=row['NOMBRE_PROYECTO']
                ).add_to(marker_cluster)
            
            folium_static(m, width=1200, height=500)
            
        with tab2:
            heat_data = [[row['LATITUD'], row['LONGITUD']] for _, row in proyectos_con_coords.iterrows()]
            heat_map = folium.Map(location=[center_lat, center_lon], zoom_start=8)
            HeatMap(heat_data, radius=15, blur=10).add_to(heat_map)
            folium_static(heat_map, width=1200, height=500)
    else:
        st.info("ℹ️ No hay proyectos con coordenadas válidas")
        
except ImportError:
    st.warning("⚠️ Librerías de mapas no instaladas")

# ============================================
# TABLA DE DATOS
# ============================================
st.subheader("📋 Detalle de Proyectos")

columnas_mostrar = [
    'ID', 'NOMBRE_PROYECTO', 'ANIO_INICIO', 'INSTITUCION', 'TIPO_PROYECTO',
    'DEPARTAMENTO', 'MUNICIPIO', 'AVANCE_FISICO', 'AVANCE_FINANCIERO',
    'ESTATUS', 'MONTO_MODIFICADO', 'EMPRESA'
]

columnas_existentes = [col for col in columnas_mostrar if col in df_filtrado.columns]

busqueda = st.text_input("🔍 Buscar proyecto:", "")
if busqueda:
    df_filtrado = df_filtrado[df_filtrado['NOMBRE_PROYECTO'].str.contains(busqueda, case=False, na=False)]

st.dataframe(
    df_filtrado[columnas_existentes].style.format({
        'AVANCE_FISICO': '{:.1f}%',
        'AVANCE_FINANCIERO': '{:.1f}%',
        'MONTO_MODIFICADO': 'Q{:,.2f}'
    }),
    use_container_width=True,
    height=400
)

# ============================================
# ALERTAS
# ============================================
st.subheader("⚠️ Alertas")

proyectos_criticos = df_filtrado[df_filtrado['AVANCE_FISICO'] < 30]
if len(proyectos_criticos) > 0:
    st.warning(f"🚨 {len(proyectos_criticos)} proyectos con avance menor al 30%")
    st.dataframe(proyectos_criticos[['NOMBRE_PROYECTO', 'INSTITUCION', 'AVANCE_FISICO', 'EMPRESA']])

proyectos_atraso = df_filtrado[df_filtrado['SALDO_PENDIENTE'] > df_filtrado['MONTO_MODIFICADO'] * 0.3]
if len(proyectos_atraso) > 0:
    st.info(f"📉 {len(proyectos_atraso)} proyectos con saldo pendiente mayor al 30%")

# ============================================
# EXPORTAR
# ============================================
st.sidebar.markdown("---")
st.sidebar.subheader("📥 Exportar")

if st.sidebar.button("Exportar a CSV"):
    csv = df_filtrado.to_csv(index=False)
    st.sidebar.download_button(
        label="Descargar",
        data=csv,
        file_name=f"proyectos_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# ============================================
# INFORMACIÓN
# ============================================
with st.expander("ℹ️ Información"):
    st.markdown(f"""
    **Resumen:**
    - Total proyectos: {len(df_filtrado)}
    - Monto total: Q{df_filtrado['MONTO_MODIFICADO'].sum():,.2f}
    - Avance promedio: {df_filtrado['AVANCE_FISICO'].mean():.1f}%
    - Empresas: {df_filtrado['EMPRESA'].nunique()}
    - Instituciones: {df_filtrado['INSTITUCION'].nunique()}
    """)

st.markdown("---")
st.markdown(f"📅 Actualizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
