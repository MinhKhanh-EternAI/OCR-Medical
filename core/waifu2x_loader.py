import torch
from core.status import status_manager


def load_waifu2x(
    model_type="art_scan",
    method="noise_scale",
    noise_level=3,
    scale=2,
    tile_size=64,
    batch_size=4,
    device_ids=None,   # auto detect nếu None
    amp=True,
    source="github",
    repo="nagadomi/nunif",
):
    """
    Load model Waifu2x với tự động phát hiện thiết bị (GPU / CPU).
    """
    try:
        # ------------------------------------------------
        # 🔍 Tự động phát hiện thiết bị
        # ------------------------------------------------
        if device_ids is None:
            if torch.cuda.is_available():
                device_ids = [0]
                device_name = torch.cuda.get_device_name(0)
                status_manager.add(f"💪 Phát hiện GPU: {device_name}")
            else:
                device_ids = [-1]
                status_manager.add("⚙️ Không có GPU — sử dụng CPU")

        # ------------------------------------------------
        # 🚀 Load model
        # ------------------------------------------------
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
            amp=amp if torch.cuda.is_available() else False,  # tắt amp nếu không có GPU
        )

        status_manager.add("✅ Load model Waifu2x thành công")
        return upscaler

    except Exception as e:
        status_manager.add(f"❌ Lỗi load model Waifu2x: {e}")
        raise


# ==========================================================
# 🔧 TEST TRỰC TIẾP FILE NÀY
# ==========================================================
if __name__ == "__main__":
    status_manager.add("🚀 Test load Waifu2x model bắt đầu...")
    try:
        upscaler = load_waifu2x()
        status_manager.add("🎉 Model load thành công (test)")
        # Bạn có thể test thêm với ảnh:
        # img_path = "sample.png"
        # output = upscaler.process(img_path)
        # output.save("output_upscaled.png")
        # status_manager.add("📸 Ảnh kết quả: output_upscaled.png")
    except Exception as e:
        status_manager.add(f"❌ Lỗi khi test load model: {e}")
