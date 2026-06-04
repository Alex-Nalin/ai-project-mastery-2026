import requests
import json
from pathlib import Path
from typing import List, Dict
import markdown

class AvatarExplainerPipeline:
    """
    Create interactive avatar explainer videos from markdown scripts.
    
    Workflow:
    1. Parse markdown script into segments
    2. Generate interactive branches
    3. Create Synthesia 3 avatar video
    4. Deploy with interactive agent
    """
    
    def __init__(
        self,
        synthesia_api_key: str,
        avatar_id: str = "anna-2d-standard",
        background_id: str = "office-1"
    ):
        self.synthesia = SynthesiaClient(synthesia_api_key)
        self.avatar_id = avatar_id
        self.background_id = background_id
    
    def from_markdown(
        self,
        markdown_path: str,
        title: str = "AI Explainer Video",
        interactive: bool = True
    ) -> str:
        """
        Create avatar video from markdown file.
        
        Args:
            markdown_path: Path to markdown script
            title: Video title
            interactive: Enable agent interactivity
        
        Returns:
            Video ID for status tracking
        """
        # Parse markdown into segments
        segments = self._parse_markdown(markdown_path)
        
        # Add interactive branches
        if interactive:
            segments = self._add_interactive_branches(segments)
        
        # Create Synthesia video
        video_id = self.synthesia.create_avatar_video(
            script_segments=segments,
            avatar_id=self.avatar_id,
            background_id=self.background_id,
            interactive=interactive
        )
        
        return video_id
    
    def _parse_markdown(self, markdown_path: str) -> List[Dict]:
        """Parse markdown into script segments."""
        with open(markdown_path, "r") as f:
            content = f.read()
        
        # Convert markdown to structured segments
        segments = []
        current_segment = {"text": "", "actions": []}
        
        for line in content.split("\n"):
            if line.startswith("## "):
                # New section - save current and start new
                if current_segment["text"].strip():
                    segments.append(current_segment)
                current_segment = {
                    "text": "",
                    "actions": [],
                    "section": line[3:].strip()
                }
            elif line.startswith("!action "):
                action = line[8:].strip()
                current_segment["actions"].append(action)
            elif line.startswith("!branch "):
                branch_data = json.loads(line[8:])
                current_segment.setdefault("branches", []).append(branch_data)
            else:
                current_segment["text"] += line + " "
        
        # Add final segment
        if current_segment["text"].strip():
            segments.append(current_segment)
        
        return segments
    
    def _add_interactive_branches(self, segments: List[Dict]) -> List[Dict]:
        """Add interactive branching to segments."""
        for i, segment in enumerate(segments):
            # Add continue option
            if i < len(segments) - 1:
                segment.setdefault("branches", [])
                segment["branches"].append({
                    "condition": "user_says_continue",
                    "target_segment": i + 1,
                    "label": "Continue"
                })
            
            # Add rewind option
            if i > 0:
                segment["branches"].append({
                    "condition": "user_says_rewind",
                    "target_segment": i - 1,
                    "label": "Go back"
                })
            
            # Add question handler
            segment["branches"].append({
                "condition": "user_asks_question",
                "target_segment": "ai_response",
                "label": "Ask a question"
            })
        
        return segments
    
    def check_progress(self, video_id: str) -> Dict:
        """Check video generation progress."""
        return self.synthesia.check_status(video_id)

# Example markdown script
example_script = """
## Introduction
Welcome to our AI platform tutorial. I'm going to show you how to automate your workflow in minutes.
!action wave_hand

## Getting Started
First, create an account and connect your data sources.
!action point_to_screen
!branch {"condition": "user_asks_question", "target_segment": 2, "label": "What data sources?"}

## Features Overview
Our platform supports over 200 integrations. Here are the most popular ones.
!action show_list

## Advanced Features
For power users, we offer custom API access and webhook support.
!action emphasize

## Conclusion
Ready to get started? Click the button below to begin your free trial.
!action open_palms
!branch {"condition": "user_says_yes", "target_segment": "redirect_signup", "label": "Start free trial"}
"""

# Usage
pipeline = AvatarExplainerPipeline(
    synthesia_api_key="syn-...",
    avatar_id="sophia-2d-professional"
)

# Create video from markdown
with open("tutorial_script.md", "w") as f:
    f.write(example_script)

video_id = pipeline.from_markdown(
    markdown_path="tutorial_script.md",
    title="AI Platform Tutorial - Getting Started"
)

# Monitor progress
import time
while True:
    status = pipeline.check_progress(video_id)
    print(f"Status: {status['status']}")
    if status['status'] == 'completed':
        print(f"Video URL: {status['url']}")
        break
    time.sleep(30)
