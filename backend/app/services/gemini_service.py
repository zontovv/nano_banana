"""
Service for interacting with Gemini API through OpenRouter.
"""

import httpx
import json
import base64
import time
from typing import Optional, Dict, Any
from ..config import get_settings
from ..prompts.doodle_prompt import create_doodle_prompt


class GeminiService:
    """
    Service class for Gemini API interactions.
    """
    
    def __init__(self):
        """
        Initialize the Gemini service with configuration.
        """
        self.settings = get_settings()
        self.client = httpx.AsyncClient(
            timeout=self.settings.image_generation_timeout
        )
        
    async def __aenter__(self):
        """
        Async context manager entry.
        """
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Async context manager exit - close the HTTP client.
        """
        await self.client.aclose()
    
    async def generate_doodle(
        self, 
        occasion: str, 
        style_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a doodle using Gemini API.
        
        Args:
            occasion: The event or occasion for the doodle
            style_hint: Optional style guidance
            
        Returns:
            dict: Response containing image data or error
        """
        
        start_time = time.time()
        
        try:
            # Gemini понимает русский и украинский напрямую - перевод не нужен
            prompt = create_doodle_prompt(occasion, style_hint)
            
            headers = {
                "Authorization": f"Bearer {self.settings.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/gowombat/doodle-generator",
                "X-Title": "GoWombat Doodle Generator"
            }
            
            payload = {
                "model": self.settings.gemini_model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "modalities": ["image", "text"],
                "temperature": 0.8,
                "max_tokens": 1000
            }
            
            response = await self.client.post(
                f"{self.settings.openrouter_base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            
            generation_time = time.time() - start_time
            
            if response.status_code != 200:
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_detail = error_json.get('error', {}).get('message', error_detail)
                except:
                    pass
                    
                return {
                    "success": False,
                    "error": f"API Error ({response.status_code}): {error_detail}",
                    "generation_time": generation_time
                }
            
            result = response.json()
            
            # Handle Gemini Image Preview response format
            if "choices" in result and len(result["choices"]) > 0:
                choice = result["choices"][0]
                message = choice.get("message", {})
                
                # Check if there are images in the message
                if "images" in message and len(message["images"]) > 0:
                    image_obj = message["images"][0]
                    
                    # Handle dict format with image_url field
                    if isinstance(image_obj, dict) and "image_url" in image_obj:
                        image_url_obj = image_obj["image_url"]
                        
                        # Handle nested dict with url field
                        if isinstance(image_url_obj, dict) and "url" in image_url_obj:
                            image_url = image_url_obj["url"]
                        elif isinstance(image_url_obj, str):
                            image_url = image_url_obj
                        else:
                            image_url = None
                        
                        if isinstance(image_url, str):
                            if image_url.startswith("data:image"):
                                base64_data = image_url.split(",")[1] if "," in image_url else image_url
                                return {
                                    "success": True,
                                    "image_base64": base64_data,
                                    "generation_time": generation_time
                                }
                            elif image_url.startswith("http"):
                                return {
                                    "success": True,
                                    "image_url": image_url,
                                    "generation_time": generation_time
                                }
                    
                    # Handle direct string format
                    elif isinstance(image_obj, str):
                        if image_obj.startswith("data:image"):
                            base64_data = image_obj.split(",")[1] if "," in image_obj else image_obj
                            return {
                                "success": True,
                                "image_base64": base64_data,
                                "generation_time": generation_time
                            }
                        else:
                            # Try as direct base64
                            try:
                                base64.b64decode(image_obj[:100])
                                return {
                                    "success": True,
                                    "image_base64": image_obj,
                                    "generation_time": generation_time
                                }
                            except:
                                pass
                
                # Fallback: check content for image data
                content = message.get("content")
                if isinstance(content, str):
                    if content.startswith("data:image"):
                        base64_data = content.split(",")[1] if "," in content else content
                        return {
                            "success": True,
                            "image_base64": base64_data,
                            "generation_time": generation_time
                        }
                    elif content.startswith("http"):
                        return {
                            "success": True,
                            "image_url": content,
                            "generation_time": generation_time
                        }
                
                # Handle list format in content
                elif isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict):
                            if item.get("type") == "image" or "image" in str(item):
                                if "data" in item:
                                    return {
                                        "success": True,
                                        "image_base64": item["data"],
                                        "generation_time": generation_time
                                    }
                                elif "url" in item:
                                    return {
                                        "success": True,
                                        "image_url": item["url"],
                                        "generation_time": generation_time
                                    }
                    
            return {
                "success": False,
                "error": "No image found in response",
                "generation_time": generation_time
            }
            
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Request timeout - generation took too long",
                "generation_time": time.time() - start_time
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "generation_time": time.time() - start_time
            }
    
    async def close(self):
        """
        Close the HTTP client.
        """
        await self.client.aclose()