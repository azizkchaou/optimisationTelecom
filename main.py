import sys
from PyQt6.QtWidgets import QApplication
from views.main_window import MainWindow
from controllers.app_controller import AppController

def main():
    app = QApplication(sys.argv)
    
    # Initialize Controller
    controller = AppController()
    
    # Initialize View
    window = MainWindow(controller)
    controller.set_view(window)
    
    # Apply Stylesheet
    try:
        with open("assets/styles.qss", "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Warning: styles.qss not found.")

    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
