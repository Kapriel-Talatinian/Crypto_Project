<div align="center">

# 🌐 BlockchainFeeAnalyzer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-latest-green.svg)](https://flask.palletsprojects.com/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-latest-blue.svg)](https://tailwindcss.com/)

</div>

## 📌 Overview

BlockchainFeeAnalyzer is an open-source tool providing real-time analytics for blockchain transaction fees across Ethereum, Binance Smart Chain, and Solana networks. Built with optimization and efficiency in mind.

## 🚀 Features

### Core Functionality
- Real-time fee tracking across networks
- Cost analysis engine
- Customizable alert system

### Supported Networks
- Ethereum
- Binance Smart Chain
- Solana

## 🛠 Tech Stack

- **Backend**: Python/Flask
- **Database**: MySQL
- **Frontend**: TailwindCSS
- **Analytics**: Plotly
- **ML Engine**: scikit-learn

## 📋 Prerequisites

- Python 3.8+
- MySQL 8.0+
- MAMP or XAMPP (for local development)

## ⚡ Installation

```bash
# Clone repository
git clone https://github.com/Kapriel-Talatinian/Crypto_Project
cd Crypto_Project

# Create virtual environment
python -m venv venv

# Activate virtual environment
# For MacOS/Linux:
source venv/bin/activate
# For Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Database initialization
python -m src.database.init_db

# Start application
python app.py
```

## ⚙️ Configuration

Make sure your `config/config.env` contains:

```env
DB_HOST=localhost
DB_PORT=8889
DB_USER=root
DB_PASSWORD=root
DB_NAME=blockchain_fees
```

Note: For Windows users using XAMPP, typically use port 3306 instead of 8889.

## 🔄 Development Pipeline

- Automated transaction handling
- Wallet integration system 
- ML-powered predictions
- DeFi protocol integration

## 📬 Contact

- **Email**: kapriel.talatinian@gmail.com
- **LinkedIn**: Kapriel TALATINIAN

## 📜 License

MIT License © 2025 Kapriel TALATINIAN

---

<div align="center">
Made with ❤️ by Kapriel TALATINIAN
</div>
