# app.py
from flask import Flask, render_template, request, jsonify
import paho.mqtt.client as mqtt

app = Flask(__name__)


sensor1 = 0
sensor2 = 0
sensor3 = 0
sensor4 = 0


# ======================================
# MQTT CONFIG
# ======================================
BROKER = "127.0.0.1"
PORT = 1883

# subscribe topics
TOPIC_SUB = ["pb1", "pb2", "pb3", "sensor1", "sensor2", "sensor3", "sensor4"]

# publish topics
TOPIC_PUB = ["pwm1", "pwm2", "pwm3"]

# simpan data subscribe terbaru
a = [0, 0, 0, 0]


current_pwm = [
    {"n": "D3", "v": 128},
    {"n": "D5", "v": 64},
    {"n": "D6", "v": 200}
]


# ======================================
# MQTT CALLBACK
# ======================================
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker with result code:", rc)

    for topic in TOPIC_SUB:
        client.subscribe(topic)
        print("Subscribe ke topic:", topic)


def on_message(client, userdata, msg):
    global a
    topic = msg.topic
    payload = msg.payload.decode()
    
    if(topic == "sensor1"):
        global sensor1
        sensor1 = payload
        print(sensor1)
        
    if(topic == "sensor2"):
        global sensor2
        sensor2 = payload
        print(sensor2)
        
    if(topic == "sensor3"):
        global sensor3
        sensor3 = payload
        print(sensor3)
        
    if(topic == "sensor4"):
        global sensor4
        sensor4 = payload
        print(sensor4)

    
    a = [int(sensor1), int(sensor2), int(sensor3), int(sensor4)]
    print("a =", a)
    #print(f"Message diterima [{topic}] : {payload}")


# ======================================
# MQTT CLIENT INIT
# ======================================
mqtt_client = mqtt.Client()

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(BROKER, PORT, 60)
mqtt_client.loop_start()


# ======================================
# Python -> JavaScript
# ======================================


@app.route("/")
def index():
    return render_template(
        "iot_dashboard.html",
        data_a=a
    )


@app.route("/get_sensor")
def get_sensor():
    return jsonify({
        "a": a
    })


@app.route('/last_pwm', methods=['GET'])
def last_pwm():
    # Mengembalikan data PWM terakhir saat diminta oleh JS
    print(current_pwm)
    return jsonify(current_pwm)


# ======================================
# JavaScript -> Python
# publish ke pwm1 pwm2 pwm3
# ======================================
@app.route("/get_pwm", methods=["POST"])
def get_pv():
    global current_pwm
    data = request.json

    pwm1 = data.get("pwm1", 0)
    pwm2 = data.get("pwm2", 0)
    pwm3 = data.get("pwm3", 0)

    #print("PWM dari JavaScript:")
    print("pwm1 =", pwm1)
    print("pwm2 =", pwm2)
    print("pwm3 =", pwm3)
    
    
    if((pwm1 != 0) and (pwm2 != 0) and (pwm3 != 0)):
        current_pwm = [
            {"n": "D3", "v": pwm1},
            {"n": "D5", "v": pwm2},
            {"n": "D6", "v": pwm3}
        ]

    # publish MQTT
    mqtt_client.publish("pwm1", str(pwm1))
    mqtt_client.publish("pwm2", str(pwm2))
    mqtt_client.publish("pwm3", str(pwm3))

    return jsonify({
        "status": "success",
        "pwm1": pwm1,
        "pwm2": pwm2,
        "pwm3": pwm3
    })


# ======================================
# Ambil hasil subscribe pb1 pb2 pb3
# ======================================
@app.route("/get_mqtt_data", methods=["GET"])
def get_mqtt_data():
    return jsonify(latest_mqtt_data)


current_dw = [
    {"n": "D13", "v": 0},
    {"n": "D1",  "v": 0},
    {"n": "D0",  "v": 0},
    {"n": "D14", "v": 0},
]

@app.route('/last_dw', methods=['GET'])
def last_dw():
    return jsonify(current_dw)

@app.route('/set_dw', methods=['POST'])
def set_dw():
    global current_dw
    data = request.json
    i = data.get('index')
    v = data.get('value', 0)
    if i is not None and 0 <= i < len(current_dw):
        current_dw[i]['v'] = v
        # publish to MQTT if needed:
        # mqtt_client.publish(current_dw[i]['n'], str(v))
    print("DW state:", current_dw)
    return jsonify({"status": "ok", "dw": current_dw})

# ======================================
# MAIN
# ======================================
if __name__ == "__main__":
    app.run(debug=False, port=8081)
