from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class ChartsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Matplotlib Figure
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.figure.patch.set_facecolor('#2b2b2b') # Match main window background
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

    def plot_results(self, results):
        """Plot Prices and Revenue share."""
        self.figure.clear()
        
        # Subplot 1: Prices per Plan
        ax1 = self.figure.add_subplot(211)
        ax1.set_facecolor('#323232') # Darker background for plot area
        
        plans = list(results['prices'].keys())
        prices = list(results['prices'].values())
        
        bars = ax1.bar(plans, prices, color='#64b5f6') # Light Blue
        ax1.set_title("Optimal Prices per Plan", color='white', pad=10)
        ax1.set_ylabel("Price ($)", color='white')
        ax1.tick_params(colors='white')
        
        # Grid and Spines
        ax1.grid(True, axis='y', linestyle='--', alpha=0.3, color='white')
        for spine in ax1.spines.values():
            spine.set_color('#505050')
            
        ax1.bar_label(bars, fmt='%.2f', color='white')

        # Subplot 2: Segment Usage (Total Qty) by Plan
        # Group by plan
        ax2 = self.figure.add_subplot(212)
        ax2.set_facecolor('#323232')
        
        # Aggregate quantity per plan
        plan_qty = {p: 0 for p in plans}
        for (f, s), q in results['quantities'].items():
            plan_qty[f] += q
            
        qtys = [plan_qty[p] for p in plans]
        
        bars2 = ax2.bar(plans, qtys, color='#81c784') # Light Green
        ax2.set_title("Total Quantity Sold per Plan", color='white', pad=10)
        ax2.set_ylabel("Units", color='white')
        ax2.tick_params(colors='white')
        
        ax2.grid(True, axis='y', linestyle='--', alpha=0.3, color='white')
        for spine in ax2.spines.values():
            spine.set_color('#505050')
            
        ax2.bar_label(bars2, fmt='%.0f', color='white')

        self.figure.tight_layout()
        self.canvas.draw()
