from pathlib import Path
from PIL import Image
from ocr_medical.core.status import status_manager


def save_original(img: Image.Image, img_name: str, output_root: Path) -> Path:
    """
    Lưu ảnh gốc vào output/{img_name}/original
    """
    try:
        out_dir = output_root / img_name / "original"
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"{img_name}_original.png"
        img.save(path)
        status_manager.add("✅ Lưu ảnh gốc (original)")
        return path
    except Exception as e:
        status_manager.add(f"❌ Lỗi lưu ảnh gốc: {e}")
        raise


def enhance_image(upscaler, img: Image.Image, img_name: str, output_root: Path) -> Path:
    """
    Xử lý ảnh bằng Waifu2x và lưu vào output/{img_name}/processed
    """
    try:
        out_dir = output_root / img_name / "processed"
        out_dir.mkdir(parents=True, exist_ok=True)
        enhanced = upscaler(img)
        path = out_dir / f"{img_name}_processed.png"
        enhanced.save(path)
        status_manager.add("✅ Xử lý ảnh (processed)")
        return path
    except Exception as e:
        status_manager.add(f"❌ Lỗi xử lý ảnh: {e}")
        raise


def process_image(upscaler, img: Image.Image, img_name: str, output_root: Path) -> tuple[Path, Path]:
    """
    Trả về (path ảnh gốc, path ảnh đã xử lý)
    """
    orig = save_original(img, img_name, output_root)
    proc = enhance_image(upscaler, img, img_name, output_root)
    return orig, proc
