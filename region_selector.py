#!/usr/bin/env python3
"""
Platform-specific screen capture with macOS permission handling
"""

import platform
import subprocess
import tempfile
import os
from PIL import Image
import mss
import tkinter as tk
from tkinter import messagebox

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
            return RegionSelector._capture_macos_with_permission_check()
        else:  # Windows, Linux, etc.
            return RegionSelector._capture_mss()
    
    @staticmethod
    def _capture_macos_with_permission_check():
        """Capture screen on macOS with permission checking"""
        try:
            # First, try a quick test capture to see if we have permissions
            temp_test = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            temp_test.close()
            
            # Test capture
            cmd = ['screencapture', '-x', '-t', 'png', temp_test.name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and os.path.exists(temp_test.name):
                # Check if we actually captured something meaningful
                test_img = Image.open(temp_test.name)
                
                # Check if image has very few unique colors (might indicate blank desktop)
                colors = test_img.getcolors(maxcolors=100)
                if colors and len(colors) < 10:
                    os.unlink(temp_test.name)
                    return RegionSelector._show_permission_dialog()
                
                print(f"macOS screen capture successful: {test_img.size}")
                os.unlink(temp_test.name)
                
                # Now do the actual capture
                temp_final = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                temp_final.close()
                
                result = subprocess.run(['screencapture', '-x', '-t', 'png', temp_final.name], 
                                      capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0 and os.path.exists(temp_final.name):
                    final_img = Image.open(temp_final.name)
                    os.unlink(temp_final.name)
                    return final_img
                else:
                    if os.path.exists(temp_final.name):
                        os.unlink(temp_final.name)
                    return None
            else:
                if os.path.exists(temp_test.name):
                    os.unlink(temp_test.name)
                return RegionSelector._show_permission_dialog()
                
        except Exception as e:
            print(f"macOS capture error: {e}")
            return RegionSelector._show_permission_dialog()
    
    @staticmethod
    def _show_permission_dialog():
        """Show dialog about screen recording permissions"""
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            
            result = messagebox.askyesno(
                "Screen Recording Permission Required",
                "This app needs Screen Recording permission to capture your screen.\n\n"
                "Steps to enable:\n"
                "1. Open System Preferences\n"
                "2. Go to Security & Privacy\n"
                "3. Click on Privacy tab\n"
                "4. Select 'Screen Recording' from the list\n"
                "5. Check the box next to Python or Terminal\n"
                "6. Restart this application\n\n"
                "Would you like to try MSS capture instead?\n"
                "(This might work without special permissions)"
            )
            
            root.destroy()
            
            if result:
                return RegionSelector._capture_mss()
            else:
                return None
                
        except Exception as e:
            print(f"Permission dialog error: {e}")
            # Fallback to MSS if dialog fails
            return RegionSelector._capture_mss()
    
    @staticmethod
    def _capture_mss():
        """Capture screen using MSS library (cross-platform)"""
        try:
            with mss.mss() as sct:
                # Get all monitors
                monitors = sct.monitors
                print(f"MSS: Available monitors: {len(monitors)}")
                
                # Capture the primary monitor (index 1, index 0 is 'all monitors')
                if len(monitors) > 1:
                    screenshot = sct.grab(monitors[1])
                else:
                    # Fallback to all monitors
                    screenshot = sct.grab(monitors[0])
                
                # Convert to PIL Image
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                print(f"MSS screen capture successful: {img.size}")
                return img
                
        except Exception as e:
            print(f"MSS capture error: {e}")
            return None
    
    @staticmethod
    def open_system_preferences():
        """Open macOS System Preferences to Screen Recording settings"""
        try:
            subprocess.run([
                'open', 
                'x-apple.systempreferences:com.apple.preference.security?Privacy_ScreenCapture'
            ])
        except Exception as e:
            print(f"Could not open System Preferences: {e}")
    
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