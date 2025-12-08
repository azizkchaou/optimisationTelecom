from PyQt6.QtCore import QObject, pyqtSlot, QThread, pyqtSignal
from utils.data_generator import generate_demo_data
from models.optimization_model import PricingModel

class OptimizationWorker(QThread):
    finished = pyqtSignal(object) # Returns results dict or None
    error = pyqtSignal(str)

    def __init__(self, model, plans, segments, capacity):
        super().__init__()
        self.model = model
        self.plans = plans
        self.segments = segments
        self.capacity = capacity

    def run(self):
        try:
            results = self.model.build_and_solve(self.plans, self.segments, self.capacity)
            if results:
                self.finished.emit(results)
            else:
                self.error.emit("Optimization failed to find a solution (or Gurobi missing).")
        except Exception as e:
            self.error.emit(str(e))

class AppController(QObject):
    def __init__(self):
        super().__init__()
        self.model = PricingModel()
        self.view = None # Set later
        
        # Data State
        self.plans = []
        self.segments = []
        self.capacity = 0.0

    def set_view(self, main_window):
        self.view = main_window
        # Check solver on startup
        if self.model.check_solver():
            self.view.update_status("Ready. Gurobi Solver detected.")
        else:
            self.view.update_status("Warning: Gurobi not found. Optimization will fail.")

    def load_demo_data(self):
        self.plans, self.segments, self.capacity = generate_demo_data()
        self.view.input_tab.load_data(self.plans, self.segments, self.capacity)
        self.view.show_info("Demo data loaded! Click 'Run Optimization'.")

    def run_optimization(self):
        # Scrape data from View (SOURCE OF TRUTH)
        # We no longer rely on self.plans/self.segments being up to date from load_demo_data
        # because user might have edited them.
        self.plans, self.segments, self.capacity = self.view.input_tab.get_data()

        if not self.plans:
            self.view.show_error("No valid plan data found. Please add plans.")
            return

        self.view.update_status("Optimizing... please wait.")
        
        self.worker = OptimizationWorker(self.model, self.plans, self.segments, self.capacity)
        self.worker.finished.connect(self.on_optimization_finished)
        self.worker.error.connect(self.on_optimization_error)
        self.worker.start()

    @pyqtSlot(object)
    def on_optimization_finished(self, results):
        self.view.update_status("Optimization Complete.")
        
        # Update Results Tab
        self.view.results_tab.display_results(results, self.plans)
        
        # Update Charts Tab
        self.view.charts_tab.plot_results(results)
        
        self.view.tabs.setCurrentIndex(1) # Switch to results tab

    @pyqtSlot(str)
    def on_optimization_error(self, err_msg):
        self.view.update_status("Optimization Failed.")
        self.view.show_error(f"Error: {err_msg}")
