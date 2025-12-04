"""
Tests for IQ Test Lite API
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns API info"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "endpoints" in data


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_get_test_items():
    """Test getting test items"""
    response = client.get("/api/test-items")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) > 0
    
    # Check that correct answers are not included
    for item in data["items"]:
        assert "id" in item
        assert "question" in item
        assert "options" in item
        assert "correct" not in item


def test_submit_test_all_correct():
    """Test submitting test with all correct answers"""
    # First get the items to know structure
    response = client.get("/api/test-items")
    items = response.json()["items"]
    
    # Load correct answers from data file
    import json
    with open(Path(__file__).parent.parent / "data" / "test_items.json") as f:
        test_data = json.load(f)
    
    # Create submission with all correct answers
    answers = []
    for item in test_data["items"]:
        answers.append({
            "question_id": item["id"],
            "selected_option": item["correct"]
        })
    
    response = client.post("/api/submit", json={"answers": answers})
    assert response.status_code == 200
    data = response.json()
    
    assert "raw_score" in data
    assert "iq_score" in data
    assert "percentile" in data
    assert "description" in data
    assert "disclaimer" in data
    assert data["raw_score"] == len(test_data["items"])


def test_submit_test_all_wrong():
    """Test submitting test with all wrong answers"""
    response = client.get("/api/test-items")
    items = response.json()["items"]
    
    # Create submission with wrong answers (always select option 99 which doesn't exist)
    answers = []
    for item in items:
        answers.append({
            "question_id": item["id"],
            "selected_option": 99
        })
    
    response = client.post("/api/submit", json={"answers": answers})
    assert response.status_code == 200
    data = response.json()
    
    assert data["raw_score"] == 0
    assert data["iq_score"] > 0  # Should still return a score


def test_submit_test_partial_correct():
    """Test submitting test with some correct answers"""
    import json
    with open(Path(__file__).parent.parent / "data" / "test_items.json") as f:
        test_data = json.load(f)
    
    # Create submission with first half correct, second half wrong
    answers = []
    for i, item in enumerate(test_data["items"]):
        if i < len(test_data["items"]) // 2:
            answers.append({
                "question_id": item["id"],
                "selected_option": item["correct"]
            })
        else:
            answers.append({
                "question_id": item["id"],
                "selected_option": (item["correct"] + 1) % len(item["options"])
            })
    
    response = client.post("/api/submit", json={"answers": answers})
    assert response.status_code == 200
    data = response.json()
    
    expected_score = len(test_data["items"]) // 2
    assert data["raw_score"] == expected_score


def test_submit_empty_answers():
    """Test submitting with empty answers list"""
    response = client.post("/api/submit", json={"answers": []})
    assert response.status_code == 200
    data = response.json()
    assert data["raw_score"] == 0


def test_data_files_exist():
    """Test that required data files exist"""
    data_dir = Path(__file__).parent.parent / "data"
    assert (data_dir / "test_items.json").exists()
    assert (data_dir / "scoring_norms.csv").exists()


def test_test_items_structure():
    """Test that test items have correct structure"""
    import json
    with open(Path(__file__).parent.parent / "data" / "test_items.json") as f:
        data = json.load(f)
    
    assert "items" in data
    assert len(data["items"]) > 0
    
    for item in data["items"]:
        assert "id" in item
        assert "question" in item
        assert "options" in item
        assert "correct" in item
        assert "type" in item
        assert isinstance(item["options"], list)
        assert len(item["options"]) > 0
        assert 0 <= item["correct"] < len(item["options"])


def test_scoring_norms_structure():
    """Test that scoring norms have correct structure"""
    import csv
    with open(Path(__file__).parent.parent / "data" / "scoring_norms.csv") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    assert len(rows) > 0
    
    for row in rows:
        assert "raw_score" in row
        assert "iq_score" in row
        assert "percentile" in row
        assert "description" in row
        assert int(row["raw_score"]) >= 0
        assert int(row["iq_score"]) > 0
        assert 0 <= int(row["percentile"]) <= 100
