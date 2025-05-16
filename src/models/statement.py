from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field

VALID_VERBS = {
    'initialized', 'launched', 'terminated', 'completed', 'passed',
    'failed', 'satisfied', 'waived', 'abandoned', 'progressed',
    'voided', 'attempted', 'interacted', 'experienced', 'answered',
    'hintrequested'
}


class Statement(BaseModel):

    platform_id: str = Field(..., description="Unique identifier for the platform", examples=["LMS"])
    activity_id: str = Field(..., description="Unique identifier for the activity", examples=["12"])
    activity_type: str = Field(..., description="Activity: lesson, theory, video", examples=["theory"])
    verb_id: str = Field(..., description="Unique identifier for the verb", examples=["completed"])
    actor_id: str = Field(..., description="Unique identifier for the actor , email or user id", examples=["1027"])
    context: dict[str, Any] = Field(default_factory=dict, examples=[{"ai": "activated"}])
    # timestamp: datetime = Field(default_factory=datetime.now)
