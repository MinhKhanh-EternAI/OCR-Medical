import base64
import json
import requests
from ocr_medical.core.status import status_manager

BASE_URL = "http://192.168.1.11:1234//v1"
MODEL_ID = "qwen/qwen2.5-vl-7b"


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
    mime = infer_mime_from_filename(path)
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"


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
        "temperature": 0.1,
        "max_tokens": 1500,
        "stream": False,
    }
    headers = {"Content-Type": "application/json"}

    try:
        status_manager.add(f"🔄 OCR cho ảnh: {image_path}")
        resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=180)
        resp.raise_for_status()
        data = resp.json()
        result = data["choices"][0]["message"]["content"]
        status_manager.add("✅ OCR thành công")
        return result
    except Exception as e:
        status_manager.add(f"❌ Lỗi OCR: {e}")
        raise
