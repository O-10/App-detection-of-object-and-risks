import streamlit as st
import cv2
import pandas as pd
import os
import random
from datetime import datetime, timedelta
from roboflow import Roboflow
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt

# 🔧 Configuración de la página
st.set_page_config(page_title="Análisis de Riesgos", layout="wide")
st.title("🦺 Detección de Riesgos en Tiempo Real")

# 🧠 Conectar con Roboflow
rf = Roboflow(api_key="ZTgQTJF0CA75bTfQixhE")
project = rf.workspace().project("construccion-oscar")
model = project.version(1).model

# 📁 Carpeta de frames
frame_folder = "frames"
os.makedirs(frame_folder, exist_ok=True)

# 🧠 Base de palabras clave
keywords_db = {
    "casco": "protección cabeza, evitar golpes",
    "arnés": "prevención caídas, altura",
    "chaleco": "alta visibilidad, maquinaria",
    "persona": "presencia humana, riesgo exposición",
    "escalera": "trabajo en altura, caída",
    "andamio": "estructura elevada, colapso"
}

def get_keywords(obj):
    corpus = list(keywords_db.values())
    keys = list(keywords_db.keys())
    if obj in keys:
        vectorizer = TfidfVectorizer()
        tfidf = vectorizer.fit_transform(corpus + [obj])
        sim = cosine_similarity(tfidf[-1], tfidf[:-1])
        idx = sim.argmax()
        return corpus[idx].split(", ")
    else:
        return ["riesgo", "precaución", "evaluar"]

def asignar_valor(lista, rep):
    base = random.choice(lista)
    return min(base + int(rep / 2), max(lista))

def procesar_frame(frame, frame_number, start_time):
    frame_path = os.path.join(frame_folder, f"frame_{frame_number}.jpg")
    cv2.imwrite(frame_path, frame)
    
    try:
        result = model.predict(frame_path, confidence=40, overlap=30)
        predictions = result.json().get("predictions", [])
    except:
        predictions = []

    eventos = []
    tiempo_simulado = (start_time + timedelta(seconds=frame_number * 2)).strftime("%H:%M:%S")

    for pred in predictions:
        objeto = pred["class"]
        palabras_clave = get_keywords(objeto)
        eventos.append({
            "frame": frame_number,
            "tiempo": tiempo_simulado,
            "objeto": objeto,
            "confidence": pred["confidence"],
            "palabras_clave": ", ".join(palabras_clave)
        })

        x, y, w, h = int(pred["x"]), int(pred["y"]), int(pred["width"]), int(pred["height"])
        cv2.rectangle(frame, (x - w//2, y - h//2), (x + w//2, y + h//2), (0, 255, 0), 2)
        cv2.putText(frame, objeto, (x - w//2, y - h//2 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    return frame, eventos

# 🎥 Capturar un solo frame desde la cámara o video
video_url = 0  # o reemplaza por una imagen o video
cap = cv2.VideoCapture(video_url)

if not cap.isOpened():
    st.error("❌ No se pudo acceder a la cámara")
    st.stop()

st.info("🔄 Capturando un frame para análisis...")
ret, frame = cap.read()
cap.release()

if not ret:
    st.error("❌ No se pudo capturar un frame")
    st.stop()

start_time = datetime.strptime("08:00:00", "%H:%M:%S")
frame_procesado, eventos = procesar_frame(frame, 0, start_time)

# Mostrar frame con detecciones
st.image(frame_procesado, channels="BGR", caption="Frame Analizado")

# Crear DataFrame y calcular riesgos
df = pd.DataFrame(eventos)
if not df.empty:
    df["repeticiones"] = df.groupby(["frame", "objeto"])["objeto"].transform("count")

    deficiencia_vals = [10, 6, 4, 2]
    exposicion_vals = [4, 3, 2, 1]
    consecuencia_vals = [100, 60, 25, 10]

    calculos = []
    for _, row in df.iterrows():
        rep = row["repeticiones"]
        d = asignar_valor(deficiencia_vals, rep)
        e = asignar_valor(exposicion_vals, rep)
        c = asignar_valor(consecuencia_vals, rep)
        p = d * e
        riesgo = p * c
        aceptabilidad = "🟥 No Aceptable" if riesgo >= 600 else "🟧 Aceptable con Control" if riesgo >= 150 else "🟩 Aceptable"
        calculos.append((d, e, p, c, riesgo, aceptabilidad))

    df[["deficiencia", "exposicion", "probabilidad", "consecuencia", "peligrosidad", "aceptabilidad"]] = pd.DataFrame(calculos, index=df.index)

    st.subheader("📋 Tabla de Eventos y Riesgos")
    st.dataframe(df)

    # Guardar en archivo Excel
    excel_file = "eventos_riesgos.xlsx"
    df.to_excel(excel_file, index=False)

    st.info(f"📂 Los datos de los eventos y riesgos han sido guardados en {excel_file}")

    st.subheader("📈 Gráfico de Peligrosidad Acumulada")
    df["probabilidad_acumulada"] = df["probabilidad"].cumsum()
    df["peligrosidad_acumulada"] = df["peligrosidad"].cumsum()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["frame"], df["probabilidad_acumulada"], label="Probabilidad Acumulada", color="blue")
    ax.plot(df["frame"], df["peligrosidad_acumulada"], label="Peligrosidad Acumulada", color="red")
    ax.set_xlabel("Frame")
    ax.set_ylabel("Valor")
    ax.set_title("Riesgos Acumulados")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)
else:
    st.warning("⚠️ No se detectaron objetos de interés en el frame.")
   

      


   
