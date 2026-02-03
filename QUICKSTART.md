# Quick Start Guide

Get the Marketplace Analyzer running in 5 minutes!

## Prerequisites

- Docker Desktop installed
- 4GB RAM minimum
- 10GB free disk space

## Step 1: Clone Repository

```bash
git clone https://github.com/IAmSoThirsty/IAmSoThirsty-marketplace-analyzer.git
cd IAmSoThirsty-marketplace-analyzer
```

## Step 2: Run Setup Script

```bash
./setup.sh
```

Select option **1** to start all services.

That's it! The script will:
- Create environment configuration
- Start all Docker containers
- Set up the database
- Launch the application

## Step 3: Access the Application

Open your browser to:
- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs

## Using the Application

### 1. Upload an Image

- Click "Choose Image from Device" or "Take Photo with Camera"
- Select or capture an image

### 2. Analyze the Image

- Click "Start Analysis"
- Wait for AI to detect objects (progress bar shows status)
- View detected items with confidence scores

### 3. Find Marketplace Prices

- Click "Find Marketplace Prices"
- Select marketplaces to search (eBay, Amazon, StockX, Grailed)
- Click "Search Selected Marketplaces"
- View real-time results as they load

## Example Workflow

```
Upload Image → Analyze → Get Results → Search Marketplaces → Compare Prices
```

## Troubleshooting

### Services not starting?

```bash
# Check Docker is running
docker ps

# View logs
./setup.sh  # Select option 3

# Reset everything
./setup.sh  # Select option 4
```

### Port conflicts?

If ports 5173, 8000, 5432, 5672, or 9000 are in use:

```bash
# Edit docker-compose.yml to change ports
nano docker-compose.yml
```

### Frontend not loading?

```bash
# Check frontend logs
docker-compose logs frontend

# Restart frontend
docker-compose restart frontend
```

## Advanced Usage

### Running Tests

```bash
./setup.sh  # Select option 5
```

### Viewing Logs

```bash
./setup.sh  # Select option 3
```

### Manual Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart a service
docker-compose restart backend
```

## Configuration

Edit `.env` file to customize:

```env
# Change model type
MODEL_TYPE=yolov8  # or vit

# Add API keys for real marketplace data
EBAY_APP_ID=your-key
AMAZON_ACCESS_KEY=your-key
```

## Next Steps

- Read the [API Documentation](API.md)
- Check [Deployment Guide](DEPLOYMENT.md) for production setup
- See [Contributing Guidelines](CONTRIBUTING.md) to contribute

## Need Help?

- Check the [README](README.md) for detailed information
- Open an issue on GitHub
- Review the API docs at http://localhost:8000/docs

## Clean Up

To remove everything:

```bash
docker-compose down -v  # Removes containers and data
```

---

Happy analyzing! 🚀
