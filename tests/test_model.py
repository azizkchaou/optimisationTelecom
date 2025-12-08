import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.optimization_model import PricingModel
from utils.data_generator import generate_demo_data

def test_model():
    print("Initializing Model...")
    model = PricingModel()
    
    if not model.check_solver():
        print("SKIP: Gurobi not available.")
        return

    print("Generating Data...")
    plans, segments, capacity = generate_demo_data()
    
    print("Solving...")
    results = model.build_and_solve(plans, segments, capacity, verbose=False)
    
    if results:
        print("\nOptimization Successful!")
        print(f"Objective (Profit): {results['objective']:.2f}")
        print("Prices:")
        for f, p in results['prices'].items():
            print(f"  {f}: {p:.2f}")
        
        print("\nMarket Share (Segment Choices):")
        for s in [seg['id'] for seg in segments]:
            chosen = [f for f in results['prices'] if results['choices'][(f,s)] > 0.5]
            print(f"  {s}: {chosen[0] if chosen else 'None'}")
    else:
        print("Optimization Failed or Infeasible.")

if __name__ == "__main__":
    test_model()
