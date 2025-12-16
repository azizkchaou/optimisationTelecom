
import sys
import os
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QApplication

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from views.charts_tab import ChartsTab

def verify_charts():
    app = QApplication(sys.argv)
    
    # Mock Data
    results = {
        'objective': 1000.0,
        'status': 'Optimal',
        'prices': {'PlanA': 10.0, 'PlanB': 20.0, 'PlanC': 50.0},
        'quantities': {
            ('PlanA', 'Seg1'): 10, ('PlanA', 'Seg2'): 20,
            ('PlanB', 'Seg1'): 5,  ('PlanB', 'Seg2'): 30,
            ('PlanC', 'Seg1'): 0,  ('PlanC', 'Seg2'): 5
        },
        'choices': {},
        'active': {},
        'total_usage': 500
    }
    
    print("Initializing ChartsTab...")
    try:
        charts_tab = ChartsTab()
        print("ChartsTab initialized.")
        
        print("Plotting Results...")
        charts_tab.plot_results(results)
        print("Plotting succesful!")
        
        # Check if 4 axes were created
        axes = charts_tab.figure.axes
        print(f"Number of axes created: {len(axes)}")
        if len(axes) != 4:
            print("ERROR: Expected 4 axes, found", len(axes))
            sys.exit(1)
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print("Verification Passed.")
    sys.exit(0)

if __name__ == "__main__":
    verify_charts()
