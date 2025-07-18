#!/usr/bin/env python3
"""
Helper module for token-based authentication with Amazon Bedrock
"""

import os
import json
import requests
import base64
from urllib.parse import urlparse

class BedrockTokenClient:
    """Client for making API calls to Amazon Bedrock using a bearer token"""
    
    def __init__(self, token=None, region='us-east-1'):
        self.token = token or os.environ.get('AWS_BEARER_TOKEN_BEDROCK')
        if not self.token:
            raise ValueError("No Bedrock API token provided")
        
        self.region = region
        self.base_url = f"https://bedrock-runtime.{region}.amazonaws.com"
    
    def invoke_model(self, modelId, body):
        """Invoke a model using the token-based authentication"""
        url = f"{self.base_url}/model/{modelId}/invoke"
        
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, headers=headers, data=body)
        
        if response.status_code != 200:
            raise Exception(f"API call failed with status {response.status_code}: {response.text}")
        
        # Create a response object similar to boto3's response
        class ResponseBody:
            def read(self):
                return response.text
        
        class Response:
            def __init__(self, body, status_code):
                self.body = body
                self.status_code = status_code
        
        return Response(ResponseBody(), response.status_code)