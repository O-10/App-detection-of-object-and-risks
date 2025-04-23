import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from io import BytesIO
from fpdf import FPDF

# Configuración de correo electrónico
sender_email = 'arisergte@gmail.com'  # Reemplaza con tu correo
password = 'Oscar10-'  # Usa una contraseña de aplicación si usas Gmail
smtp_server = 'smtp.gmail.com'
smtp_port = 587

# Diccionario de usuarios
users = {'admin': 'admin123', 'usuario1': 'clave123'}

# Función para enviar correo
def send_email(user_email, password):
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, password)

        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = user_email
        message['Subject'] = 'Acceso al Sistema'

        body = f'Hola, \n\nTu cuenta ha sido creada. Tu usuario es: {user_email} y tu contraseña temporal es: {password}'
        message.attach(MIMEText(body, 'plain'))

        server.sendmail(sender_email, user_email, message.as_string())
        server.quit()
        st.success('Correo enviado exitosamente!')
    except Exception as e:
        st.error(f'Error al enviar el correo: {e}')

# Función para cargar archivo y mostrar análisis
def load_and_analyze_file(uploaded_file):
    df = pd.read_excel(uploaded_file)

    # Mostrar los datos en una tabla
    st.write(df)

    # Análisis: Calculando el nivel de riesgo promedio
    if 'Nivel de Riesgo' in df.columns:
        avg_risk = df['Nivel de Riesgo'].mean()
        st.write(f'Nivel de riesgo promedio: {avg_risk}')

        # Generar gráfico de barras
        plt.figure(figsize=(10, 6))
        df.groupby('Área')['Nivel de Riesgo'].mean().plot(kind='bar', color='skyblue')
        plt.title('Nivel de Riesgo por Área')
        plt.xlabel('Área')
        plt.ylabel('Nivel de Riesgo')
        st.pyplot(plt)

# Función para generar el PDF
def generate_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Título
    pdf.cell(200, 10, txt="Informe de Riesgos Laborales", ln=True, align='C')

    # Agregar tabla con los datos
    for i in range(df.shape[0]):
        row = df.iloc[i]
        row_str = ' | '.join(str(x) for x in row)
        pdf.multi_cell(0, 10, row_str)

    # Guardar el archivo en un buffer
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)

    return pdf_output

# Página de login
def login():
    st.title('Sistema de Gestión de Riesgos Laborales')

    # Campos de autenticación
    username = st.text_input('Nombre de usuario')
    password = st.text_input('Contraseña', type='password')

    if st.button('Iniciar sesión'):
        if username in users and users[username] == password:
            st.success(f'¡Bienvenido {username}!')
            return True
        else:
            st.error('Credenciales incorrectas')
            return False
    return False

# Página principal
def main():
    if login():
        page = st.sidebar.radio('Ir a:', ['Cargar Datos', 'Generar Informe PDF', 'Análisis de Riesgos'])

        if page == 'Cargar Datos':
            uploaded_file = st.file_uploader("Carga un archivo Excel", type=["xlsx"])
            if uploaded_file is not None:
                load_and_analyze_file(uploaded_file)

        elif page == 'Generar Informe PDF':
            df = pd.DataFrame({'Área': ['Área 1', 'Área 2'], 'Nivel de Riesgo': [3, 7]})  # Ejemplo de datos
            if st.button('Generar PDF'):
                pdf = generate_pdf(df)
                st.download_button("Descargar Informe", pdf, "informe_riesgo.pdf")

        elif page == 'Análisis de Riesgos':
            st.write("Aquí puedes realizar el análisis de riesgos laborales.")
            # Implementa el análisis según tu flujo de trabajo

# Ejecutar la app
if __name__ == '__main__':
    main()
