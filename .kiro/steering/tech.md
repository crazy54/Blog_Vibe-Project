# Technology Stack

## Core Technologies
- **Python 3.8+** - Main programming language
- **Tkinter** - GUI framework (built into Python)
- **PIL/Pillow** - Image processing and manipulation
- **boto3** - AWS SDK for Bedrock integration
- **mss** - Cross-platform screen capture library
- **requests** - HTTP client for token-based authentication

## Key Dependencies
```
pillow>=10.0.0
boto3>=1.34.0
plyer>=2.1.0
requests>=2.31.0
pngquant-cli>=0.1.0
mss>=9.0.1
```

## Platform-Specific Features
- **macOS**: Uses `screencapture` command with permission handling
- **Cross-platform**: MSS library fallback for all platforms
- **Permission management**: Automated macOS screen recording permission setup

## AWS Integration
- **Amazon Bedrock**: Claude 3 Sonnet model (`anthropic.claude-3-sonnet-20240229-v1:0`)
- **Authentication methods**:
  - Standard AWS credentials (access key/secret)
  - Bearer token authentication via custom client
  - Environment variables support

## Common Commands

### Setup and Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Configure AWS credentials (if not using environment variables)
aws configure
```

### Running the Application
```bash
# Normal mode (requires AWS credentials)
python main.py

# Mock mode (no AWS credentials needed)
python main.py --mock
```

### Testing and Development
```bash
# Test screen capture capabilities
python test_screenshot.py

# Fix macOS permissions (macOS only)
python fix_permissions.py
```

### Environment Variables
```bash
# AWS credentials
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-east-1"

# Bearer token authentication
export AWS_BEARER_TOKEN_BEDROCK="your-token"
```