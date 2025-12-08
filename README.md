# Telecom Price Optimization Project

This project provides a desktop application to determine optimal pricing for telecom data plans using Mixed Integer Linear Programming (MILP) with Gurobi.

## Features
- **Optimization**: Maximizes profit considering demand elasticity, network capacity, and market segmentation.
- **Interactive UI**: Built with PyQt6 for easy data entry and control.
- **Visualization**: Integrated Matplotlib charts for demand and financial analysis.
- **Architecture**: Modular MVC design.

## Prerequisites
- **Python 3.8+**
- **Gurobi Optimizer**: Must be installed and licensed.
    - [Gurobi Installation Guide](https://www.gurobi.com/documentation/quickstart.html)

## Installation

1. Clone or extract the project.
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python main.py
   ```
2. **Load Data**: Click "Load Demo Data" in the Input tab to populate with sample plans and segments.
3. **Run Optimization**: Click "Run Optimization".
    - *Note*: If Gurobi is not detected, an error will be shown.
4. **View Results**: The application will automatically switch to the Results tab.
5. **Charts**: Explore the Visualization tab for graphical insights.

## Project Structure
- `main.py`: Application entry point.
- `models/`: Gurobi optimization logic (`optimization_model.py`).
- `views/`: PyQt UI components (`main_window.py`, tabs).
- `controllers/`: Logic connecting UI and Model (`app_controller.py`).
- `utils/`: Helper functions and data generators.
