# Deployment Guide

## Production Deployment

### Prerequisites

- Docker and Docker Compose installed
- Domain name configured (for HTTPS)
- SSL certificates (Let's Encrypt recommended)
- Minimum 4GB RAM, 2 CPUs
- 20GB+ storage

### Step-by-Step Deployment

#### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. Application Setup

```bash
# Clone repository
git clone https://github.com/IAmSoThirsty/IAmSoThirsty-marketplace-analyzer.git
cd IAmSoThirsty-marketplace-analyzer

# Create production environment file
cp .env.example .env

# Edit .env with production values
nano .env
```

#### 3. Configure Production Environment

Update `.env` with production settings:

```env
# Database - Use strong passwords
DATABASE_URL=postgresql+asyncpg://analyzer:STRONG_PASSWORD@postgres:5432/marketplace_analyzer

# Security - Generate secure keys
SECRET_KEY=<generate-using-openssl-rand-hex-32>

# API Keys - Add your marketplace API credentials
EBAY_APP_ID=your-production-ebay-app-id
AMAZON_ACCESS_KEY=your-production-amazon-key
STOCKX_API_KEY=your-production-stockx-key
GRAILED_API_KEY=your-production-grailed-key

# CORS - Set to your domain
CORS_ORIGINS=["https://yourdomain.com"]
```

Generate secure SECRET_KEY:
```bash
openssl rand -hex 32
```

#### 4. Create Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: marketplace_analyzer
      POSTGRES_USER: analyzer
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  rabbitmq:
    image: rabbitmq:3.12-management-alpine
    environment:
      RABBITMQ_DEFAULT_USER: analyzer
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_PASSWORD}
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    restart: unless-stopped

  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_USER}
      MINIO_ROOT_PASSWORD: ${MINIO_PASSWORD}
    volumes:
      - minio_data:/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

  backend:
    build:
      context: .
      dockerfile: Dockerfile
    command: uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
    environment:
      DATABASE_URL: ${DATABASE_URL}
      CELERY_BROKER_URL: ${CELERY_BROKER_URL}
      CELERY_RESULT_BACKEND: ${CELERY_RESULT_BACKEND}
      S3_ENDPOINT: http://minio:9000
      S3_ACCESS_KEY: ${MINIO_USER}
      S3_SECRET_KEY: ${MINIO_PASSWORD}
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      - postgres
      - rabbitmq
      - redis
      - minio
    restart: unless-stopped

  celery_worker:
    build:
      context: .
      dockerfile: Dockerfile
    command: celery -A backend.celery_app worker --loglevel=info --concurrency=4
    environment:
      DATABASE_URL: ${DATABASE_URL}
      CELERY_BROKER_URL: ${CELERY_BROKER_URL}
      CELERY_RESULT_BACKEND: ${CELERY_RESULT_BACKEND}
      S3_ENDPOINT: http://minio:9000
      S3_ACCESS_KEY: ${MINIO_USER}
      S3_SECRET_KEY: ${MINIO_PASSWORD}
    depends_on:
      - postgres
      - rabbitmq
      - redis
      - minio
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
  rabbitmq_data:
  minio_data:
  redis_data:
```

#### 5. Configure Nginx

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    server {
        listen 80;
        server_name yourdomain.com;
        
        # Redirect to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        client_max_body_size 100M;

        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /ws {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
        }
    }
}
```

#### 6. SSL Certificate Setup (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d yourdomain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ./ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ./ssl/key.pem
```

#### 7. Start Production Services

```bash
# Build and start
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

#### 8. Health Checks

```bash
# Check backend
curl https://yourdomain.com/health

# Check services
docker-compose -f docker-compose.prod.yml ps
```

### Monitoring

#### Setup Prometheus and Grafana (Optional)

Add to `docker-compose.prod.yml`:

```yaml
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    restart: unless-stopped
```

### Backup Strategy

#### Database Backups

```bash
# Daily backup script
docker-compose exec postgres pg_dump -U analyzer marketplace_analyzer > backup_$(date +%Y%m%d).sql

# Restore from backup
cat backup_20240101.sql | docker-compose exec -T postgres psql -U analyzer marketplace_analyzer
```

#### S3/MinIO Backups

```bash
# Use MinIO client to sync to backup location
mc mirror minio/marketplace-images s3://backup-bucket/
```

### Scaling

#### Horizontal Scaling

1. **Add more Celery workers:**
   ```bash
   docker-compose -f docker-compose.prod.yml scale celery_worker=4
   ```

2. **Load balance backend:**
   - Deploy multiple backend instances
   - Update Nginx upstream configuration

3. **Database read replicas:**
   - Configure PostgreSQL streaming replication
   - Update application to route reads to replicas

### Maintenance

#### Update Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Run migrations if needed
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

#### View Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend
```

### Troubleshooting

#### Common Issues

1. **Database connection errors:**
   - Check PostgreSQL is running
   - Verify DATABASE_URL is correct
   - Check network connectivity

2. **Celery tasks not processing:**
   - Check RabbitMQ is running
   - Verify worker logs
   - Check task queue status

3. **Image upload failures:**
   - Check MinIO is accessible
   - Verify S3 credentials
   - Check disk space

### Security Checklist

- [ ] Change all default passwords
- [ ] Enable firewall (ufw/iptables)
- [ ] Configure fail2ban
- [ ] Enable HTTPS/SSL
- [ ] Restrict database access
- [ ] Set up regular backups
- [ ] Configure monitoring/alerting
- [ ] Enable rate limiting
- [ ] Review CORS settings
- [ ] Audit API keys
- [ ] Keep dependencies updated

### Performance Tuning

#### Database

```sql
-- Create indexes
CREATE INDEX idx_images_user_id ON images(user_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_analyses_image_id ON analyses(image_id);
CREATE INDEX idx_marketplace_items_analysis_id ON marketplace_items(analysis_id);
```

#### Nginx

```nginx
# Enable gzip compression
gzip on;
gzip_types text/plain text/css application/json application/javascript;

# Enable caching
location /static {
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

## Support

For production support, contact the development team or open an issue on GitHub.
