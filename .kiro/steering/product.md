# AI Screen Assistant

A desktop GUI application that captures the user's screen and uses Amazon Bedrock's Claude 3 Sonnet to analyze what they're working on and provide helpful suggestions.

## Core Features
- One-button screen capture interface
- AI-powered screen analysis using Claude 3 Sonnet via Amazon Bedrock
- Cross-platform screen capture (macOS screencapture, MSS fallback)
- Screenshot approval workflow before AI analysis
- Mock mode for testing without AWS credentials
- AWS credentials management with GUI setup dialog

## Target Use Cases
- Code review and debugging assistance
- Document and UI analysis
- Error message interpretation
- General productivity suggestions based on current screen content

## Authentication
- Supports standard AWS credentials (access key/secret)
- Bearer token authentication for Bedrock API
- Graceful fallback to mock mode when credentials unavailable