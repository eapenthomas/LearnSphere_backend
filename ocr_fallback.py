"""
OCR Fallback Service for Teacher Verification
Provides alternative OCR solutions when Tesseract is not available
"""

import os
import requests
import base64
from typing import Optional, Dict, Any
from PIL import Image
import io

class OCRFallbackService:
    """Fallback OCR service using cloud APIs when Tesseract is not available"""
    
    def __init__(self):
        self.google_vision_api_key = os.getenv('GOOGLE_VISION_API_KEY')
        self.azure_vision_endpoint = os.getenv('AZURE_VISION_ENDPOINT')
        self.azure_vision_key = os.getenv('AZURE_VISION_KEY')
    
    def extract_text_with_google_vision(self, image_bytes: bytes) -> Optional[str]:
        """Extract text using Google Cloud Vision API"""
        if not self.google_vision_api_key:
            return None
            
        try:
            # Encode image to base64
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Prepare request
            url = f"https://vision.googleapis.com/v1/images:annotate?key={self.google_vision_api_key}"
            payload = {
                "requests": [{
                    "image": {"content": image_b64},
                    "features": [{"type": "TEXT_DETECTION", "maxResults": 1}]
                }]
            }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if 'responses' in result and result['responses']:
                text_annotations = result['responses'][0].get('textAnnotations', [])
                if text_annotations:
                    return text_annotations[0].get('description', '').strip()
            
            return None
            
        except Exception as e:
            print(f"Google Vision API error: {e}")
            return None
    
    def extract_text_with_azure_vision(self, image_bytes: bytes) -> Optional[str]:
        """Extract text using Azure Computer Vision API"""
        if not self.azure_vision_endpoint or not self.azure_vision_key:
            return None
            
        try:
            # Prepare request
            url = f"{self.azure_vision_endpoint}/vision/v3.2/read/analyze"
            headers = {
                'Ocp-Apim-Subscription-Key': self.azure_vision_key,
                'Content-Type': 'application/octet-stream'
            }
            
            # Send initial request
            response = requests.post(url, headers=headers, data=image_bytes, timeout=30)
            response.raise_for_status()
            
            # Get operation location
            operation_location = response.headers.get('Operation-Location')
            if not operation_location:
                return None
            
            # Poll for results
            import time
            for _ in range(30):  # Max 30 seconds
                result_response = requests.get(operation_location, headers=headers, timeout=10)
                result_response.raise_for_status()
                
                result = result_response.json()
                if result.get('status') == 'succeeded':
                    # Extract text from results
                    text_parts = []
                    for read_result in result.get('analyzeResult', {}).get('readResults', []):
                        for line in read_result.get('lines', []):
                            text_parts.append(line.get('text', ''))
                    return ' '.join(text_parts).strip()
                elif result.get('status') == 'failed':
                    break
                    
                time.sleep(1)
            
            return None
            
        except Exception as e:
            print(f"Azure Vision API error: {e}")
            return None
    
    def extract_text_with_ocr_space(self, image_bytes: bytes) -> Optional[str]:
        """Extract text using OCR.space API (free tier available)"""
        try:
            # OCR.space API endpoint
            url = "https://api.ocr.space/parse/image"
            
            # Prepare request
            files = {'file': ('image.png', image_bytes, 'image/png')}
            data = {
                'apikey': os.getenv('OCR_SPACE_API_KEY', 'helloworld'),  # Free API key
                'language': 'eng',
                'isOverlayRequired': False
            }
            
            response = requests.post(url, files=files, data=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if result.get('IsErroredOnProcessing'):
                return None
                
            parsed_results = result.get('ParsedResults', [])
            if parsed_results:
                return parsed_results[0].get('ParsedText', '').strip()
            
            return None
            
        except Exception as e:
            print(f"OCR.space API error: {e}")
            return None
    
    def extract_text_fallback(self, image_bytes: bytes) -> Optional[str]:
        """Try multiple OCR services in order of preference"""
        print("🔄 Trying fallback OCR services...")
        
        # Try Google Vision API first (most accurate)
        if self.google_vision_api_key:
            print("🔍 Trying Google Cloud Vision API...")
            text = self.extract_text_with_google_vision(image_bytes)
            if text and len(text.strip()) > 10:
                print("✅ Google Vision API succeeded")
                return text
        
        # Try Azure Computer Vision
        if self.azure_vision_endpoint and self.azure_vision_key:
            print("🔍 Trying Azure Computer Vision...")
            text = self.extract_text_with_azure_vision(image_bytes)
            if text and len(text.strip()) > 10:
                print("✅ Azure Vision API succeeded")
                return text
        
        # Try OCR.space as last resort
        print("🔍 Trying OCR.space API...")
        text = self.extract_text_with_ocr_space(image_bytes)
        if text and len(text.strip()) > 10:
            print("✅ OCR.space API succeeded")
            return text
        
        print("❌ All fallback OCR services failed")
        return None

# Global instance
ocr_fallback_service = OCRFallbackService()
