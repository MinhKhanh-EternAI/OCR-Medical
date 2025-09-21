import sys
from pathlib import Path

# Thư mục gốc OCR-Medical
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.pipeline import process_input
from core.status import status_manager


def test_image():
    img_path = r"C:\Users\khanhnvm\Documents\workspace\BData 2025\n6_ocrmedical\ocr_medical\data\samples\test_04.jpg"
    process_input(img_path)

    print("\n--- Log xử lý ảnh đơn ---")
    for msg in status_manager.messages:
        print(msg)


def test_folder():
    folder_path = r"C:\Users\khanhnvm\Documents\workspace\BData\n6_ocrmedical\OCR-Medical\data\samples"
    process_input(folder_path)

    print("\n--- Log xử lý folder ---")
    for msg in status_manager.messages:
        print(msg)


def test_url():
    url = "https://example.com/test.png"
    process_input(url)

    print("\n--- Log xử lý ảnh từ URL ---")
    for msg in status_manager.messages:
        print(msg)


if __name__ == "__main__":
    test_image()
    # test_folder()
    # test_url()

    # python -m ocr_medical.tests.test_pipeline
