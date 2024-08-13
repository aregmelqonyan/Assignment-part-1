from sqlalchemy import text
from sqlalchemy.orm import Session
import schemas
from typing import Optional, Tuple, List, Dict, Any
from datetime import timedelta

def insert_user_metric(db: Session, user_metric: schemas.UserMetricCreate) -> int:
    query = text("""
        SELECT insert_user_metric(
            :custom_timestamp,
            :custom_user_id,
            :custom_session_id,
            :custom_metric_type
        )
    """)
    result = db.execute(query, {
        "custom_timestamp": user_metric.timestamp,
        "custom_user_id": user_metric.user_id,
        "custom_session_id": user_metric.session_id,
        "custom_metric_type": user_metric.metric_type
    })
    db.commit()
    return result.scalar()

def insert_talked_time(db: Session, talked_time: schemas.TalkedTimeCreate) -> int:
    query = text("""
        SELECT insert_talked_time(
            :custom_user_metric_id,
            :custom_duration
        )
    """)
    result = db.execute(query, {
        "custom_user_metric_id": talked_time.user_metric_id,
        "custom_duration": talked_time.duration
    })
    return result.scalar()

def insert_microphone_used(db: Session, microphone_used: schemas.MicrophoneUsedCreate) -> int:
    query = text("""
        SELECT insert_microphone_used(
            :custom_user_metric_id,
            :custom_status,
            :custom_volume_level
        )
    """)
    result = db.execute(query, {
        "custom_user_metric_id": microphone_used.user_metric_id,
        "custom_status": microphone_used.status,
        "custom_volume_level": microphone_used.volume_level
    })
    return result.scalar()

def insert_speaker_used(db: Session, speaker_used: schemas.SpeakerUsedCreate) -> int:
    query = text("""
        SELECT insert_speaker_used(
            :custom_user_metric_id,
            :custom_status,
            :custom_volume_level
        )
    """)
    result = db.execute(query, {
        "custom_user_metric_id": speaker_used.user_metric_id,
        "custom_status": speaker_used.status,
        "custom_volume_level": speaker_used.volume_level
    })
    return result.scalar()

def insert_voice_sentiment(db: Session, voice_sentiment: schemas.VoiceSentimentCreate) -> int:
    query = text("""
        SELECT insert_voice_sentiment(
            :custom_user_metric_id,
            :custom_sentiment_score,
            :custom_confidence_level
        )
    """)
    result = db.execute(query, {
        "custom_user_metric_id": voice_sentiment.user_metric_id,
        "custom_sentiment_score": voice_sentiment.sentiment_score,
        "custom_confidence_level": voice_sentiment.confidence_level
    })
    return result.scalar()

def get_total_talked_time(db: Session, user_id: int, session_id: int) -> str:
    query = text("""
        SELECT total_talked_time(:custom_user_id, :custom_session_id)
    """)
    result = db.execute(query, {
        "custom_user_id": user_id,
        "custom_session_id": session_id
    })
    return result.scalar()

def calculate_voice_sentiment_summary(db: Session, session_id: int) -> Optional[Tuple[float, float]]:
    query = text("""
        SELECT avg_sentiment_score, avg_confidence_level
        FROM calculate_voice_sentiment_summary(:custom_session_id)
    """)
    result = db.execute(query, {"custom_session_id": session_id})
    row = result.fetchone()
    if row:
        # Access tuple elements by index
        avg_sentiment_score = row[0]
        avg_confidence_level = row[1]
        return (avg_sentiment_score, avg_confidence_level)
    return None

def generate_user_activity_report(db: Session, session_id: int) -> List[Dict[str, Any]]:
    query = text("""
        SELECT * FROM generate_user_activity_report(:custom_session_id)
    """)
    result = db.execute(query, {"custom_session_id": session_id}).mappings().all()
    return [dict(row) for row in result]

def update_talked_time_record(db: Session, record_id: int, new_duration: timedelta):
    sql_query = text("""
        SELECT update_talked_time_record(:record_id, :new_duration);
    """)
    db.execute(sql_query, {"record_id": record_id, "new_duration": new_duration})
    db.commit()

def update_microphone_used_record(db: Session, record_id: int, new_status: bool, new_volume_level: int):
    sql_query = text("""
        SELECT update_microphone_used_record(:record_id, :new_status, :new_volume_level);
    """)
    db.execute(sql_query, {"record_id": record_id, "new_status": new_status, "new_volume_level": new_volume_level})
    db.commit()

def update_speaker_used_record(db: Session, record_id: int, new_status: bool, new_volume_level: int):
    sql_query = text("""
        SELECT update_speaker_used_record(:record_id, :new_status, :new_volume_level);
    """)
    db.execute(sql_query, {"record_id": record_id, "new_status": new_status, "new_volume_level": new_volume_level})
    db.commit()

def update_voice_sentiment_record(db: Session, record_id: int, new_sentiment_score: float, new_confidence_level: float):
    sql_query = text("""
        SELECT update_voice_sentiment_record(:record_id, :new_sentiment_score, :new_confidence_level);
    """)
    db.execute(sql_query, {"record_id": record_id, "new_sentiment_score": new_sentiment_score, "new_confidence_level": new_confidence_level})
    db.commit()

def get_microphone_usage_summary(db: Session, session_id: int):
    sql_query = text("""
        SELECT * FROM microphone_usage_summary(:session_id);
    """)
    result = db.execute(sql_query, {"session_id": session_id}).fetchone()
    return result

def get_speaker_usage_summary(db: Session, session_id: int):
    sql_query = text("""
        SELECT * FROM speaker_usage_summary(:session_id);
    """)
    result = db.execute(sql_query, {"session_id": session_id}).fetchone()
    return result

def get_talked_time(db: Session):
    sql_query = text("""
        SELECT * FROM talked_time;
    """)
    result = db.execute(sql_query).fetchall()

    # Convert the result to a list of dictionaries
    talked_time_list = [
        dict(row._mapping)  # Use _mapping to get a dictionary-like object of row data
        for row in result
    ]
    
    return talked_time_list

def get_microhone_used(db: Session):
    sql_query = text("""
        SELECT * FROM microphone_used;
    """)
    result = db.execute(sql_query).fetchall()
    microphone_used_list = [
        dict(row._mapping)  # Use _mapping to get a dictionary-like object of row data
        for row in result
    ]
    
    return microphone_used_list

def speaker_used(db: Session):
    sql_query = text("""
        SELECT * FROM speaker_used;
    """)
    result = db.execute(sql_query).fetchall()
    speaker_used_list = [
        dict(row._mapping)  # Use _mapping to get a dictionary-like object of row data
        for row in result
    ]
    
    return speaker_used_list

def voice_sentiment(db: Session):
    sql_query = text("""
        SELECT * FROM voice_sentiment;
    """)
    result = db.execute(sql_query).fetchall()

    voice_sentiement_list = [
        dict(row._mapping)  # Use _mapping to get a dictionary-like object of row data
        for row in result
    ]
    
    return voice_sentiement_list
