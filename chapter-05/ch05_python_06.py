import requests
import json
from pathlib import Path
import time

class GrokImagineClient:
    """Client for Grok Imagine 1.0 video generation."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.x.ai/v1/imagine"
    
    def generate_video(
        self,
        prompt: str,
        reference_image: str = None,
        duration: int = 10,
        style: str = "cinematic",
        negative_prompt: str = "blurry, low quality, jittery"
    ) -> str:
        """
        Generate a video clip using Grok Imagine 1.0.
        
        Args:
            prompt: Description of the video
            reference_image: Optional URL or base64 image for consistency
            duration: Clip length in seconds (max 10)
            style: 'cinematic', 'anime', 'realistic', '3d-render'
            negative_prompt: What to avoid
        
        Returns:
            URL to the generated video file
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "grok-imagine-1.0",
            "prompt": prompt,
            "duration": duration,
            "style": style,
            "negative_prompt": negative_prompt,
            "fps": 24
        }
        
        if reference_image:
            payload["reference_image"] = reference_image
        
        # Submit generation job
        response = requests.post(
            f"{self.base_url}/generations",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        job_id = response.json()["id"]
        
        # Poll for completion
        while True:
            status = requests.get(
                f"{self.base_url}/generations/{job_id}",
                headers=headers
            ).json()
            
            if status["status"] == "completed":
                return status["output"]["video_url"]
            elif status["status"] == "failed":
                raise Exception(f"Generation failed: {status['error']}")
            
            time.sleep(5)

# Usage
client = GrokImagineClient(api_key="xai-...")
video_url = client.generate_video(
    prompt="A sleek black sports car driving along a coastal highway "
           "at sunset, dramatic clouds, cinematic tracking shot, "
           "slow motion, professional automotive photography style",
    style="cinematic"
)
print(f"Video generated: {video_url}")
