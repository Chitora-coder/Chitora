"""
MINIMAL TEST - Just create and show a window
"""
import ctypes
import time

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

print("Creating test window...")

# Create a simple popup window
hwnd = user32.CreateWindowExA(
    0x00000008,  # WS_EX_TOPMOST
    b"Static",   # Built-in class
    b"TEST",
    0x80000000,  # WS_POPUP
    100, 100,    # x, y
    200, 100,    # width, height
    None, None, None, None
)

print(f"Window handle: {hwnd}")

if hwnd:
    # Apply capture protection
    result = user32.SetWindowDisplayAffinity(hwnd, 0x00000011)
    print(f"SetWindowDisplayAffinity result: {result}")
    if not result:
        print(f"Error: {ctypes.get_last_error()}")
    
    # Show the window
    user32.ShowWindow(hwnd, 5)  # SW_SHOW
    user32.UpdateWindow(hwnd)
    
    print("\n*** WINDOW SHOULD BE VISIBLE NOW ***")
    print("Check your screen at position (100, 100)")
    print("Press Ctrl+C to close")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nClosing...")
        user32.DestroyWindow(hwnd)
else:
    print(f"Failed to create window! Error: {ctypes.get_last_error()}")
