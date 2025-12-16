from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import matplotlib.pyplot as plt

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
        """Plot Grid of 4 Charts."""
        self.figure.clear()
        
        # Data Preparation
        plans = sorted(list(results['prices'].keys()))
        prices = [results['prices'][p] for p in plans]
        
        # 1. Prices per Plan (Top-Left)
        ax1 = self.figure.add_subplot(221)
        ax1.set_facecolor('#323232')
        bars1 = ax1.bar(plans, prices, color='#64b5f6') 
        ax1.set_title("Optimal Prices per Plan", color='white', pad=10)
        ax1.set_ylabel("Price ($)", color='white')
        ax1.tick_params(colors='white')
        ax1.grid(True, axis='y', linestyle='--', alpha=0.3, color='white')
        for spine in ax1.spines.values(): spine.set_color('#505050')
        ax1.bar_label(bars1, fmt='%.2f', color='white')

        # 2. Revenue per Plan (Top-Right)
        # Calculate revenue per plan
        plan_revenue = {p: 0 for p in plans}
        plan_qty = {p: 0 for p in plans}
        
        for (f, S), q in results['quantities'].items():
            if q > 0:
                p_val = results['prices'][f]
                # Rev = q * price
                rev = q * p_val
                plan_revenue[f] += rev
                plan_qty[f] += q
        
        revenues = [plan_revenue[p] for p in plans]
        
        ax2 = self.figure.add_subplot(222)
        ax2.set_facecolor('#323232')
        bars2 = ax2.bar(plans, revenues, color='#81c784')
        ax2.set_title("Total Revenue per Plan", color='white', pad=10)
        ax2.set_ylabel("Revenue ($)", color='white')
        ax2.tick_params(colors='white')
        ax2.grid(True, axis='y', linestyle='--', alpha=0.3, color='white')
        for spine in ax2.spines.values(): spine.set_color('#505050')
        # Format revenue labels K/M if large
        labels2 = [f"${v/1000:.1f}k" if v > 1000 else f"${v:.0f}" for v in revenues]
        ax2.bar_label(bars2, labels=labels2, color='white')

        # 3. Quantity by Segment (Bottom-Left)
        # Stacked bar: X=Segment, Stack=Plan
        # Get all segments
        all_segments = sorted(list(set(k[1] for k in results['quantities'].keys())))
        
        ax3 = self.figure.add_subplot(223)
        ax3.set_facecolor('#323232')
        
        bottom = np.zeros(len(all_segments))
        colors = ['#ff8a65', '#ffd54f', '#4db6ac', '#ba68c8', '#90a4ae'] # Palette
        
        for i, p in enumerate(plans):
            # Quantities for this plan across all segments
            qs = []
            for s in all_segments:
                qs.append(results['quantities'].get((p, s), 0))
            
            c = colors[i % len(colors)]
            ax3.bar(all_segments, qs, bottom=bottom, label=p, color=c)
            bottom += np.array(qs)
            
        ax3.set_title("Quantity Sold by Segment", color='white', pad=10)
        ax3.set_ylabel("Quantity", color='white')
        ax3.tick_params(colors='white')
        # Rotate segment labels if many
        plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')
        ax3.grid(True, axis='y', linestyle='--', alpha=0.3, color='white')
        for spine in ax3.spines.values(): spine.set_color('#505050')
        ax3.legend(facecolor='#323232', labelcolor='white', edgecolor='#505050', fontsize='small')

        # 4. Revenue Share by Segment (Bottom-Right)
        # Pie chart
        segment_revenue = {s: 0 for s in all_segments}
        for (f, s), q in results['quantities'].items():
            if q > 0:
                rev = q * results['prices'][f]
                segment_revenue[s] += rev
        
        # Filter zero revenue segments to avoid clutter
        pie_labels = []
        pie_data = []
        for s in all_segments:
            if segment_revenue[s] > 1: # Threshold to show
                pie_labels.append(s)
                pie_data.append(segment_revenue[s])
        
        ax4 = self.figure.add_subplot(224)
        ax4.set_facecolor('#323232') # Pie chart ignores this mostly but good practice
        
        if pie_data:
            wedges, texts, autotexts = ax4.pie(pie_data, labels=pie_labels, autopct='%1.1f%%',
                                               textprops={'color': 'white'},
                                               colors=colors,
                                               startangle=90)
            ax4.set_title("Revenue Share by Segment", color='white', pad=10)
        else:
            ax4.text(0.5, 0.5, "No Revenue Data", color='white', ha='center', va='center')

        self.figure.tight_layout()
        self.canvas.draw()
