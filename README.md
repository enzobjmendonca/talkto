# TalkTo - Historical Character AI Conversations

TalkTo is an innovative AI-powered platform that enables users to have meaningful conversations with historical figures through advanced AI agents. Each character is designed as a digital twin that thinks and behaves authentically as their historical counterpart.

## 🎯 Project Vision

The main idea behind TalkTo is to leverage AI technology to create immersive, educational, and engaging conversations with historical characters - both famous figures and common people from different eras. The AI agents are designed to truly embody their characters, providing authentic perspectives and insights from their time period.

## ✨ Key Features

- **Authentic Character AI**: Each historical figure is powered by advanced AI that thinks and responds as their real counterpart would
- **Diverse Historical Figures**: From famous leaders and artists to common people from various time periods
- **Educational Experience**: Learn history through interactive conversations
- **Immersive Interactions**: Feel like you're truly talking to someone from the past
- **Contextual Awareness**: Characters understand their historical context and limitations

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/talkto.git
cd talkto
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

6. Run the application:
```bash
python main.py
```

## 📁 Project Structure

```
talkto/
├── src/
│   ├── characters/          # Historical character definitions
│   ├── ai_engine/          # AI conversation engine
│   ├── api/                # API endpoints
│   ├── database/           # Database models and operations
│   └── utils/              # Utility functions
├── tests/                  # Test files
├── docs/                   # Documentation
├── data/                   # Character data and resources
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── main.py                # Application entry point
└── README.md              # This file
```

## 🎭 Available Characters

The platform includes a diverse range of historical figures:

- **Political Leaders**: Abraham Lincoln, Winston Churchill, Cleopatra
- **Scientists & Inventors**: Albert Einstein, Leonardo da Vinci, Marie Curie
- **Artists & Writers**: William Shakespeare, Vincent van Gogh, Jane Austen
- **Common People**: Medieval peasants, Renaissance merchants, Victorian servants

## 🔧 Configuration

Create a `.env` file with the following variables:

```env
# AI API Configuration
OPENAI_API_KEY=your_openai_api_key
AI_MODEL=gpt-4

# Database Configuration
DATABASE_URL=sqlite:///talkto.db

# Application Settings
DEBUG=True
PORT=8000
```

## 🧪 Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black src/
isort src/
```

### Type Checking
```bash
mypy src/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Historical research and character development
- AI/ML community for inspiration and tools
- Open source contributors

## 📞 Support

If you have any questions or need help, please open an issue on GitHub or contact the development team.

---

**Note**: This project is for educational and entertainment purposes. Historical conversations are AI-generated and should not be considered as actual historical records.
