import atexit
import time
import random
import capture
import ai_engine_v2 as ai_engine
import re
import pyperclip
import threading
import tkinter as tk
import ctypes
import ctypes.wintypes
from pynput.keyboard import Controller as KeyboardController

# --- Hide Console Window ---
try:
    hWnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hWnd:
        # ctypes.windll.user32.ShowWindow(hWnd, 0)
        pass
except Exception:
    pass

# --- Win32 DPI Awareness ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()

# --- Configuration ---
MOD_ALT = 0x0001
VK_S = 0x53
VK_V = 0x56
VK_D = 0x44
HOTKEY_ID_SOLVE = 1
HOTKEY_ID_TYPE = 2
HOTKEY_ID_TOGGLE = 3
WM_HOTKEY = 0x0312
TRANS_COLOR = '#000001'

# Ensure hotkeys are freed if process exits
atexit.register(lambda: (
    ctypes.windll.user32.UnregisterHotKey(None, HOTKEY_ID_SOLVE),
    ctypes.windll.user32.UnregisterHotKey(None, HOTKEY_ID_TYPE),
    ctypes.windll.user32.UnregisterHotKey(None, HOTKEY_ID_TOGGLE)
))

def is_mcq_answer(answer):
    """Check if the answer looks like MCQ option(s): A, B, C, D, True, False."""
    a = answer.strip().upper()
    a = re.sub(r'[.,\s]+', ' ', a).strip()
    parts = a.split()
    return bool(parts) and all(p in ('A', 'B', 'C', 'D', 'TRUE', 'FALSE') for p in parts)

class AIShellOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()

        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.85)

        self.root.config(bg=TRANS_COLOR)
        self.root.wm_attributes("-transparentcolor", TRANS_COLOR)

        screen_h = self.root.winfo_screenheight()
        self.win_w, self.win_h = 260, 60
        self.win_x, self.win_y = 12, screen_h - self.win_h - 40
        self.root.geometry(f"{self.win_w}x{self.win_h}+{self.win_x}+{self.win_y}")

        self.main_frame = tk.Frame(self.root, bg=TRANS_COLOR, highlightthickness=0)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.content_label = tk.Label(
            self.main_frame,
            text="",
            fg="#FFFFFF",
            bg=TRANS_COLOR,
            font=("Consolas", 26, "bold"),
            wraplength=250,
            justify=tk.LEFT,
            anchor="w"
        )
        self.content_label.pack(fill=tk.BOTH, expand=True, padx=0)

        # Force window realization to obtain valid HWND for Win32 API calls
        self.root.update()
        wid = self.root.winfo_id()
        self.hwnd = ctypes.windll.user32.GetAncestor(wid, 2) or wid

        self._apply_stealth()

        self.visible = False
        self.is_displaying = False
        self._hide_timer = None

    def _apply_stealth(self):
        try:
            if hasattr(self, 'hwnd') and self.hwnd:
                # Set layered, transparent (click-through), and toolwindow styles
                style = ctypes.windll.user32.GetWindowLongW(self.hwnd, -20)
                ctypes.windll.user32.SetWindowLongW(self.hwnd, -20, style | 0x80000 | 0x20 | 0x80)

                # WDA_EXCLUDEFROMCAPTURE = 0x00000011 (makes window invisible to capture/screenshare)
                WDA_EXCLUDEFROMCAPTURE = 0x00000011
                res = ctypes.windll.user32.SetWindowDisplayAffinity(self.hwnd, WDA_EXCLUDEFROMCAPTURE)
                if not res:
                    ctypes.windll.user32.SetWindowDisplayAffinity(self.hwnd, 0x00000001)
        except Exception as e:
            print(f"Failed to apply stealth affinity: {e}")

    def show_text(self, text, duration_ms=1600):
        """Show text answer on the overlay (defaults to a quick 1.6s glance)."""
        # Cancel any previous auto-hide timer
        if self._hide_timer:
            try:
                self.root.after_cancel(self._hide_timer)
            except Exception:
                pass
            self._hide_timer = None

        if not self.visible:
            self._apply_stealth()
            self.root.deiconify()
            self.visible = True

        self.content_label.config(text=text, fg="#FFFFFF")
        self.root.update()

        if duration_ms > 0:
            self._hide_timer = self.root.after(duration_ms, self.hide)

    def show_options(self, answer, duration_ms=1600):
        """Show MCQ option letter(s) on overlay."""
        self.show_text(str(answer), duration_ms=duration_ms)

    def show_copied(self):
        """Subtle dot — answer is ready."""
        self.show_text(".", duration_ms=1000)

    def show_error(self, text="ERR"):
        """Subtle error indicator on overlay."""
        if self._hide_timer:
            try:
                self.root.after_cancel(self._hide_timer)
            except Exception:
                pass
            self._hide_timer = None

        if not self.visible:
            self._apply_stealth()
            self.root.deiconify()
            self.visible = True

        self.content_label.config(text=text, fg="#FF5555")
        self.root.update()
        self._hide_timer = self.root.after(1200, self.hide)

    def hide(self):
        if self._hide_timer:
            try:
                self.root.after_cancel(self._hide_timer)
            except Exception:
                pass
            self._hide_timer = None
        self.root.withdraw()
        self.visible = False
        self.is_displaying = False
        self.content_label.config(text="")
        self.root.update()

    def run(self):
        self.root.mainloop()

