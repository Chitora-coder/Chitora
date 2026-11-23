import mss
from PIL import Image, ImageDraw
import ctypes

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

def get_mouse_pos():
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y

def capture_screen():
    """
    Captures the primary monitor content and draws a red circle at the mouse cursor.
    Returns:
        PIL.Image.Image: The captured screenshot with the cursor highlighted.
    """
    with mss.mss() as sct:
        # Capture the primary monitor (monitor 1)
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        
        # Convert to PIL Image
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        
        # Get current mouse position using Win32 API (100% reliable on Windows)
        try:
            mx, my = get_mouse_pos()
            
            # Draw a red circle around the cursor location to guide the AI
            draw = ImageDraw.Draw(img)
            r = 40  # Circle radius
            draw.ellipse((mx - r, my - r, mx + r, my + r), outline="red", width=6)
            draw.ellipse((mx - 5, my - 5, mx + 5, my + 5), fill="red") # Center dot
        except Exception as e:
            print(f"Failed to draw cursor target: {e}")
            
        return img

if __name__ == "__main__":
    # Test capture
    print("Capturing screen...")
    img = capture_screen()
    print(f"Captured image size: {img.size}")
    # img.show() # Debug only
