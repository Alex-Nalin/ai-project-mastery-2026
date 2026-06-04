import requests
import json
from typing import List, Dict

class SynthesiaClient:
    """Client for Synthesia 3 interactive avatar videos."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.synthesia.io/v3"
    
    def create_avatar_video(
        self,
        script_segments: List[Dict],
        avatar_id: str = "anna-2d-standard",
        background_id: str = "office-1",
        interactive: bool = True
    ) -> str:
        """
        Create an interactive avatar video from script segments.
        
        Args:
            script_segments: List of script segments with text and actions
            avatar_id: Synthesia avatar identifier
            background_id: Background scene identifier
            interactive: Enable agent-based interactivity
        
        Returns:
            Video ID for status tracking
        """
        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Build the interactive script
        script = {
            "type": "interactive" if interactive else "linear",
            "avatar": avatar_id,
            "background": background_id,
            "segments": []
        }
        
        for segment in script_segments:
            script["segments"].append({
                "speaker": segment.get("speaker", "avatar"),
                "text": segment["text"],
                "actions": segment.get("actions", []),
                "branches": segment.get("branches", [])
            })
        
        payload = {
            "title": "AI Explainer Video",
            "script": script,
            "quality": "1080p",
            "format": "mp4"
        }
        
        response = requests.post(
            f"{self.base_url}/videos",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()["id"]
    
    def check_status(self, video_id: str) -> Dict:
        """Check video generation status."""
        headers = {"Authorization": self.api_key}
        response = requests.get(
            f"{self.base_url}/videos/{video_id}",
            headers=headers
        )
        return response.json()

# Example: Interactive product tutorial
script = [
    {
        "text": "Welcome to your interactive product tutorial. "
                "I'll guide you through the key features of our platform.",
        "actions": ["wave_hand"],
        "branches": [
            {
                "condition": "user_says_yes",
                "target_segment": 1,
                "label": "Yes, show me everything"
            },
            {
                "condition": "user_says_no",
                "target_segment": 3,
                "label": "Just the basics, please"
            }
        ]
    },
    {
        "text": "Excellent! Let's start with the dashboard overview. "
                "Here you can see all your active projects...",
        "actions": ["point_to_screen"]
    },
    {
        "text": "And that's the full tour. Any questions?",
        "actions": ["open_palms"],
        "branches": [
            {
                "condition": "user_asks_question",
                "target_segment": 1,
                "label": "Yes, go back to..."
            }
        ]
    }
]

client = SynthesiaClient(api_key="syn-...")
video_id = client.create_avatar_video(script)
