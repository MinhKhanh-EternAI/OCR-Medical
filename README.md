# OCR-Medical

OCR-Medical là ứng dụng desktop (Python + PySide6) giúp trích xuất văn bản và bảng biểu từ ảnh y học.  
Ứng dụng kết hợp mô hình **Waifu2x** để nâng chất lượng ảnh và **Qwen2.5-VL-7B** (qua LM Studio) để nhận dạng văn bản.

---

## 1. Tính năng chính

- Nâng chất lượng ảnh bằng **Waifu2x** (model *art_scan*, *noise_scale*)
- Trích xuất văn bản và bảng biểu bằng **Qwen2.5-VL-7B-Instruct**
- Cấu hình **API Base URL**, **Temperature**, **Max Tokens**, **Storage Directory** trong phần *Settings*
- Lưu kết quả theo cấu trúc: `data/output/<tên_ảnh>/`
- Giao diện trực quan, hỗ trợ đa theme (Light/Dark)

---

## 2. Giao diện ứng dụng

| Trang | Ảnh minh họa |
|:------|:--------------|
| **Home Page** | ![Homepage](docs/screenshots/homepage.png) |
| **Extract Info Page** | ![Extract Info](docs/screenshots/extract_info_page.png) |
| **File Log Page** | ![File Log](docs/screenshots/file_log_page.png) |
| **Setting Page** | ![Setting Page](docs/screenshots/setting_page.png) |

---

## 3. Cấu trúc dự án

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
├─ docs/
│   └─ screenshots/        ← ảnh minh họa giao diện
├─ ui/
├─ utils/
├─ requirements.txt
├─ main.py
├─ setup_env.bat
└─ run_app.bat
```

---

## 4. Cài đặt môi trường

Yêu cầu: **Python 3.9+** (khuyên dùng Windows)

1. Mở Command Prompt trong thư mục dự án.  
2. Chạy:
   ```bash
   setup_env.bat
   ```
   Script này sẽ:
   - Tạo môi trường ảo `.venv`
   - Cài đặt toàn bộ thư viện cần thiết
   - Kiểm tra tải model Waifu2x

---

## 5. Cấu hình LM Studio

1. Cài **LM Studio**: https://lmstudio.ai  
2. Tải model `Qwen/Qwen2.5-VL-7B-Instruct` và khởi chạy model.  
3. Ghi nhớ endpoint, ví dụ:
   ```
   http://localhost:1234/v1
   ```
4. Mở file `config/app_config.json` và chỉnh nội dung:
   ```json
   {
     "base_url": "http://localhost:1234/v1",
     "storage_path": "data/output"
   }
   ```

---

## 6. Sử dụng

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
- `processed/` : ảnh sau khi nâng chất lượng  
- `text/` : file markdown chứa kết quả OCR

---

## 7. Làm mới môi trường

```bash
rmdir /s /q .venv
setup_env.bat
```

---

## 8. Thông tin thêm

- **Ngôn ngữ:** Python 3.9+  
- **Framework:** PySide6  
- **Model:** Waifu2x + Qwen2.5-VL-7B  
