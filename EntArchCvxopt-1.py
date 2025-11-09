import numpy as np
from cvxopt import matrix, solvers
import matplotlib.pyplot as plt
import pandas as pd


class ModelSelectionOptimizer:
    """
    Optimizer for pretrained model selection problem using CVXOPT.

    Problem:
    - 4 pretrained models with different API costs
    - Each model contributes equally to both agent groups
    - Must satisfy minimum requirements for both agent groups
    - Minimize total daily API costs
    """

    def __init__(self):
        # Model data from the table
        self.models = {
            'Model 1': {'cost': 50, 'agent_a': 2, 'agent_b': 2},
            'Model 2': {'cost': 60, 'agent_a': 2, 'agent_b': 2},
            'Model 3': {'cost': 58, 'agent_a': 2, 'agent_b': 2},
            'Model 4': {'cost': 63, 'agent_a': 2, 'agent_b': 2}
        }

        # Requirements
        self.min_monthly_budget = 1000
        self.min_agent_a = 1000
        self.min_agent_b = 1000

        # Extract data for optimization
        self.costs = [self.models[f'Model {i + 1}']['cost'] for i in range(4)]
        self.agent_a_contrib = [self.models[f'Model {i + 1}']['agent_a'] for i in range(4)]
        self.agent_b_contrib = [self.models[f'Model {i + 1}']['agent_b'] for i in range(4)]

    def setup_optimization_problem(self):
        """
        Set up the linear programming problem in CVXOPT format.

        Standard form:
        minimize c^T * x
        subject to G*x <= h and A*x = b

        Our problem:
        minimize: 50*x1 + 60*x2 + 58*x3 + 63*x4
        subject to:
        - 2*x1 + 2*x2 + 2*x3 + 2*x4 >= 1000  (Agent Group A)
        - 2*x1 + 2*x2 + 2*x3 + 2*x4 >= 1000  (Agent Group B)
        - x1, x2, x3, x4 >= 0                 (Non-negativity)
        """

        # Objective function coefficients (costs)
        c = matrix(self.costs, tc='d')

        # Inequality constraints: G*x <= h
        # Convert >= constraints to <= by multiplying by -1
        # G matrix should have 4 columns (variables) and 6 rows (constraints)
        G_data = [
            # x1 column
            [-2.0, -2.0, -1.0, 0.0, 0.0, 0.0],
            # x2 column
            [-2.0, -2.0, 0.0, -1.0, 0.0, 0.0],
            # x3 column
            [-2.0, -2.0, 0.0, 0.0, -1.0, 0.0],
            # x4 column
            [-2.0, -2.0, 0.0, 0.0, 0.0, -1.0]
        ]

        # Create G matrix in column-major format (4 columns, 6 rows)
        G = matrix(G_data, tc='d')

        h = matrix([
            -self.min_agent_a,  # -1000 (Agent Group A)
            -self.min_agent_b,  # -1000 (Agent Group B)
            0.0, 0.0, 0.0, 0.0  # Non-negativity bounds for x1, x2, x3, x4
        ], tc='d')

        return c, G, h

    def solve_optimization(self, verbose=True):
        """
        Solve the optimization problem using CVXOPT.
        """
        print("=" * 60)
        print("PRETRAINED MODEL SELECTION OPTIMIZATION")
        print("=" * 60)

        # Display problem setup
        self.display_problem_setup()

        # Set up optimization problem
        c, G, h = self.setup_optimization_problem()

        # Solve using CVXOPT
        if not verbose:
            solvers.options['show_progress'] = False

        sol = solvers.lp(c, G, h)

        if sol['status'] == 'optimal':
            return self.process_solution(sol)
        else:
            print(f"Optimization failed with status: {sol['status']}")
            return None

    def display_problem_setup(self):
        """Display the problem formulation."""
        print("\nProblem Setup:")
        print("-" * 40)

        # Create and display model data table
        df = pd.DataFrame.from_dict(self.models, orient='index')
        print("Model Data:")
        print(df)

        print(f"\nConstraints:")
        print(f"- Agent Group A requirement: >= {self.min_agent_a}")
        print(f"- Agent Group B requirement: >= {self.min_agent_b}")
        print(f"- Non-negativity: x1, x2, x3, x4 >= 0")

        print(f"\nObjective:")
        print(
            f"Minimize total daily cost = {self.costs[0]}*x1 + {self.costs[1]}*x2 + {self.costs[2]}*x3 + {self.costs[3]}*x4")

    def process_solution(self, sol):
        """Process and display the optimization solution."""
        x_optimal = np.array(sol['x']).flatten()
        optimal_cost = sol['primal objective']

        print("\n" + "=" * 60)
        print("OPTIMIZATION RESULTS")
        print("=" * 60)

        print(f"\nOptimal Solution:")
        print("-" * 20)
        for i, x_val in enumerate(x_optimal):
            print(f"Model {i + 1} (x{i + 1}): {x_val:.2f} units")

        print(f"\nMinimum Daily Cost: ${optimal_cost:.2f}")

        # Verify constraints
        self.verify_constraints(x_optimal)

        # Cost breakdown
        self.cost_breakdown(x_optimal)

        # Sensitivity analysis
        self.sensitivity_analysis(x_optimal)

        return {
            'optimal_allocation': x_optimal,
            'minimum_cost': optimal_cost,
            'solution': sol
        }

    def verify_constraints(self, x_optimal):
        """Verify that the solution satisfies all constraints."""
        print(f"\nConstraint Verification:")
        print("-" * 25)

        agent_a_satisfied = sum(x_optimal[i] * self.agent_a_contrib[i] for i in range(4))
        agent_b_satisfied = sum(x_optimal[i] * self.agent_b_contrib[i] for i in range(4))

        print(
            f"Agent Group A: {agent_a_satisfied:.2f} >= {self.min_agent_a} ✓" if agent_a_satisfied >= self.min_agent_a else f"Agent Group A: {agent_a_satisfied:.2f} < {self.min_agent_a} ✗")
        print(
            f"Agent Group B: {agent_b_satisfied:.2f} >= {self.min_agent_b} ✓" if agent_b_satisfied >= self.min_agent_b else f"Agent Group B: {agent_b_satisfied:.2f} < {self.min_agent_b} ✗")

        non_negative = all(x >= -1e-10 for x in x_optimal)  # Allow for small numerical errors
        print(f"Non-negativity: {'✓' if non_negative else '✗'}")

    def cost_breakdown(self, x_optimal):
        """Provide detailed cost breakdown."""
        print(f"\nCost Breakdown:")
        print("-" * 20)

        total_cost = 0
        for i, x_val in enumerate(x_optimal):
            model_cost = x_val * self.costs[i]
            total_cost += model_cost
            if x_val > 1e-6:  # Only show models that are actually used
                print(f"Model {i + 1}: {x_val:.2f} units × ${self.costs[i]} = ${model_cost:.2f}")

        print(f"Total Daily Cost: ${total_cost:.2f}")
        print(f"Monthly Cost (30 days): ${total_cost * 30:.2f}")

    def sensitivity_analysis(self, x_optimal):
        """Perform basic sensitivity analysis."""
        print(f"\nSensitivity Analysis:")
        print("-" * 25)

        # Cost efficiency analysis
        efficiency = [(self.costs[i] / (self.agent_a_contrib[i] + self.agent_b_contrib[i])) for i in range(4)]
        sorted_models = sorted(enumerate(efficiency), key=lambda x: x[1])

        print("Cost efficiency ranking (cost per unit contribution):")
        for rank, (model_idx, eff) in enumerate(sorted_models):
            print(f"{rank + 1}. Model {model_idx + 1}: ${eff:.2f} per unit")

    def visualize_results(self, result):
        """Create visualizations of the optimization results."""
        if result is None:
            return

        x_optimal = result['optimal_allocation']

        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))

        # Plot 1: Optimal allocation
        models = [f'Model {i + 1}' for i in range(4)]
        ax1.bar(models, x_optimal, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
        ax1.set_title('Optimal Model Allocation')
        ax1.set_ylabel('Number of Units')
        ax1.grid(True, alpha=0.3)

        # Plot 2: Cost comparison
        total_costs = [x_optimal[i] * self.costs[i] for i in range(4)]
        ax2.bar(models, total_costs, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
        ax2.set_title('Cost Contribution by Model')
        ax2.set_ylabel('Daily Cost ($)')
        ax2.grid(True, alpha=0.3)

        # Plot 3: Cost per unit efficiency
        efficiency = [self.costs[i] / (self.agent_a_contrib[i] + self.agent_b_contrib[i]) for i in range(4)]
        ax3.bar(models, efficiency, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
        ax3.set_title('Cost Efficiency (Cost per Unit Contribution)')
        ax3.set_ylabel('Cost per Unit ($)')
        ax3.grid(True, alpha=0.3)

        # Plot 4: Constraint satisfaction
        constraints = ['Agent Group A', 'Agent Group B']
        satisfied = [
            sum(x_optimal[i] * self.agent_a_contrib[i] for i in range(4)),
            sum(x_optimal[i] * self.agent_b_contrib[i] for i in range(4))
        ]
        required = [self.min_agent_a, self.min_agent_b]

        x_pos = np.arange(len(constraints))
        width = 0.35

        ax4.bar(x_pos - width / 2, satisfied, width, label='Satisfied', color='green', alpha=0.7)
        ax4.bar(x_pos + width / 2, required, width, label='Required', color='red', alpha=0.7)
        ax4.set_title('Constraint Satisfaction')
        ax4.set_ylabel('Units')
        ax4.set_xticks(x_pos)
        ax4.set_xticklabels(constraints)
        ax4.legend()
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()


def main():
    """Main function to run the optimization."""
    # Create optimizer instance
    optimizer = ModelSelectionOptimizer()

    # Solve the optimization problem
    result = optimizer.solve_optimization(verbose=False)

    # Visualize results
    if result:
        optimizer.visualize_results(result)

        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"✓ Optimal solution found!")
        print(f"✓ Minimum daily cost: ${result['minimum_cost']:.2f}")
        print(f"✓ Monthly cost: ${result['minimum_cost'] * 30:.2f}")
        print(f"✓ Primary model used: Model 1 (most cost-efficient)")


if __name__ == "__main__":
    main()
