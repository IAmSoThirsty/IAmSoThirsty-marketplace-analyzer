# Thirsty's Value Finder

A production-grade, monolithic web application for image analysis and marketplace value resolution. Built with FastAPI, React, PostgreSQL, Celery, and modern ML models (YOLOv8/Vision Transformer).

## Features

### Backend
- **FastAPI** REST API with async support
- **Celery** distributed task engine with RabbitMQ
- **PostgreSQL** database with SQLAlchemy ORM
- **S3/MinIO** object storage for images
- **WebSocket** real-time updates
- **Image Analysis** using YOLOv8 or Vision Transformer models
- **Marketplace Integration** with eBay, Amazon, StockX, and Grailed

### Frontend
- **React** with Vite for fast development
- **TailwindCSS** for responsive styling
- **Real-time camera** capture and file upload
- **WebSocket** live progress updates
- **Mobile-compatible** responsive design

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 18+

### Development Setup with Docker

1. **Clone the repository**
   ```bash
   git clone https://github.com/IAmSoThirsty/IAmSoThirsty-marketplace-analyzer.git
   cd IAmSoThirsty-marketplace-analyzer
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings if needed
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - RabbitMQ Management: http://localhost:15672 (user: analyzer, pass: analyzer_pass)
   - MinIO Console: http://localhost:9001 (user: analyzer, pass: analyzer_pass)

## Usage

1. Navigate to http://localhost:5173
2. Upload an image or capture from camera
3. Click "Start Analysis" to identify objects
4. View detected objects and confidence scores
5. Click "Find Marketplace Prices" to search marketplaces
6. Select marketplaces (eBay, Amazon, StockX, Grailed)
7. View real-time results from multiple platforms

## API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

```bash
# Backend tests
pytest tests/ -v

# Frontend tests (when in frontend directory)
cd frontend
npm test
```

## Project Structure

```
.
├── backend/              # FastAPI backend
│   ├── api/             # API endpoints
│   ├── core/            # Configuration & security
│   ├── models/          # Database models
│   ├── services/        # Business logic
│   └── tasks/           # Celery tasks
├── frontend/            # React frontend
│   └── src/
│       ├── components/  # UI components
│       ├── pages/       # Page components
│       └── services/    # API client
├── tests/               # Test files
├── docker-compose.yml   # Docker services
└── requirements.txt     # Python dependencies
```

## License

Apache License 2.0
