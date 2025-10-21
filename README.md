# OCR-Medical

OCR-Medical là ứng dụng desktop (Python + PySide6) giúp trích xuất văn bản và bảng biểu từ ảnh y học.  
Ứng dụng kết hợp mô hình Waifu2x để nâng chất lượng ảnh và Qwen2.5-VL-7B (qua LM Studio) để nhận dạng văn bản.

---

## 1. Tính năng

- Nâng chất lượng ảnh bằng Waifu2x (model art_scan, noise_scale)
- Trích xuất văn bản và bảng từ ảnh bằng Qwen2.5-VL-7B
- Tùy chỉnh base_url của LM Studio trong Setting
- Lưu kết quả theo cấu trúc: `data/output/<tên_ảnh>/`
- Giao diện trực quan bằng PySide6

---

## 2. Cấu trúc dự án

```
OCR-MEDICAL/
├─ assets/
├─ config/
│   └─ app_config.json
├─ core/
│   ├─ pipeline.py
│   ├─ process_image.py
│   ├─ ocr_extract.py
│   ├─ waifu2x_loader.py
│   └─ status.py
├─ data/
│   ├─ samples/
│   └─ output/
├─ ui/
├─ utils/
├─ requirements.txt
├─ main.py
├─ setup_env.bat
└─ run_app.bat
```

---

## 3. Cài đặt

Yêu cầu: Python 3.9+ (khuyên dùng Windows)

1. Mở Command Prompt trong thư mục dự án.
2. Chạy:
   ```bash
   setup_env.bat
   ```
   Script này sẽ:
   - Tạo môi trường ảo `.venv`
   - Cài đặt thư viện cần thiết
   - Kiểm tra tải model Waifu2x

---

## 4. Cấu hình LM Studio

1. Cài LM Studio: https://lmstudio.ai  
2. Tải model `Qwen/Qwen2.5-VL-7B-Instruct` và chạy model.
3. Ghi nhớ endpoint hiển thị, ví dụ:
   ```
   http://localhost:1234/v1
   ```
4. Mở file `config/app_config.json` và chỉnh:
   ```json
   {
     "base_url": "http://localhost:1234/v1",
     "storage_path": "data/output"
   }
   ```

---

## 5. Sử dụng

### Chạy ứng dụng giao diện:
```bash
run_app.bat
```

### Chạy pipeline bằng mã Python:
```python
from core.pipeline import process_input

process_input("data/samples")
```

Kết quả được lưu trong `data/output/<tên_ảnh>/` gồm:
- `original/` : ảnh gốc  
- `processed/` : ảnh đã nâng chất lượng  
- `text/` : file markdown chứa kết quả OCR

---

## 6. Làm mới môi trường

```bash
rmdir /s /q .venv
setup_env.bat
```

---