# --- Global ---
overlay = None
processing_lock = threading.Lock()
typing_lock = threading.Lock()
last_answer = None

def toggle_overlay():
    """Instantly toggle overlay on/off on demand (Peek or Dismiss)."""
    global last_answer
    if not overlay:
        return
    if overlay.visible:
        # If currently shown, dismiss it immediately
        overlay.root.after(0, overlay.hide)
    else:
        # If hidden, peek at the answer for 2 seconds (or until Alt+D is pressed again)
        text = last_answer or pyperclip.paste() or "NO ANS"
        overlay.root.after(0, lambda: overlay.show_text(str(text), duration_ms=2500))

def _do_process():
    global last_answer
    try:
        img = capture.capture_screen()

        print("AI Analyzing...")
        answer = ai_engine.get_answer_from_image(img)

        if answer and answer not in ["NO_QUESTION", "ERROR", "RATE_LIMIT"]:
            last_answer = answer
            if is_mcq_answer(answer):
                print(f"MCQ: {answer}")
                overlay.root.after(0, lambda: overlay.show_options(answer))
            else:
                print(f"FILL: {answer} (visible on overlay, press Alt+V to auto-type)")
                overlay.root.after(0, lambda: overlay.show_text(answer))
                def copy_to_clipboard():
                    try:
                        pyperclip.copy(answer)
                    except:
                        pass
                threading.Thread(target=copy_to_clipboard, daemon=True).start()
        elif answer == "RATE_LIMIT":
            print("Rate limit hit - try again in a moment")
            overlay.root.after(0, lambda: overlay.show_error("WAIT"))
        elif answer == "ERROR":
            print(f"Error from AI engine")
            overlay.root.after(0, lambda: overlay.show_error("ERR"))
        else:
            print(f"No answer: {answer}")
            overlay.root.after(0, overlay.hide)
    except Exception as e:
        print(f"Error: {e}")
        overlay.root.after(0, lambda: overlay.show_error("ERR"))
    finally:
        processing_lock.release()

def process_hotkey():
    if not processing_lock.acquire(blocking=False):
        return
    threading.Thread(target=_do_process, daemon=True).start()

def type_answer():
    """Simulates real keyboard keystrokes to type text, completely bypassing paste blockers."""
    if not typing_lock.acquire(blocking=False):
        return
    try:
        global last_answer
        # Use bot's answer, or fall back to whatever is currently in the clipboard
        text_to_type = last_answer or pyperclip.paste()
        if not text_to_type:
            print("No text available to type.")
            if overlay:
                overlay.root.after(0, lambda: overlay.show_error("NO TEXT"))
            return

        # Give user 200ms to release the Alt+V keys so modifiers aren't active
        time.sleep(0.2)
        keyboard = KeyboardController()
        print(f"Auto-typing ({len(str(text_to_type))} chars)...")
        for char in str(text_to_type):
            keyboard.type(char)
            # Fast, natural keystroke interval (bypasses paste-blocking scripts)
            time.sleep(random.uniform(0.012, 0.025))
        print("Auto-typing completed.")
    except Exception as e:
        print(f"Typing error: {e}")
    finally:
        typing_lock.release()

def setup_hotkey():
    user32 = ctypes.windll.user32
    if not user32.RegisterHotKey(None, HOTKEY_ID_SOLVE, MOD_ALT, VK_S):
        print("ERROR: Alt+S hotkey failed. Another app might be using it.")
    if not user32.RegisterHotKey(None, HOTKEY_ID_TYPE, MOD_ALT, VK_V):
        print("ERROR: Alt+V hotkey failed. Another app might be using it.")
    if not user32.RegisterHotKey(None, HOTKEY_ID_TOGGLE, MOD_ALT, VK_D):
        print("ERROR: Alt+D hotkey failed. Another app might be using it.")

    msg = ctypes.wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0):
        if msg.message == WM_HOTKEY:
            if msg.wParam == HOTKEY_ID_SOLVE:
                process_hotkey()
            elif msg.wParam == HOTKEY_ID_TYPE:
                threading.Thread(target=type_answer, daemon=True).start()
            elif msg.wParam == HOTKEY_ID_TOGGLE:
                toggle_overlay()

    user32.UnregisterHotKey(None, HOTKEY_ID_SOLVE)
    user32.UnregisterHotKey(None, HOTKEY_ID_TYPE)
    user32.UnregisterHotKey(None, HOTKEY_ID_TOGGLE)

def main():
    global overlay
    print("="*50)
    print("  AI ASSISTANT READY")
    print("  Alt + S : Capture & Solve")
    print("  Alt + D : Toggle Answer (Peek or Dismiss instantly)")
    print("  Alt + V : Auto-Type Answer (bypasses paste blocks)")
    print("="*50)

    threading.Thread(target=setup_hotkey, daemon=True).start()
    overlay = AIShellOverlay()
    overlay.run()

if __name__ == "__main__":
    main()
