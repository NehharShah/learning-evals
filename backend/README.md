# LLM Evaluation Tool - Backend API

A modular and secure FastAPI backend for evaluating Large Language Model (LLM) performance with comprehensive metrics and security analysis.

## 🚀 Features

- **File Upload**: Support for CSV and JSONL datasets with validation
- **LLM Evaluation**: Integration with OpenAI API for model evaluation
- **Scoring Metrics**: Exact match and fuzzy match calculations using rapidfuzz
- **Security Analysis**: Prompt injection detection and toxicity screening
- **Export Functionality**: Download results as CSV or JSON
- **Rate Limiting**: Per-IP rate limiting to prevent abuse
- **CORS Support**: Configured for frontend integration
- **Comprehensive Logging**: Structured logging with security monitoring
- **Production Ready**: Docker support and deployment configurations

## 📋 Requirements

- Python 3.11+
- OpenAI API key
- FastAPI and dependencies (see requirements.txt)

## 🛠️ Installation

### Local Development

1. **Clone and navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp env.template .env
   # Edit .env with your configuration
   ```

5. **Run the development server**:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Docker Deployment

1. **Build the Docker image**:
   ```bash
   docker build -t llm-eval-backend .
   ```

2. **Run with environment variables**:
   ```bash
   docker run -d \
     --name llm-eval-api \
     -p 8000:8000 \
     -e OPENAI_API_KEY=your_api_key \
     -e ENVIRONMENT=production \
     llm-eval-backend
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file based on `env.template`:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Application Settings
ENVIRONMENT=development  # or production
DEBUG=true

# Security
SECRET_KEY=your_secret_key_here
MAX_FILE_SIZE_MB=5
ALLOWED_FILE_TYPES=.csv,.jsonl

# CORS (comma-separated)
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
EVALUATION_RATE_LIMIT_PER_MINUTE=10

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json  # or standard
```

### Model Configuration

The API supports multiple model providers:

- **OpenAI**: gpt-4, gpt-3.5-turbo, gpt-4-turbo-preview
- **Anthropic**: claude-3 (fallback to GPT-4)
- **Google**: gemini-pro (fallback to GPT-3.5)
- **Meta**: llama-2 (fallback to GPT-3.5)

*Note: Non-OpenAI models currently use OpenAI fallbacks. Full multi-provider support coming soon.*

## 📖 API Documentation

### Endpoints Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check and API info |
| `/health` | GET | Detailed health status |
| `/docs` | GET | Interactive API documentation |
| `/api/v1/upload` | POST | Upload dataset files |
| `/api/v1/evaluate` | POST | Run LLM evaluation |
| `/api/v1/export` | POST | Export results |

### Upload Dataset

**POST** `/api/v1/upload`

Upload CSV or JSONL files containing prompts and expected outputs.

**Request**: Multipart form with file upload

**Response**:
```json
{
  "success": true,
  "message": "Successfully uploaded and parsed 10 prompts",
  "data": [...],
  "total_prompts": 10,
  "preview": [...]
}
```

**Supported File Formats**:

- **CSV**: Must contain `prompt` and `expected_output` columns
- **JSONL**: One JSON object per line with `prompt` and `expected_output` fields

### Run Evaluation

**POST** `/api/v1/evaluate`

Evaluate prompts against selected LLM model.

**Request**:
```json
{
  "prompts": [
    {
      "prompt": "What is the capital of France?",
      "expected_output": "Paris"
    }
  ],
  "model": "gpt-3.5-turbo",
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 1000,
    "top_p": 1.0,
    "frequency_penalty": 0.0
  }
}
```

**Response**:
```json
{
  "success": true,
  "message": "Successfully evaluated 1 prompts in 2.34 seconds",
  "results": [
    {
      "id": "eval_1",
      "prompt": "What is the capital of France?",
      "modelResponse": "The capital of France is Paris.",
      "expectedOutput": "Paris",
      "exactMatch": 100.0,
      "fuzzyMatch": 95.2,
      "toxicity": false,
      "model": "gpt-3.5-turbo",
      "timestamp": "2024-01-15T10:30:00Z",
      "securityFlags": null
    }
  ],
  "total_evaluations": 1,
  "summary": {...}
}
```

### Export Results

**POST** `/api/v1/export`

Export evaluation results to CSV or JSON format.

**Request**:
```json
{
  "format": "csv",
  "include_metadata": true
}
```

**Response**: File download with appropriate headers

## 🔒 Security Features

### Prompt Injection Detection

The API automatically detects potential prompt injection attempts using:

- Keyword-based detection (configurable)
- Pattern matching for common injection techniques
- Security scoring (0-100, higher is safer)

### Rate Limiting

- **General endpoints**: 60 requests per minute per IP
- **Evaluation endpoints**: 10 requests per minute per IP
- **File uploads**: Size limited to 5MB by default

### Input Validation

- File type and size validation
- Request header validation
- Content sanitization
- Pydantic model validation

### Security Headers

Automatic addition of security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security` (production only)

