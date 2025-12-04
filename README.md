# IQ Test Lite

An educational, single-page IQ-style reasoning test for learning purposes.

## ⚠️ Important Disclaimer

**This is NOT a clinical or official IQ test.** Results are approximate and for educational/entertainment purposes only. A proper IQ assessment should be administered by a qualified professional.

## Features

- **12 Fluid Reasoning Questions**: Number sequences, patterns, logical reasoning, and analogies
- **Simple Scoring**: Transparent scoring system with approximate IQ estimates
- **Single-Page UI**: Clean, responsive web interface
- **FastAPI Backend**: RESTful API for serving questions and calculating scores
- **Educational Purpose**: Designed for learning and entertainment, not clinical assessment

## Tech Stack

- **Frontend**: HTML, CSS, Vanilla JavaScript
- **Backend**: Python + FastAPI
- **Data**: JSON for test items, CSV for scoring norms
- **Tests**: pytest

## Project Structure

```
IQ-test-lite/
├── backend/
│   └── main.py              # FastAPI application
├── frontend/
│   ├── index.html           # Main HTML page
│   ├── styles.css           # Styling
│   └── app.js               # Frontend logic
├── data/
│   ├── test_items.json      # Question bank
│   └── scoring_norms.csv    # Scoring lookup table
├── tests/
│   ├── __init__.py
│   └── test_api.py          # API tests
├── requirements.txt         # Python dependencies
└── README.md
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/GIL794/IQ-test-lite.git
cd IQ-test-lite
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

### Start the Backend Server

```bash
cd backend
python main.py
```

Or using uvicorn directly:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Access the Frontend

Open your browser and navigate to:
```
http://localhost:8000/static/index.html
```

## API Endpoints

- `GET /` - API information
- `GET /api/health` - Health check
- `GET /api/test-items` - Get all test questions (without answers)
- `POST /api/submit` - Submit answers and get results

### Example API Usage

Get test items:
```bash
curl http://localhost:8000/api/test-items
```

Submit answers:
```bash
curl -X POST http://localhost:8000/api/submit \
  -H "Content-Type: application/json" \
  -d '{"answers": [{"question_id": 1, "selected_option": 1}]}'
```

## Running Tests

Run all tests:
```bash
pytest tests/
```

Run with verbose output:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ --cov=backend --cov-report=html
```

## How It Works

1. **Test Items**: Questions are stored in `data/test_items.json` with correct answers
2. **API Serves Questions**: Frontend fetches questions from API (without correct answers)
3. **User Takes Test**: User answers all questions through the web interface
4. **Submit & Score**: Answers are submitted to the API, which calculates the raw score
5. **IQ Estimation**: Raw score is mapped to an approximate IQ score using `scoring_norms.csv`
6. **Results Display**: Results are shown with percentile and category

## Scoring

The scoring system is simplified and approximate:

- **Raw Score**: Number of correct answers (0-12)
- **IQ Score**: Mapped from raw score using norms table (70-130 range)
- **Percentile**: Indicates performance relative to the norming sample
- **Category**: Descriptive label (e.g., Average, Above Average, Superior)

## Limitations

- Small question bank (12 items)
- No time limits
- Simplified scoring model
- Not standardized or validated
- Does not account for age, education, or other factors
- Single domain (fluid reasoning) - real IQ tests assess multiple domains

## Development

### Adding New Questions

Edit `data/test_items.json`:
```json
{
  "id": 13,
  "question": "Your question here?",
  "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
  "correct": 0,
  "type": "category_name"
}
```

### Modifying Scoring

Edit `data/scoring_norms.csv` to adjust the raw score to IQ mapping.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available for educational purposes.

## Acknowledgments

This is a learning project designed to demonstrate:
- Building a simple web application with FastAPI
- Creating interactive frontend with vanilla JavaScript
- Implementing a basic assessment system
- Writing tests with pytest