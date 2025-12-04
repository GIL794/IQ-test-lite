"""
FastAPI backend for IQ Test Lite
Serves test items and calculates scores
"""
import json
import csv
from pathlib import Path
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="IQ Test Lite API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
FRONTEND_DIR = BASE_DIR / "frontend"

# Load test items
def load_test_items() -> Dict[str, Any]:
    """Load test items from JSON file"""
    with open(DATA_DIR / "test_items.json", "r") as f:
        return json.load(f)

# Load scoring norms
def load_scoring_norms() -> List[Dict[str, Any]]:
    """Load scoring norms from CSV file"""
    norms = []
    with open(DATA_DIR / "scoring_norms.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            norms.append({
                "raw_score": int(row["raw_score"]),
                "iq_score": int(row["iq_score"]),
                "percentile": int(row["percentile"]),
                "description": row["description"]
            })
    return norms

# Request/Response models
class Answer(BaseModel):
    question_id: int
    selected_option: int

class TestSubmission(BaseModel):
    answers: List[Answer]

class ScoreResponse(BaseModel):
    raw_score: int
    total_questions: int
    iq_score: int
    percentile: int
    description: str
    disclaimer: str

# Mount static files (frontend)
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "message": "IQ Test Lite API",
        "version": "1.0.0",
        "endpoints": {
            "test_items": "/api/test-items",
            "submit": "/api/submit",
            "health": "/api/health"
        }
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/api/test-items")
async def get_test_items():
    """Get all test items (without correct answers)"""
    try:
        data = load_test_items()
        # Remove correct answers from response
        items_without_answers = []
        for item in data["items"]:
            item_copy = item.copy()
            item_copy.pop("correct", None)
            items_without_answers.append(item_copy)
        return {"items": items_without_answers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading test items: {str(e)}")

@app.post("/api/submit", response_model=ScoreResponse)
async def submit_test(submission: TestSubmission):
    """Submit test answers and get score"""
    try:
        # Load test items with correct answers
        data = load_test_items()
        test_items = {item["id"]: item for item in data["items"]}
        
        # Calculate raw score
        raw_score = 0
        for answer in submission.answers:
            if answer.question_id in test_items:
                correct_answer = test_items[answer.question_id]["correct"]
                if answer.selected_option == correct_answer:
                    raw_score += 1
        
        # Load scoring norms
        norms = load_scoring_norms()
        
        # Find corresponding IQ score
        # Default to lowest if score is too low, highest if too high
        score_data = norms[0]  # Default
        for norm in norms:
            if raw_score == norm["raw_score"]:
                score_data = norm
                break
            elif raw_score > norm["raw_score"]:
                score_data = norm  # Keep updating to get closest
        
        return ScoreResponse(
            raw_score=raw_score,
            total_questions=len(data["items"]),
            iq_score=score_data["iq_score"],
            percentile=score_data["percentile"],
            description=score_data["description"],
            disclaimer="This is NOT a clinical or official IQ test. Results are approximate and for educational/entertainment purposes only. A proper IQ assessment should be administered by a qualified professional."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating score: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
