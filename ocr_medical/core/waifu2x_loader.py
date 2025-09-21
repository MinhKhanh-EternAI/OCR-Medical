import torch
from ocr_medical.core.status import status_manager

def load_waifu2x(
    # ---- Tham số quan trọng ----
    model_type="art_scan",  # kiểu model:
                            #   'art'       = tranh, anime, chữ (OCR thường chọn cái này)
                            #   'photo'     = ảnh chụp
                            #   'art_scan'  = scan giấy/tài liệu

    method="noise_scale",   # chế độ xử lý:
                            #   'scale'        = chỉ phóng to
                            #   'noise'        = chỉ khử nhiễu (không đổi size)
                            #   'noise_sca  le'  = khử nhiễu + phóng to (thường dùng cho OCR)
                            #   'auto_scale'   = tự động chọn scale theo input
    
    noise_level=3,  # mức khử nhiễu:
                    #   -1 = tắt
                    #    0 = none/very low
                    #    1 = low
                    #    2 = medium
                    #    3 = high

    scale=2,    # hệ số phóng to:
                #   1 (no upscale), 1.6, 2, 4 (tuỳ model hỗ trợ)

    # ---- Tối ưu hiệu năng ----
    tile_size=64,       # chia ảnh thành tile 64/128/256/400/640 (VRAM thấp thì giảm)
    batch_size=4,       # số tile xử lý song song (tăng khi có nhiều VRAM)
    device_ids=[-1],    # [-1] = CPU, [0] = GPU, [0,1] = multi-GPU          
    amp=True,           # True = dùng FP16 (tăng tốc, giảm VRAM); chỉ hoạt động trên GPU NVIDIA    


    # ---- Đường dẫn ----
    source="github",        # cho phép đổi sang 'local' nếu muốn
    repo="nagadomi/nunif",  # đường dẫn repo local hoặc 'nagadomi/nunif' trên GitHub
):
    try:
        status_manager.add("🔄 Đang load model Waifu2x...")
        upscaler = torch.hub.load(
            repo,
            'waifu2x',
            source=source,
            model_type=model_type,
            method=method,
            noise_level=noise_level,
            scale=scale,
            tile_size=tile_size,
            batch_size=batch_size,
            device_ids=device_ids,
            amp=amp
        )
        status_manager.add("✅ Load model Waifu2x thành công")
        return upscaler
    except Exception as e:
        status_manager.add(f"❌ Lỗi load model Waifu2x: {e}")
        raise
