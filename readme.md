# News Analyzer

AI-powered news headline analyzer that assigns conspiracy scores and categorizes headlines.

## Features:
- Real-time headline classification using FastAPI.
- Interactive React frontend for CRUD operations.
- PostgreSQL database integration.

## Installation:
1. Backend:
    ```
    cd backend
    python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    python main.py  # Start backend server at http://localhost:8000/docs
    ```

2. Frontend:
    ```
    cd frontend
    npm install && npm start  # Start frontend server at http://localhost:3000/
    ```

## API Endpoints:
- `/classify`: Classify a headline.
- `/headlines`: Manage stored headlines.

## License:
MIT License.
