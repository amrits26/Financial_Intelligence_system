# 🚀 Financial Intelligence System

## Advanced Multi-Agent AI Platform for Financial Analysis & Portfolio Management

A comprehensive, production-ready financial intelligence system powered by multi-agent AI architecture, featuring real-time market analysis, sentiment evaluation, risk management, and portfolio optimization.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

The Financial Intelligence System is a multi-agent AI platform that provides institutional-grade financial analysis through coordinated specialized agents. Built with Flask and powered by both local (Ollama) and cloud (Gemini) LLMs, it's designed for academic research, thesis projects, and commercial deployment.

### Key Highlights

- **10 Specialized AI Agents** working in coordination
- **Real-time Market Data** from Yahoo Finance & Alpha Vantage
- **Sentiment Analysis** from news and social media
- **Advanced Risk Management** with VaR, stress testing
- **Portfolio Optimization** using Modern Portfolio Theory
- **Professional Web Interface** with Bootstrap 5
- **Complete REST API** for programmatic access
- **University Cluster Ready** - No Docker required

---

## ✨ Features

### 1. Multi-Agent Analysis
- Market Data Agent - Real-time price and fundamental data
- Sentiment Agent - Financial text sentiment analysis
- Risk Agent - Comprehensive risk assessment
- Master Orchestrator - Coordinates all agents

### 2. Market Intelligence
- Live stock quotes and historical data
- Company fundamentals (P/E, ROE, Market Cap)
- Technical indicators (RSI, MACD, Bollinger Bands)
- News aggregation from multiple sources

### 3. Risk Management
- Value at Risk (VaR) calculation
- Volatility analysis
- Maximum drawdown tracking
- Risk level classification

### 4. LLM Integration
- Dual support: Ollama (local) + Gemini (cloud)
- Automatic fallback mechanism
- AI-generated investment summaries

### 5. Web Interface
- Professional dashboard
- Interactive stock analysis
- Portfolio management
- Risk monitoring

---

## 🏗️ System Architecture

### Three-Tier Architecture

```
┌─────────────────────────────────────┐
│   Tier 1: Orchestration Layer       │
│   - Master Orchestrator             │
│   - Workflow Management             │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│   Tier 2: Intelligence Layer        │
│   - Market Data Agent               │
│   - Sentiment Agent                 │
│   - Risk Agent                      │
│   - Additional Agents               │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│   Tier 3: Infrastructure Layer      │
│   - SQLite Database                 │
│   - LLM Manager                     │
│   - Data Fetcher                    │
└─────────────────────────────────────┘
```

### Data Flow

```
User Input → Orchestrator → Agents → Database → Results → Web UI / API
```

---

## 💿 Installation

### Prerequisites

- Python 3.8+ (3.10+ recommended)
- pip (latest version)
- Git
- Ollama (optional, for local LLM)

### Quick Start

```bash
# Clone repository
git clone https://github.com/your-repo/financial-intelligence-system.git
cd financial-intelligence-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Initialize database
python -c "from core.database import Database; db = Database(); db.initialize()"

# Run application
python app.py
```

Visit: **http://localhost:5000**

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file:

```bash
# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
USE_GEMINI=False
GEMINI_API_KEY=

# Financial Data APIs
ALPHA_VANTAGE_API_KEY=your_key_here
FINNHUB_API_KEY=your_key_here

# Flask
SECRET_KEY=your-secret-key
DEBUG=True
HOST=0.0.0.0
PORT=5000

# Database
DATABASE_URL=sqlite:///financial_data.db
```

### Required API Keys

1. **Alpha Vantage** (Free): https://www.alphavantage.co/support/#api-key
2. **Finnhub** (Optional): https://finnhub.io/register
3. **Gemini** (Optional): https://ai.google.dev

### Ollama Setup

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull model
ollama pull llama3.1:8b

# Start service
ollama serve
```

---

## 🚀 Usage

### Web Interface

1. **Dashboard**: Navigate to http://localhost:5000
2. **Analyze Stock**: Enter symbol (e.g., AAPL) and click Analyze
3. **View Results**: Review multi-agent analysis results

### Python API

```python
from agents.orchestrator import MasterOrchestrator

orchestrator = MasterOrchestrator()
result = orchestrator.analyze_stock('AAPL', period='1y')

print(f"Recommendation: {result['recommendation']}")
print(f"Confidence: {result['confidence']:.2%}")
```

### REST API

```bash
# Analyze stock
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "period": "1y"}'

