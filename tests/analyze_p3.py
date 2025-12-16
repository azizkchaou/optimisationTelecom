
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.optimization_model import PricingModel
from utils.data_generator import generate_demo_data

def analyze_p3():
    model = PricingModel()
    if not model.check_solver():
        print("Gurobi not found.")
        return

    plans, segments, capacity = generate_demo_data()
    print("Running Optimization...")
    results = model.build_and_solve(plans, segments, capacity, verbose=False)
    
    if not results:
        print("Optimization failed.")
        return

    print("\n--- RESULTS ANALYSIS ---")
    prices = results['prices']
    print("Optimal Prices:")
    for pid, p in prices.items():
        print(f"  {pid}: ${p:.2f}")

    print("\nSegment Choices:")
    for s in segments:
        sid = s['id']
        # Find which plan this segment chose
        choice = None
        for pid in plans:
            if results['choices'].get((pid['id'], sid), 0) > 0.5:
                choice = pid['id']
                break
        
        print(f"  Segment {sid} chose: {choice}")
        
        # Calculate theoretical profit for P3 for this segment at current P3 price
        # vs Chosen Plan
        if choice and choice != 'P3':
            p3_price = prices['P3']
            chosen_price = prices[choice]
            
            # P3 calc
            p3_params = s['params'].get('P3', {'a':0, 'b':0})
            p3_q = p3_params['a'] - p3_params['b'] * p3_price
            p3_cost = next(p for p in plans if p['id']=='P3')['cost']
            p3_profit = p3_q * (p3_price - p3_cost)
            
            # Chosen calc
            c_params = s['params'].get(choice, {'a':0, 'b':0})
            c_q = c_params['a'] - c_params['b'] * chosen_price
            c_cost = next(p for p in plans if p['id']==choice)['cost']
            c_profit = c_q * (chosen_price - c_cost)
            
            print(f"    - Profit if P3 (${p3_price:.2f}): {p3_profit:.2f}")
            print(f"    - Profit if {choice} (${chosen_price:.2f}): {c_profit:.2f}")
            if p3_profit < c_profit:
                print("    -> P3 is less profitable.")

if __name__ == "__main__":
    analyze_p3()
