# LLM Evaluation Tool

A full-stack application for evaluating Large Language Model (LLM) performance with clean UI, comprehensive metrics, and a secure FastAPI backend.

## ✨ Features

- **📁 Dataset Upload**: Support for CSV and JSONL files with drag-and-drop interface
- **🤖 Multi-Provider Support**: Choose from OpenAI, Anthropic, Google, Groq, and custom providers
- **📊 Evaluation Metrics**: Exact Match, Fuzzy Match, and Advanced NLP metrics (BLEU, ROUGE, Semantic Similarity)
- **📈 Score Visualization**: Color-coded progress bars with percentage display
- **📱 Responsive Design**: Clean, mobile-friendly interface
- **⚡ Real-time Results**: Live evaluation progress and results display
- **🔧 Provider Management**: Easy configuration and management of multiple AI providers

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ (for frontend)
- Python 3.11+ (for backend)
- OpenAI API key

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/llm-evaluation-tool.git
   cd llm-evaluation-tool
   ```

2. **Set up the backend**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp env.template .env
   # Edit .env with your OpenAI API key
   uvicorn main:app --reload --port 8000
   ```

3. **Set up the frontend** (in a new terminal):
   ```bash
   npm install
   npm run dev
   ```

4. **Open the application**:
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## 📖 Usage

### Dataset Format

Your dataset should contain at least two fields:

**CSV Example:**
``csv
prompt,expected_output
"What is the capital of France?","Paris"
"Explain quantum computing","Quantum computing uses quantum mechanics principles"
``

**JSONL Example:**
``jsonl
{"prompt": "What is the capital of France?", "expected_output": "Paris"}
{"prompt": "Explain quantum computing", "expected_output": "Quantum computing uses quantum mechanics principles"}
``

### Workflow

1. **Upload Dataset**: Drag and drop your CSV or JSONL file
2. **Select Model**: Choose from available LLM options
3. **Configure Metrics**: Expand sidebar to select evaluation method
4. **Run Evaluation**: Click the prominent "Run Evaluation" button
5. **View Results**: Analyze results in the responsive table with score visualization

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 14 with App Router
- **UI Library**: shadcn/ui + Tailwind CSS
- **Language**: TypeScript
- **Icons**: Lucide React

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **API Integration**: OpenAI API
- **Security**: Rate limiting, prompt injection detection
- **Data Processing**: rapidfuzz for fuzzy matching
- **Deployment**: Docker, Fly.io, Render compatible

## 📁 Project Structure

```
├── frontend/               # Next.js React frontend
│   ├── app/
│   │   ├── layout.tsx     # Root layout
│   │   └── page.tsx       # Main page
│   ├── components/
│   │   ├── ui/            # shadcn/ui components
│   │   ├── upload/        # Dataset upload components
│   │   ├── results/       # Results display components
│   │   └── models/        # Model selection components
│   └── llm-evaluation-tool.tsx
└── backend/                # FastAPI Python backend
    ├── main.py            # FastAPI app entry point
    ├── app/
    │   ├── config.py      # Configuration management
    │   ├── models/        # Pydantic data models
    │   ├── routers/       # API route handlers
    │   ├── middleware/    # Security middleware
    │   └── utils/         # Utilities and helpers
    ├── requirements.txt   # Python dependencies
    ├── Dockerfile         # Container configuration
    └── README.md          # Backend documentation
```

## 🚀 Deployment

This is a full-stack application with separate frontend and backend components.

### Frontend Deployment
- Deploy the Next.js frontend to Vercel, Netlify, or any static hosting platform
- Configure environment variables to point to your backend API

### Backend Deployment  
- Deploy the FastAPI backend using Docker to Fly.io, Render, or any container platform
- Set up environment variables including your OpenAI API key
- See `backend/README.md` for detailed deployment instructions

## 🗺️ Roadmap

- [x] Real LLM API integration (OpenAI GPT models)
- [x] Export functionality (CSV, JSON)
- [x] Batch processing for large datasets
- [x] Security features (prompt injection detection, rate limiting)
- [x] Advanced evaluation metrics (BLEU, ROUGE, Semantic Similarity)
- [x] Multi-provider support (OpenAI, Anthropic Claude, Google Gemini, Groq, Custom providers)
- [ ] Historical evaluation tracking with database
- [ ] Custom model configuration and fine-tuning
- [ ] A/B testing between models
- [ ] Real-time collaboration features
- [ ] Advanced analytics and reporting

## Contributing

This project is an LLM evaluation tool for testing and comparing language model performance. Contributions are welcome in areas like:
- Adding new evaluation metrics and methodologies
- Supporting additional LLM providers and models
- Improving the UI/UX and visualization features
- Enhancing data processing and analysis capabilities
- Bug fixes and documentation improvements

## 🙏 Acknowledgments

- UI components from [shadcn/ui](https://ui.shadcn.com)
- Icons from [Lucide](https://lucide.dev)
- FastAPI framework for the backend API
- OpenAI for LLM API access
