import mss
from PIL import Image

def capture_screen():
    """
    Captures the primary monitor content using MSS.
    Returns:
        PIL.Image.Image: The captured screenshot.
    """
    with mss.mss() as sct:
        # Capture the primary monitor (monitor 1)
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        
        # Convert to PIL Image
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        return img

if __name__ == "__main__":
    # Test capture
    print("Capturing screen...")
    img = capture_screen()
    print(f"Captured image size: {img.size}")
    # img.show() # Debug only