# System health
curl http://localhost:5000/api/health
```

---

## 📡 API Documentation

### Endpoints

#### POST /api/analyze
Comprehensive stock analysis

**Request:**
```json
{
  "symbol": "AAPL",
  "period": "1y"
}
```

**Response:**
```json
{
  "symbol": "AAPL",
  "recommendation": "buy",
  "confidence": 0.85,
  "agent_results": {...}
}
```

#### GET /api/health
System health check

**Response:**
```json
{
  "status": "healthy",
  "health": {...}
}
```

---

## 📂 Project Structure

```
financial_intelligence_system/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── README.md                  # This file
│
├── config/
│   ├── __init__.py
│   └── settings.py            # Configuration management
│
├── core/
│   ├── __init__.py
│   ├── llm_manager.py         # LLM integration
│   ├── database.py            # Database operations
│   └── state_manager.py       # Workflow state
│
├── agents/
│   ├── __init__.py
│   ├── base_agent.py          # Agent base class
│   ├── orchestrator.py        # Master orchestrator
│   ├── market_data_agent.py   # Market data
│   ├── sentiment_agent.py     # Sentiment analysis
│   ├── risk_agent.py          # Risk management
│   └── [additional agents]
│
├── modules/
│   ├── __init__.py
│   ├── data_fetcher.py        # Data fetching
│   ├── analyzers.py           # Analysis functions
│   ├── risk_calculator.py     # Risk calculations
│   └── portfolio_manager.py   # Portfolio management
│
├── utils/
│   ├── __init__.py
│   ├── helpers.py             # Helper functions
│   ├── validators.py          # Input validation
│   └── logging_config.py      # Logging setup
│
├── api/
│   ├── __init__.py
│   ├── routes.py              # API routes
│   └── schemas.py             # Data schemas
│
├── templates/
│   ├── base.html              # Base template
│   ├── index.html             # Dashboard
│   ├── analyze.html           # Analysis page
│   ├── portfolio.html         # Portfolio page
│   └── risk_dashboard.html    # Risk page
│
├── static/
│   ├── css/main.css           # Styling
│   └── js/app.js              # JavaScript
│
├── tests/
│   ├── __init__.py
│   └── test_agents.py         # Unit tests
│
├── data/
│   ├── models/                # ML models
│   └── cache/                 # Cached data
│
└── logs/                      # Application logs
```

---

## 🧪 Testing

### Run Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_agents.py

# With coverage
python -m pytest --cov=agents tests/
```

### Manual Testing

```bash
# Test market data
python -c "from agents.market_data_agent import MarketDataAgent; agent = MarketDataAgent(); print(agent.run({'symbol': 'AAPL'}))"

# Test orchestrator
python -c "from agents.orchestrator import MasterOrchestrator; o = MasterOrchestrator(); print(o.analyze_stock('AAPL'))"
```

---

## 🌐 Deployment

### Local Development
```bash
python app.py
```

### University Cluster (No Docker)
```bash
# Load Python
module load python/3.10

# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run
export PORT=8080
python app.py
```

### Production (Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 🐛 Troubleshooting

### Issue: Cannot connect to Ollama
**Solution:**
```bash
ollama serve
ollama pull llama3.1:8b
```

### Issue: API rate limit exceeded
**Solution:**
- Enable caching in .env
- Use premium API tier
- Reduce request frequency

### Issue: Module not found
**Solution:**
```bash
pip install -r requirements.txt --upgrade
```

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

### Areas for Contribution
- Additional agents
- More data sources
- Enhanced ML models
- UI improvements
- Documentation
- Bug fixes

---

## 📄 License

MIT License - See LICENSE file for details

---

## 📧 Support

- **Issues**: GitHub Issues
- **Documentation**: This README + code comments
- **Email**: support@financial-intelligence.ai

---

## 🎓 Academic Use

Perfect for:
- Master's thesis projects
- PhD research
- Capstone projects
- Financial AI courses
- Research papers

### Citation
```bibtex
@software{financial_intelligence_2025,
  title={Financial Intelligence System},
  author={Your Name},
  year={2025},
  institution={University of Massachusetts Dartmouth}
}
```

---

## ⚠️ Disclaimer

This software is for **educational and research purposes only**. Not financial advice. Consult professional financial advisors before making investment decisions.

---

## 🎉 Quick Reference

### Essential Commands
```bash
pip install -r requirements.txt
cp .env.example .env
python app.py
```

### Essential URLs
- Dashboard: http://localhost:5000
- Analysis: http://localhost:5000/analyze
- API Health: http://localhost:5000/api/health

---

**Built with ❤️ for the financial technology community**

**Status:** ✅ Production Ready | **Version:** 1.0.0 | **Last Updated:** October 2025
