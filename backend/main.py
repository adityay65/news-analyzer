# main.py
from typing import List, Optional
import json
from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel
import spacy
from transformers import pipeline
from sqlalchemy import create_engine, Column, Integer, String, Float, ARRAY
from sqlalchemy.orm import sessionmaker, Session
import os
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, Field

# Initialize FastAPI with metadata
app = FastAPI(
    title="News Conspiracy Classifier",
    description="API for analyzing news headlines conspiracy potential",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None
)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost/newsdb")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database model
class NewsHeadline(Base):
    __tablename__ = "headlines"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(500), unique=True, index=True)
    category = Column(String(50))
    score = Column(Float)
    suspicious_words = Column(ARRAY(String))
    created_at = Column(String, default=datetime.utcnow().isoformat())

# Pydantic models
class HeadlineRequest(BaseModel):
    text: str
    example: dict[str, str] = Field(
        default={"text": "Secret government project revealed!"},
        examples=[{"text": "Secret government project revealed!"}]
    )

class HeadlineResponse(BaseModel):
    id: int
    text: str
    category: str
    score: float
    suspicious_words: List[str]
    created_at: str

    class Config:
        orm_mode = True

# Initialize NLP models
try:
    nlp = spacy.load("en_core_web_sm")
    classifier = pipeline(
        "text-classification",
        model="facebook/bart-large-mnli",
        device=-1,  # Force CPU usage
        framework="pt"
    )
except Exception as e:
    raise RuntimeError(f"Failed to load NLP models: {str(e)}")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def classify_headline(text: str) -> dict:
    """Analyze headline for conspiracy indicators"""
    suspicious_words = {"hoax", "secret", "hidden", "exposed", "leak", "cover-up", "agenda"}
    doc = nlp(text.lower())
    found_words = list({token.text for token in doc if token.text in suspicious_words})
    
    try:
        result = classifier(text, truncation=True)[0]
        return {
            "category": result["label"].capitalize(),
            "score": round(result["score"] * 100, 2),
            "suspicious_words": found_words
        }
    except Exception as e:
        return {
            "category": "Classification Error",
            "score": 0.0,
            "suspicious_words": []
        }

def load_initial_data():
    """Seed database with initial dataset"""
    try:
        with open("news_headlines_large.json") as f:
            data = json.load(f)
        
        db = SessionLocal()
        existing_count = db.query(NewsHeadline).count()
        
        if existing_count == 0:
            for article in data["articles"]:
                classification = classify_headline(article["headline"])
                headline = NewsHeadline(
                    text=article["headline"],
                    category=classification["category"],
                    score=classification["score"],
                    suspicious_words=classification["suspicious_words"]
                )
                db.add(headline)
            db.commit()
            print(f"Loaded {len(data['articles'])} initial headlines")
    except Exception as e:
        print(f"Error loading initial data: {str(e)}")
    finally:
        db.close()

# Application lifecycle events
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    load_initial_data()
    print("Application startup complete")

@app.get("/", include_in_schema=False)
def root():
    return {"status": "active", "docs": "/docs"}

@app.post("/classify", response_model=HeadlineResponse)
def classify_headline_endpoint(request: HeadlineRequest, db: Session = Depends(get_db)):
    """Classify a new headline and store result"""
    classification = classify_headline(request.text)
    
    # Check for existing entry
    existing = db.query(NewsHeadline).filter_by(text=request.text).first()
    if existing:
        raise HTTPException(status_code=400, detail="Headline already exists")
    
    headline = NewsHeadline(
        text=request.text,
        **classification
    )
    db.add(headline)
    db.commit()
    db.refresh(headline)
    return headline

@app.get("/headlines", response_model=List[HeadlineResponse])
def get_headlines(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    """Retrieve paginated headlines"""
    return db.query(NewsHeadline).offset(skip).limit(limit).all()

@app.patch("/headlines/{headline_id}", response_model=HeadlineResponse)
def update_headline_score(
    headline_id: int,
    category: Optional[str] = None,
    score: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """Update headline classification manually"""
    headline = db.query(NewsHeadline).filter_by(id=headline_id).first()
    if not headline:
        raise HTTPException(status_code=404, detail="Headline not found")
    
    if score is not None:
        headline.score = score
    if category is not None:
        headline.category = category
    
    db.commit()
    return headline

@app.delete("/headlines/{headline_id}")
def delete_headline(headline_id: int, db: Session = Depends(get_db)):
    """Remove a headline from the database"""
    headline = db.query(NewsHeadline).filter_by(id=headline_id).first()
    if not headline:
        raise HTTPException(status_code=404, detail="Headline not found")
    
    db.delete(headline)
    db.commit()
    return {
        "status": "success",
        "message": "Headline deleted",
        "deleted_id": headline_id
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        log_level="info"
    )
