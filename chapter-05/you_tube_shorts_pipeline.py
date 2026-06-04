import asyncio
from pathlib import Path
from typing import Optional
import json
import subprocess

class YouTubeShortsPipeline:
    """
    Automated YouTube Shorts creation pipeline.
    
    Workflow:
    1. Generate script from topic using GPT-5.5
    2. Create voiceover using ElevenLabs
    3. Generate video clips using Grok Imagine
    4. Combine audio and video with captions
    5. Upload to YouTube
    """
    
    def __init__(
        self,
        openai_api_key: str,
        elevenlabs_api_key: str,
        grok_api_key: str,
        youtube_api_key: str,
        output_dir: str = "./shorts_output"
    ):
        self.openai_api_key = openai_api_key
        self.elevenlabs = ElevenLabsVoiceCloner(elevenlabs_api_key)
        self.grok = GrokImagineClient(grok_api_key)
        self.youtube_api_key = youtube_api_key
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    async def create_short(
        self,
        topic: str,
        duration: int = 30,
        voice_id: str = "21m00Tcm4TlvDq8ikWAM",
        style: str = "educational"
    ) -> str:
        """
        Create a complete YouTube Short.
        
        Args:
            topic: Content topic
            duration: Target duration in seconds
            voice_id: ElevenLabs voice for narration
            style: 'educational', 'entertaining', 'motivational'
        
        Returns:
            URL of uploaded YouTube Short
        """
        print(f"Creating Short about: {topic}")
        
        # Step 1: Generate script
        print("  Step 1: Generating script...")
        script = await self._generate_script(topic, duration, style)
        
        # Step 2: Generate voiceover
        print("  Step 2: Creating voiceover...")
        audio_path = self.output_dir / "voiceover.mp3"
        self.elevenlabs.generate_speech(
            text=script["narration"],
            voice_id=voice_id,
            output_path=str(audio_path)
        )
        
        # Step 3: Generate video clips
        print("  Step 3: Generating video clips...")
        video_paths = []
        for i, scene in enumerate(script["scenes"]):
            clip_url = self.grok.generate_video(
                prompt=scene["visual"],
                duration=min(scene["duration"], 10)
            )
            clip_path = self.output_dir / f"clip_{i}.mp4"
            await self._download_video(clip_url, clip_path)
            video_paths.append(clip_path)
        
        # Step 4: Combine everything
        print("  Step 4: Assembling final video...")
        final_path = self.output_dir / "final_short.mp4"
        self._assemble_video(
            video_paths=video_paths,
            audio_path=audio_path,
            captions=script["captions"],
            output_path=final_path
        )
        
        # Step 5: Upload to YouTube
        print("  Step 5: Uploading to YouTube...")
        youtube_url = self._upload_to_youtube(
            video_path=final_path,
            title=script["title"],
            description=script["description"],
            tags=script["tags"]
        )
        
        print(f"  Done! Published at: {youtube_url}")
        return youtube_url
    
    async def _generate_script(self, topic: str, duration: int, style: str) -> dict:
        """Generate video script using GPT-5.5."""
        import openai
        
        client = openai.OpenAI(api_key=self.openai_api_key)
        
        prompt = f"""Create a YouTube Shorts script about '{topic}'.
        
Duration: {duration} seconds
Style: {style}

Requirements:
- Engaging hook in first 3 seconds
- Fast-paced, visual storytelling
- Natural narration that matches the visual flow
- Each scene 3–10 seconds with clear visual description
- Include exact caption text for each scene

Return as JSON with:
- title: Catchy title (max 60 chars)
- description: SEO-optimized description
- tags: List of 5–10 relevant tags
- narration: Full narration text
- scenes: List of scenes with 'visual' and 'duration' and 'caption'
- captions: List of caption texts with timestamps
"""
        
        response = client.chat.completions.create(
            model="gpt-5.5",
            messages=[
                {"role": "system", "content": "You are a viral content creator specializing in YouTube Shorts."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def _download_video(self, url: str, path: Path):
        """Download video from URL."""
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                with open(path, "wb") as f:
                    f.write(await response.read())
    
    def _assemble_video(
        self,
        video_paths: list,
        audio_path: str,
        captions: list,
        output_path: Path
    ):
        """Combine video clips, audio, and captions using FFmpeg."""
        # Create concat file for FFmpeg
        concat_file = self.output_dir / "concat.txt"
        with open(concat_file, "w") as f:
            for video_path in video_paths:
                f.write(f"file '{video_path}'\n")
        
        # First pass: concatenate videos
        temp_video = self.output_dir / "temp_concat.mp4"
        subprocess.run([
            "ffmpeg", "-f", "concat", "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            str(temp_video)
        ], check=True)
        
        # Second pass: add audio and captions
        # Create SRT subtitle file
        srt_path = self.output_dir / "captions.srt"
        with open(srt_path, "w") as f:
            for i, caption in enumerate(captions, 1):
                start = caption["start"]
                end = caption["end"]
                text = caption["text"]
                f.write(f"{i}\n")
                f.write(f"{self._format_time(start)} --> {self._format_time(end)}\n")
                f.write(f"{text}\n\n")
        
        # Final assembly
        subprocess.run([
            "ffmpeg",
            "-i", str(temp_video),
            "-i", audio_path,
            "-vf", f"subtitles={srt_path}:force_style='FontSize=24,FontName=Arial,PrimaryColour=&H00FFFFFF'",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-shortest",
            str(output_path)
        ], check=True)
        
        # Cleanup
        temp_video.unlink()
        concat_file.unlink()
        srt_path.unlink()
    
    def _format_time(self, seconds: float) -> str:
        """Convert seconds to SRT timestamp format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}".replace(".", ",")
    
    def _upload_to_youtube(
        self,
        video_path: Path,
        title: str,
        description: str,
        tags: list
    ) -> str:
        """Upload video to YouTube using API."""
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        
        # Authenticate (simplified - see Google API docs for full OAuth flow)
        credentials = Credentials(token=self.youtube_api_key)
        youtube = build("youtube", "v3", credentials=credentials)
        
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": "22"  # People & Blogs
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        }
        
        media = MediaFileUpload(
            str(video_path),
            chunksize=-1,
            resumable=True
        )
        
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )
        
        response = request.execute()
        return f"https://youtube.com/shorts/{response['id']}"

# Usage
pipeline = YouTubeShortsPipeline(
    openai_api_key="sk-...",
    elevenlabs_api_key="eleven-...",
    grok_api_key="xai-...",
    youtube_api_key="ya29..."
)

# Create a short
url = asyncio.run(pipeline.create_short(
    topic="How AI is transforming healthcare in 2026",
    duration=45,
    style="educational"
))
