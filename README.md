# AI Screen Assistant

A simple GUI application that captures your screen and uses Amazon Bedrock's Claude 3 Sonnet to analyze what you're doing and offer helpful suggestions.

## Features
- Simple one-button interface
- On-demand screen capture
- AI vision analysis using Amazon Bedrock (Claude 3 Sonnet)
- Detailed AI suggestions in the app

## How It Works
1. Launch the application
2. Click the "Analyze Screen" button
3. The app will minimize briefly to capture your screen
4. Claude 3 Sonnet analyzes your screen and provides suggestions
5. Results appear in the app window

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Configure AWS credentials:
   - Using AWS CLI: `aws configure`
   - Or set environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
   - Optionally set region: `export AWS_REGION=us-east-1`
3. Ensure you have access to Claude 3 Sonnet in Amazon Bedrock
4. Run: `python main.py`

## Requirements
- Python 3.8+
- AWS account with Bedrock access
- Claude 3 Sonnet model enabled in Bedrock
- Screen capture permissions (macOS will prompt)