<div align="center">
  <br>
  <h1>🔍 LocateAnything-3B — Streamlit Web Interface</h1>
  <p><strong>Self-hosted visual grounding UI powered by NVIDIA Eagle VLM</strong></p>
  <br>
</div>

**LocateAnything-3B** is a visual grounding model from NVIDIA that can detect objects, ground text descriptions, perform OCR, identify GUI elements, and point to locations in images. This project wraps it in a clean, self-hosted web interface using Streamlit.

Upload an image, describe what you're looking for, and get instant bounding boxes — all running on your own GPU, no data leaves your machine.

---

## ✨ Use Cases

- **Object Detection** — Detect categories like `person, car, bicycle` in any image
- **Visual Grounding** — Find "people wearing red shirts" or "the leftmost coffee cup"
- **OCR** — Automatically detect all visible text with bounding boxes
- **GUI Grounding** — Locate UI elements like "the search button" or "settings icon"
- **Pointing** — Get precise coordinates for "the traffic light" or "the exit sign"

---

## 🖥️ Requirements

- **Windows PC** with an NVIDIA GPU (8GB+ VRAM recommended)
- **Python 3.10+** installed
- **CUDA** drivers installed

---

## 🚀 Quick Start

### 1. Clone or copy the project

```powershell
git clone https://github.com/your-username/streamlit-locany.git
cd streamlit-locany
```

Or simply copy the `streamlit-locany` folder to your GPU PC.

### 2. Create a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Set your access password

```powershell
echo APP_PASSWORD = "your-secret-password" > .streamlit\secrets.toml
```

> Replace `your-secret-password` with a strong password. This is required to log into the web app. Do **not** commit `secrets.toml` to Git.

### 5. Accept the model license

The model (`nvidia/LocateAnything-3B`) is gated on HuggingFace. You must accept the terms at:

https://huggingface.co/nvidia/LocateAnything-3B

Then authenticate from your machine:

```powershell
pip install huggingface-hub
huggingface-cli login
```

> If you skip this step, the model download will fail on first launch.

### 6. Start the app

**Double-click** `start_app.bat` or run:

```powershell
streamlit run app.py --server.port 8501
```

The model will download automatically on first launch (~4GB). The app opens at **http://localhost:8501**.

### 7. (Optional) Access from other devices

Install [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/):

```powershell
winget install Cloudflare.cloudflared
```

Then **double-click** `start_tunnel.bat`. A public URL will appear like:

```
https://random-words.trycloudflare.com
```

Copy that URL and paste it into any browser — share it with friends along with your password.

---

## 🧪 How to use

1. Open **http://localhost:8501** in your browser
2. Enter your password to log in
3. Upload an image
4. Select a task type (Detection, Grounding, OCR, etc.)
5. Enter categories or a description
6. Click **🚀 Run Inference**
7. View annotated results with bounding boxes and detection statistics

---

## 📁 Project structure

```
streamlit-locany/
├── app.py                    # Streamlit web interface
├── requirements.txt          # Python dependencies
├── start_app.bat             # One-click launcher
├── start_tunnel.bat          # Cloudflare tunnel launcher
├── .streamlit/
│   ├── config.toml           # Dark theme & server config
│   └── secrets.toml          # Password (do NOT commit)
└── ../
    ├── locateanything_worker.py  # Model wrapper (parent dir)
    └── ...                       # Other LocateAnything scripts
```

---

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/) — Python-based web UI
- **Model**: [NVIDIA LocateAnything-3B](https://huggingface.co/nvidia/LocateAnything-3B) — Eagle VLM
- **Tunnel**: [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/) — secure public URL
