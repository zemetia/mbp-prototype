# MBP v2.0 Deployment Guide

## Prerequisites

- Python 3.10+
- Virtual environment
- Moonshot AI API key

## Local Development

### 1. Setup Environment

```bash
cd /mnt/d/Yoel/projects/mbp-prototype/backend-v2
source ../backend/venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure

Create `.env`:
```
MOONSHOT_API_KEY=sk-...
API_HOST=0.0.0.0
API_PORT=8000
```

### 3. Run

Development mode:
```bash
./run.sh
```

Or:
```bash
python main.py
```

### 4. Test

```bash
./run_tests.sh
```

## Production Deployment

### Using Docker (Recommended)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t mbp-v2 .
docker run -p 8000:8000 --env-file .env mbp-v2
```

### Using Systemd

Create `/etc/systemd/system/mbp-v2.service`:
```ini
[Unit]
Description=MBP v2.0 API
After=network.target

[Service]
Type=simple
User=mbp
WorkingDirectory=/opt/mbp-v2
Environment=MOONSHOT_API_KEY=sk-...
ExecStart=/opt/mbp-v2/venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable mbp-v2
sudo systemctl start mbp-v2
```

## Monitoring

### Logs
```bash
journalctl -u mbp-v2 -f
```

### Health Check
```bash
curl http://localhost:8000/health
```

## Performance Tuning

### Fast Mode
```python
from core.config import set_fast_mode
set_fast_mode()
```

### Accuracy Mode
```python
from core.config import set_accuracy_mode
set_accuracy_mode()
```

## Troubleshooting

### Import Errors
Ensure you're in the correct virtual environment:
```bash
source ../backend/venv/bin/activate
```

### API Key Issues
Verify key is set:
```bash
echo $MOONSHOT_API_KEY
```

### Memory Issues
Reduce `MAX_HISTORY_MESSAGES` in `core/config.py`.
