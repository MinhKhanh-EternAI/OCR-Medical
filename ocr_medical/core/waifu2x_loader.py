import torch
import json
import logging
from pathlib import Path
from ocr_medical.core.status import status_manager

logger = logging.getLogger(__name__)

# ============================================================
#  Utility: Device selection
# ============================================================
def get_device_from_config():
    """Chọn thiết bị dựa theo app_config.json (auto / cpu / cuda)."""
    try:
        config_path = Path(__file__).resolve().parent.parent / "config" / "app_config.json"
        device_pref = "auto"

        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                device_pref = cfg.get("device_preference", "auto").lower()

        if device_pref == "cpu":
            device = torch.device("cpu")
            status_manager.add("⚙️ Running on CPU (forced by config)")
        elif device_pref == "cuda":
            if torch.cuda.is_available():
                device = torch.device("cuda")
                status_manager.add("🚀 Using GPU (CUDA) as configured")
            else:
                device = torch.device("cpu")
                status_manager.add("⚠️ GPU not available. Falling back to CPU.")
        else:  # auto
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            if device.type == "cuda":
                status_manager.add("🚀 GPU detected — using CUDA for processing")
            else:
                status_manager.add("⚙️ No GPU found — using CPU")

        logger.info(f"[Waifu2x] Selected device: {device}")
        return device

    except Exception as e:
        logger.error(f"Error reading config for device selection: {e}")
        status_manager.add("⚠️ Defaulting to CPU due to config error")
        return torch.device("cpu")


# ============================================================
#  Main: Load Waifu2x model
# ============================================================
def load_waifu2x(
    # ---- Model options ----
    model_type="art_scan",     # 'art', 'photo', 'art_scan'
    method="noise_scale",      # 'scale', 'noise', 'noise_scale', 'auto_scale'
    noise_level=3,             # -1=off, 0=none, 1=low, 2=medium, 3=high
    scale=2,                   # 1, 1.6, 2, 4

    # ---- Performance options ----
    tile_size=64,              # 64/128/256 (smaller for low VRAM)
    batch_size=4,              # parallel tiles
    amp=True,                  # use FP16 if available
    source="github",           # model source
    repo="nagadomi/nunif",     # repo or local model path
):
    """
    Load the Waifu2x model dynamically via torch.hub with auto GPU/CPU selection.
    """
    try:
        # Tự chọn thiết bị
        device = get_device_from_config()
        device_ids = [0] if device.type == "cuda" else [-1]

        status_manager.add("🔄 Loading Waifu2x model...")

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

        # Nếu model hỗ trợ .to(device)
        if hasattr(upscaler, "to"):
            upscaler = upscaler.to(device)

        status_manager.add(f"✅ Waifu2x model loaded successfully on {device.type.upper()}")
        logger.info(f"[Waifu2x] Model ready on {device.type}")
        return upscaler

    except Exception as e:
        status_manager.add(f"❌ Failed to load Waifu2x model: {e}")
        logger.error(f"[Waifu2x] Error: {e}")
        raise
