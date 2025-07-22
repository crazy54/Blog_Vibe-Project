#!/usr/bin/env python3
"""
Test script for thumbnail functionality
"""

import tkinter as tk
from PIL import Image, ImageDraw
import sys
import os

# Add the current directory to the path so we can import main
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import ScreenAssistantApp, THUMBNAIL_CONFIG

def create_test_image(width=800, height=600):
    """Create a test image for thumbnail testing"""
    image = Image.new('RGB', (width, height), color='lightblue')
    draw = ImageDraw.Draw(image)
    
    # Draw some test content
    draw.rectangle([50, 50, width-50, height-50], outline='darkblue', width=3)
    draw.text((100, 100), "Test Screenshot", fill='darkblue')
    draw.text((100, 150), f"Size: {width}x{height}", fill='darkblue')
    
    return image

def test_thumbnail_generation():
    """Test thumbnail generation functionality"""
    print("Testing thumbnail generation...")
    
    # Create a test app instance
    root = tk.Tk()
    root.withdraw()  # Hide the main window for testing
    app = ScreenAssistantApp(root, mock_mode=True)
    
    # Test with different image sizes
    test_cases = [
        (800, 600),   # Standard size
        (1920, 1080), # Large size
        (400, 300),   # Small size
        (1000, 500),  # Wide aspect ratio
        (500, 1000),  # Tall aspect ratio
    ]
    
    for width, height in test_cases:
        print(f"\nTesting {width}x{height} image:")
        
        # Create test image
        test_image = create_test_image(width, height)
        
        # Generate thumbnail
        thumbnail = app.generate_thumbnail(test_image)
        
        if thumbnail:
            thumb_width, thumb_height = thumbnail.size
            print(f"  Original: {width}x{height}")
            print(f"  Thumbnail: {thumb_width}x{thumb_height}")
            
            # Verify size constraints
            max_width = THUMBNAIL_CONFIG['max_width']
            max_height = THUMBNAIL_CONFIG['max_height']
            
            if thumb_width <= max_width and thumb_height <= max_height:
                print("  ✅ Size constraints satisfied")
            else:
                print("  ❌ Size constraints violated")
            
            # Verify aspect ratio preservation
            original_ratio = width / height
            thumb_ratio = thumb_width / thumb_height
            ratio_diff = abs(original_ratio - thumb_ratio)
            
            if ratio_diff < 0.01:  # Allow small floating point differences
                print("  ✅ Aspect ratio preserved")
            else:
                print(f"  ❌ Aspect ratio changed: {original_ratio:.3f} -> {thumb_ratio:.3f}")
        else:
            print("  ❌ Thumbnail generation failed")
    
    root.destroy()
    print("\nThumbnail generation test completed!")

def test_screenshot_storage():
    """Test screenshot storage functionality"""
    print("\nTesting screenshot storage...")
    
    root = tk.Tk()
    root.withdraw()
    app = ScreenAssistantApp(root, mock_mode=True)
    
    # Test storing and retrieving screenshot
    test_image = create_test_image(640, 480)
    
    # Store screenshot
    app.store_screenshot(test_image)
    
    # Retrieve screenshot
    stored_image = app.get_current_screenshot()
    
    if stored_image:
        if stored_image.size == test_image.size:
            print("  ✅ Screenshot storage and retrieval working")
        else:
            print("  ❌ Screenshot size mismatch after storage")
    else:
        print("  ❌ Screenshot storage failed")
    
    # Test clearing screenshot
    app.store_screenshot(None)
    cleared_image = app.get_current_screenshot()
    
    if cleared_image is None:
        print("  ✅ Screenshot clearing working")
    else:
        print("  ❌ Screenshot clearing failed")
    
    root.destroy()
    print("Screenshot storage test completed!")

def main():
    """Run all tests"""
    print("🧪 Testing Thumbnail Functionality")
    print("=" * 40)
    
    try:
        test_thumbnail_generation()
        test_screenshot_storage()
        
        print("\n🎉 All tests completed!")
        print("\nTo test the full UI functionality:")
        print("1. Run: python main.py --mock")
        print("2. Click 'Analyze Screen'")
        print("3. Approve a screenshot")
        print("4. Check if thumbnail appears above AI output")
        print("5. Click thumbnail to open full-size viewer")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()