# API Documentation

## Endpoints

### 1. **POST** `/api/analyze`

Analyzes the given article text and returns insights like sentiment, bias, emotional language, and related articles.

**Request Body:**
```json
{
    "article_text": "Your article content here."
}
```

**Response:**
```json
{
    "analysis": { ... },
    "keywords": { ... },
    "political_analysis": { ... },
    "related_articles": [ ... ],
    "status": "success"
}
```

### 2. **GET** `/api/health`

Checks the health of the API.

**Response:**
```json
{
    "environment": "development",
    "status": "healthy"
}
```

---

## Usage

- `/api/analyze`: Post article text for detailed analysis.
- `/api/health`: Get the current health status of the API.