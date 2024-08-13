from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import crud, schemas
from database import SessionLocal
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/user_metrics/", response_model=schemas.UserMetricResponse)
def create_user_metric(user_metric: schemas.UserMetricCreate, db: Session = Depends(get_db)):
    try:
        user_metric_id = crud.insert_user_metric(db, user_metric)
        if user_metric_id is None:
            raise HTTPException(status_code=500, detail="Failed to insert user metric.")
        return schemas.UserMetricResponse(id=user_metric_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/talked_time/", response_model=schemas.TalkedTimeResponse)
def create_talked_time(talked_time: schemas.TalkedTimeCreate, db: Session = Depends(get_db)):
    try:
        talked_time_id = crud.insert_talked_time(db, talked_time)
        if talked_time_id is None:
            raise HTTPException(status_code=500, detail="Failed to insert talked time.")
        return schemas.TalkedTimeResponse(id=talked_time_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/microphone_used/", response_model=schemas.MicrophoneUsedResponse)
def create_microphone_used(microphone_used: schemas.MicrophoneUsedCreate, db: Session = Depends(get_db)):
    try:
        microphone_used_id = crud.insert_microphone_used(db, microphone_used)
        if microphone_used_id is None:
            raise HTTPException(status_code=500, detail="Failed to insert microphone used record.")
        return schemas.MicrophoneUsedResponse(id=microphone_used_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/speaker_used/", response_model=schemas.SpeakerUsedResponse)
def create_speaker_used(speaker_used: schemas.SpeakerUsedCreate, db: Session = Depends(get_db)):
    try:
        speaker_used_id = crud.insert_speaker_used(db, speaker_used)
        if speaker_used_id is None:
            raise HTTPException(status_code=500, detail="Failed to insert speaker used record.")
        return schemas.SpeakerUsedResponse(id=speaker_used_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/voice_sentiment/", response_model=schemas.VoiceSentimentResponse)
def create_voice_sentiment(voice_sentiment: schemas.VoiceSentimentCreate, db: Session = Depends(get_db)):
    try:
        voice_sentiment_id = crud.insert_voice_sentiment(db, voice_sentiment)
        if voice_sentiment_id is None:
            raise HTTPException(status_code=500, detail="Failed to insert voice sentiment record.")
        return schemas.VoiceSentimentResponse(id=voice_sentiment_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/total_talked_time/")
def read_total_talked_time(user_id: int, session_id: int, db: Session = Depends(get_db)):
    try:
        total_duration = crud.get_total_talked_time(db, user_id, session_id)
        return {"total_duration": str(total_duration)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/voice_sentiment_summary/")
def read_voice_sentiment_summary(session_id: int, db: Session = Depends(get_db)):
    try:
        result = crud.calculate_voice_sentiment_summary(db, session_id)
        if result is None:
            raise HTTPException(status_code=404, detail="No sentiment data found for the session.")
        return {
            "avg_sentiment_score": result[0],
            "avg_confidence_level": result[1]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/user_activity_report/")
def read_user_activity_report(session_id: int, db: Session = Depends(get_db)):
    try:
        report = crud.generate_user_activity_report(db, session_id)
        if not report:
            raise HTTPException(status_code=404, detail="No activity report found for the session.")
        return report
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/talked_time/update")
def update_talked_time_record(request: schemas.UpdateTalkedTimeRequest, db: Session = Depends(get_db)):
    try:
        crud.update_talked_time_record(db, request.record_id, request.new_duration)
        return {"status": "success", "message": "Record updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/microphone_used/update")
def update_microphone_used_record(request: schemas.UpdateMicrophoneUsedRequest, db: Session = Depends(get_db)):
    try:
        crud.update_microphone_used_record(db, request.record_id, request.new_status, request.new_volume_level)
        return {"status": "success", "message": "Record updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint to update a speaker used record
@app.put("/speaker_used/update")
def update_speaker_used_record(request: schemas.UpdateSpeakerUsedRequest, db: Session = Depends(get_db)):
    try:
        crud.update_speaker_used_record(db, request.record_id, request.new_status, request.new_volume_level)
        return {"status": "success", "message": "Record updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint to update a voice sentiment record
@app.put("/voice_sentiment/update")
def update_voice_sentiment_record(request: schemas.UpdateVoiceSentimentRequest, db: Session = Depends(get_db)):
    try:
        crud.update_voice_sentiment_record(db, request.record_id, request.new_sentiment_score, request.new_confidence_level)
        return {"status": "success", "message": "Record updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@app.get("/microphone_usage_summary", response_model=schemas.MicrophoneUsageSummaryResponse)
def read_microphone_usage_summary(session_id: int, db: Session = Depends(get_db)):
    try:
        summary = crud.get_microphone_usage_summary(db, session_id)
        if summary is None:
            raise HTTPException(status_code=404, detail="Summary not found")
        return {"total_records": summary.total_records, "used_count": summary.used_count, "usage_percentage": summary.usage_percentage}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/speaker_usage_summary", response_model=schemas.SpeakerUsageSummaryResponse)
def read_speaker_usage_summary(session_id: int, db: Session = Depends(get_db)):
    try:
        summary = crud.get_speaker_usage_summary(db, session_id)
        if summary is None:
            raise HTTPException(status_code=404, detail="Summary not found")
        return {"total_records": summary.total_records, "used_count": summary.used_count, "usage_percentage": summary.usage_percentage}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/talked_time/")
def read_talked_time(db: Session = Depends(get_db)):
    return crud.get_talked_time(db)

@app.get('/microphone_used')
def get_microphone_used(db: Session = Depends(get_db)):
    return crud.get_microhone_used(db)

@app.get('/speaker_used')
def speaker_used(db: Session = Depends(get_db)):
    return crud.speaker_used(db)

@app.get('/voice_sentiment')
def voice_sentiment(db: Session = Depends(get_db)):
    return crud.voice_sentiment(db)