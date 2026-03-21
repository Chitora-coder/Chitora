import capture
import ai_engine
import pyperclip
from pynput import keyboard
import threading
import sys
import os
import ctypes
import time

# --- Cursor Logic ---
user32 = ctypes.windll.user32
IDC_WAIT = 32514
OCR_NORMAL = 32512
SPI_SETCURSORS = 0x0057

def set_busy_cursor():
    """Sets the global system cursor to the 'Wait' (Hourglass/Circle) cursor."""
    try:
        # Load the Wait cursor
        # 2 = IMAGE_CURSOR, 0x00008000 = LR_SHARED
        hCursor = user32.LoadImageW(0, IDC_WAIT, 2, 0, 0, 0x00008000)
        # Replace the Standard Arrow (OCR_NORMAL) with the Wait cursor
        user32.SetSystemCursor(hCursor, OCR_NORMAL)
    except Exception as e:
        print(f"Cursor Error: {e}")

def restore_cursor():
    """Restores the global system cursors to default."""
    try:
        # Reloading system cursors resets any SetSystemCursor changes
        user32.SystemParametersInfoW(SPI_SETCURSORS, 0, None, 0)
    except Exception as e:
        print(f"Cursor Reset Error: {e}")

# --- Main App ---

# Hotkey configuration
HOTKEY_COMBINATION = {keyboard.Key.ctrl_l, keyboard.Key.alt_l, keyboard.KeyCode.from_char('s')}

def on_activate():
    print("Hotkey triggered!")
    
    # Run in a separate thread so visual feedback is immediate and doesn't block
    threading.Thread(target=process_request).start()

def process_request():
    print("Processing...")
    set_busy_cursor() # Show loading
    
    try:
        # 1. Capture
        print("[1/3] Capturing screen...")
        img = capture.capture_screen()
        print(f"[1/3] Screen captured: {img.size}")
        
        # 2. Process
        print("[2/3] Sending to AI...")
        answer = ai_engine.get_answer_from_image(img)
        print(f"[2/3] AI Response: '{answer}'")
        
        if answer and answer != "NO_QUESTION_FOUND":
            # 3. Clipboard
            print("[3/3] Copying to clipboard...")
            pyperclip.copy(answer)
            print("✓ Answer copied to clipboard.")
            print(f"   Content: {answer}")
        else:
            print("✗ No question found or empty response.")
            
    except Exception as e:
        import traceback
        print(f"✗ ERROR during processing:")
        print(traceback.format_exc())
        
    finally:
        restore_cursor() # Always restore
        print("Done.\n")

def main():
    print("Zero-Interface AI Assistant Started.")
    print("Press Alt+S to capture and solve.")
    
    # Hotkey listener
    # Note: Using Key.alt_l is safer for specific 'Alt+S' detection
    with keyboard.GlobalHotKeys({
        '<alt>+s': on_activate
    }) as h:
        h.join()

if __name__ == "__main__":
    main()
