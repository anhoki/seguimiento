import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import folium_static
import geopandas as gpd
from shapely.geometry import Point

@st.cache_data
def cargar_datos():
    try:
        # Leer tu archivo Excel
        df = pd.read_excel('BD encabezados.xlsx')  # Ajusta la ruta
        
        # Lista de columnas que deben ser numéricas
        columnas_numericas = [
            'AVANCE DE DISEÑO Y PLANIFICACIÓN (%)',
            'AVANCE EN PLANIFICACION',
            'REVISIÓN DE ESPECIALISTA ESTRUCTURAL',
            'REVISIÓN DE ESPECIALISTA AMBIENTAL',
            'REVISIÓN DE ESPECIALISTA EN TIERRAS',
            'REVISIÓN DE ESPECIALISTA ELECTRICISTA',
            'REVISIÓN DE ESPECIALISTA GEOLOGO',
            'AVANCE EN RENGLONEO Y CUANTIFICACION',
            'AVANCE EN PERFIL DEL PROYECTO',
            'AVANCE AVAL CONRED',
            'AVANCE EXPEDIENTE SANITARIO MSPAS',
            'AVANCE EN DOCUMENTOS SUBIDOS AL SNIP',
            'Metros cuadrados de la edificacion',
            'Monto del Contrato de Planificación Externa',
            'Monto pagado a la fecha'
        ]
        
        # Convertir cada columna a numérico, forzando errores a NaN
        for col in columnas_numericas:
            if col in df.columns:
                # Eliminar caracteres especiales como '%', 'Q', etc.
                df[col] = df[col].astype(str).str.replace('%', '', regex=False)
                df[col] = df[col].astype(str).str.replace('Q', '', regex=False)
                df[col] = df[col].astype(str).str.replace(',', '', regex=False)
                df[col] = df[col].astype(str).str.strip()
                
                # Convertir a numérico
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Convertir columnas de fecha
        columnas_fecha = [
            'FECHA DE ASIGNACION/CONTRATO',
            'FECHA ESTIMADA DE ENTREGA DEL PROYECTO',
            'FECHA DE ENTREGA SEGUN CONTRATO'
        ]
        
        for col in columnas_fecha:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Eliminar filas con valores nulos en columnas críticas
        df = df.dropna(subset=['PROYECTO', 'AVANCE DE DISEÑO Y PLANIFICACIÓN (%)'])
        
        # Llenar valores nulos con 0 en columnas numéricas
        for col in columnas_numericas:
            if col in df.columns:
                df[col] = df[col].fillna(0)
        
        st.sidebar.success(f"✅ Datos cargados: {len(df)} registros")
        return df
        
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        # Datos de ejemplo como respaldo
        return crear_datos_ejemplo()

def crear_datos_ejemplo():
    """Función de respaldo con datos de ejemplo"""
    data = {
        'NO.': [1, 2, 3],
        'PROYECTO': ['Proyecto A', 'Proyecto B', 'Proyecto C'],
        'AVANCE DE DISEÑO Y PLANIFICACIÓN (%)': [45, 70, 30],
        'DEPARTAMENTO': ['Guatemala', 'Sacatepéquez', 'Escuintla'],
        'MUNICIPIO': ['Guatemala', 'Antigua', 'Escuintla'],
        # ... agregar más columnas según necesites
    }
    return pd.DataFrame(data)

# Cargar datos
df = cargar_datos()

# Sidebar - Filtros
st.sidebar.header("🔍 Filtros")

# Filtros múltiples
departamentos = st.sidebar.multiselect(
    "Seleccionar Departamento",
    options=df['DEPARTAMENTO'].unique(),
    default=df['DEPARTAMENTO'].unique()
)

municipios = st.sidebar.multiselect(
    "Seleccionar Municipio",
    options=df['MUNICIPIO'].unique(),
    default=df['MUNICIPIO'].unique()
)

tipo_proyecto = st.sidebar.multiselect(
    "Tipo de Proyecto",
    options=df['TIPO'].unique(),
    default=df['TIPO'].unique()
)

