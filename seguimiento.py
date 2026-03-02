import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

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
    st.subheader("Distribución Geográfica")
    
    # Gráfico de barras por departamento
    df_departamento = df_filtrado.groupby('DEPARTAMENTO').agg({
        'PROYECTO': 'count',
        'Monto del Contrato de Planificación Externa': 'sum'
    }).reset_index()
    df_departamento.columns = ['DEPARTAMENTO', 'Cantidad Proyectos', 'Monto Total']
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_dep = px.bar(
            df_departamento,
            x='DEPARTAMENTO',
            y='Cantidad Proyectos',
            title="Proyectos por Departamento"
        )
        st.plotly_chart(fig_dep, use_container_width=True)
    
    with col2:
        fig_dep_monto = px.bar(
            df_departamento,
            x='DEPARTAMENTO',
            y='Monto Total',
            title="Monto Total por Departamento"
        )
        st.plotly_chart(fig_dep_monto, use_container_width=True)
    
    # Tabla por municipio
    st.subheader("Detalle por Municipio")
    df_municipio = df_filtrado.groupby(['DEPARTAMENTO', 'MUNICIPIO']).agg({
        'PROYECTO': 'count',
        'Monto del Contrato de Planificación Externa': 'sum'
    }).reset_index()
    df_municipio.columns = ['DEPARTAMENTO', 'MUNICIPIO', 'Cantidad Proyectos', 'Monto Total']
    st.dataframe(df_municipio, use_container_width=True, hide_index=True)

# Footer con información adicional
st.markdown("---")
st.markdown("📅 Última actualización: " + datetime.now().strftime("%d/%m/%Y %H:%M"))
