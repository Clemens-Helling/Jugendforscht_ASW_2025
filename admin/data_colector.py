from flask import Flask, jsonify
import psutil, time

app = Flask(__name__)

def network_speed():
    n1 = psutil.net_io_counters()
    time.sleep(1)
    n2 = psutil.net_io_counters()
    return {
        "upload_kb_s": (n2.bytes_sent - n1.bytes_sent) / 1024,
        "download_kb_s": (n2.bytes_recv - n1.bytes_recv) / 1024
    }

@app.route("/metrics")
def metrics():
    net = network_speed()
    return jsonify({
        "cpu_percent": psutil.cpu_percent(),
        "ram_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "network": net
    })

app.run(host="0.0.0.0", port=5000)
