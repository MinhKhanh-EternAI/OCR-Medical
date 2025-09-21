# OCR_Medical

Ứng dụng OCR hỗ trợ nhận diện và trích xuất thông tin từ **phiếu xét nghiệm y tế**, phát triển bằng **Python + PySide6**.

---

## 🚀 Tính năng chính
- Giao diện đồ họa (PySide6) cho thao tác trực quan.
- Kéo thả ảnh phiếu xét nghiệm để xử lý.
- Pipeline OCR tự động:
  - Tiền xử lý ảnh (lọc nhiễu, scale, waifu2x).
  - Phân tích và trích xuất văn bản bằng mô hình OCR.
- Xem và tải kết quả dưới dạng text/table.
- Hỗ trợ theme sáng / tối.
- Ghi log và quản lý file xử lý.

---

## 📂 Cấu trúc dự án

```bash
OCR_Medical/
│   main.py              # file chạy chính
│   requirements.txt     # thư viện cần thiết
│   app_config.json      # cấu hình app
│   watch.py             # auto reload khi dev
│
├── assets/              # font, icon, logo
├── core/                # xử lý OCR, pipeline, tiền xử lý ảnh
├── data/                # dữ liệu mẫu + output
├── tests/               # unit test
├── ui/                  # giao diện (PySide6)
│   ├── pages/           # Home, File Log, Extract, Review, Setting
│   ├── style/           # theme, QSS
│   └── widgets/         # custom widget
└── utils/               # tiện ích (logger, helpers)
```

---

## ⚙️ Cài đặt

Yêu cầu Python **>=3.10**.

1. Clone dự án:
```bash
git clone https://github.com/<username>/OCR_Medical.git
cd OCR_Medical/ocr_medical
```

2. Cài thư viện:
```bash
pip install -r requirements.txt
```

---

## ▶️ Chạy ứng dụng

```bash
python -m ocr_medical.main
```

Hoặc chạy trực tiếp:
```bash
python main.py
```

---

## 🧪 Test

```bash
pytest tests/
```

---

## 📖 Tài liệu liên quan
- [Kickoff N6-BData.pdf](../Requirement/Kickoff%20N6-BData.pdf)

---
