# Project Structure

## Root Files
- `main.py` - Main application entry point with GUI and core logic
- `requirements.txt` - Python dependencies
- `README.md` - Project documentation and setup instructions

## Core Modules
- `region_selector.py` - Platform-specific screen capture utilities
- `token_auth.py` - Bearer token authentication client for Bedrock API
- `fix_permissions.py` - macOS screen recording permission helper

## Testing and Development
- `test_screenshot.py` - Screen capture testing utility
- `test_*.png` - Generated test images from capture tests
- `permission_test.png` - Permission test output image

## Architecture Patterns

### Main Application (`main.py`)
- **ScreenAssistantApp class** - Main GUI application controller
- **CredentialsDialog class** - AWS credentials setup dialog
- **Threading pattern** - UI operations run in separate threads to prevent blocking
- **Progress tracking** - Step-by-step progress updates during screen analysis

### Screen Capture (`region_selector.py`)
- **RegionSelector class** - Static methods for platform-specific capture
- **Platform detection** - Automatic macOS vs cross-platform handling
- **Permission management** - Graceful handling of macOS screen recording permissions
- **Fallback strategy** - MSS library as backup when native capture fails

### Authentication (`token_auth.py`)
- **BedrockTokenClient class** - Custom client for bearer token authentication
- **Response compatibility** - Mimics boto3 response structure for seamless integration

## Code Organization Principles
- **Single responsibility** - Each module handles one specific concern
- **Platform abstraction** - OS-specific code isolated in dedicated modules
- **Error handling** - Graceful degradation with user-friendly error messages
- **Mock mode support** - Testing capability without external dependencies

## File Naming Conventions
- Snake_case for Python files
- Descriptive names indicating module purpose
- Test files prefixed with `test_`
- Generated images include descriptive suffixes

## Key Design Patterns
- **Factory pattern** - Platform-specific capture method selection
- **Observer pattern** - Progress updates via callback mechanisms
- **Strategy pattern** - Multiple authentication methods (credentials vs tokens)
- **Template method** - Consistent error handling across modules