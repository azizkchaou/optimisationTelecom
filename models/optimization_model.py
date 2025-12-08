import logging
import logging

try:
    import gurobipy as gp
    from gurobipy import GRB
    GUROBI_AVAILABLE = True
except ImportError:
    gp = None
    GRB = None
    GUROBI_AVAILABLE = False

class PricingModel:
    """
    Gurobi optimization model for Telecom Plan Pricing using PLNE/MILP.
    """

    def __init__(self):
        self.model = None
        self.logger = logging.getLogger(__name__)

    def check_solver(self):
        """Check if Gurobi is available and licensed."""
        if not GUROBI_AVAILABLE:
            self.logger.error("Gurobi library not found.")
            return False
            
        try:
            m = gp.Model()
            m.dispose()
            return True
        except gp.GurobiError as e:
            self.logger.error(f"Gurobi initialization failed: {e}")
            return False

    def build_and_solve(self, plans_data, segments_data, network_capacity, cannibalization_margin=5.0, verbose=True):
        """
        Builds the MILP model and solves it.

        Args:
            plans_data (list of dict): List of plans with 'id', 'name', 'data_limit', 'cost'.
            segments_data (list of dict): List of segments with 'id', 'name', 'size', 
                                          and demand params ('a', 'b') for each plan.
                                          e.g. {'id': 'S1', 'size': 1000, 'params': {plan_id: {'a': 100, 'b': 2}}}
            network_capacity (float): Total network capacity (e.g. Total GB).
            cannibalization_margin (float): Min price difference between ordered plans.
            verbose (bool): Whether to print Gurobi logs.

        Returns:
            dict: Optimization results or None if failed.
        """
        if not GUROBI_AVAILABLE:
            self.logger.error("Attempted to solve without Gurobi.")
            return None

        try:
            # Sort plans by data_limit to ensure price-ordering constraints (p_1 <= p_2 ...) make sense
            # i.e., Plan with more data should be more expensive
            plans_data = sorted(plans_data, key=lambda x: x['data_limit'])

            # Create Model
            m = gp.Model("TelecomPricing")
            m.setParam('OutputFlag', 1 if verbose else 0)  # Enable logging based on verbose flag

            # Indices
            F = [p['id'] for p in plans_data]         # Plans
            S = [s['id'] for s in segments_data]      # Segments
            
            # Mappings for easy access
            plan_map = {p['id']: p for p in plans_data}
            seg_map = {s['id']: s for s in segments_data}

            # --- VARIABLES ---
            
            # Price for each plan f
            # Bounds: p >= cost (to ensure non-negative margin per unit, roughly) or just >= 0
            p = m.addVars(F, lb=0.0, vtype=GRB.CONTINUOUS, name="price")
            
            # Choice of segment s for plan f (Binary) -> x[f,s] = 1 if segment s chooses plan f
            x = m.addVars(F, S, vtype=GRB.BINARY, name="x")
            
            # Activation of plan f (Binary) -> y[f] = 1 if plan offered
            y = m.addVars(F, vtype=GRB.BINARY, name="y")

            # Auxiliary variable for Quantity q[f,s]
            # Since q depends on p and x, and demand is linear q = a - bp
            # usage: total_q[f,s] = x[f,s] * (a - b * p[f])
            # This is non-linear (x * p). Linearization required.
            # Let real_q[f,s] be the actual quantity.
            # If x=1, real_q = a - b*p. If x=0, real_q = 0.
            # Linearization using Big-M:
            # real_q <= M * x
            # real_q <= a - b*p + M(1-x)
            # real_q >= a - b*p - M(1-x)
            # real_q >= 0
            # BUT: "Segment chooses plain" implies it buys it. 
            # Simplified: q[f,s] = size_segment * (prob of purchase or just quantity per user?)
            # Prompt says: q_f_s = (a - b*p) * x_f_s
            # We assume q is "quantity per user in segment" or "total quantity for segment"?
            # Let's assume input a, b refer to TOTAL demand of segment if price is p.
            
            q_vars = m.addVars(F, S, lb=0.0, vtype=GRB.CONTINUOUS, name="q")
            
            # Big-M for price linearization (assuming max reasonable price e.g. 200)
            M_price = 1000.0 
            M_q = 1000000.0 # Max possible demand

            # --- CONSTRAINTS ---

            for f in F:
                for s in S:
                    param = seg_map[s]['params'].get(f, {'a': 0, 'b': 0})
                    a_val = param['a']
                    b_val = param['b']
                    
                    # 1. Linearization of q[f,s] = x[f,s] * (a - b*p[f])
                    # If x=0 => q=0
                    m.addConstr(q_vars[f,s] <= M_q * x[f,s], name=f"lin_q_zero_{f}_{s}")
                    
                    # If x=1 => q = a - b*p
                    # q <= a - b*p + M(1-x)
                    m.addConstr(q_vars[f,s] <= a_val - b_val * p[f] + M_q * (1 - x[f,s]), name=f"lin_q_high_{f}_{s}")
                    # q >= a - b*p - M(1-x)
                    m.addConstr(q_vars[f,s] >= a_val - b_val * p[f] - M_q * (1 - x[f,s]), name=f"lin_q_low_{f}_{s}")
                
                # Link activation y to x: If no segment picks f, is y 0? 
                # Or rather: if y=0, no segment can pick f.
                m.addConstr(gp.quicksum(x[f, s] for s in S) <= len(S) * y[f], name=f"activation_{f}")


            # 2. Single Choice per Segment
            # Each segment must choose exactly one plan (or none? Prompt says "Σ x = 1")
            for s in S:
                m.addConstr(gp.quicksum(x[f, s] for f in F) == 1, name=f"single_choice_{s}")

            # 3. Price Ordering & Cannibalization
            # p_1 <= p_2 <= ... 
            # p_{f+1} >= p_f + margin (only if both active? prompt implies strict structure)
            # Assuming F is ordered list of IDs.
            for i in range(len(F) - 1):
                f_curr = F[i]
                f_next = F[i+1]
                
                # Basic ordering: p_next >= p_curr + margin
                # If we consider y (activation), maybe we don't enforce if inactive? 
                # For simplicity based on prompt "p_f+1 >= p_f + margin_min", we enforce it globally for the structure.
                m.addConstr(p[f_next] >= p[f_curr] + cannibalization_margin, name=f"order_{f_curr}_{f_next}")

            # 4. Network Capacity
            # Σ_f Σ_s q_f_s * data_limit_f <= Cap
            total_data_usage = gp.quicksum(
                q_vars[f, s] * plan_map[f]['data_limit'] 
                for f in F for s in S
            )
            m.addConstr(total_data_usage <= network_capacity, name="capacity_constr")

            # --- OBJECTIVE ---
            # Max Profit = Σ (p_f - cost_f) * q_{fs}
            # Term: p[f] * q[f,s] is Quadratic (Continuous * Continuous) since q depends on p.
            # But wait, q is already (a-bp)x. 
            # x is binary. p is continuous.
            # Revenue = p * (a-bp)*x = (ap - bp^2)x = a*p*x - b*p^2*x.
            # This is cubic if we substituted, or quadratic if we keep q.
            # Gurobi handles MIQP (Mixed Integer Quadratic Programming).
            # Let's write objective using q and p directly.
            # Profit = Σ (p[f] * q[f,s] - c[f] * q[f,s])
            # p[f] * q[f,s] is Non-Convex quadratic? 
            # Actually, q ~ (a - bp). Revenue ~ p(a-bp) = ap - bp^2. This is concave quadratic (good for max).
            # But we have 'x' multiplied.
            # Let's introduce revenue variable r[f,s] to linearize or use MIQP capability.
            # user demanded "PL / PLNE / PLM". Gurobi handles Non-Convex MIQP, but standard MIQP is better.
            # (ap - bp^2) is concave. Multiplication by binary x is fine for Gurobi.
            # We will just write the expression directly.
            
            obj_expr = gp.quicksum(
                (p[f] - plan_map[f]['cost']) * q_vars[f,s]
                for f in F for s in S
            )

            m.setObjective(obj_expr, GRB.MAXIMIZE)
            
            # Solve
            m.optimize()

            if m.status == GRB.OPTIMAL:
                results = {
                    'status': 'Optimal',
                    'objective': m.objVal,
                    'prices': {f: p[f].X for f in F},
                    'quantities': {(f,s): q_vars[f,s].X for f in F for s in S},
                    'choices': {(f,s): x[f,s].X for f in F for s in S},
                    'active': {f: y[f].X for f in F},
                    'total_usage': total_data_usage.getValue()
                }
                return results
            else:
                self.logger.warning(f"Optimization ended with status {m.status}")
                return None

        except gp.GurobiError as e:
            self.logger.error(f"Gurobi Error: {e}")
            return None
        except Exception as e:
            self.logger.exception("Unexpected error in optimization")
            return None