personal_ucee = st.sidebar.multiselect(
    "Personal UCEE",
    options=df['PERSONAL UCEE'].unique(),
    default=df['PERSONAL UCEE'].unique()
)

# Aplicar filtros
df_filtrado = df[
    (df['DEPARTAMENTO'].isin(departamentos)) &
    (df['MUNICIPIO'].isin(municipios)) &
    (df['TIPO'].isin(tipo_proyecto)) &
    (df['PERSONAL UCEE'].isin(personal_ucee))
]

# Métricas principales en la parte superior
st.subheader("📈 Métricas Generales")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Proyectos",
        len(df_filtrado),
        delta=f"{len(df_filtrado) - len(df)} vs total"
    )

with col2:
    avance_promedio = df_filtrado['AVANCE DE DISEÑO Y PLANIFICACIÓN (%)'].mean()
    st.metric(
        "Avance Promedio",
        f"{avance_promedio:.1f}%",
        delta=f"{avance_promedio - df['AVANCE DE DISEÑO Y PLANIFICACIÓN (%)'].mean():.1f}% vs global"
    )

with col3:
    monto_total = df_filtrado['Monto del Contrato de Planificación Externa'].sum()
    st.metric(
        "Monto Total Contratos",
        f"Q{monto_total:,.0f}"
    )

with col4:
    monto_pagado = df_filtrado['Monto pagado a la fecha'].sum()
    porcentaje_pagado = (monto_pagado / monto_total * 100) if monto_total > 0 else 0
    st.metric(
        "Monto Pagado",
        f"Q{monto_pagado:,.0f}",
        delta=f"{porcentaje_pagado:.1f}% del total"
    )

st.markdown("---")

# Pestañas para organizar la información
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Vista General",
    "📊 Avances por Especialidad",
    "💰 Gestión Financiera",
    "📅 Cronograma",
    "🗺️ Geolocalización"
])

with tab1:
    st.subheader("Tabla de Proyectos")
    
    # Selector de columnas a mostrar
    columnas_mostrar = st.multiselect(
        "Seleccionar columnas a mostrar",
        options=df_filtrado.columns.tolist(),
        default=['NO.', 'PROYECTO', 'PERSONAL UCEE', 'TIPO', 'MUNICIPIO', 
                 'DEPARTAMENTO', 'AVANCE DE DISEÑO Y PLANIFICACIÓN (%)']
    )
    
    if columnas_mostrar:
        st.dataframe(
            df_filtrado[columnas_mostrar],
            use_container_width=True,
            hide_index=True
        )
    
    # Gráfico de avance por proyecto
    st.subheader("Avance por Proyecto")
    fig_avance = px.bar(
        df_filtrado,
        x='PROYECTO',
        y='AVANCE DE DISEÑO Y PLANIFICACIÓN (%)',
        color='TIPO',
        title="Porcentaje de Avance por Proyecto",
        labels={'AVANCE DE DISEÑO Y PLANIFICACIÓN (%)': 'Avance (%)'}
    )
    st.plotly_chart(fig_avance, use_container_width=True)

