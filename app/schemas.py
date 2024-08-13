from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from datetime import timedelta

class UserMetricBase(BaseModel):
    timestamp: datetime
    user_id: int
    session_id: int
    metric_type: str

class UserMetricCreate(UserMetricBase):
    pass

class UserMetricResponse(BaseModel):
    id: int

    class Config:
        orm_mode = True

class TalkedTimeBase(BaseModel):
    user_metric_id: int
    duration: timedelta

class TalkedTimeCreate(TalkedTimeBase):
    pass

class TalkedTimeResponse(BaseModel):
    id: int

    class Config:
        orm_mode = True

class MicrophoneUsedBase(BaseModel):
    user_metric_id: int
    status: bool
    volume_level: Optional[int]

class MicrophoneUsedCreate(MicrophoneUsedBase):
    pass

class MicrophoneUsedResponse(BaseModel):
    id: int

    class Config:
        orm_mode = True

class SpeakerUsedBase(BaseModel):
    user_metric_id: int
    status: bool
    volume_level: Optional[int]

class SpeakerUsedCreate(SpeakerUsedBase):
    pass

class SpeakerUsedResponse(BaseModel):
    id: int

    class Config:
        orm_mode = True

class VoiceSentimentBase(BaseModel):
    user_metric_id: int
    sentiment_score: float
    confidence_level: Optional[float]

class VoiceSentimentCreate(VoiceSentimentBase):
    pass

class VoiceSentimentResponse(BaseModel):
    id: int

    class Config:
        orm_mode = True

class UpdateTalkedTimeRequest(BaseModel):
    record_id: int
    new_duration: timedelta

class UpdateMicrophoneUsedRequest(BaseModel):
    record_id: int
    new_status: bool
    new_volume_level: int

class UpdateSpeakerUsedRequest(BaseModel):
    record_id: int
    new_status: bool
    new_volume_level: int

class UpdateVoiceSentimentRequest(BaseModel):
    record_id: int
    new_sentiment_score: float
    new_confidence_level: float

class MicrophoneUsageSummaryResponse(BaseModel):
    total_records: int
    used_count: int
    usage_percentage: float

class SpeakerUsageSummaryResponse(BaseModel):
    total_records: int
    used_count: int
    usage_percentage: float