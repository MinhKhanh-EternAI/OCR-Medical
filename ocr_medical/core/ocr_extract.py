import base64
import json
import requests
from pathlib import Path
from ocr_medical.core.status import status_manager
from ocr_medical.utils.path_helper import resource_path


# =====================================================
#   Load configuration safely (for .py and .exe)
# =====================================================
def load_config() -> dict:
    """
    Đọc config từ ocr_medical/config/app_config.json
    (tự động tương thích PyInstaller)
    """
    config_path = resource_path("ocr_medical/config/app_config.json")

    try:
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                status_manager.add("⚙️ Config loaded successfully.")
                return data
        else:
            status_manager.add("⚠️ Config file not found, using defaults.")
            return {}
    except Exception as e:
        status_manager.add(f"❌ Error reading config: {e}")
        return {}


# =====================================================
#   Global configuration values
# =====================================================
CONFIG = load_config()

BASE_URL = CONFIG.get("base_url", "http://127.0.0.1:1234/v1")
MODEL_ID = CONFIG.get("model_id", "qwen/qwen2.5-vl-7b")
TEMPERATURE = CONFIG.get("temperature", 0.1)
MAX_TOKENS = CONFIG.get("max_tokens", 1500)
STREAM = CONFIG.get("stream", False)
IS_MAXIMIZED = CONFIG.get("is_maximized", True)


# =====================================================
#   Helper functions
# =====================================================
def infer_mime_from_filename(filename: str) -> str:
    low = filename.lower()
    if low.endswith(".png"):
        return "image/png"
    if low.endswith((".jpg", ".jpeg")):
        return "image/jpeg"
    if low.endswith(".webp"):
        return "image/webp"
    return "application/octet-stream"


def to_data_url(path: str) -> str:
    """
    Đọc file ảnh và encode thành data URL (base64)
    """
    try:
        abs_path = Path(path).resolve()
        if not abs_path.exists():
            raise FileNotFoundError(f"Image not found: {abs_path}")
        mime = infer_mime_from_filename(abs_path.name)
        with open(abs_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        return f"data:{mime};base64,{b64}"
    except Exception as e:
        status_manager.add(f"❌ Error encoding image: {e}")
        raise


# =====================================================
#   OCR call to Qwen API
# =====================================================
def call_qwen_ocr(image_path: str, prompt_text: str) -> str:
    """
    Gọi API Qwen OCR với ảnh đã xử lý (png/jpg/jpeg/webp)
    """
    url = f"{BASE_URL}/chat/completions"
    image_url = to_data_url(image_path)

    payload = {
        "model": MODEL_ID,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "stream": STREAM,
    }
    headers = {"Content-Type": "application/json"}

    try:
        status_manager.add(f"🔄 Sending OCR request: {Path(image_path).name}")
        resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=180)
        resp.raise_for_status()
        data = resp.json()

        if "choices" not in data or not data["choices"]:
            raise ValueError("Invalid OCR response (no 'choices').")

        result = data["choices"][0]["message"]["content"]
        status_manager.add("✅ OCR completed successfully.")
        return result

    except requests.exceptions.ConnectionError:
        status_manager.add("❌ Connection failed. Check BASE_URL or network.")
        raise
    except Exception as e:
        status_manager.add(f"❌ OCR failed: {e}")
        raise


# =====================================================
#   Window state helper
# =====================================================
def get_window_state():
    """
    Trả về trạng thái hiển thị mặc định khi khởi động app
    """
    if IS_MAXIMIZED:
        return "maximized"
    return "normal"
