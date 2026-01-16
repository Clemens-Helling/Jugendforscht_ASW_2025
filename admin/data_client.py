# python
# file: admin/data_client.py
import tkinter as tk
import requests
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def create_dashboard(parent, server_url, interval=1000, max_points=50):
    """
    Embed a 3x2 matplotlib dashboard into the given Tk parent frame.
    Returns (canvas_widget, animation) - keep the animation reference alive.
    """
    fig, axs = plt.subplots(3, 2, figsize=(10, 7))
    fig.tight_layout(pad=4)

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    x_data = []
    cpu_data = []
    ram_data = []
    disk_data = []
    upload_data = []
    download_data = []
    temp_data = []

    def update(frame):
        try:
            r = requests.get(server_url, timeout=2)
            r.raise_for_status()
            data = r.json()
        except Exception:
            return  # on failure, skip this frame

        cpu_data.append(data.get("cpu_percent", 0))
        ram_data.append(data.get("ram_percent", 0))
        disk_data.append(data.get("disk_percent", 0))
        net = data.get("network", {}) or {}
        upload_data.append(net.get("upload_kb_s", 0))
        download_data.append(net.get("download_kb_s", 0))
        temp_data.append(data.get("temperature", 0))
        x_data.append(len(x_data) if x_data else 0)

        # keep lists bounded
        if len(x_data) > max_points:
            for lst in (x_data, cpu_data, ram_data, disk_data, upload_data, download_data, temp_data):
                lst.pop(0)

        if not cpu_data:
            return

        # CPU
        axs[0, 0].clear()
        axs[0, 0].plot(x_data, cpu_data, color="red")
        axs[0, 0].set_title("CPU %")
        axs[0, 0].set_ylim(0, 100)

        # RAM
        axs[0, 1].clear()
        axs[0, 1].plot(x_data, ram_data, color="blue")
        axs[0, 1].set_title("RAM %")
        axs[0, 1].set_ylim(0, 100)

        # Disk
        axs[1, 0].clear()
        axs[1, 0].plot(x_data, disk_data, color="purple")
        axs[1, 0].set_title("Disk %")
        axs[1, 0].set_ylim(0, 100)

        # Network
        axs[1, 1].clear()
        axs[1, 1].plot(x_data, upload_data, color="green", label="Upload KB/s")
        axs[1, 1].plot(x_data, download_data, color="orange", label="Download KB/s")
        axs[1, 1].set_title("Network KB/s")
        max_net = max(max(upload_data + download_data), 1)
        axs[1, 1].set_ylim(0, max_net)
        axs[1, 1].legend()

        # Temp
        axs[2, 0].clear()
        axs[2, 0].plot(x_data, temp_data, color="brown")
        axs[2, 0].set_title("CPU Temp °C")
        max_temp = max(max(temp_data), 50)
        axs[2, 0].set_ylim(0, max_temp)

        # Summary text
        axs[2, 1].clear()
        text = (f"Last Update:\n"
                f"CPU: {cpu_data[-1]:.1f}%\n"
                f"RAM: {ram_data[-1]:.1f}%\n"
                f"Disk: {disk_data[-1]:.1f}%\n"
                f"Upload: {upload_data[-1]:.2f} KB/s\n"
                f"Download: {download_data[-1]:.2f} KB/s\n"
                f"Temp: {temp_data[-1]:.1f} °C")
        axs[2, 1].text(0.5, 0.5, text, fontsize=12, ha='center', va='center')
        axs[2, 1].axis('off')

        canvas.draw_idle()

    ani = FuncAnimation(fig, update, interval=interval, cache_frame_data=False)
    return canvas, ani

def start_data_stream(server_url, on_data):
    """
    Start streaming data from the server_url.
    Calls on_data(data_dict) whenever new data is received.
    """
    import threading
    import time

    def stream():
        while True:
            try:
                r = requests.get(server_url, timeout=5)
                r.raise_for_status()
                data = r.json()
                on_data(data)
            except Exception:
                pass
            time.sleep(1)

    thread = threading.Thread(target=stream, daemon=True)
    thread.start()
# file: admin_panel.py

