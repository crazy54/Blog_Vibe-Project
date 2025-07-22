e#!/usr/bin/env python3
"""
Helper script to fix macOS screen recording permissions
"""

import subprocess
import sys
import os
import shutil

def get_python_executable_info():
    """Get information about the current Python executable"""
    python_path = sys.executable
    python_name = os.path.basename(python_path)
    
    # Check if it's a framework Python (like from python.org installer)
    if "Python.framework" in python_path:
        # Find the actual app bundle
        parts = python_path.split("/")
        for i, part in enumerate(parts):
            if part == "Python.framework":
                # Look for Python.app in the framework
                framework_path = "/".join(parts[:i+1])
                possible_app = os.path.join(framework_path, "Versions", "Current", "Resources", "Python.app")
                if os.path.exists(possible_app):
                    return possible_app, "Python.app"
                break
    
    # Check if it's Homebrew Python
    if "homebrew" in python_path.lower() or "/opt/homebrew" in python_path:
        return python_path, f"Homebrew Python ({python_name})"
    
    # Check if it's system Python
    if python_path.startswith("/usr/bin/"):
        return python_path, f"System Python ({python_name})"
    
    # Default case
    return python_path, f"Python ({python_name})"

def main():
    print("🔧 macOS Screen Recording Permission Fix")
    print("=" * 50)
    
    # Get Python executable info
    python_path, python_description = get_python_executable_info()
    
    print(f"\n🐍 Detected Python: {python_description}")
    print(f"📍 Location: {python_path}")
    
    print("\n📋 Here's what you need to do:")
    print("1. I'll open System Preferences for you")
    print("2. Go to Privacy & Security → Screen Recording")
    print("3. Look for your Python app in the list")
    print("4. If it's not there, click '+' and navigate to:")
    print(f"   {python_path}")
    print("5. Enable the checkbox next to it")
    print("6. You might need to restart this application")
    
    print("\n🚀 Opening System Preferences...")
    
    try:
        # Try to open the Screen Recording settings directly
        subprocess.run([
            'open', 
            'x-apple.systempreferences:com.apple.preference.security?Privacy_ScreenCapture'
        ])
        print("✅ Opened System Preferences to Screen Recording settings")
    except:
        try:
            # Fallback: just open System Preferences
            subprocess.run(['open', '/System/Applications/System Preferences.app'])
            print("✅ Opened System Preferences - navigate to Privacy & Security > Screen Recording")
        except:
            print("❌ Could not open System Preferences automatically")
    
    print(f"\n⚠️  IMPORTANT - Look for: {python_description}")
    print(f"📂 If not found, manually add: {python_path}")
    
    # Also try to open Finder to the Python location to make it easier
    try:
        if os.path.exists(python_path):
            if python_path.endswith('.app'):
                # Open the parent directory and select the app
                parent_dir = os.path.dirname(python_path)
                subprocess.run(['open', '-R', python_path])
                print(f"✅ Opened Finder showing {python_description}")
            else:
                # Open the directory containing the executable
                parent_dir = os.path.dirname(python_path)
                subprocess.run(['open', parent_dir])
                print(f"✅ Opened Finder to Python directory")
    except Exception as e:
        print(f"⚠️  Could not open Finder: {e}")
    
    input("\nPress Enter after you've enabled Screen Recording permission...")
    
    print("\n🧪 Testing screen capture now...")
    
    # Test the capture
    import tempfile
    from PIL import Image
    
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    temp_file.close()
    
    try:
        result = subprocess.run([
            'screencapture', '-x', '-t', 'png', temp_file.name
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and os.path.exists(temp_file.name):
            img = Image.open(temp_file.name)
            print(f"✅ Screen capture working! Size: {img.size}")
            
            # Save test image
            img.save("permission_test.png")
            print("✅ Saved test image as 'permission_test.png'")
            
            # Quick check if it's just desktop
            colors = img.getcolors(maxcolors=100)
            if colors and len(colors) < 5:
                print("⚠️  Warning: Image might still be just desktop wallpaper")
                print("   Try opening some windows and test again")
            else:
                print("🎉 Screen capture appears to be working correctly!")
                print("   You can now use the main application!")
                
        else:
            print("❌ Screen capture still not working")
            print("   You may need to restart Terminal/Python or check permissions again")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)

if __name__ == "__main__":
    main()