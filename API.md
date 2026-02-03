# API Documentation

## Base URL

- Development: `http://localhost:8000`
- Production: `https://api.yourdomain.com`

## Authentication

Currently using simplified authentication. JWT-based authentication is implemented but optional for demo purposes.

### Register User

```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "password123"
}
```

Response:
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-01-01T00:00:00"
}
```

### Login

```http
POST /auth/login
Content-Type: application/json

{
  "username": "username",
  "password": "password123"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Images

### Upload Image

```http
POST /images/upload
Content-Type: multipart/form-data

file: [binary image data]
```

Response:
```json
{
  "id": 1,
  "filename": "image.jpg",
  "s3_key": "images/uuid.jpg",
  "content_type": "image/jpeg",
  "size": 102400,
  "uploaded_at": "2024-01-01T00:00:00",
  "user_id": 1
}
```

### List Images

```http
GET /images/?skip=0&limit=100
```

Response:
```json
[
  {
    "id": 1,
    "filename": "image.jpg",
    "s3_key": "images/uuid.jpg",
    "content_type": "image/jpeg",
    "size": 102400,
    "uploaded_at": "2024-01-01T00:00:00",
    "user_id": 1
  }
]
```

### Get Image

```http
GET /images/{image_id}
```

Response:
```json
{
  "id": 1,
  "filename": "image.jpg",
  "s3_key": "images/uuid.jpg",
  "content_type": "image/jpeg",
  "size": 102400,
  "uploaded_at": "2024-01-01T00:00:00",
  "user_id": 1
}
```

### Get Image Download URL

```http
GET /images/{image_id}/download-url
```

Response:
```json
{
  "url": "https://minio.example.com/marketplace-images/images/uuid.jpg?..."
}
```

### Delete Image

```http
DELETE /images/{image_id}
```

Response: `204 No Content`

## Analysis

### Start Image Analysis

```http
POST /analysis/
Content-Type: application/json

{
  "image_id": 1
}
```

Response:
```json
{
  "id": 1,
  "celery_task_id": "abc123...",
  "job_type": "analysis",
  "status": "pending",
  "progress": 0,
  "result": null,
  "error": null,
  "created_at": "2024-01-01T00:00:00",
  "completed_at": null
}
```

### Get Analysis Job Status

```http
GET /analysis/jobs/{job_id}
```

Response:
```json
{
  "id": 1,
  "celery_task_id": "abc123...",
  "job_type": "analysis",
  "status": "completed",
  "progress": 100,
  "result": {
    "analysis_id": 1,
    "labels": ["person", "car"],
    "detections": [...],
    "confidence_scores": {"person": 0.95, "car": 0.87}
  },
  "error": null,
  "created_at": "2024-01-01T00:00:00",
  "completed_at": "2024-01-01T00:01:00"
}
```

### Get Image Analyses

```http
GET /analysis/image/{image_id}
```

Response:
```json
[
  {
    "id": 1,
    "image_id": 1,
    "job_id": 1,
    "model_type": "yolov8",
    "model_version": "yolov8n",
    "detections": [
      {
        "label": "person",
        "confidence": 0.95,
        "bbox": [100, 200, 300, 400]
      }
    ],
    "labels": ["person", "car"],
    "confidence_scores": {"person": 0.95, "car": 0.87},
    "processing_time": 1.23,
    "created_at": "2024-01-01T00:00:00"
  }
]
```

### Get Analysis

```http
GET /analysis/{analysis_id}
```

Response:
```json
{
  "id": 1,
  "image_id": 1,
  "job_id": 1,
  "model_type": "yolov8",
  "model_version": "yolov8n",
  "detections": [
    {
      "label": "person",
      "confidence": 0.95,
      "bbox": [100, 200, 300, 400]
    }
  ],
  "labels": ["person", "car"],
  "confidence_scores": {"person": 0.95, "car": 0.87},
  "processing_time": 1.23,
  "created_at": "2024-01-01T00:00:00"
}
```

## Marketplace

### Start Marketplace Search

```http
POST /marketplace/search
Content-Type: application/json

{
  "analysis_id": 1,
  "providers": ["ebay", "amazon", "stockx", "grailed"]
}
```

Response:
```json
{
  "id": 2,
  "celery_task_id": "def456...",
  "job_type": "marketplace",
  "status": "pending",
  "progress": 0,
  "result": null,
  "error": null,
  "created_at": "2024-01-01T00:00:00",
  "completed_at": null
}
```

### Get Marketplace Job Status

```http
GET /marketplace/jobs/{job_id}
```

Response:
```json
{
  "id": 2,
  "celery_task_id": "def456...",
  "job_type": "marketplace",
  "status": "completed",
  "progress": 100,
  "result": {
    "items_found": 20,
    "items": [...],
    "query": "person car"
  },
  "error": null,
  "created_at": "2024-01-01T00:00:00",
  "completed_at": "2024-01-01T00:02:00"
}
```

### Get Marketplace Items

```http
GET /marketplace/analysis/{analysis_id}?skip=0&limit=100
```

Response:
```json
[
  {
    "id": 1,
    "analysis_id": 1,
    "job_id": 2,
    "provider": "ebay",
    "item_name": "Vintage Car Model",
    "item_url": "https://ebay.com/item/123",
    "price": 29.99,
    "currency": "USD",
    "condition": "Used",
    "availability": "In Stock",
    "image_url": "https://ebay.com/image.jpg",
    "relevance_score": 0.85,
    "metadata": {
      "seller": "user123",
      "location": "USA"
    },
    "created_at": "2024-01-01T00:00:00"
  }
]
```

### Get Marketplace Item

```http
GET /marketplace/item/{item_id}
```

Response:
```json
{
  "id": 1,
  "analysis_id": 1,
  "job_id": 2,
  "provider": "ebay",
  "item_name": "Vintage Car Model",
  "item_url": "https://ebay.com/item/123",
  "price": 29.99,
  "currency": "USD",
  "condition": "Used",
  "availability": "In Stock",
  "image_url": "https://ebay.com/image.jpg",
  "relevance_score": 0.85,
  "metadata": {
    "seller": "user123",
    "location": "USA"
  },
  "created_at": "2024-01-01T00:00:00"
}
```

## WebSocket

### Connect to Job Updates

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/{job_id}');

ws.onopen = () => {
  console.log('Connected');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Update:', data);
  // {
  //   "type": "job_update",
  //   "job_id": 1,
  //   "status": "processing",
  //   "progress": 50,
  //   "result": null
  // }
};

ws.onerror = (error) => {
  console.error('Error:', error);
};

ws.onclose = () => {
  console.log('Disconnected');
};
```

### Connect to All Updates

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Receives all job updates
};
```

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Invalid input"
}
```

### 401 Unauthorized

```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found

```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error

```json
{
  "detail": [
    {
      "loc": ["body", "image_id"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

Currently no rate limiting is enforced. For production use, implement rate limiting based on your needs.

## Pagination

List endpoints support pagination with `skip` and `limit` parameters:

```http
GET /images/?skip=0&limit=100
```

- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 100, max: 100)

## Interactive Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
