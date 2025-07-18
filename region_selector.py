#!/usr/bin/env python3
"""
Platform-specific screen capture - native tools for macOS, MSS for others
"""

import platform
import subprocess
import tempfile
import os
from PIL import Image
import mss

class RegionSelector:
    """Platform-specific screen capture utility"""
    
    @staticmethod
    def capture_region(parent=None):
        """Capture the full screen using platform-appropriate method"""
        return RegionSelector.capture_full_screen()
    
    @staticmethod
    def capture_full_screen():
        """Capture the full screen using the best method for each platform"""
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            return RegionSelector._capture_macos()
        else:  # Windows, Linux, etc.
            return RegionSelector._capture_mss()
    
    @staticmethod
    def _capture_macos():
        """Capture screen using macOS native screencapture command"""
        try:
            # Create a temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            temp_file.close()
            
            # Use macOS screencapture command
            # -x = no sound
            # -t png = PNG format
            cmd = ['screencapture', '-x', '-t', 'png', temp_file.name]
            
            print(f"Running macOS screencapture: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                print(f"screencapture failed with return code {result.returncode}")
                print(f"stderr: {result.stderr}")
                if os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)
                return None
            
            # Check if the file was created and has content
            if os.path.exists(temp_file.name) and os.path.getsize(temp_file.name) > 0:
                # Load the image
                screenshot = Image.open(temp_file.name)
                # Clean up temp file
                os.unlink(temp_file.name)
                print(f"Successfully captured macOS screen: {screenshot.size}")
                return screenshot
            else:
                print("screencapture did not create a valid file")
                if os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)
                return None
                
        except subprocess.TimeoutExpired:
            print("screencapture command timed out")
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
            return None
        except Exception as e:
            print(f"Error in macOS screen capture: {e}")
            if 'temp_file' in locals() and os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
            return None
    
    @staticmethod
    def _capture_mss():
        """Capture screen using MSS library (cross-platform)"""
        try:
            with mss.mss() as sct:
                # Get all monitors
                monitors = sct.monitors
                print(f"Available monitors: {len(monitors)} (including 'all')")
                
                # Capture the primary monitor (index 1, index 0 is 'all monitors')
                if len(monitors) > 1:
                    screenshot = sct.grab(monitors[1])
                else:
                    # Fallback to all monitors
                    screenshot = sct.grab(monitors[0])
                
                # Convert to PIL Image
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                print(f"Successfully captured screen with MSS: {img.size}")
                return img
                
        except Exception as e:
            print(f"Error in MSS screen capture: {e}")
            return None
    
    @staticmethod
    def test_capture_capability():
        """Test if screen capture is working on this platform"""
        system = platform.system().lower()
        
        if system == "darwin":
            try:
                # Test if screencapture command exists
                result = subprocess.run(['which', 'screencapture'], 
                                      capture_output=True, text=True, timeout=5)
                return result.returncode == 0
            except:
                return False
        else:
            try:
                # Test MSS
                with mss.mss() as sct:
                    monitors = sct.monitors
                    return len(monitors) > 0
            except:
                return False