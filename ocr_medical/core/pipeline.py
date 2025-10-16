from pathlib import Path
from urllib.parse import urlparse
from io import BytesIO
import requests
from PIL import Image
from ocr_medical.core.waifu2x_loader import load_waifu2x
from ocr_medical.core.process_image import process_image
from ocr_medical.core.ocr_extract import call_qwen_ocr
from ocr_medical.core.status import status_manager

# Output mặc định: OCR-Medical/data/output/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "output"   # 📌 sửa lại đường dẫn để nằm trong data/output

# 📌 Prompt mặc định
DEFAULT_PROMPT = (
    "Hãy trích xuất toàn bộ nội dung văn bản có trong ảnh, bao gồm cả chữ, số, ký hiệu đặc biệt "
    "và các cấu trúc bảng nếu có. "
    "Yêu cầu trình bày kết quả như sau:\n"
    "1. Nếu ảnh chứa bảng dữ liệu:\n"
    "   - Trình bày lại dưới dạng **bảng Markdown** với định dạng rõ ràng.\n"
    "   - Hàng tiêu đề in đậm.\n"
    "   - Các cột căn chỉnh bằng dấu | và khoảng trắng đều.\n"
    "   - Các mục quan trọng (ví dụ: MIỄN DỊCH, PXN VI SINH) phải in đậm.\n"
    "   - Giữ nguyên ký hiệu đặc biệt (ví dụ dấu * phải hiển thị là \\*).\n"
    "   - Giá trị số và đơn vị giữ nguyên định dạng gốc.\n"
    "2. Nếu ảnh **không chứa bảng** mà chỉ có đoạn văn, chữ viết hoặc ký tự rời:\n"
    "   - Hãy trích xuất toàn bộ văn bản đúng theo thứ tự hiển thị từ trên xuống dưới, trái sang phải.\n"
    "   - Giữ nguyên ngắt dòng, dấu câu và ký hiệu đặc biệt.\n"
    "   - Không thêm lời giải thích hay định dạng Markdown.\n"
    "Kết quả chỉ bao gồm phần nội dung đã trích xuất, không thêm mô tả hoặc phân tích."
)


def save_text(processed_path: Path, img_name: str, output_root: Path):
    """
    Gọi OCR và lưu kết quả Markdown
    """
    try:
        out_dir_text = output_root / img_name / "text"
        out_dir_text.mkdir(parents=True, exist_ok=True)

        extracted = call_qwen_ocr(str(processed_path), DEFAULT_PROMPT)
        ocr_path = out_dir_text / f"{img_name}_processed.md"
        with open(ocr_path, "w", encoding="utf-8") as f:
            f.write(extracted)

        status_manager.add("✅ Lưu OCR (text)")
    except Exception as e:
        status_manager.add(f"❌ Lỗi lưu OCR: {e}")
        raise

def process_input(input_path: str, output_root: str = None):
    """
    Pipeline OCR:
    - Input: file ảnh, folder, URL
    - Output: original, processed, text (.md)
    """
    status_manager.reset()
    output_root = Path(output_root) if output_root else DEFAULT_OUTPUT
    upscaler = load_waifu2x()

    # Nếu là URL
    if input_path.startswith(("http://", "https://")):
        response = requests.get(input_path)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content)).convert("RGB")
        img_name = Path(urlparse(input_path).path).stem
        _, proc_path = process_image(upscaler, img, img_name, output_root)
        save_text(proc_path, img_name, output_root)
        return status_manager

    p = Path(input_path)
    if p.is_file():
        img = Image.open(p).convert("RGB")
        img_name = p.stem
        _, proc_path = process_image(upscaler, img, img_name, output_root)
        save_text(proc_path, img_name, output_root)

    elif p.is_dir():
        for file in p.glob("*.*"):
            if file.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"]:
                img = Image.open(file).convert("RGB")
                img_name = file.stem
                _, proc_path = process_image(upscaler, img, img_name, output_root)
                save_text(proc_path, img_name, output_root)
    else:
        status_manager.add(f"❌ Input {input_path} không tồn tại")
        raise FileNotFoundError(f"Input {input_path} không tồn tại")

    return status_manager
