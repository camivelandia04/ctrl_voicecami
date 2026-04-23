import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
import paho.mqtt.client as paho
import json

# ---------------- MQTT ----------------
def on_publish(client, userdata, result):
    print("Mensaje enviado correctamente")

def on_message(client, userdata, message):
    global message_received
    time.sleep(1)
    message_received = str(message.payload.decode("utf-8"))
    st.success("Respuesta recibida: " + message_received)

broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("nuevo_camilo")
client1.on_message = on_message

# ---------------- ESTILO ----------------
def add_bg():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #1f1c2c, #928dab);
            color: white;
        }
        h1, h2, h3 {
            color: #ffdd57;
            text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

add_bg()

# ---------------- INTERFAZ ----------------
st.title("🎤 Control Inteligente por Voz")
st.subheader("Habla y deja que el sistema responda")

# Imagen nueva
image = Image.open('gritando.png')
st.image(image, width=250)

st.write("Presiona el botón y di lo que necesites 🚀")

# Botón de voz
stt_button = Button(label="🎙️ Escuchar ahora", width=220)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="voz",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

# ---------------- RESPUESTA ----------------
if result:
    if "GET_TEXT" in result:
        texto = result.get("GET_TEXT")
        st.info("🗣️ Dijiste: " + texto)

        client1.on_publish = on_publish
        client1.connect(broker, port)

        message = json.dumps({"voz": texto.strip()})
        client1.publish("voiceClientecamilo", message)

# Carpeta temporal
try:
    os.mkdir("temp")
except:
    pass
