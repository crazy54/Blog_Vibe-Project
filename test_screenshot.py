#!/usr/bin/env python3
"""
Simple test to see what's being captured
"""

import platform
import subprocess
import tempfile
import os
from PIL import Image
import mss

def test_macos_capture():
    """Test macOS screencapture"""
    print("Testing macOS screencapture...")
    
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    temp_file.close()
    
    try:
        # Use macOS screencapture command
        cmd = ['screencapture', '-x', '-t', 'png', temp_file.name]
        print(f"Running: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            if os.path.exists(temp_file.name) and os.path.getsize(temp_file.name) > 0:
                screenshot = Image.open(temp_file.name)
                print(f"✓ macOS capture successful: {screenshot.size}")
                
                # Save a test copy to see what was captured
                test_file = "test_macos_capture.png"
                screenshot.save(test_file)
                print(f"✓ Saved test image to: {test_file}")
                
                os.unlink(temp_file.name)
                return screenshot
            else:
                print("✗ macOS capture failed: no file created")
        else:
            print(f"✗ macOS capture failed: return code {result.returncode}")
            print(f"stderr: {result.stderr}")
    except Exception as e:
        print(f"✗ macOS capture error: {e}")
    
    if os.path.exists(temp_file.name):
        os.unlink(temp_file.name)
    return None

def test_mss_capture():
    """Test MSS capture"""
    print("\nTesting MSS capture...")
    
    try:
        with mss.mss() as sct:
            monitors = sct.monitors
            print(f"Available monitors: {monitors}")
            
            # Try capturing the primary monitor
            screenshot = sct.grab(monitors[1])
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            print(f"✓ MSS capture successful: {img.size}")
            
            # Save a test copy
            test_file = "test_mss_capture.png"
            img.save(test_file)
            print(f"✓ Saved test image to: {test_file}")
            
            return img
    except Exception as e:
        print(f"✗ MSS capture error: {e}")
        return None

def main():
    system = platform.system().lower()
    print(f"Platform: {system}")
    
    if system == "darwin":
        macos_result = test_macos_capture()
        mss_result = test_mss_capture()
        
        if macos_result:
            print(f"\n✓ macOS method works: {macos_result.size}")
        if mss_result:
            print(f"✓ MSS method works: {mss_result.size}")
            
        if not macos_result and not mss_result:
            print("\n✗ Both methods failed!")
        elif not macos_result:
            print("\n⚠ macOS method failed, but MSS works")
        elif not mss_result:
            print("\n⚠ MSS method failed, but macOS works")
        else:
            print("\n✓ Both methods work!")
    else:
        mss_result = test_mss_capture()
        if mss_result:
            print(f"\n✓ MSS method works: {mss_result.size}")
        else:
            print("\n✗ MSS method failed!")

if __name__ == "__main__":
    main()