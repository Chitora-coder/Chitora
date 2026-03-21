import capture
import ai_engine_v2 as ai_engine
from pynput import keyboard
import pyperclip
import threading
import time
import tkinter as tk
from tkinter import font as tkfont
import ctypes

# --- Win32 DPI Awareness ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()

# --- Configuration ---
HOTKEY = '<alt>+s'
OVERLAY_DURATION = 4  # Seconds to show a single answer
TRANS_COLOR = '#000001' # Custom transparency key

class AIShellOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw() 
        
        # Window Setup
        self.root.overrideredirect(True) 
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 1.0) 
        
        # Transparent background setup
        self.root.config(bg=TRANS_COLOR)
        self.root.wm_attributes("-transparentcolor", TRANS_COLOR)
        
        # Window size & position (More Left & More Top)
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        self.win_w, self.win_h = 400, 100
        # x=10 (further left), y = screen_h - height - 40 (bottom left)
        self.win_x, self.win_y = 10, screen_h - self.win_h - 40 
        self.root.geometry(f"{self.win_w}x{self.win_h}+{self.win_x}+{self.win_y}")

        # Main Container (Transparent)
        self.main_frame = tk.Frame(self.root, bg=TRANS_COLOR, highlightthickness=0)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Content (Pure White text)
        self.content_label = tk.Label(
            self.main_frame,
            text="",
            fg="#FFFFFF", # Pure White text
            bg=TRANS_COLOR,
            font=("Arial", 32, "bold"), 
            wraplength=380,
            justify=tk.LEFT,
            anchor="w"
        )
        self.content_label.pack(fill=tk.BOTH, expand=True, padx=0)

        # Make window click-through (Win32)
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
        style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, style | 0x80000 | 0x20 | 0x80)

        self.visible = False
        self.is_displaying = False

    def show(self, text, status='text'):
        # Force immediate update
        self.content_label.config(text=text)
        if not self.visible:
            self.root.deiconify()
            self.visible = True
        self.root.update()

    def show_sequential(self, answer):
        """Handle multi-correct or single answers with sequential logic."""
        if self.is_displaying: return
        self.is_displaying = True
        
        if not self.visible:
            self.root.deiconify()
            self.visible = True
        
        # Split by comma if multiple answers
        parts = [p.strip() for p in str(answer).split(',')]
        
        def display_part(index):
            if index < len(parts):
                # Briefly blank the screen so user sees the change
                self.content_label.config(text="")
                self.root.update()
                time.sleep(0.1)
                
                # Show the answer part
                self.content_label.config(text=parts[index])
                self.root.update()
                
                # Wait 2 seconds (buffer gap)
                self.root.after(2000, lambda: display_part(index + 1))
            else:
                self.hide()
                self.is_displaying = False

        display_part(0)

    def hide(self):
        self.root.withdraw()
        self.visible = False
        self.content_label.config(text="")
        self.root.update()

    def run(self):
        self.root.mainloop()

# --- Global Engine Instance ---
overlay = None
processing_lock = threading.Lock()

def _do_process():
    try:
        # 📸 INSTANT CAPTURE: No delays, no dots.
        img = capture.capture_screen()
        
        print("🧠 AI Analyzing (Timeout: 110s)...")
        answer = ai_engine.get_answer_from_image(img)
        
        if answer and answer not in ["NO_QUESTION", "ERROR"]:
            print(f"✅ AI ANSWER: {answer}")
            
            # Use threading for clipboard to avoid blocking
            def copy_to_clipboard():
                try:
                    pyperclip.copy(answer)
                except:
                    pass
            threading.Thread(target=copy_to_clipboard, daemon=True).start()
            
            # Show the real answer(s)
            overlay.root.after(0, lambda: overlay.show_sequential(answer))
        else:
            print(f"❌ FAILED: {answer}")
            # Stealth: show nothing on screen if it fails
            overlay.root.after(0, overlay.hide)
    except Exception as e:
        print(f"Error: {e}")
        overlay.root.after(0, overlay.hide)
    finally:
        processing_lock.release()
        print("READY.")

def process_hotkey():
    # Capture timestamp for debugging
    print("\n🚀 HOTKEY TRIGGERED - INSTANT CAPTURE")
    
    if not processing_lock.acquire(blocking=False): 
        print("⏳ Already processing, ignoring hotkey...")
        return
        
    threading.Thread(target=_do_process, daemon=True).start()

def setup_hotkey():
    with keyboard.GlobalHotKeys({HOTKEY: process_hotkey}) as h:
        h.join()

def main():
    global overlay
    print("="*50)
    print("AI MCQ ASSISTANT V5.1 - STEALTH MODE")
    print("="*50)
    
    # 1. Start Hotkey Thread
    threading.Thread(target=setup_hotkey, daemon=True).start()
    
    # 2. Start Overlay (Main Thread)
    overlay = AIShellOverlay()
    
    print(f"[+] Hotkey Active: {HOTKEY}")
    print("[!] Stealth mode enabled. No startup messages.")
    print("="*50)
    
    overlay.run()

if __name__ == "__main__":
    main()
