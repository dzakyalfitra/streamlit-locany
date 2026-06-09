"""
LocateAnything-3B — Streamlit Web Interface
NVIDIA Visual Grounding Demo (Self-hosted)

Run: streamlit run app.py
"""

import streamlit as st
import streamlit.components.v1 as components
import re
import time
import io
import os
import torch
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ═══════════════════════════════════════════════════════════════
# Page Configuration
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="LocateAnything-3B | NVIDIA",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════
# Custom CSS — NVIDIA Premium Dark Theme
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── Global ── */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #111820 100%);
        border-right: 1px solid rgba(118, 185, 0, 0.15);
    }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stTextInput label,
    section[data-testid="stSidebar"] .stTextArea label,
    section[data-testid="stSidebar"] .stSlider label,
    section[data-testid="stSidebar"] .stRadio label {
        color: #c9d1d9 !important;
        font-weight: 500;
    }

    /* ── Primary button (NVIDIA Green) ── */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #76B900 0%, #5a9400 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 700 !important;
        letter-spacing: 0.03em;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 20px rgba(118, 185, 0, 0.25);
        border-radius: 10px !important;
        padding: 0.6rem 1.5rem !important;
    }
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="stBaseButton-primary"]:hover {
        background: linear-gradient(135deg, #8ed600 0%, #76B900 100%) !important;
        box-shadow: 0 6px 25px rgba(118, 185, 0, 0.4);
        transform: translateY(-1px);
    }

    /* ── Form submit styled as primary ── */
    .stFormSubmitButton > button {
        background: linear-gradient(135deg, #76B900 0%, #5a9400 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 700 !important;
        letter-spacing: 0.03em;
        box-shadow: 0 4px 20px rgba(118, 185, 0, 0.25);
        border-radius: 10px !important;
        padding: 0.6rem 1.5rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .stFormSubmitButton > button:hover {
        background: linear-gradient(135deg, #8ed600 0%, #76B900 100%) !important;
        box-shadow: 0 6px 25px rgba(118, 185, 0, 0.4);
        transform: translateY(-1px);
    }

    /* ── Header Banner ── */
    .nvidia-header {
        background: linear-gradient(135deg, rgba(118, 185, 0, 0.06) 0%, rgba(0, 0, 0, 0) 60%);
        border: 1px solid rgba(118, 185, 0, 0.12);
        border-radius: 16px;
        padding: 1.8rem 2.2rem;
        margin-bottom: 1.8rem;
        position: relative;
        overflow: hidden;
    }
    .nvidia-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #76B900, transparent);
    }
    .nvidia-header h1 {
        background: linear-gradient(135deg, #76B900 0%, #a3e635 60%, #76B900 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2rem;
        font-weight: 800;
        margin: 0 0 0.3rem 0;
        letter-spacing: -0.02em;
    }
    .nvidia-header p {
        color: #8b949e;
        font-size: 0.92rem;
        margin: 0;
        font-weight: 400;
    }

    /* ── Login Page ── */
    .login-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 55vh;
        text-align: center;
    }
    .login-logo {
        font-size: 4rem;
        margin-bottom: 0.8rem;
        filter: drop-shadow(0 0 20px rgba(118, 185, 0, 0.3));
    }
    .login-title {
        background: linear-gradient(135deg, #76B900 0%, #a3e635 50%, #76B900 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.4rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .login-subtitle {
        color: #6e7681;
        font-size: 0.95rem;
        margin: 0.4rem 0 2.5rem 0;
    }

    /* ── Stat Cards ── */
    .stat-row {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        margin: 1rem 0;
    }
    .stat-card {
        flex: 1;
        min-width: 120px;
        background: linear-gradient(135deg, rgba(118, 185, 0, 0.07) 0%, rgba(118, 185, 0, 0.02) 100%);
        border: 1px solid rgba(118, 185, 0, 0.18);
        border-radius: 12px;
        padding: 0.9rem 1.1rem;
        text-align: center;
    }
    .stat-value {
        color: #76B900;
        font-size: 1.35rem;
        font-weight: 700;
        margin: 0;
        font-variant-numeric: tabular-nums;
    }
    .stat-label {
        color: #8b949e;
        font-size: 0.72rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin: 0.2rem 0 0 0;
    }

    /* ── Detection Table (scrollable container) ── */
    .det-scroll-container {
        max-height: 280px;
        overflow-y: auto;
        border-radius: 10px;
        border: 1px solid rgba(118, 185, 0, 0.15);
    }
    .det-scroll-container::-webkit-scrollbar {
        width: 6px;
    }
    .det-scroll-container::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.2);
        border-radius: 3px;
    }
    .det-scroll-container::-webkit-scrollbar-thumb {
        background: rgba(118, 185, 0, 0.3);
        border-radius: 3px;
    }
    .det-scroll-container::-webkit-scrollbar-thumb:hover {
        background: rgba(118, 185, 0, 0.5);
    }
    .det-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        font-size: 0.85rem;
    }
    .det-table thead th {
        background: rgba(118, 185, 0, 0.1);
        color: #c9d1d9;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.72rem;
        letter-spacing: 0.05em;
        padding: 0.7rem 1rem;
        text-align: left;
        border-bottom: 1px solid rgba(118, 185, 0, 0.15);
        position: sticky;
        top: 0;
        z-index: 1;
    }
    .det-table tbody td {
        padding: 0.55rem 1rem;
        color: #c9d1d9;
        border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    }
    .det-table tbody tr:last-child td {
        border-bottom: none;
    }
    .det-table tbody tr:hover {
        background: rgba(118, 185, 0, 0.04);
    }
    .det-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        color: white;
    }

    /* ── Section Headers ── */
    .section-header {
        color: #c9d1d9;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        padding-bottom: 0.5rem;
        margin-bottom: 0.8rem;
        border-bottom: 1px solid rgba(118, 185, 0, 0.15);
    }

    /* ── File Uploader ── */
    [data-testid="stFileUploader"] {
        border: 2px dashed rgba(118, 185, 0, 0.25) !important;
        border-radius: 14px !important;
        transition: border-color 0.3s ease;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(118, 185, 0, 0.5) !important;
    }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        font-weight: 600 !important;
        color: #c9d1d9 !important;
    }

    /* ── Divider ── */
    .nvidia-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(118, 185, 0, 0.3), transparent);
        margin: 1.2rem 0;
        border: none;
    }

    /* ── Hide Streamlit Branding ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {
        background: rgba(13, 17, 23, 0.8);
        backdrop-filter: blur(10px);
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# JavaScript — Lightbox + Enter Key Handling
# ═══════════════════════════════════════════════════════════════
def inject_javascript():
    """Inject lightbox and keyboard shortcut scripts via components.html."""
    components.html("""
    <script>
    (function() {
        var doc = window.parent.document;

        // ── Enter key triggers primary button (for inference) ──
        doc.addEventListener('keydown', function(e) {
            if (e.key !== 'Enter' || e.shiftKey) return;
            var el = doc.activeElement;
            if (!el) return;
            // Skip if inside a form (login form handles Enter natively)
            if (el.closest('form, [data-testid="stForm"]')) return;
            // Only trigger for text inputs, not textareas
            if (el.tagName === 'INPUT' && el.type === 'text') {
                e.preventDefault();
                var btn = doc.querySelector(
                    'button[kind="primary"], button[data-testid="stBaseButton-primary"]'
                );
                if (btn) btn.click();
            }
        });
    })();
    </script>
    """, height=0)


# ═══════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════
TASK_CONFIGS = {
    "Detection": {
        "template": "Locate all the instances that matches the following description: {cats}.",
        "label": "Categories",
        "placeholder": "person, car, bicycle",
        "help": "Comma-separated object categories to detect.",
        "needs_input": True,
    },
    "Grounding": {
        "template": "Locate all the instances that match the following description: {cats}.",
        "label": "Description",
        "placeholder": "people wearing red shirts",
        "help": "Describe what to locate in the image.",
        "needs_input": True,
    },
    "OCR": {
        "template": "Detect all the text in box format.",
        "label": None,
        "needs_input": False,
    },
    "GUI Grounding": {
        "template": "Locate the region that matches the following description: {cats}.",
        "label": "UI Element",
        "placeholder": "the search button",
        "help": "Describe the GUI element to locate.",
        "needs_input": True,
    },
    "Pointing": {
        "template": "Point to: {cats}.",
        "label": "Target",
        "placeholder": "the traffic light",
        "help": "Describe what to point to.",
        "needs_input": True,
    },
}

BOX_COLORS = [
    (8, 145, 178),    # Teal
    (220, 38, 38),    # Red
    (22, 163, 74),    # Green
    (37, 99, 235),    # Blue
    (217, 119, 6),    # Amber
    (147, 51, 234),   # Purple
    (236, 72, 153),   # Pink
    (234, 179, 8),    # Yellow
    (6, 182, 212),    # Cyan
    (249, 115, 22),   # Orange
]


# ═══════════════════════════════════════════════════════════════
# Authentication (Enter key works via st.form)
# ═══════════════════════════════════════════════════════════════
def check_password() -> bool:
    """Render login gate. Returns True if authenticated."""
    if st.session_state.get("authenticated", False):
        return True

    st.markdown("""
        <div class="login-container">
            <div class="login-logo">🔍</div>
            <h1 class="login-title">LocateAnything-3B</h1>
            <p class="login-subtitle">NVIDIA Visual Grounding &bull; Self-hosted Private Instance</p>
        </div>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1.2, 1, 1.2])
    with col_c:
        with st.form("login_form", clear_on_submit=False, border=False):
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter access password…",
                label_visibility="collapsed",
            )
            submitted = st.form_submit_button(
                "🔓  Access",
                use_container_width=True,
                type="primary",
            )
            if submitted:
                correct = (
                    st.secrets.get("APP_PASSWORD", None)
                    or os.environ.get("APP_PASSWORD", None)
                    or "locateanything"
                )
                if password == correct:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Incorrect password. Please try again.")
        st.caption(
            '<p style="text-align:center;color:#484f58;margin-top:1rem;">'
            'Powered by NVIDIA LocateAnything-3B • Eagle VLM</p>',
            unsafe_allow_html=True,
        )
    return False


# ═══════════════════════════════════════════════════════════════
# Model Loading (cached across sessions)
# ═══════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner="Loading LocateAnything-3B model… (first time takes ~60s)")
def load_worker():
    """Load the LocateAnythingWorker and keep it in GPU memory."""
    from locateanything_worker import LocateAnythingWorker

    model_path = os.environ.get("MODEL_PATH", "nvidia/LocateAnything-3B")
    worker = LocateAnythingWorker(model_path, device="cuda", dtype=torch.bfloat16)
    return worker


# ═══════════════════════════════════════════════════════════════
# Inference (full parameter control, bypasses worker.predict)
# ═══════════════════════════════════════════════════════════════
@torch.no_grad()
def run_inference(worker, image, prompt, generation_mode, max_new_tokens, temperature, top_p):
    """Run model inference with full control over generation parameters."""
    messages = [{"role": "user", "content": [
        {"type": "image", "image": image},
        {"type": "text", "text": prompt},
    ]}]

    text = worker.processor.py_apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True,
    )
    images_list, videos_list = worker.processor.process_vision_info(messages)
    inputs = worker.processor(
        text=[text], images=images_list, videos=videos_list, return_tensors="pt",
    ).to(worker.device)

    pixel_values = inputs["pixel_values"].to(worker.dtype)
    input_ids = inputs["input_ids"]
    image_grid_hws = inputs.get("image_grid_hws", None)

    t0 = time.time()
    response = worker.model.generate(
        pixel_values=pixel_values,
        input_ids=input_ids,
        attention_mask=inputs["attention_mask"],
        image_grid_hws=image_grid_hws,
        tokenizer=worker.tokenizer,
        max_new_tokens=max_new_tokens,
        use_cache=True,
        generation_mode=generation_mode,
        temperature=temperature,
        do_sample=True,
        top_p=top_p,
        repetition_penalty=1.1,
        verbose=True,
    )
    elapsed = time.time() - t0

    result = {"answer": "", "stats": "", "elapsed": round(elapsed, 2)}
    if isinstance(response, tuple):
        result["answer"] = response[0] if len(response) >= 1 else ""
        if len(response) >= 3:
            result["stats"] = response[2]
    else:
        result["answer"] = response

    return result


# ═══════════════════════════════════════════════════════════════
# Color Assignment — Sequential per unique label (no collisions)
# ═══════════════════════════════════════════════════════════════
def build_color_map(detections: list) -> dict:
    """
    Assign colors to labels sequentially so that different categories
    always get visually distinct colors. Returns {label: (R, G, B)}.
    """
    color_map = {}
    idx = 0
    for det in detections:
        label = det.get("label", "object")
        if label not in color_map:
            color_map[label] = BOX_COLORS[idx % len(BOX_COLORS)]
            idx += 1
    return color_map


# ═══════════════════════════════════════════════════════════════
# Output Parsing — handles all model output formats
# ═══════════════════════════════════════════════════════════════
def parse_results(answer_text: str, category_str: str = ""):
    """
    Parse model output into structured detections.

    Uses a streaming token approach that correctly handles:
    - One <ref> followed by MULTIPLE <box> tags (e.g. 3 people)
    - <ref>label</ref><box><x1><y1><x2><y2></box>  (labeled boxes)
    - <box><x1><y1><x2><y2></box>                   (unlabeled boxes)
    - <box><x1><y1></box>                            (points)
    """
    results = []
    expected_cats = [c.strip().lower() for c in category_str.split("</c>") if c.strip()]

    # ── Primary: streaming ref/box tokens (handles multi-box per ref) ──
    token_pat = re.compile(
        r"(<ref>.*?</ref>)|(<box>.*?</box>)", re.IGNORECASE | re.DOTALL
    )
    current_label = None
    for m in token_pat.finditer(answer_text):
        token = m.group(0)
        if token.lower().startswith("<ref>"):
            raw_label = re.sub(r"</?ref>", "", token, flags=re.IGNORECASE).strip()
            if raw_label:
                current_label = raw_label
        else:
            content = re.sub(r"</?box>", "", token, flags=re.IGNORECASE)
            nums = [float(n) for n in re.findall(r"<\s*(\d+(?:\.\d+)?)\s*>", content)]
            if not nums:
                continue
            label = current_label or (expected_cats[0] if expected_cats else "object")
            if len(nums) == 4:
                results.append({"type": "box", "label": label, "coords": nums})
            elif len(nums) == 2:
                results.append({"type": "point", "label": label, "coords": nums})

    if results:
        return results

    # ── Fallback: raw <box> blocks with preceding text for label guess ──
    box_split = re.compile(r"<box>(.*?)</box>", re.IGNORECASE)
    parts = box_split.split(answer_text)
    for i in range(1, len(parts), 2):
        preceding = parts[i - 1].lower()
        content = parts[i]
        label = expected_cats[0] if expected_cats else "object"
        for cat in expected_cats:
            if cat in preceding[-200:]:
                label = cat
                break
        nums = [float(n) for n in re.findall(r"<\s*(\d+(?:\.\d+)?)\s*>", content)]
        if len(nums) == 4:
            results.append({"type": "box", "label": label, "coords": nums})
        elif len(nums) == 2:
            results.append({"type": "point", "label": label, "coords": nums})

    return results


def parse_stats_string(stats_str) -> dict:
    """Parse 'Stastic Info, forward_step=10;num_tokens=85;...' into a dict."""
    if not stats_str:
        return {}
    cleaned = re.sub(r"^[Ss]tast?ic\s*[Ii]nfo\s*,?\s*", "", str(stats_str).strip())
    stats = {}
    for part in cleaned.split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            stats[k.strip()] = v.strip()
    return stats


# ═══════════════════════════════════════════════════════════════
# Drawing — Adaptive scaling, z-ordering, distinct colors
# ═══════════════════════════════════════════════════════════════
def _load_font(size: int = 18):
    """Try system fonts, then fallback to PIL default."""
    for name in ["arial.ttf", "Arial.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except (IOError, OSError):
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def draw_detections(image: Image.Image, detections: list) -> Image.Image:
    """
    Draw bounding boxes and points on the image with labels.

    - Scales line width & font size based on image dimensions
    - Draws larger boxes first so small boxes appear on top
    - Uses sequential color assignment (distinct per label)
    """
    img = image.copy().convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    w_img, h_img = img.size

    # ── Dynamic scaling based on image size ──
    diag = (w_img ** 2 + h_img ** 2) ** 0.5
    scale = max(0.4, min(2.5, diag / 1000))
    line_w = max(2, round(3 * scale))
    font_size = max(10, round(16 * scale))
    point_r = max(4, round(8 * scale))
    pad_x = max(3, round(6 * scale))
    pad_y = max(2, round(3 * scale))

    font = _load_font(font_size)

    # ── Build color map (sequential, no collisions) ──
    color_map = build_color_map(detections)

    # ── Convert to pixel coords ──
    parsed_items = []
    for det in detections:
        label = det.get("label", "object")
        color = color_map.get(label, (200, 200, 200))
        coords = det["coords"]

        if det["type"] == "point" and len(coords) >= 2:
            cx = max(0, min(w_img, coords[0] * w_img / 1000))
            cy = max(0, min(h_img, coords[1] * h_img / 1000))
            parsed_items.append(("point", label, color, cx, cy, 0))  # area=0 for points
        elif det["type"] == "box" and len(coords) >= 4:
            x1 = max(0, min(w_img, coords[0] * w_img / 1000))
            y1 = max(0, min(h_img, coords[1] * h_img / 1000))
            x2 = max(0, min(w_img, coords[2] * w_img / 1000))
            y2 = max(0, min(h_img, coords[3] * h_img / 1000))
            x1, x2 = min(x1, x2), max(x1, x2)
            y1, y2 = min(y1, y2), max(y1, y2)
            area = (x2 - x1) * (y2 - y1)
            parsed_items.append(("box", label, color, x1, y1, x2, y2, area))

    # ── Sort: largest boxes first (drawn at bottom), points last (on top) ──
    def sort_key(item):
        if item[0] == "box":
            return (0, -item[7])  # boxes first, largest area first
        return (1, 0)             # points after boxes
    parsed_items.sort(key=sort_key)

    # ── Draw fills & outlines ──
    for item in parsed_items:
        if item[0] == "box":
            _, _, color, x1, y1, x2, y2, _ = item
            fill_color = color + (50,)
            draw.rectangle([x1, y1, x2, y2], fill=fill_color, outline=color, width=line_w)
        elif item[0] == "point":
            _, _, color, cx, cy, _ = item
            draw.ellipse(
                [cx - point_r, cy - point_r, cx + point_r, cy + point_r],
                fill=color, outline="white", width=max(1, line_w // 2),
            )

    # ── Draw labels (in reverse order so small box labels are on top) ──
    for item in reversed(parsed_items):
        if item[0] == "box":
            _, label, color, x1, y1, x2, y2, _ = item
            if not label:
                continue
            bbox = draw.textbbox((0, 0), label, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            tag_h = th + pad_y * 2
            tag_w = tw + pad_x * 2
            tag_y = y1 - tag_h - 2
            if tag_y < 0:
                tag_y = y2 + 2
            draw.rectangle([x1, tag_y, x1 + tag_w, tag_y + tag_h], fill=color)
            draw.text((x1 + pad_x, tag_y + pad_y), label, fill="white", font=font)
        elif item[0] == "point":
            _, label, color, cx, cy, _ = item
            if not label:
                continue
            bbox = draw.textbbox((0, 0), label, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            tx, ty = cx + point_r + 4, cy - th // 2
            draw.rectangle([tx - 2, ty - 2, tx + tw + pad_x, ty + th + pad_y], fill=color)
            draw.text((tx + 1, ty), label, fill="white", font=font)

    return Image.alpha_composite(img, overlay).convert("RGB")


# ═══════════════════════════════════════════════════════════════
# Prompt Generation
# ═══════════════════════════════════════════════════════════════
def generate_prompt(task_type: str, user_input: str) -> str:
    """Build the model prompt from task type and user input."""
    config = TASK_CONFIGS[task_type]
    if not config["needs_input"]:
        return config["template"]
    cats = "</c>".join(c.strip() for c in user_input.split(",") if c.strip())
    return config["template"].format(cats=cats)


# ═══════════════════════════════════════════════════════════════
# Sidebar Controls
# ═══════════════════════════════════════════════════════════════
def render_sidebar():
    """Render all sidebar controls and return the settings dict."""
    with st.sidebar:
        st.markdown(
            '<p style="color:#76B900;font-weight:700;font-size:0.75rem;'
            'text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.3rem;">'
            '🟢 LocateAnything-3B</p>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="nvidia-divider"></div>', unsafe_allow_html=True)

        # ── Task Type ──
        st.markdown(
            '<p class="section-header">📋 Task Configuration</p>',
            unsafe_allow_html=True,
        )
        task_type = st.selectbox(
            "Task Type",
            list(TASK_CONFIGS.keys()),
            index=0,
            help="Select the visual grounding task to perform.",
        )
        config = TASK_CONFIGS[task_type]

        # ── User Input (text_input for Enter key support) ──
        user_input = ""
        if config["needs_input"]:
            user_input = st.text_input(
                config["label"],
                placeholder=config["placeholder"],
                help=config["help"],
            )

        st.markdown('<div class="nvidia-divider"></div>', unsafe_allow_html=True)

        # ── Advanced Settings ──
        with st.expander("⚙️  Advanced Settings", expanded=False):
            inference_mode = st.radio(
                "Inference Mode",
                ["hybrid", "fast", "slow"],
                index=0,
                horizontal=True,
                help=(
                    "**Hybrid** = MTP with AR fallback (best quality). "
                    "**Fast** = MTP only (fastest). "
                    "**Slow** = AR only (most precise)."
                ),
            )

            st.markdown("---")

            max_objects = st.slider(
                "Max Objects", 0, 100, 0,
                help="Maximum number of detected objects to display. 0 = unlimited.",
            )

            temperature = st.slider(
                "Temperature", 0.0, 1.5, 0.7, 0.05,
                help="Higher = more creative, lower = more deterministic.",
            )
            top_p = st.slider(
                "Top-P (nucleus sampling)", 0.0, 1.0, 0.9, 0.05,
                help="Cumulative probability cutoff for token sampling.",
            )
            max_tokens = st.slider(
                "Max New Tokens", 256, 8192, 2048, 256,
                help="Maximum number of tokens the model can generate.",
            )

        # ── Custom Prompt Override ──
        with st.expander("✏️  Custom Prompt Override", expanded=False):
            custom_prompt = st.text_area(
                "Raw Prompt",
                placeholder="Leave empty to use the auto-generated prompt above.",
                help="Override the auto-generated prompt with your own.",
                height=80,
                label_visibility="collapsed",
            )

        st.markdown('<div class="nvidia-divider"></div>', unsafe_allow_html=True)

        # ── Run Button ──
        run_clicked = st.button(
            "🚀  Run Inference",
            type="primary",
            use_container_width=True,
        )

        # ── Logout ──
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔒 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

    return {
        "task_type": task_type,
        "user_input": user_input.strip(),
        "inference_mode": inference_mode if "inference_mode" in dir() else "hybrid",
        "temperature": temperature if "temperature" in dir() else 0.7,
        "top_p": top_p if "top_p" in dir() else 0.9,
        "max_tokens": max_tokens if "max_tokens" in dir() else 2048,
        "max_objects": max_objects if "max_objects" in dir() else 0,
        "custom_prompt": custom_prompt.strip() if "custom_prompt" in dir() else "",
        "run_clicked": run_clicked,
    }


# ═══════════════════════════════════════════════════════════════
# Results Display
# ═══════════════════════════════════════════════════════════════
def render_stats(stats_dict: dict, elapsed: float):
    """Render inference statistics as styled cards."""
    cards = []
    if elapsed:
        cards.append(("⏱️", f"{elapsed:.1f}s", "Inference Time"))
    if "tps" in stats_dict:
        cards.append(("⚡", stats_dict["tps"], "Tokens/sec"))
    if "bps" in stats_dict:
        cards.append(("📦", stats_dict["bps"], "Boxes/sec"))
    if "forward_step" in stats_dict:
        cards.append(("🔄", stats_dict["forward_step"], "Forward Steps"))
    if "num_tokens" in stats_dict:
        cards.append(("🔤", stats_dict["num_tokens"], "Tokens"))
    if "num_boxes" in stats_dict:
        cards.append(("🎯", stats_dict["num_boxes"], "Boxes"))

    if not cards:
        return

    html = '<div class="stat-row">'
    for icon, value, label in cards:
        html += f'''
        <div class="stat-card">
            <p class="stat-value">{icon} {value}</p>
            <p class="stat-label">{label}</p>
        </div>'''
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_detection_table(detections: list, color_map: dict):
    """Render parsed detections as a styled HTML table inside a scrollable box."""
    if not detections:
        st.info("No objects detected.", icon="ℹ️")
        return

    html = '<div class="det-scroll-container">'
    html += '<table class="det-table"><thead><tr>'
    html += "<th>#</th><th>Label</th><th>Type</th><th>Coordinates (normalized 0–1000)</th>"
    html += "</tr></thead><tbody>"

    for i, det in enumerate(detections, 1):
        label = det.get("label", "object")
        dtype = det.get("type", "box")
        color = color_map.get(label, (200, 200, 200))
        color_hex = f"rgb({color[0]},{color[1]},{color[2]})"
        coords = det.get("coords", [])
        coords_str = ", ".join(str(int(c)) for c in coords)

        badge_html = f'<span class="det-badge" style="background:{color_hex}">{label}</span>'
        type_emoji = "🔲" if dtype == "box" else "📍"

        html += f"<tr><td>{i}</td><td>{badge_html}</td>"
        html += f"<td>{type_emoji} {dtype}</td><td>{coords_str}</td></tr>"

    html += "</tbody></table></div>"
    st.markdown(html, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# Main Application
# ═══════════════════════════════════════════════════════════════
def main():
    # ── Auth Gate ──
    if not check_password():
        return

    # ── Header ──
    st.markdown("""
        <div class="nvidia-header">
            <h1>🔍 LocateAnything-3B</h1>
            <p>NVIDIA Eagle VLM &bull; Visual Grounding &bull; Object Detection &bull; OCR &bull; GUI Grounding</p>
        </div>
    """, unsafe_allow_html=True)

    # ── Inject JavaScript (lightbox + Enter key) ──
    inject_javascript()

    # ── Sidebar ──
    settings = render_sidebar()

    # ── Preload model (warm cache) ──
    worker = load_worker()

    # ── Main Content ──
    col_input, col_output = st.columns([1, 1], gap="large")

    with col_input:
        st.markdown('<p class="section-header">📷 Input Image</p>', unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "Upload an image",
            type=["jpg", "jpeg", "png", "bmp", "webp"],
            label_visibility="collapsed",
            help="Drag and drop or click to upload an image.",
        )

        if uploaded:
            image = Image.open(uploaded).convert("RGB")
            st.image(image, use_container_width=True, caption=f"{uploaded.name} • {image.size[0]}×{image.size[1]}")
        else:
            st.markdown(
                '<div style="text-align:center;padding:4rem 2rem;color:#484f58;'
                'border:2px dashed rgba(118,185,0,0.15);border-radius:14px;">'
                '<p style="font-size:2.5rem;margin:0;">📷</p>'
                '<p style="margin:0.5rem 0 0 0;">Upload an image to get started</p>'
                '</div>',
                unsafe_allow_html=True,
            )

        # Show auto-generated prompt
        if settings["user_input"] or not TASK_CONFIGS[settings["task_type"]]["needs_input"]:
            prompt = settings["custom_prompt"] or generate_prompt(
                settings["task_type"], settings["user_input"]
            )
            st.markdown(
                f'<div style="background:rgba(118,185,0,0.06);border:1px solid rgba(118,185,0,0.15);'
                f'border-radius:8px;padding:0.6rem 1rem;margin-top:0.8rem;font-size:0.82rem;color:#94a3b8;">'
                f'<strong style="color:#76B900;">Prompt:</strong> {prompt}</div>',
                unsafe_allow_html=True,
            )

    with col_output:
        st.markdown('<p class="section-header">🎯 Output</p>', unsafe_allow_html=True)

        # ── Run Inference ──
        if settings["run_clicked"]:
            if not uploaded:
                st.warning("Please upload an image first.", icon="⚠️")
            elif TASK_CONFIGS[settings["task_type"]]["needs_input"] and not settings["user_input"]:
                st.warning("Please enter categories or a description.", icon="⚠️")
            else:
                image = Image.open(uploaded).convert("RGB")
                prompt = settings["custom_prompt"] or generate_prompt(
                    settings["task_type"], settings["user_input"]
                )

                # Build category string for parser
                if settings["task_type"] == "Detection":
                    category_str = "</c>".join(
                        c.strip() for c in settings["user_input"].split(",") if c.strip()
                    )
                else:
                    category_str = settings["user_input"]

                with st.spinner("🧠 Running inference on GPU…"):
                    try:
                        result = run_inference(
                            worker=worker,
                            image=image,
                            prompt=prompt,
                            generation_mode=settings["inference_mode"],
                            max_new_tokens=settings["max_tokens"],
                            temperature=settings["temperature"],
                            top_p=settings["top_p"],
                        )

                        answer = result["answer"]
                        stats_raw = result.get("stats", "")
                        elapsed = result.get("elapsed", 0)

                        # Parse detections
                        detections = parse_results(answer, category_str)

                        # Apply max_objects limit
                        max_obj = settings["max_objects"]
                        if max_obj > 0:
                            detections = detections[:max_obj]

                        # Draw with correct colors
                        annotated = draw_detections(image, detections)

                        # Store in session
                        st.session_state["last_result"] = {
                            "annotated": annotated,
                            "detections": detections,
                            "answer": answer,
                            "stats_raw": stats_raw,
                            "elapsed": elapsed,
                            "prompt": prompt,
                        }

                    except torch.cuda.OutOfMemoryError:
                        st.error(
                            "⚠️ GPU out of memory! Try a smaller image or reduce Max New Tokens.",
                            icon="🔥",
                        )
                    except Exception as e:
                        st.error(f"Inference failed: {e}", icon="❌")

        # ── Display Results (persisted in session state) ──
        last = st.session_state.get("last_result")
        if last:
            # Annotated image
            st.image(
                last["annotated"],
                use_container_width=True,
                caption=f"Detected {len(last['detections'])} object(s)",
            )

            # Stats
            stats_dict = parse_stats_string(last["stats_raw"])
            render_stats(stats_dict, last["elapsed"])

            # Detection table (scrollable)
            st.markdown(
                '<p class="section-header" style="margin-top:1.2rem;">📊 Detection Results</p>',
                unsafe_allow_html=True,
            )
            color_map = build_color_map(last["detections"])
            render_detection_table(last["detections"], color_map)

            # Raw output
            with st.expander("🔤 Raw Model Output", expanded=False):
                st.code(last["answer"], language=None)

            # Download button
            buf = io.BytesIO()
            last["annotated"].save(buf, format="PNG")
            st.download_button(
                label="⬇️  Download Annotated Image",
                data=buf.getvalue(),
                file_name="locateanything_output.png",
                mime="image/png",
                use_container_width=True,
            )
        else:
            st.markdown(
                '<div style="text-align:center;padding:6rem 2rem;color:#484f58;">'
                '<p style="font-size:2.5rem;margin:0;">🎯</p>'
                '<p style="margin:0.5rem 0 0 0;">Results will appear here</p>'
                '<p style="font-size:0.8rem;margin:0.3rem 0 0 0;">'
                'Upload an image → Set task → Run Inference</p>'
                '</div>',
                unsafe_allow_html=True,
            )


# ═══════════════════════════════════════════════════════════════
# Entry Point
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    main()
