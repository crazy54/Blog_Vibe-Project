# Design Document

## Overview

The screenshot thumbnail preview feature will add a visual reference component to the AI Screen Assistant interface. This feature integrates a thumbnail display area above the AI output text box and provides a full-size screenshot viewer window. The design leverages the existing Tkinter GUI framework and PIL/Pillow image processing capabilities already present in the application.

## Architecture

### Component Integration
The thumbnail preview feature will be integrated into the existing `ScreenAssistantApp` class with minimal disruption to the current architecture. The feature consists of three main components:

1. **Thumbnail Display Area** - A new UI component in the main window
2. **Screenshot Storage** - In-memory storage of the current screenshot
3. **Full-Size Viewer Window** - A modal window for displaying the full screenshot

### Data Flow
```
Screenshot Capture → Image Processing → Thumbnail Generation → UI Display
                                    ↓
                  Full-Size Storage → Click Handler → Viewer Window
```

## Components and Interfaces

### 1. Thumbnail Display Component

**Location**: Positioned above the AI results text area in the main window
**Implementation**: 
- New `ttk.Label` widget to display the thumbnail image
- Container frame to manage layout and provide visual separation
- Placeholder state when no screenshot is available

**Key Methods**:
```python
def update_thumbnail(self, image: PIL.Image) -> None
def clear_thumbnail(self) -> None
def on_thumbnail_click(self, event) -> None
```

### 2. Screenshot Manager

**Purpose**: Manages screenshot storage and thumbnail generation
**Implementation**: New methods added to `ScreenAssistantApp` class

**Key Methods**:
```python
def store_screenshot(self, image: PIL.Image) -> None
def generate_thumbnail(self, image: PIL.Image, max_size: tuple) -> PIL.Image
def get_current_screenshot(self) -> PIL.Image
```

**Thumbnail Specifications**:
- Maximum dimensions: 200x150 pixels
- Maintain aspect ratio of original screenshot
- Use high-quality resampling (LANCZOS/ANTIALIAS)
- Format: PNG for quality preservation

### 3. Full-Size Viewer Window

**Implementation**: New `ScreenshotViewer` class extending `tk.Toplevel`
**Features**:
- Modal window behavior
- Responsive sizing up to 1080p resolution
- Centered positioning on screen
- Multiple close methods (button, Escape key, window X)

**Key Methods**:
```python
class ScreenshotViewer(tk.Toplevel):
    def __init__(self, parent, image: PIL.Image)
    def setup_ui(self) -> None
    def close_window(self) -> None
    def on_escape_key(self, event) -> None
```

## Data Models

### Screenshot State Management
```python
class ScreenAssistantApp:
    def __init__(self):
        self.current_screenshot: PIL.Image = None
        self.thumbnail_label: ttk.Label = None
        self.thumbnail_frame: ttk.Frame = None
```

### Image Processing Parameters
```python
THUMBNAIL_CONFIG = {
    'max_width': 200,
    'max_height': 150,
    'quality': 'high',
    'format': 'PNG'
}

VIEWER_CONFIG = {
    'max_width': 1920,
    'max_height': 1080,
    'center_on_screen': True,
    'modal': True
}
```

## Error Handling

### Image Processing Errors
- **PIL/Pillow exceptions**: Graceful fallback with error logging
- **Memory constraints**: Automatic image resizing for large screenshots
- **Format compatibility**: Ensure PNG format support across all operations

### UI State Management
- **Missing screenshot**: Hide thumbnail area when no image is available
- **Window focus**: Proper focus management between main window and viewer
- **Threading safety**: Ensure UI updates occur on main thread

### User Experience Safeguards
- **Click responsiveness**: Prevent multiple viewer windows from opening
- **Window positioning**: Handle edge cases for multi-monitor setups
- **Resource cleanup**: Proper disposal of image resources and window objects

## Testing Strategy

### Unit Testing
1. **Thumbnail Generation**
   - Test aspect ratio preservation
   - Verify size constraints
   - Validate image quality

2. **Screenshot Storage**
   - Test image storage and retrieval
   - Verify memory management
   - Test with various image formats and sizes

3. **UI Component Integration**
   - Test thumbnail display updates
   - Verify click event handling
   - Test layout responsiveness

### Integration Testing
1. **End-to-End Workflow**
   - Capture screenshot → Display thumbnail → Open viewer
   - Test with multiple screenshot cycles
   - Verify proper cleanup between captures

2. **Window Management**
   - Test modal behavior of viewer window
   - Verify proper focus handling
   - Test multiple close methods

3. **Cross-Platform Compatibility**
   - Test on macOS (primary platform)
   - Verify Tkinter behavior consistency
   - Test image processing performance

### User Acceptance Testing
1. **Usability Testing**
   - Thumbnail visibility and clarity
   - Click target size and responsiveness
   - Viewer window usability

2. **Performance Testing**
   - Thumbnail generation speed
   - Memory usage with large screenshots
   - UI responsiveness during image processing

## Implementation Considerations

### Performance Optimization
- **Lazy Loading**: Generate thumbnails only when needed
- **Caching**: Store processed thumbnails to avoid regeneration
- **Threading**: Perform image processing off main UI thread when possible

### UI/UX Design
- **Visual Hierarchy**: Ensure thumbnail doesn't dominate the interface
- **Accessibility**: Provide keyboard navigation support
- **Responsive Design**: Adapt to different window sizes

### Integration Points
- **Screenshot Approval Workflow**: Update thumbnail during approval process
- **Progress Indicators**: Show thumbnail update status
- **Mock Mode**: Ensure feature works in mock mode with test images

### Future Extensibility
- **Multiple Screenshots**: Design allows for potential screenshot history
- **Annotation Support**: Structure supports future annotation features
- **Export Functionality**: Framework supports screenshot export capabilities