## 📊 Monitoring and Logging

### Structured Logging

The API uses structured logging with configurable formats:

- **JSON**: Machine-readable logs for production
- **Colored**: Human-readable logs for development

### Log Levels

- **DEBUG**: Detailed debugging information
- **INFO**: General operational messages
- **WARNING**: Important notices and security alerts
- **ERROR**: Error conditions requiring attention
- **CRITICAL**: Serious failures requiring immediate action

### Security Monitoring

Automatic logging of:
- Suspicious request patterns
- Rate limit violations
- Potential security threats
- File upload activities

## 🚀 Deployment

### Render Deployment

1. Connect your GitHub repository to Render
2. Set environment variables in Render dashboard
3. Use these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Fly.io Deployment

1. Install Fly CLI and login
2. Create `fly.toml`:
   ```toml
   app = "llm-eval-api"
   
   [build]
     dockerfile = "Dockerfile"
   
   [[services]]
     internal_port = 8000
     protocol = "tcp"
   
     [[services.ports]]
       port = 80
       handlers = ["http"]
   
     [[services.ports]]
       port = 443
       handlers = ["tls", "http"]
   ```
3. Deploy: `fly deploy`

### Docker Compose (Local)

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ENVIRONMENT=production
    volumes:
      - ./logs:/app/logs
```

## 🧪 Testing

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

### Manual Testing

Use the interactive API documentation at `http://localhost:8000/docs` to test endpoints manually.

## 📝 Development

### Code Style

The project uses:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting

```bash
# Format code
black .
isort .

# Lint code
flake8 .
```

### Adding New Models

To add support for new LLM providers:

1. Update `app/models/schemas.py` with new model names
2. Modify `app/utils/evaluation.py` to handle new API calls
3. Add provider-specific configuration to `app/config.py`

### Database Integration

For production use, replace in-memory storage with a database:

1. Add database dependencies to `requirements.txt`
2. Create database models in `app/models/database.py`
3. Update routers to use database operations
4. Add database connection to `app/config.py`

## 🐛 Troubleshooting

### Common Issues

**OpenAI API Errors**:
- Verify API key is correct and has sufficient credits
- Check rate limits and quotas
- Ensure model names are valid

**File Upload Issues**:
- Check file size limits (default 5MB)
- Verify file format (CSV/JSONL only)
- Ensure proper column names in CSV files

**CORS Issues**:
- Update `ALLOWED_ORIGINS` in environment variables
- Check frontend URL configuration

**Rate Limiting**:
- Adjust rate limits in configuration
- Implement caching for repeated requests

### Logs and Debugging

Check logs for detailed error information:

```bash
# View logs (Docker)
docker logs llm-eval-api

# View logs (local)
tail -f logs/app.log
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 🙋 Support

For questions and support:
- Check the [API documentation](http://localhost:8000/docs)
- Review the troubleshooting section
- Open an issue on GitHub 