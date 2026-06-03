"""
Human review interface for content quality control
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class ReviewStatus(BaseModel):
    """Tracks the review process"""
    content_id: str
    status: str  # pending_review, in_review, approved, needs_revision, published
    reviewer: Optional[str] = None
    feedback: Optional[str] = None
    quality_score: Optional[int] = None  # 1-10
    reviewed_at: Optional[datetime] = None

class ContentReviewer:
    """Manages the human review workflow"""
    
    def __init__(self, notion

```python
    def __init__(self, notion_api_key: str, database_id: str):
        self.notion_api_key = notion_api_key
        self.database_id = database_id
        self.review_queue: list[ReviewStatus] = []
    
    def add_to_queue(self, content_id: str) -> ReviewStatus:
        """Add generated content to review queue"""
        status = ReviewStatus(
            content_id=content_id,
            status="pending_review"
        )
        self.review_queue.append(status)
        return status
    
    def assign_reviewer(self, content_id: str, reviewer: str) -> Optional[ReviewStatus]:
        """Assign a human reviewer to content"""
        for status in self.review_queue:
            if status.content_id == content_id and status.status == "pending_review":
                status.status = "in_review"
                status.reviewer = reviewer
                return status
        return None
    
    def submit_review(self, content_id: str, feedback: str, quality_score: int, approved: bool) -> Optional[ReviewStatus]:
        """Submit review results"""
        for status in self.review_queue:
            if status.content_id == content_id and status.status == "in_review":
                status.feedback = feedback
                status.quality_score = quality_score
                status.reviewed_at = datetime.now()
                status.status = "approved" if approved else "needs_revision"
                return status
        return None
