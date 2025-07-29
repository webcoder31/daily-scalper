# Daily Scalper

A user-friendly Python application for testing, evaluating, and saving cryptocurrency trading strategies.

---

## Overview

Daily Scalper lets you backtest and compare crypto trading strategies with an interactive menu and clear visualizations. No coding required for basic use.

---

## Features

- Test built-in trading strategies on historical crypto data
- Compare strategy performance
- Interactive charts and performance metrics
- Automatic saving of profitable strategies
- Simple, menu-driven interface

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Steps

1. **Clone the project**
   ```bash
   git clone <your-repo-url>
   cd daily-scalper
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate     # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Test the installation**
   ```bash
   python test_setup.py
   ```
   If all tests pass, you're ready to go!

---

## Usage

### Quick Start

```bash
source venv/bin/activate
python main.py
```

### Menu Options

1. Test a single strategy configuration
2. Compare different strategy configurations
3. View saved profitable strategies
4. View application settings
5. Exit application

### Available Strategies

- **Simple Moving Average Crossover (SMA)**
- **Relative Strength Index (RSI) Threshold**
- **Bollinger Bands**

Each strategy can be customized via the menu.

---

## Configuration

All settings (default capital, commission, cache, etc.) can be changed in [`config.py`](config.py).  
To modify: edit the file and restart the app.

---

## Results & Visualizations

- Results and charts are saved in the `results/` directory.
- Interactive charts open in your browser.
- Profitable strategies are saved automatically.

---

## Troubleshooting

- **Dependency error:**  
  Update pip and reinstall requirements:
  ```bash
  pip install --upgrade pip
  pip install -r requirements.txt
  ```

- **Data download error:**  
  Check your internet connection and use correct symbol format (e.g., 'BTC-USD').

- **"Module not found" error:**  
  Ensure your virtual environment is activated.

- **Slow performance:**  
  Use a shorter data period or enable cache.

---

## More Information

For technical details, developer documentation, and instructions on adding new strategies, see [`TECHNICAL_DOCUMENTATION.md`](TECHNICAL_DOCUMENTATION.md).

---

## License

MIT License. See LICENSE file for details.
