# 🩺 OCR-Medical  
**Desktop Application for Intelligent Medical Document OCR**

---

## 📘 Giới thiệu

**OCR-Medical** là ứng dụng nhận dạng và trích xuất thông tin từ **hóa đơn y tế, đơn thuốc, phiếu xét nghiệm,** …  
được xây dựng bằng **PySide6 (GUI)** kết hợp **Waifu2x (upscaler)** và **Qwen-VL OCR** để nâng cao độ chính xác khi đọc ảnh.

Ứng dụng có giao diện trực quan, hỗ trợ **xử lý hàng loạt ảnh**, **hiển thị Markdown**, và **lưu trữ kết quả có cấu trúc**.

---

## 🧭 Quy trình khởi chạy

### 🔹 1. Clone dự án
```bash
git clone https://github.com/<your-username>/OCR-Medical.git
cd OCR-Medical
```

### 🔹 2. Thiết lập môi trường (chạy 1 lần)
Chạy file **`setup_env.bat`** (Windows)  
hoặc **`setup_env.sh`** (Linux/macOS nếu có).

```bash
setup_env.bat
```

Tác dụng:
- Tự động tạo môi trường ảo (conda/venv)
- Cài toàn bộ thư viện trong `requirements.txt`
- Kiểm tra và xác nhận cài đặt thành công

---

### 🔹 3. Chạy ứng dụng
Sau khi thiết lập xong, chạy:
```bash
run_app.bat
```

Ứng dụng sẽ khởi động GUI:
- **HomePage** → chọn ảnh / thư mục  
- **ExtractInfoPage** → xử lý OCR và hiển thị kết quả  
- **FileLogPage** → xem lại lịch sử xử lý  
- **SettingPage** → đổi theme, lưu thư mục, chọn thiết bị CPU/GPU  

---

## ⚙️ Cấu trúc dự án

```
OCR-Medical/
├─ ocr_medical/
│  ├─ main.py                  # Giao diện chính
│  ├─ core/                    # Xử lý OCR, pipeline, waifu2x, status
│  ├─ ui/                      # Layout + style (PySide6)
│  ├─ utils/                   # Logging, path helper
│  ├─ data/                    # Output, sample images
│  └─ config/                  # Cấu hình app
├─ requirements.txt            # Danh sách thư viện
├─ setup_env.bat               # Thiết lập môi trường (chạy 1 lần)
├─ run_app.bat                 # Chạy ứng dụng
└─ README.md
```

---

## 🧠 Công nghệ sử dụng

| Thành phần | Mô tả |
|-------------|-------|
| **PySide6** | Giao diện người dùng (UI/UX) |
| **Torch + Waifu2x** | Tăng độ phân giải & giảm nhiễu ảnh trước OCR |
| **Markdown / QTextBrowser** | Hiển thị và chỉnh sửa kết quả OCR |
| **OpenCV + Pillow** | Xử lý ảnh đầu vào |
| **Requests / Qwen-VL API** | Gọi mô hình OCR và phân tích văn bản |
| **QSS Theme System** | Giao diện sáng – tối, tùy chỉnh qua JSON |

---

## 🧰 Cấu hình mẫu `config/app_config.json`

```json
{
  "device_preference": "auto",
  "storage_dir": "",
  "theme": "light"
}
```
- `"auto"` → tự chọn GPU nếu có  
- `"cpu"` / `"cuda"` → ép chọn thiết bị  
- `"storage_dir"` → thư mục lưu kết quả  
- `"theme"` → "light" hoặc "dark"

---

## 🧾 Cài thủ công (nếu cần)

Nếu không dùng `.bat`, bạn có thể chạy thủ công:

```bash
# 1. Tạo môi trường
conda create -n ocr-medical python=3.10
conda activate ocr-medical

# 2. Cài thư viện
pip install -r requirements.txt

# 3. Chạy app
python ocr_medical/main.py
```

---

## ⚠️ Lưu ý

- Lần đầu chạy có thể **tải model Waifu2x từ GitHub**, cần internet.  
- Nếu không có GPU, app tự chuyển sang CPU (chậm hơn).  
- Khi build `.exe` bằng PyInstaller, hãy dùng `requirements_full.txt` để đảm bảo đủ dependency.

---

## 🧑‍💻 Tác giả

**Nguyễn Văn Minh Khánh**  
Khoa Kỹ thuật & Công nghệ – Đại học Huế  
📧 [minhkhanh.dev@outlook.com](mailto:minhkhanh.dev@outlook.com)

---

## ⭐ Góp ý / Hỗ trợ
Nếu bạn thấy dự án hữu ích, hãy ⭐ **star repo** để ủng hộ!  
Mọi góp ý hoặc issue có thể gửi tại [Issues](https://github.com/<your-username>/OCR-Medical/issues).

---
