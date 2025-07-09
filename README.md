# LLM Evaluation Tool

A minimalist React application for evaluating Large Language Model (LLM) performance with clean UI and comprehensive metrics.

[![Deployed on Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-black?style=for-the-badge&logo=vercel)](https://vercel.com/nihar-shahs-projects-60f0b993/v0-llm-evals)
[![Built with v0](https://img.shields.io/badge/Built%20with-v0.dev-black?style=for-the-badge)](https://v0.dev/chat/projects/XjtZEK3f5U8)

## ✨ Features

- **📁 Dataset Upload**: Support for CSV and JSONL files with drag-and-drop interface
- **🤖 Model Selection**: Choose from popular LLMs (GPT-4, Claude, Gemini, etc.)
- **📊 Evaluation Metrics**: Exact Match and Fuzzy Match scoring
- **📈 Score Visualization**: Color-coded progress bars with percentage display
- **📱 Responsive Design**: Clean, mobile-friendly interface
- **⚡ Real-time Results**: Live evaluation progress and results display

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Clone the repository:
``bash
git clone https://github.com/your-username/llm-evaluation-tool.git
cd llm-evaluation-tool
``

2. Install dependencies:
``bash
npm install
``

3. Run the development server:
``bash
npm run dev
``

4. Open [http://localhost:3000](http://localhost:3000) in your browser

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

- **Framework**: Next.js 14 with App Router
- **UI Library**: shadcn/ui + Tailwind CSS
- **Language**: TypeScript
- **Icons**: Lucide React
- **Deployment**: Vercel

## 📁 Project Structure

```
├── app/
│   ├── layout.tsx          # Root layout
│   └── page.tsx            # Main page
├── components/
│   ├── ui/                 # shadcn/ui components
│   ├── file-upload.tsx     # Dataset upload component
│   ├── metrics-sidebar.tsx # Evaluation metrics sidebar
│   ├── results-table.tsx   # Results display table
│   └── score-bar.tsx       # Score visualization component
├── llm-evaluation-tool.tsx # Main application component
└── README.md
```

## 🚀 Deployment

This project is automatically deployed on Vercel. Any changes pushed to the main branch will trigger a new deployment.

**Live Demo**: [https://vercel.com/nihar-shahs-projects-60f0b993/v0-llm-evals](https://vercel.com/nihar-shahs-projects-60f0b993/v0-llm-evals)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🗺️ Roadmap

- [ ] Real LLM API integration
- [ ] Advanced evaluation metrics (BLEU, ROUGE, Semantic Similarity)
- [ ] Batch processing for large datasets
- [ ] Export functionality (CSV, JSON)
- [ ] Historical evaluation tracking
- [ ] Custom model configuration
- [ ] A/B testing between models

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [v0.dev](https://v0.dev) for rapid prototyping
- UI components from [shadcn/ui](https://ui.shadcn.com)
- Icons from [Lucide](https://lucide.dev)

---

*Automatically synced with your [v0.dev](https://v0.dev) deployments*
