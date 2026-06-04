import requests

class HiggsfieldClient:
    """Client for Higgsfield AI character-consistent video."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.higgsfield.ai/v1"
    
    def create_character(
        self,
        reference_images: list,
        character_name: str
    ) -> str:
        """
        Create a consistent character model.
        
        Args:
            reference_images: List of image URLs or file paths
            character_name: Identifier for this character
        
        Returns:
            Character ID for use in video generation
        """
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        files = []
        for i, img in enumerate(reference_images):
            files.append(("images", (f"ref_{i}.jpg", open(img, "rb"), "image/jpeg")))
        
        response = requests.post(
            f"{self.base_url}/characters",
            headers=headers,
            files=files,
            data={"name": character_name}
        )
        response.raise_for_status()
        return response.json()["character_id"]
    
    def generate_video(
        self,
        character_id: str,
        prompt: str,
        duration: int = 10
    ) -> str:
        """
        Generate a video with consistent character.
        
        Args:
            character_id: From create_character()
            prompt: Scene description
            duration: Clip length in seconds
        
        Returns:
            Video URL
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "character_id": character_id,
            "prompt": prompt,
            "duration": duration,
            "resolution": "1080p"
        }
        
        response = requests.post(
            f"{self.base_url}/videos",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()["video_url"]

# Usage
client = HiggsfieldClient(api_key="hg-...")

# Create character from 3 reference photos
char_id = client.create_character(
    reference_images=["face_front.jpg", "face_side.jpg", "face_smile.jpg"],
    character_name="Brand Ambassador"
)

# Generate multiple scenes with same character
scenes = [
    "Professional woman in business attire walking through modern office lobby",
    "Same woman presenting to a boardroom, confident posture, gesturing to screen",
    "Close-up shot of woman smiling, professional headshot style"
]

for scene in scenes:
    video = client.generate_video(char_id, scene)
    print(f"Generated: {video}")
