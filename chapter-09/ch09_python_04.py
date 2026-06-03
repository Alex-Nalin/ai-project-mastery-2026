"""
Complete AI writing service pipeline orchestrator
"""

import json
from pathlib import Path
from datetime import datetime
from generator.content_generator import ContentGenerator, ContentBrief
from reviewer.review_dashboard import ContentReviewer
from delivery.delivery_manager import DeliveryManager

class WritingServicePipeline:
    """Orchestrates the entire content creation workflow"""
    
    def __init__(self, config_path: str = "config/pipeline_config.json"):
        with open(config_path) as f:
            self.config = json.load(f)
        
        self.generator = ContentGenerator()
        self.reviewer = ContentReviewer(
            notion_api_key=self.config['notion_api_key'],
            database_id=self.config['review_database_id']
        )
        self.delivery = DeliveryManager(
            smtp_config=self.config['smtp'],
            notion_token=self.config.get('notion_token')
        )
        
        # Track pipeline state
        self.pipeline_state = {}
    
    def process_brief(self, brief_data: dict) -> str:
        """Process a client brief through the entire pipeline"""
        
        # Generate unique content ID
        content_id = f"content_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Step 1: Validate and parse brief
        brief = ContentBrief(**brief_data)
        self.pipeline_state[content_id] = {"status": "brief_received", "brief": brief}
        
        # Step 2: Generate content
        print(f"[{content_id}] Generating content...")
        generated = self.generator.generate(brief)
        self.pipeline_state[content_id]["generated_content"] = generated
        self.pipeline_state[content_id]["status"] = "generated"
        
        # Step 3: Add to review queue
        print(f"[{content_id}] Adding to review queue...")
        self.reviewer.add_to_queue(content_id)
        self.pipeline_state[content_id]["status"] = "pending_review"
        
        # Step 4: Save for human review
        self._save_for_review(content_id, generated, brief)
        
        return content_id
    
    def handle_review_result(self, content_id: str, feedback: str, quality_score: int, approved: bool):
        """Handle the result of human review"""
        
        if not approved:
            # Revise based on feedback
            print(f"[{content_id}] Revising based on feedback...")
            original = self.pipeline_state[content_id]["generated_content"]
            revised = self.generator.revise(original, feedback)
            self.pipeline_state[content_id]["generated_content"] = revised
            self.pipeline_state[content_id]["status"] = "revised"
            
            # Re-add to review queue
            self.reviewer.add_to_queue(content_id)
            return
        
        # Content is approved - deliver
        self.pipeline_state[content_id]["status"] = "approved"
        
        brief = self.pipeline_state[content_id]["brief"]
        content = self.pipeline_state[content_id]["generated_content"]
        
        # Deliver via email
        print(f"[{content_id}] Delivering via email...")
        email_success = self.delivery.deliver_via_email(
            recipient=brief.client_name,
            subject=f"Your Content: {content.title}",
            content=content.body
        )
        
        # Deliver via Notion
        print(f"[{content_id}] Delivering to Notion...")
        notion_success = self.delivery.deliver_via_notion(
            database_id=self.config['delivery_database_id'],
            title=content.title,
            content=content.body,
            tags=[brief.content_type, brief.tone]
        )
        
        self.pipeline_state[content_id]["delivery_status"] = {
            "email": "delivered" if email_success else "failed",
            "notion": "delivered" if notion_success else "failed"
        }
        self.pipeline_state[content_id]["status"] = "completed"
    
    def _save_for_review(self, content_id: str, content, brief):
        """Save generated content for human review"""
        review_dir = Path("review_queue")
        review_dir.mkdir(exist_ok=True)
        
        review_file = review_dir / f"{content_id}.json"
        with open(review_file, 'w') as f:
            json.dump({
                "content_id": content_id,
                "brief": brief.dict(),
                "generated_content": content.dict(),
                "created_at": datetime.now().isoformat()
            }, f, indent=2)
    
    def get_pipeline_status(self, content_id: str) -> dict:
        """Get current status of a pipeline run"""
        return self.pipeline_state.get(content_id, {"status": "not_found"})

# Example usage
if __name__ == "__main__":
    pipeline = WritingServicePipeline()
    
    # Simulate client brief
    brief = {
        "client_name": "client@example.com",
        "project_title": "The Future of Edge AI in 2026",
        "content_type": "blog_post",
        "target_audience": "Technical decision-makers at mid-size companies",
        "tone": "professional",
        "word_count": 2000,
        "key_points": [
            "1-bit LLMs enabling on-device AI",
            "Edge deployment reducing cloud costs",
            "Privacy benefits of local processing",
            "Real-world case studies from manufacturing"
        ],
        "target_keywords": ["edge AI", "1-bit LLMs", "on-device inference", "private AI"],
        "brand_voice": "Forward-thinking but grounded in practical examples"
    }
    
    # Process through pipeline
    content_id = pipeline.process_brief(brief)
    print(f"Content generated: {content_id}")
    
    # Simulate human review
    pipeline.handle_review_result(
        content_id=content_id,
        feedback="Great first draft. Please add more specific metrics and a comparison table.",
        quality_score=8,
        approved=True
    )
    
    print(f"Final status: {pipeline.get_pipeline_status(content_id)}")
