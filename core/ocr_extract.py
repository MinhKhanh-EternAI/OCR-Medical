import base64
import json
import requests
from pathlib import Path
from core.status import status_manager
from utils.path_helper import resource_path


# =====================================================
#   Load configuration safely (for .py and .exe)
# =====================================================
def load_config() -> dict:
    """
    Đọc config từ config/app_config.json
    (tự động tương thích PyInstaller)
    """
    config_path = resource_path("config/app_config.json")

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
#   Get config values (RELOAD mỗi lần gọi)
# =====================================================
def get_config_value(key: str, default):
    """
    Đọc config real-time để luôn lấy giá trị mới nhất
    """
    config = load_config()
    return config.get(key, default)


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
    # 🔥 RELOAD config mỗi lần gọi để lấy giá trị mới nhất
    base_url = get_config_value("base_url", "http://127.0.0.1:1234/v1")
    model_id = get_config_value("model_id", "qwen/qwen2.5-vl-7b")
    temperature = get_config_value("temperature", 0.1)
    max_tokens = get_config_value("max_tokens", 1500)
    stream = get_config_value("stream", False)

    url = f"{base_url}/chat/completions"
    image_url = to_data_url(image_path)

    payload = {
        "model": model_id,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": stream,
    }
    headers = {"Content-Type": "application/json"}

    try:
        status_manager.add(f"🔄 Sending OCR request to: {base_url}")
        status_manager.add(f"📸 Processing: {Path(image_path).name}")
        resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=180)
        resp.raise_for_status()
        data = resp.json()

        if "choices" not in data or not data["choices"]:
            raise ValueError("Invalid OCR response (no 'choices').")

        result = data["choices"][0]["message"]["content"]
        status_manager.add("✅ OCR completed successfully.")
        return result

    except requests.exceptions.ConnectionError as e:
        status_manager.add(f"❌ Connection failed: {e}")
        status_manager.add(f"🔍 Check BASE_URL: {base_url}")
        raise
    except requests.exceptions.Timeout:
        status_manager.add("❌ Request timeout (>180s)")
        raise
    except requests.exceptions.HTTPError as e:
        status_manager.add(f"❌ HTTP Error: {e}")
        status_manager.add(f"Response: {e.response.text if e.response else 'No response'}")
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
    is_maximized = get_config_value("is_maximized", True)
    if is_maximized:
        return "maximized"
    return "normal"