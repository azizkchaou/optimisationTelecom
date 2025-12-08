from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QLabel, QHeaderView, QTextEdit, QSplitter)
from PyQt6.QtCore import Qt

class ResultsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Summary Label
        self.summary_label = QLabel("Optimization Status: Pending")
        self.summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.summary_label.setStyleSheet("""
            QLabel {
                background-color: #323232; 
                border-radius: 8px; 
                padding: 15px; 
                font-size: 18px; 
                font-weight: bold; 
                color: #ffca28; /* Amber accent */
                border: 1px solid #505050;
            }
        """)
        layout.addWidget(self.summary_label)

        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # 1. Optimal Prices Table
        self.prices_table = QTableWidget()
        self.prices_table.setColumnCount(3)
        self.prices_table.setHorizontalHeaderLabels(["Plan ID", "Recommended Price ($)", "Active?"])
        self.prices_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        splitter.addWidget(self.prices_table)
        
        # 2. Market Share / Quantity Table
        self.qty_table = QTableWidget()
        self.qty_table.setColumnCount(4)
        self.qty_table.setHorizontalHeaderLabels(["Plan", "Segment", "Quantity/User", "Total Segment Rev"])
        self.qty_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        splitter.addWidget(self.qty_table)

        # 3. Log Output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("Solver logs will appear here...")
        splitter.addWidget(self.log_output)

        layout.addWidget(splitter)

    def display_results(self, results, plans):
        """Display results dictionary."""
        profit = results['objective']
        status = results['status']
        self.summary_label.setText(f"Status: {status} | Total Profit: ${profit:,.2f}")
        
        # Prices
        prices = results['prices']
        active = results['active']
        self.prices_table.setRowCount(len(prices))
        for i, (pid, price) in enumerate(prices.items()):
            self.prices_table.setItem(i, 0, QTableWidgetItem(pid))
            self.prices_table.setItem(i, 1, QTableWidgetItem(f"{price:.2f}"))
            is_active = active.get(pid, 1.0) > 0.5
            self.prices_table.setItem(i, 2, QTableWidgetItem("Yes" if is_active else "No"))

        # Detailed Quantities (Simplified view)
        # We need plan list to map names if desired, but results uses IDs
        # Flatten entries
        rows = []
        for (f,s), q in results['quantities'].items():
            if q > 0.01: # Filter small values
                p_price = prices[f]
                rev = q * p_price
                rows.append((f, s, q, rev))
        
        self.qty_table.setRowCount(len(rows))
        for i, (f, s, q, rev) in enumerate(rows):
            self.qty_table.setItem(i, 0, QTableWidgetItem(str(f)))
            self.qty_table.setItem(i, 1, QTableWidgetItem(str(s)))
            self.qty_table.setItem(i, 2, QTableWidgetItem(f"{q:.2f}"))
            self.qty_table.setItem(i, 3, QTableWidgetItem(f"${rev:,.2f}"))
