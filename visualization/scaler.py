REFERENCE_WIDTH = 2560
REFERENCE_HEIGHT = 1440
MIN_UI_SCALE = 0.5
MAX_UI_SCALE = 1.5


def ui_scale(window) -> float:
    """Return a scale factor for text and spacing based on window size."""
    scale = min(window.width / REFERENCE_WIDTH,
                window.height / REFERENCE_HEIGHT)
    return max(MIN_UI_SCALE, min(scale, MAX_UI_SCALE))