with tab2:
    st.subheader("Avances por Especialidad")
    
    # Selección de proyecto para ver detalles
    proyecto_seleccionado = st.selectbox(
        "Seleccionar Proyecto para ver detalles",
        options=df_filtrado['PROYECTO'].tolist()
    )
    
    if proyecto_seleccionado:
        df_proyecto = df_filtrado[df_filtrado['PROYECTO'] == proyecto_seleccionado].iloc[0]
        
        # Gráfico radial de avances por especialidad
        especialidades = [
            'REVISIÓN DE ESPECIALISTA ESTRUCTURAL',
            'REVISIÓN DE ESPECIALISTA AMBIENTAL',
            'REVISIÓN DE ESPECIALISTA EN TIERRAS',
            'REVISIÓN DE ESPECIALISTA ELECTRICISTA',
            'REVISIÓN DE ESPECIALISTA GEOLOGO'
        ]
        
        valores = [df_proyecto[esp] for esp in especialidades]
        
        fig = go.Figure(data=go.Scatterpolar(
            r=valores,
            theta=especialidades,
            fill='toself'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=False,
            title=f"Avances por Especialidad - {proyecto_seleccionado}"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabla de avances específicos
        st.subheader("Detalle de Avances")
        avances_detalle = {
            'Área': ['Planificación', 'Rengloneo', 'Perfil', 'Aval CONRED', 
                     'Expediente MSPAS', 'Documentos SNIP'],
            'Avance (%)': [
                df_proyecto['AVANCE EN PLANIFICACION'],
                df_proyecto['AVANCE EN RENGLONEO Y CUANTIFICACION'],
                df_proyecto['AVANCE EN PERFIL DEL PROYECTO'],
                df_proyecto['AVANCE AVAL CONRED'],
                df_proyecto['AVANCE EXPEDIENTE SANITARIO MSPAS'],
                df_proyecto['AVANCE EN DOCUMENTOS SUBIDOS AL SNIP']
            ]
        }
        df_avances = pd.DataFrame(avances_detalle)
        st.dataframe(df_avances, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Gestión Financiera")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de montos por proyecto
        fig_montos = px.bar(
            df_filtrado,
            x='PROYECTO',
            y=['Monto del Contrato de Planificación Externa', 'Monto pagado a la fecha'],
            title="Montos de Contrato vs Pagado por Proyecto",
            barmode='group'
        )
        st.plotly_chart(fig_montos, use_container_width=True)
    
    with col2:
        # Gráfico de torta - distribución por tipo
        fig_pie = px.pie(
            df_filtrado,
            values='Monto del Contrato de Planificación Externa',
            names='TIPO',
            title="Distribución de Montos por Tipo de Proyecto"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Tabla financiera
    st.subheader("Detalle Financiero")
    columnas_financieras = ['PROYECTO', 'Monto del Contrato de Planificación Externa', 
                           'Monto pagado a la fecha', 'Metros cuadrados de la edificacion']
    st.dataframe(
        df_filtrado[columnas_financieras],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Monto del Contrato de Planificación Externa": st.column_config.NumberColumn(format="Q%d"),
            "Monto pagado a la fecha": st.column_config.NumberColumn(format="Q%d")
        }
    )

with tab4:
    st.subheader("Cronograma de Proyectos")
    
    # Preparar datos para el diagrama de Gantt
    df_gantt = df_filtrado.copy()
    df_gantt['Inicio'] = df_gantt['FECHA DE ASIGNACION/CONTRATO']
    df_gantt['Fin'] = df_gantt['FECHA ESTIMADA DE ENTREGA DEL PROYECTO']
    
    fig_gantt = px.timeline(
        df_gantt,
        x_start="Inicio",
        x_end="Fin",
        y="PROYECTO",
        color="TIPO",
        title="Cronograma de Proyectos",
        labels={"PROYECTO": "Proyecto"}
    )
    fig_gantt.update_yaxes(autorange="reversed")
    st.plotly_chart(fig_gantt, use_container_width=True)
    
    # Tabla de fechas
    st.subheader("Fechas Clave")
    columnas_fechas = ['PROYECTO', 'FECHA DE ASIGNACION/CONTRATO', 
                       'FECHA ESTIMADA DE ENTREGA DEL PROYECTO', 
                       'FECHA DE ENTREGA SEGUN CONTRATO']
    st.dataframe(
        df_filtrado[columnas_fechas],
        use_container_width=True,
        hide_index=True
    )

with tab5:
    st.subheader("🗺️ Distribución Geográfica")
    
    # Filtros en la misma pestaña
    col1, col2 = st.columns(2)
    
    with col1:
        # Filtro de departamentos (único o múltiple)
        departamentos_disponibles = df_filtrado['DEPARTAMENTO'].dropna().unique()
        
        if len(departamentos_disponibles) > 0:
            # Opción para seleccionar tipo de visualización
            tipo_seleccion = st.radio(
                "Seleccionar departamentos:",
                ["Un departamento", "Múltiples departamentos"],
                key="tipo_seleccion_mapa"
            )
            
            if tipo_seleccion == "Un departamento":
                depto_seleccionado = st.selectbox(
                    "Seleccionar departamento:",
                    options=sorted(departamentos_disponibles),
                    key="depto_unico"
                )
                deptos_filtro = [depto_seleccionado]
            else:
                deptos_filtro = st.multiselect(
                    "Seleccionar departamentos:",
                    options=sorted(departamentos_disponibles),
                    default=sorted(departamentos_disponibles)[:3] if len(departamentos_disponibles) > 0 else [],
                    key="depto_multiple"
                )
        else:
            st.warning("No hay datos de departamentos disponibles")
            deptos_filtro = []
    
    with col2:
        # Filtro de municipios (dependiente del departamento seleccionado)
        if deptos_filtro:
            # Filtrar municipios por los departamentos seleccionados
            municipios_disponibles = df_filtrado[
                df_filtrado['DEPARTAMENTO'].isin(deptos_filtro)
            ]['MUNICIPIO'].dropna().unique()
            
            if len(municipios_disponibles) > 0:
                municipios_seleccionados = st.multiselect(
                    "Filtrar por municipios (opcional):",
                    options=sorted(municipios_disponibles),
                    key="municipios_mapa"
                )
            else:
                municipios_seleccionados = []
                st.info("No hay municipios disponibles para los departamentos seleccionados")
        else:
            municipios_seleccionados = []
            st.info("Selecciona al menos un departamento")
    
    # Aplicar filtros
    df_mapa = df_filtrado.copy()
    
    if deptos_filtro:
        df_mapa = df_mapa[df_mapa['DEPARTAMENTO'].isin(deptos_filtro)]
    
    if municipios_seleccionados:
        df_mapa = df_mapa[df_mapa['MUNICIPIO'].isin(municipios_seleccionados)]
    
    # Verificar si hay datos para mostrar
    if len(df_mapa) == 0:
        st.warning("No hay proyectos que coincidan con los filtros seleccionados")
    else:
        # Crear mapa interactivo con Folium
        st.markdown("### Mapa de Proyectos")
        
        # Coordenadas aproximadas de Guatemala (centro)
        lat_centro, lon_centro = 15.7835, -90.2308
        
        # Crear mapa base
        m = folium.Map(
            location=[lat_centro, lon_centro],
            zoom_start=7,
            tiles='OpenStreetMap'
        )
        
        # Diccionario de colores para tipos de proyecto
        colores_tipo = {
            'Nuevo': 'green',
            'Reforma': 'blue',
            'Mantenimiento': 'orange',
            'Ampliación': 'purple',
            'Remodelación': 'red',
            'Otro': 'gray'
        }
        
        # Agrupar por municipio para mostrar conteo
        df_agrupado = df_mapa.groupby(['DEPARTAMENTO', 'MUNICIPIO']).agg({
            'PROYECTO': 'count',
            'Monto del Contrato de Planificación Externa': 'sum',
            'AVANCE DE DISEÑO Y PLANIFICACIÓN (%)': 'mean'
        }).reset_index()
        
        df_agrupado.columns = ['DEPARTAMENTO', 'MUNICIPIO', 'Cantidad Proyectos', 
                               'Monto Total', 'Avance Promedio']
        
        # Aquí necesitarías tener coordenadas reales de los municipios
        # Por ahora, usaré coordenadas aproximadas
        # Idealmente, tendrías un archivo con las coordenadas de cada municipio
        
        # Si no tienes coordenadas reales, puedes crear puntos aleatorios alrededor del centro
        import random
        
        for idx, row in df_agrupado.iterrows():
            # Generar coordenadas aleatorias cercanas al centro del departamento
            # (Esto es solo un ejemplo, idealmente usarías coordenadas reales)
            lat = lat_centro + random.uniform(-1, 1)
            lon = lon_centro + random.uniform(-1, 1)
            
            # Determinar color basado en el tipo de proyecto principal
            # (Esto es simplificado, idealmente tendrías el tipo en los datos)
            color = 'blue'
            if row['Avance Promedio'] > 75:
                color = 'green'
            elif row['Avance Promedio'] > 50:
                color = 'orange'
            elif row['Avance Promedio'] > 25:
                color = 'red'
            else:
                color = 'gray'
            
            # Crear popup con información
            popup_text = f"""
            <b>{row['MUNICIPIO']}, {row['DEPARTAMENTO']}</b><br>
            Proyectos: {row['Cantidad Proyectos']}<br>
            Monto Total: Q{row['Monto Total']:,.0f}<br>
            Avance Promedio: {row['Avance Promedio']:.1f}%
            """
            
            # Añadir marcador
            folium.Marker(
                [lat, lon],
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=f"{row['MUNICIPIO']} ({row['Cantidad Proyectos']} proyectos)",
                icon=folium.Icon(color=color, icon='info-sign')
            ).add_to(m)
        
        # Añadir capa de calor si hay suficientes puntos
        if len(df_agrupado) > 3:
            from folium.plugins import HeatMap
            
            # Preparar datos para heatmap
            heat_data = []
            for idx, row in df_agrupado.iterrows():
                lat = lat_centro + random.uniform(-1, 1)
                lon = lon_centro + random.uniform(-1, 1)
                weight = row['Cantidad Proyectos']  # Peso por cantidad de proyectos
                heat_data.append([lat, lon, weight])
            
            # Añadir heatmap
            HeatMap(heat_data, radius=15, blur=10).add_to(m)
        
        # Mostrar el mapa
        folium_static(m, width=800, height=500)
        
        # Estadísticas adicionales
        st.markdown("### 📊 Resumen por área seleccionada")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Proyectos", len(df_mapa))
        
        with col2:
            st.metric("Municipios", df_mapa['MUNICIPIO'].nunique())
        
        with col3:
            monto_total = df_mapa['Monto del Contrato de Planificación Externa'].sum()
            st.metric("Monto Total", f"Q{monto_total:,.0f}")
        
        with col4:
            avance_prom = df_mapa['AVANCE DE DISEÑO Y PLANIFICACIÓN (%)'].mean()
            st.metric("Avance Promedio", f"{avance_prom:.1f}%")
        
        # Tabla de municipios
        st.markdown("### 📋 Detalle por municipio")
        
        # Preparar tabla resumen
        tabla_municipios = df_mapa.groupby(['DEPARTAMENTO', 'MUNICIPIO']).agg({
            'PROYECTO': 'count',
            'Monto del Contrato de Planificación Externa': 'sum',
            'AVANCE DE DISEÑO Y PLANIFICACIÓN (%)': 'mean'
        }).round(2).reset_index()
        
        tabla_municipios.columns = ['Departamento', 'Municipio', 
                                    'Cantidad Proyectos', 'Monto Total', 
                                    'Avance Promedio (%)']
        
        # Formatear moneda
        tabla_municipios['Monto Total'] = tabla_municipios['Monto Total'].apply(
            lambda x: f"Q{x:,.0f}"
        )
        
        st.dataframe(
            tabla_municipios,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Avance Promedio (%)": st.column_config.NumberColumn(format="%.1f%%")
            }
        )
        
        # Gráfico de barras por municipio
        st.markdown("### 📈 Proyectos por municipio")
        
        fig_municipios = px.bar(
            tabla_municipios,
            x='Municipio',
            y='Cantidad Proyectos',
            color='Departamento',
            title="Cantidad de proyectos por municipio",
            labels={'Cantidad Proyectos': 'Número de proyectos'}
        )
        fig_municipios.update_xaxis(tickangle=45)
        st.plotly_chart(fig_municipios, use_container_width=True)
# Footer con información adicional
st.markdown("---")
st.markdown("📅 Última actualización: " + datetime.now().strftime("%d/%m/%Y %H:%M"))
