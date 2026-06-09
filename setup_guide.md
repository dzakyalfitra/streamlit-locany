# 🚀 Setup Guide: LocateAnything-3B Web Interface

Complete guide to running the LocateAnything-3B Streamlit web app on your GPU PC (RTX A6000 Ada) and exposing it securely to the internet via Cloudflare Tunnel.

---

## 📋 Prerequisites

- **Windows PC** with NVIDIA GPU (RTX A6000 Ada or similar)
- **Python 3.10+** installed
- **CUDA** drivers installed (you already have this since LocateAnything works in terminal)
- **Git** (optional, for cloning)

---

## Step 1: Copy Project Files to Your GPU PC

Copy the entire `Streamlit-LocAny` folder to your GPU PC. The folder should contain:

```
Streamlit-LocAny/
├── app.py                      ← Streamlit web interface
├── locateanything_worker.py    ← Your existing model wrapper
├── quick_test.py               ← Your existing test script
├── run_interative.py           ← Your existing interactive script
├── bulk_detect.py              ← Your existing batch script
├── requirements.txt            ← Python dependencies
├── start_app.bat               ← One-click server start
├── start_tunnel.bat            ← One-click tunnel start
└── .streamlit/
    └── config.toml             ← Dark theme configuration
```

You can copy via USB, network share, or push to a Git repo and pull on the GPU PC.

---

## Step 2: Set Up Python Environment

Open **PowerShell** or **Command Prompt** on your GPU PC:

```powershell
# Navigate to the project folder
cd C:\path\to\Streamlit-LocAny

# Create a virtual environment (recommended)
python -m venv venv

# Activate it
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

> **Note:** If you already have `torch`, `transformers`, and other packages installed in a
> conda environment or global Python from your LocateAnything setup, you can skip the
> virtual environment and just install `streamlit`:
> ```
> pip install streamlit
> ```

---

## Step 3: Set Your Password

Create a secrets file so the app has a password gate:

```powershell
# Create the file (if it doesn't exist already)
echo APP_PASSWORD = "your-secret-password-here" > .streamlit\secrets.toml
```

Or manually create the file `.streamlit/secrets.toml` with this content:

```toml
APP_PASSWORD = "your-secret-password-here"
```

> **⚠️ Important:** Replace `your-secret-password-here` with a strong password.
> Share this password with your friends so they can log in.
> **Do NOT commit `secrets.toml` to Git.**

---

## Step 4: Test Locally

Start the Streamlit app:

```powershell
streamlit run app.py
```

Or simply **double-click `start_app.bat`**.

The app will:
1. Load the LocateAnything-3B model into GPU memory (~60 seconds on first launch)
2. Start the web server at **http://localhost:8501**

Open http://localhost:8501 in your browser. You should see:
1. A login page — enter your password
2. The main interface with image upload, task selection, and inference controls

**Test it:**
1. Upload any image
2. Select "Detection" task type
3. Enter categories like `person, car, bicycle`
4. Click "🚀 Run Inference"
5. See annotated output with bounding boxes

---

## Step 5: Install Cloudflare Tunnel (`cloudflared`)

This tool creates a secure encrypted tunnel from your PC to the internet.
**No ports need to be opened on your router.**

### Option A: Install via `winget` (easiest)

```powershell
winget install Cloudflare.cloudflared
```

### Option B: Manual Download

1. Go to https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
2. Download the **Windows 64-bit** executable
3. Place `cloudflared.exe` somewhere in your PATH (e.g., `C:\Windows\System32\` or your project folder)

### Verify Installation

```powershell
cloudflared --version
```

---

## Step 6: Expose to the Internet

With both the Streamlit app running (Step 4) and `cloudflared` installed (Step 5):

### Start the tunnel:

```powershell
cloudflared tunnel --url http://localhost:8501
```

Or simply **double-click `start_tunnel.bat`**.

You'll see output like:

```
2026-06-02 INF +-----------------------------------------------------------+
2026-06-02 INF |  Your quick Tunnel has been created! Visit it at:          |
2026-06-02 INF |  https://proper-creek-delhi-casting.trycloudflare.com      |
2026-06-02 INF +-----------------------------------------------------------+
```

**That HTTPS URL is your public link!** Share it with your friends along with the password.

### How it works:
```
Friend's phone → HTTPS → Cloudflare servers → encrypted tunnel → your PC → Streamlit
```

> **Notes:**
> - No Cloudflare account needed for quick tunnels
> - The URL is randomly generated and changes every time you restart the tunnel
> - The connection is fully encrypted (HTTPS)
> - Your PC's IP address is never exposed
> - No ports need to be opened on your router/firewall

---

## Step 7: Share with Friends

Send your friends:
1. **The tunnel URL** (e.g., `https://proper-creek-delhi-casting.trycloudflare.com`)
2. **The password** you set in Step 3

They can open the URL on any device (phone, tablet, laptop) and use the full LocateAnything interface.

---

## 🔒 Security Overview

Your setup has **3 layers of protection**:

| Layer | Protection | Against |
|-------|-----------|---------|
| 🌐 **Random URL** | The tunnel URL is randomly generated and unguessable | Public discovery |
| 🔑 **Password Gate** | In-app password required to access any functionality | Unauthorized access |
| 🛡️ **No Open Ports** | Your router has zero ports opened; tunnel is outbound-only | Port scanning, DDoS |

**Additional safeguards built into the app:**
- Maximum upload size: 20MB (configured in `.streamlit/config.toml`)
- XSRF protection enabled
- No file system access — only uploaded images are processed
- No command execution — only predefined model inference

---

## 🔧 Troubleshooting

### "Model loading fails / CUDA out of memory"
- Ensure no other GPU-heavy processes are running
- The model needs ~8GB VRAM. Your A6000 Ada (48GB) has plenty of headroom.
- Check CUDA is available: `python -c "import torch; print(torch.cuda.is_available())"`

### "Streamlit command not found"
- Activate your virtual environment: `.\venv\Scripts\activate`
- Or install globally: `pip install streamlit`

### "cloudflared command not found"
- Install it: `winget install Cloudflare.cloudflared`
- Or download manually from the Cloudflare website

### "Friends can't access the URL"
- Make sure both `start_app.bat` and `start_tunnel.bat` are running
- The tunnel URL changes each restart — send the new one
- Make sure you're sharing the full `https://...trycloudflare.com` URL

### "Inference is slow"
- First inference is always slower (GPU warmup + model compilation)
- Subsequent inferences should be 2-5 seconds depending on image size
- Use "fast" inference mode for quicker results (with slightly lower quality)

---

## 📁 Quick Reference: Running the App

Every time you want to use the app:

1. **Open PowerShell** → navigate to project folder
2. **Start the app**: Double-click `start_app.bat` (or `streamlit run app.py`)
3. **Wait** for "Model loaded" message (~60s first time, instant after)
4. **Start the tunnel**: Double-click `start_tunnel.bat` (in a separate terminal)
5. **Copy the URL** and share with friends + password
6. **To stop**: Press `Ctrl+C` in both terminal windows

---

## 🔮 Future: Video Support

Video support will be added in a future update. The architecture is designed to
support it — the `LocateAnythingWorker` already handles video frame processing
in `bulk_detect.py`, and the Streamlit UI can be extended with video upload
and frame-by-frame inference.
