import cv2
import pandas as pd
import os
import random
from datetime import datetime, timedelta
from roboflow import Roboflow
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt

# ⚙️ Conectar con Roboflow
rf = Roboflow(api_key="ZTgQTJF0CA75bTfQixhE")  # Usa tu API Key
project = rf.workspace().project("construccion-oscar")
model = project.version(1).model

# 🎥 Abrir la cámara
video_url = 0  # 0 = cámara del PC. Cambia por tu URL si usas IP Webcam
cap = cv2.VideoCapture(video_url)

if not cap.isOpened():
    raise Exception("No se pudo acceder a la cámara")

# 🎞 Guardar video con detección
output_path = "video_deteccion_riesgos.avi"
fourcc = cv2.VideoWriter_fourcc(*"XVID")
fps = 10.0
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

# ⏰ Simular jornada
start_time = datetime.strptime("08:00:00", "%H:%M:%S")

# 📋 Eventos
eventos = []
frame_number = 0
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

# 🎲 Valores GTC 45
def asignar_valor(lista, rep):
    base = random.choice(lista)
    return min(base + int(rep / 2), max(lista))

deficiencia_vals = [10, 6, 4, 2]
exposicion_vals = [4, 3, 2, 1]
consecuencia_vals = [100, 60, 25, 10]

# 🔁 Loop de detección
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_path = os.path.join(frame_folder, f"frame_{frame_number}.jpg")
    cv2.imwrite(frame_path, frame)

    try:
        result = model.predict(frame_path, confidence=40, overlap=30)
        predictions = result.json().get("predictions", [])
    except:
        predictions = []

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

        # Dibujar cajas
        x, y, w, h = int(pred["x"]), int(pred["y"]), int(pred["width"]), int(pred["height"])
        cv2.rectangle(frame, (x - w//2, y - h//2), (x + w//2, y + h//2), (0, 255, 0), 2)
        cv2.putText(frame, objeto, (x - w//2, y - h//2 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    out.write(frame)
    cv2.imshow("Análisis en vivo", frame)

    if cv2.waitKey(1) & 0xFF == ord("q") or frame_number > 300:
        break

    frame_number += 1

cap.release()
out.release()
cv2.destroyAllWindows()

# 📊 Crear DataFrame
df = pd.DataFrame(eventos)
df["repeticiones"] = df.groupby(["frame", "objeto"])["objeto"].transform("count")

# 📌 Calcular riesgo
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

# 🔁 Acumulados
total_frames = df["frame"].nunique()
df["probabilidad_acumulada"] = df["probabilidad"].cumsum() / total_frames
df["peligrosidad_acumulada"] = df["peligrosidad"].cumsum() / total_frames

# 💾 Guardar CSV
csv_path = "riesgos_detectados.csv"
df.to_csv(csv_path, index=False)
print(f"\n✅ CSV guardado en: {csv_path}")
print(f"🎥 Video guardado en: {output_path}")

# 📈 Gráfico acumulado
plt.figure(figsize=(10, 6))
plt.plot(df["frame"], df["probabilidad_acumulada"], label="Probabilidad Acumulada", color='blue')
plt.plot(df["frame"], df["peligrosidad_acumulada"], label="Peligrosidad Acumulada", color='red')
plt.xlabel("Frame")
plt.ylabel("Valor")
plt.title("Riesgos Acumulados")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
