import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import io
from PIL import Image  # Para mostrar una imagen (opcional)

# --- USUARIOS ---
users = {
    "usuario1": "Ariser10",
    "oscar": "Lolita40"
}

# --- LOGIN ---
def login():
    st.sidebar.title("🔐 Iniciar sesión")
    username = st.sidebar.text_input("Usuario")
    password = st.sidebar.text_input("Contraseña", type="password")

    if st.sidebar.button("Ingresar"):
        if username in users and users[username] == password:
            st.session_state["logged_in"] = True
            st.session_state["user"] = username
            st.success(f"Bienvenido, {username}")
            st.rerun()
        else:
            st.sidebar.error("Credenciales incorrectas")
    st.sidebar.markdown("---")
    st.sidebar.markdown("Creado por: Oscar Iván Solarte")
    st.sidebar.markdown("Profesional en SST y Estudiante en Ciencia de datos e Inteligencia Artificial.")
    st.sidebar.markdown("Más información: 3154013707")

# --- INTERPRETACIÓN SST ---
def interpretar_grafico(df):
    area_mayor_riesgo = df.loc[df["Nivel de Riesgo"].idxmax(), "Área"]
    riesgo_max = df["Nivel de Riesgo"].max()
    riesgo_promedio = df["Nivel de Riesgo"].mean()

    texto = f"""📊 INTERPRETACIÓN:
- Área con mayor riesgo: {area_mayor_riesgo} (nivel {riesgo_max})
- Riesgo promedio: {riesgo_promedio:.2f}\n"""

    if riesgo_max >= 8:
        texto += f"""\n⚠️ Riesgo ALTO:
- Intervención inmediata
- Inspecciones
- Verificar EPP
- Reentrenar personal
- Controles de ingeniería"""
    elif 5 <= riesgo_max < 8:
        texto += f"""\n🔶 Riesgo MODERADO:
- Plan preventivo
- Procedimientos seguros
- Señalización
- Monitoreo continuo"""
    else:
        texto += f"""\n🟢 Riesgo BAJO:
- Mantener controles
- Buenas prácticas
- Seguimiento periódico"""

    st.markdown(texto)
    return texto

# --- APP PRINCIPAL ---
def main_app():
    st.title("🤖 App de Detección de Riesgos Laborales")  # Título con emoji de robot

    uploaded_file = st.file_uploader("Sube tu archivo Excel (.xlsx)", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.subheader("Datos cargados:")
        st.dataframe(df)

        st.subheader("📈 Gráfico de Niveles de Riesgo por Área")
        fig, ax = plt.subplots()
        ax.bar(df["Área"], df["Nivel de Riesgo"], color="orange")
        ax.set_xlabel("Área")
        ax.set_ylabel("Nivel de Riesgo")
        ax.set_title("Análisis de Riesgo por Área")
        st.pyplot(fig)

        interpretar_grafico(df)

        # --- DESCARGA DE CSV ---
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Descargar datos como CSV",
            data=csv,
            file_name='datos_riesgos.csv',
            mime='text/csv'
        )

# --- CONTROL DE FLUJO ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.title("Bienvenido a la App de Riesgos Laborales")
    st.write("Por favor, inicia sesión en la barra lateral para acceder a las herramientas de análisis.")
    try:
        ia_logo = Image.open("ia_logo.png")  # Reemplaza "ia_logo.png" con la ruta de tu imagen de IA
        st.image(ia_logo, caption="Análisis con Inteligencia Artificial", width=300)
    except FileNotFoundError:
        st.warning("Imagen de IA no encontrada. Asegúrate de que 'ia_logo.png' esté en la misma carpeta.")
    st.write("Una vez que inicies sesión, podrás subir tu archivo Excel y visualizar el análisis de riesgos.")
else:
    main_app()

if __name__ == "__main__":
    main()
