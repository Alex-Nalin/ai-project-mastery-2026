import requests
import time

class RunwayGen3Client:
    """Client for Runway Gen-3 Alpha video processing."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.runwayml.com/v1"
    
    def video_to_video(
        self,
        input_video: str,
        prompt: str,
        style: str = "cinematic",
        strength: float = 0.7
    ) -> str:
        """
        Apply style transfer to an existing video.
        
        Args:
            input_video: URL or file path of input video
            prompt: Description of desired style
            style: 'cinematic', 'anime', 'oil-painting', 'sketch'
            strength: How strongly to apply the style (0.0-1.0)
        
        Returns:
            URL to processed video
        """
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        # Upload video if local file
        if not input_video.startswith("http"):
            with open(input_video, "rb") as f:
                upload = requests.post(
                    f"{self.base_url}/upload",
                    headers=headers,
                    files={"file": f}
                )
                input_video = upload.json()["url"]
        
        payload = {
            "model": "gen-3-alpha",
            "mode": "video-to-video",
            "input": {"video": input_video},
            "prompt": prompt,
            "style": style,
            "strength": strength
        }
        
        response = requests.post(
            f"{self.base_url}/tasks",
            headers=headers,
            json=payload
        )
        task_id = response.json()["id"]
        
        # Poll for completion
        while True:
            status = requests.get(
                f"{self.base_url}/tasks/{task_id}",
                headers=headers
            ).json()
            
            if status["status"] == "succeeded":
                return status["output"]["video"]
            elif status["status"] == "failed":
                raise Exception(f"Processing failed: {status['error']}")
            
            time.sleep(10)

# Example: Transform a product demo into cinematic commercial
client = RunwayGen3Client(api_key="rw-...")
result = client.video_to_video(
    input_video="product_demo.mp4",
    prompt="Convert to high-end commercial quality, "
           "golden hour lighting, smooth slow motion, "
           "professional color grading, warm tones",
    strength=0.8
)
