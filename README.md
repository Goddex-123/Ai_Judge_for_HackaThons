# 🏆 AI Hackathon Judge

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Click_Here-brightgreen?style=for-the-badge)](https://ai-judge-for-hackathons.streamlit.app/)

> **🎯 Try it now!** Click the **Live Demo** badge above to use the app instantly - no installation required!

An AI-powered hackathon project evaluation system that scores projects objectively using **NLP analysis**, **weighted scoring**, and **judge-style feedback**.

## 🌟 Features

### ⚖️ Weighted Scoring System

| Criteria                    | Weight |
| --------------------------- | ------ |
| 💡 Innovation & Originality | 25%    |
| ⚙️ Technical Depth          | 20%    |
| 🎯 Problem Relevance        | 15%    |
| 🔧 Feasibility              | 15%    |
| 📈 Scalability              | 10%    |
| 🎨 UI/UX & Presentation     | 10%    |
| 🌍 Real-World Impact        | 5%     |

### 🔍 Intelligent Detection

- **Buzzword Detector**: Flags "revolutionary", "disruptive", "game-changing" without substance
- **Vagueness Analyzer**: Penalizes "etc.", "various", "multiple" padding
- **Overclaim Detector**: Catches "first ever", "will change the world" without evidence
- **AI-Generated Content Detector**: Identifies template writing patterns

### 📊 Verdicts

| Score Range | Verdict                |
| ----------- | ---------------------- |
| 85-100      | 🏆 Winner Material     |
| 70-84       | ✅ Strong Contender    |
| 50-69       | ⚠️ Average             |
| 0-49        | ❌ Not Hackathon Ready |

### 🏅 Leaderboard

- Automatic ranking of multiple projects
- Top 3 highlighting with medals (🥇🥈🥉)
- Winner explanation — _why_ #1 beat the competition

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/Goddex-123/Ai_Judge_for_HackaThons.git
cd Ai_Judge_for_HackaThons
pip install -r requirements.txt
```

### Run the App

```bash
streamlit run app.py
```

Open browser: **http://localhost:8501**

## 📁 Project Structure

```
Ai_Judge_for_HackaThons/
├── app.py                      # Streamlit dashboard
├── config/
│   └── settings.py             # Scoring weights & keywords
├── models/
│   ├── project.py              # Data models
│   ├── scoring_engine.py       # Core scoring logic
│   └── feedback_generator.py   # Judge-style feedback
├── utils/
│   ├── nlp_analyzer.py         # NLP analysis
│   ├── validators.py           # Input validation
│   └── leaderboard.py          # Ranking system
├── data/
│   └── sample_projects.json    # Example submissions
└── assets/
    └── styles.css              # Custom styling
```

## 🧪 Sample Output

```
🎯 FINAL SCORE: 87/100
🏆 Verdict: Winner Material

📊 CATEGORY SCORES:
   💡 Innovation: 92/100
   ⚙️ Technical Depth: 89/100
   🎯 Problem Relevance: 85/100

💪 STRENGTHS:
   • Outstanding innovation with hybrid approach
   • Strong technical implementation
   • Working demo available

📜 VERDICT: "Exceptional work demonstrating creativity and technical skill."
```

## ⚠️ Disclaimer

> This tool provides **objective scoring** based on text analysis.
> Final hackathon decisions should combine AI scoring with human judgment.

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

<p align="center">
  Made with ❤️ for hackathon participants and organizers
</p>
