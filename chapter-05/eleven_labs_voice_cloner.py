import requests
from pathlib import Path

class ElevenLabsVoiceCloner:
    """Clone a voice from audio samples."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
    
   

```python
        self.base_url = "https://api.elevenlabs.io/v1"
    
    def clone_voice(
        self,
        audio_files: list,
        voice_name: str,
        description: str = "",
        labels: dict = None
    ) -> str:
        """
        Clone a voice from audio samples.
        
        Args:
            audio_files: List of paths to audio files (30s–3min each)
            voice_name: Name for the cloned voice
            description: Optional description for voice discovery
            labels: Optional metadata labels
        
        Returns:
            Voice ID for use in TTS generation
        """
        headers = {"xi-api-key": self.api_key}
        
        files = []
        for i, audio_path in enumerate(audio_files):
            files.append(("files", (f"sample_{i}.mp3", open(audio_path, "rb"), "audio/mpeg")))
        
        data = {
            "name": voice_name,
            "description": description,
            "labels": labels or {}
        }
        
        response = requests.post(
            f"{self.base_url}/voices/add",
            headers=headers,
            files=files,
            data=data
        )
        response.raise_for_status()
        return response.json()["voice_id"]
    
    def generate_speech(
        self,
        text: str,
        voice_id: str,
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        output_path: str = "output.mp3"
    ):
        """
        Generate speech using a cloned voice.
        
        Args:
            text: Text to synthesize
            voice_id: From clone_voice() or pre-existing voice
            stability: 0.0 (expressive) to 1.0 (stable)
            similarity_boost: 0.0 to 1.0, how closely to match original
            style: 0.0 to 1.0, style exaggeration
            output_path: Where to save the audio file
        """
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v3",
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": style
            }
        }
        
        response = requests.post(
            f"{self.base_url}/text-to-speech/{voice_id}",
            headers=headers,
            json=payload,
            stream=True
        )
        response.raise_for_status()
        
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=4096):
                f.write(chunk)
        
        return output_path

# Usage
cloner = ElevenLabsVoiceCloner(api_key="eleven-...")

# Clone from 3 short audio samples
voice_id = cloner.clone_voice(
    audio_files=["intro.mp3", "explanation.mp3", "outro.mp3"],
    voice_name="Narrator Voice",
    description="Professional documentary narrator"
)

# Generate speech
cloner.generate_speech(
    text="Welcome to our AI-powered platform. "
         "In this tutorial, we'll explore the key features "
         "that make our solution unique.",
    voice_id=voice_id,
    stability=0.6,
    similarity_boost=0.8,
    output_path="tutorial_intro.mp3"
)
