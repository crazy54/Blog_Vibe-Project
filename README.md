# AI Screen Assistant

A desktop GUI application that captures your screen and uses Amazon Bedrock's Claude 3 Sonnet to analyze what you're working on and provide helpful suggestions. Features a modern interface with screenshot preview, approval workflow, and cross-platform screen capture capabilities.

## Features

### Core Functionality
- **One-button screen capture** - Simple interface for quick screen analysis
- **AI-powered analysis** - Uses Claude 3 Sonnet via Amazon Bedrock for intelligent suggestions
- **Screenshot approval workflow** - Review captured screenshots before sending to AI
- **Thumbnail preview** - See a preview of your last screenshot above AI results
- **Full-size screenshot viewer** - Click thumbnails to view full-size images
- **Mock mode** - Test the application without AWS credentials

### Authentication & Security
- **Multiple authentication methods**:
  - Standard AWS credentials (access key/secret key)
  - Bearer token authentication for Bedrock API
  - Environment variables support
- **Credentials management** - Built-in GUI for AWS credentials setup
- **Graceful fallback** - Automatic switch to mock mode when credentials unavailable

### Cross-Platform Screen Capture
- **macOS native capture** - Uses `screencapture` command with permission handling
- **Cross-platform fallback** - MSS library support for Windows/Linux
- **Permission management** - Automated macOS screen recording permission setup
- **Smart capture detection** - Validates capture quality and handles edge cases

## How It Works

1. **Launch** the application: `python main.py`
2. **Position your content** - Open the application, document, or webpage you need help with
3. **Click "Analyze Screen"** - The app captures your screen after briefly hiding itself
4. **Review the screenshot** - Approve or retake the captured image
5. **AI analysis** - Claude 3 Sonnet analyzes your screen with progress updates
6. **View results** - See AI suggestions with a thumbnail preview of the analyzed screenshot
7. **Full-size viewing** - Click the thumbnail to view the full screenshot

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Authentication

#### Option A: Standard AWS Credentials
```bash
# Using AWS CLI
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-east-1"
```

#### Option B: Bearer Token Authentication
```bash
export AWS_BEARER_TOKEN_BEDROCK="your-bedrock-token"
export AWS_REGION="us-east-1"
```

#### Option C: GUI Setup
- Launch the app and use the built-in credentials dialog
- Go to Settings → AWS Credentials to configure

### 3. Enable Bedrock Access
- Ensure you have access to Claude 3 Sonnet in Amazon Bedrock
- Model ID: `anthropic.claude-3-sonnet-20240229-v1:0`

### 4. Platform-Specific Setup

#### macOS
- Grant screen recording permissions when prompted
- Or run the permission helper: `python fix_permissions.py`

#### Windows/Linux
- No additional setup required (uses MSS library)

## Usage

### Basic Usage
```bash
# Normal mode (requires AWS credentials)
python main.py

# Mock mode (no AWS credentials needed)
python main.py --mock
```

### Testing & Development
```bash
# Test screen capture functionality
python test_screenshot.py

# Test thumbnail generation
python test_thumbnail.py

# Fix macOS permissions (macOS only)
python fix_permissions.py
```

### Environment Variables
```bash
# AWS Authentication
AWS_ACCESS_KEY_ID="your-access-key"
AWS_SECRET_ACCESS_KEY="your-secret-key"
AWS_REGION="us-east-1"

# Bearer Token Authentication
AWS_BEARER_TOKEN_BEDROCK="your-token"
```

## Requirements

### System Requirements
- **Python 3.8+**
- **Operating System**: macOS, Windows, or Linux
- **Screen capture permissions** (macOS will prompt automatically)

### AWS Requirements
- AWS account with Amazon Bedrock access
- Claude 3 Sonnet model enabled in your region
- Valid AWS credentials or Bedrock API token

### Dependencies
```
pillow>=10.0.0          # Image processing
boto3>=1.34.0           # AWS SDK
plyer>=2.1.0            # Cross-platform notifications
requests>=2.31.0        # HTTP client for token auth
pngquant-cli>=0.1.0     # PNG optimization
mss>=9.0.1              # Cross-platform screen capture
```

## Architecture

### Core Components
- **`main.py`** - Main application with GUI and core logic
- **`region_selector.py`** - Platform-specific screen capture utilities
- **`token_auth.py`** - Bearer token authentication client
- **`fix_permissions.py`** - macOS permission helper

### Key Classes
- **`ScreenAssistantApp`** - Main GUI application controller
- **`CredentialsDialog`** - AWS credentials setup dialog
- **`RegionSelector`** - Static methods for screen capture
- **`BedrockTokenClient`** - Token-based authentication client

## Troubleshooting

### macOS Screen Recording Permissions
If screen capture fails on macOS:
1. Run `python fix_permissions.py`
2. Follow the guided setup process
3. Grant permissions in System Preferences → Privacy & Security → Screen Recording

### AWS Authentication Issues
- Verify your credentials with `aws sts get-caller-identity`
- Check that Bedrock is available in your region
- Ensure Claude 3 Sonnet model is enabled
- Try mock mode to test the interface: `python main.py --mock`

### Cross-Platform Issues
- Windows/Linux users: MSS library handles screen capture automatically
- If capture fails, check for conflicting screen capture software
- Ensure Python has necessary permissions to access the display

## Contributing

The application uses a modular architecture with clear separation of concerns:
- GUI logic in `main.py`
- Platform-specific code in `region_selector.py`
- Authentication handling in `token_auth.py`
- Testing utilities in `test_*.py` files

## License

This project is provided as-is for educational and development purposes.