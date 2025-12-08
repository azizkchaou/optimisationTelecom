from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget, 
                             QLabel, QPushButton, QMessageBox, QStatusBar)
from PyQt6.QtCore import Qt
from views.input_tab import InputTab
from views.results_tab import ResultsTab
from views.charts_tab import ChartsTab

class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Telecom Price Optimizer")
        self.resize(1000, 700)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # 1. Inputs Tab
        self.input_tab = InputTab()
        self.tabs.addTab(self.input_tab, "Data Input")
        self.setup_input_connections() # Connect buttons inside input tab
        
        # 2. Results Tab
        self.results_tab = ResultsTab()
        self.tabs.addTab(self.results_tab, "Optimization Results")
        
        # 3. Charts Tab
        self.charts_tab = ChartsTab()
        self.tabs.addTab(self.charts_tab, "Visualization")
        
        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready. Gurobi status unknown.")

    def setup_input_connections(self):
        # We need to add buttons to Input Tab or access them if they are there?
        # In InputTab we defined layout but not the buttons 'Run' or 'Load'. 
        # Wait, the previous main_window skeleton had setup_input_tab which added buttons.
        # But now I replaced that with InputTab class which DOES NOT have buttons in my implementation above.
        # I should add the buttons to InputTab or keep them in MainWindow and put InputTab widget inside.
        # Let's add the control buttons to the InputTab from here or modify InputTab. 
        # Better: Modify InputTab to have the buttons, OR wrap InputTab in a widget that has buttons.
        # I'll stick to adding buttons *below* the InputTab in the MainWindow input area or use the InputTab layout.
        # Actually my InputTab implementation has 'load_data' but no buttons.
        # I will inject buttons into InputTab layout here for simplicity of "Controller connects view".
        
        # Add buttons to Input Tab's layout
        from PyQt6.QtWidgets import QPushButton, QHBoxLayout
        
        btn_layout = QHBoxLayout()
        
        self.btn_load = QPushButton("Load Demo Data")
        self.btn_load.clicked.connect(self.controller.load_demo_data)
        btn_layout.addWidget(self.btn_load)
        
        self.btn_run = QPushButton("Run Optimization")
        self.btn_run.clicked.connect(self.controller.run_optimization)
        btn_layout.addWidget(self.btn_run)
        
        self.input_tab.layout().addLayout(btn_layout)

    def update_status(self, message):
        self.status_bar.showMessage(message)

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)

    def show_info(self, message):
        QMessageBox.information(self, "Info", message)
