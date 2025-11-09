import tkinter as tk
from tkinter import ttk
import math
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import random
import pandas as pd
from matplotlib.figure import Figure


class MemorizingQLearningApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Memorizing Score with AI")
        self.root.geometry("900x750")
        self.root.configure(bg="#f5f5f5")

        # Initialize Q-learning parameters
        self.initialize_qlearning()

        # Create main frames
        self.create_input_frame()
        self.create_result_frame()
        self.create_qlearning_frame()
        self.create_chart_frame()

        # Initialize score history
        self.score_history = []

    def initialize_qlearning(self):
        """Initialize Q-learning parameters and Q-table"""
        # State space dimensions
        self.attempts_range = list(range(1, 11))  # 1-10 attempts
        self.content_match_range = [0, 25, 50, 75, 100]  # Content match percentages
        self.time_slots_range = list(range(1, 11))  # 1-10 time slots

        # Action space: Study strategies
        self.actions = [
            "Visual Imagery",  # Focus on visual associations
            "Spaced Repetition",  # Distributed practice over time
            "Active Recall",  # Test yourself repeatedly
            "Chunking",  # Group information
            "Mnemonic Devices"  # Memory aids like acronyms
        ]

        # Initialize Q-table with zeros
        # Format: states x actions (attempts, content_match, time_slots) x actions
        self.q_table = {}
        for a in self.attempts_range:
            for c in self.content_match_range:
                for t in self.time_slots_range:
                    state = (a, c, t)
                    self.q_table[state] = {action: 0.0 for action in self.actions}

        # Q-learning parameters
        self.alpha = 0.1  # Learning rate
        self.gamma = 0.9  # Discount factor
        self.epsilon = 0.3  # Exploration rate
        self.current_state = None
        self.current_action = None

        # Training data
        self.training_data = []

    def create_input_frame(self):
        """Create frame for input parameters"""
        input_frame = ttk.LabelFrame(self.root, text="Input Parameters", padding=15)
        input_frame.pack(fill="x", expand=False, padx=20, pady=10)

        # Define and create input fields
        input_fields = [
            {"label": "Number of Attempts:", "var_name": "attempts", "default": 1,
             "min": 1, "max": 10, "help": "Number of tries needed to memorize (1-10)"},

            {"label": "Content Match (%):", "var_name": "content_match", "default": 75,
             "min": 0, "max": 100, "help": "Percentage of content correctly matched (0-100)"},

            {"label": "Time Slots Used:", "var_name": "time_slots", "default": 5,
             "min": 1, "max": 10, "help": "Number of time slots used for memorizing (1-10)"},

            {"label": "Maximum Time Slots:", "var_name": "max_slots", "default": 10,
             "min": 1, "max": 20, "help": "Maximum available time slots (1-20)"}
        ]

        # Create variables to store input values
        self.vars = {}

        # Create input widgets
        for i, field in enumerate(input_fields):
            # Create frame for each row
            row_frame = ttk.Frame(input_frame)
            row_frame.pack(fill="x", expand=True, pady=5)

            # Create label
            ttk.Label(row_frame, text=field["label"], width=18).pack(side=tk.LEFT)

            # Create variable
            var = tk.IntVar(value=field["default"])
            self.vars[field["var_name"]] = var

            # Create scale
            scale = ttk.Scale(
                row_frame,
                from_=field["min"],
                to=field["max"],
                variable=var,
                orient=tk.HORIZONTAL
            )
            scale.pack(side=tk.LEFT, fill="x", expand=True, padx=5)

            # Create spinbox for precise input
            spinbox = ttk.Spinbox(
                row_frame,
                from_=field["min"],
                to=field["max"],
                textvariable=var,
                width=5,
                wrap=True
            )
            spinbox.pack(side=tk.LEFT)

            # Create help button
            help_button = ttk.Button(
                row_frame,
                text="?",
                width=2,
                command=lambda h=field["help"]: messagebox.showinfo("Help", h)
            )
            help_button.pack(side=tk.LEFT, padx=5)

        # Create calculate button
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill="x", expand=True, pady=10)

        calculate_button = ttk.Button(
            button_frame,
            text="Calculate Score",
            command=self.calculate_score,
            style="Accent.TButton"
        )
        calculate_button.pack(side=tk.LEFT, padx=5, pady=10)

        get_strategy_button = ttk.Button(
            button_frame,
            text="Get Recommended Strategy",
            command=self.get_recommended_strategy,
            style="Accent.TButton"
        )
        get_strategy_button.pack(side=tk.LEFT, padx=5, pady=10)

    def create_result_frame(self):
        """Create frame for displaying results"""
        self.result_frame = ttk.LabelFrame(self.root, text="Score Results", padding=15)
        self.result_frame.pack(fill="x", expand=False, padx=20, pady=10)

        # Create results display
        result_items = [
            {"label": "Final Score:", "var_name": "final_score"},
            {"label": "Content Match Score:", "var_name": "content_score"},
            {"label": "Attempt Score:", "var_name": "attempt_score"},
            {"label": "Time Efficiency Score:", "var_name": "time_score"}
        ]

        # Create variables for results
        self.result_vars = {}

        # Create result widgets
        for item in result_items:
            row_frame = ttk.Frame(self.result_frame)
            row_frame.pack(fill="x", expand=True, pady=5)

            ttk.Label(row_frame, text=item["label"], width=20).pack(side=tk.LEFT)

            var = tk.StringVar(value="--")
            self.result_vars[item["var_name"]] = var

            # Use different styling for final score
            if item["var_name"] == "final_score":
                result_label = ttk.Label(
                    row_frame,
                    textvariable=var,
                    font=("Arial", 12, "bold")
                )
            else:
                result_label = ttk.Label(row_frame, textvariable=var)

            result_label.pack(side=tk.LEFT)

        # Add a breakdown display
        ttk.Label(self.result_frame, text="Breakdown:").pack(anchor="w", pady=(10, 0))
        self.breakdown_var = tk.StringVar(value="--")
        ttk.Label(self.result_frame, textvariable=self.breakdown_var).pack(anchor="w")

        # Add save button for history
        save_button = ttk.Button(
            self.result_frame,
            text="Save and Train AI Algorithm",
            command=self.save_and_train
        )
        save_button.pack(pady=10)

    def create_qlearning_frame(self):
        """Create frame for Q-learning controls and feedback"""
        self.qlearn_frame = ttk.LabelFrame(self.root, text="AI System", padding=15)
        self.qlearn_frame.pack(fill="x", expand=False, padx=20, pady=10)

        # Create strategy selection
        strategy_frame = ttk.Frame(self.qlearn_frame)
        strategy_frame.pack(fill="x", expand=True, pady=5)

        ttk.Label(strategy_frame, text="Study Strategy:").pack(side=tk.LEFT, padx=5)

        self.strategy_var = tk.StringVar()
        strategy_dropdown = ttk.Combobox(
            strategy_frame,
            textvariable=self.strategy_var,
            values=self.actions,
            state="readonly",
            width=20
        )
        strategy_dropdown.pack(side=tk.LEFT, padx=5)
        strategy_dropdown.current(0)

        # Create recommendation display
        recommendation_frame = ttk.Frame(self.qlearn_frame)
        recommendation_frame.pack(fill="x", expand=True, pady=10)

        ttk.Label(recommendation_frame, text="Recommended Strategy:").pack(side=tk.LEFT, padx=5)

        self.recommendation_var = tk.StringVar(value="Not available yet")
        ttk.Label(
            recommendation_frame,
            textvariable=self.recommendation_var,
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=5)

        # Create model status
        status_frame = ttk.Frame(self.qlearn_frame)
        status_frame.pack(fill="x", expand=True, pady=5)

        ttk.Label(status_frame, text="Model Status:").pack(side=tk.LEFT, padx=5)

        self.status_var = tk.StringVar(value="Initialized, waiting for training data")
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT, padx=5)

        # Add training controls
        control_frame = ttk.Frame(self.qlearn_frame)
        control_frame.pack(fill="x", expand=True, pady=10)

        # Training data size display
        ttk.Label(control_frame, text="Training Data Points:").pack(side=tk.LEFT, padx=5)
        self.train_size_var = tk.StringVar(value="0")
        ttk.Label(control_frame, textvariable=self.train_size_var).pack(side=tk.LEFT, padx=5)

        # Manual training button
        train_button = ttk.Button(
            control_frame,
            text="Train Model",
            command=self.manual_train
        )
        train_button.pack(side=tk.RIGHT, padx=5)

    def create_chart_frame(self):
        """Create frame for charts and visualization"""
        self.chart_frame = ttk.LabelFrame(self.root, text="Visualization", padding=15)
        self.chart_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Create tabs for different charts
        self.tab_control = ttk.Notebook(self.chart_frame)

        # Create tabs
        self.breakdown_tab = ttk.Frame(self.tab_control)
        self.history_tab = ttk.Frame(self.tab_control)
        self.qtable_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.breakdown_tab, text="Score Breakdown")
        self.tab_control.add(self.history_tab, text="Score History")
        self.tab_control.add(self.qtable_tab, text="Q-Learning Analysis")

        self.tab_control.pack(fill="both", expand=True)

        # Set up the breakdown chart
        self.breakdown_fig = Figure(figsize=(5, 4), dpi=100)
        self.breakdown_chart = self.breakdown_fig.add_subplot(111)
        self.breakdown_canvas = FigureCanvasTkAgg(self.breakdown_fig, self.breakdown_tab)
        self.breakdown_canvas.get_tk_widget().pack(fill="both", expand=True)

        # Set up history display
        history_frame = ttk.Frame(self.history_tab)
        history_frame.pack(fill="both", expand=True)

        self.history_listbox = tk.Listbox(history_frame, height=8)
        self.history_listbox.pack(fill="both", expand=True, padx=5, pady=5)

        # Add clear history button
        clear_button = ttk.Button(
            history_frame,
            text="Clear History",
            command=self.clear_history
        )
        clear_button.pack(pady=5)

        # Set up Q-table visualization
        self.qtable_fig = Figure(figsize=(5, 4), dpi=100)
        self.qtable_chart = self.qtable_fig.add_subplot(111)
        self.qtable_canvas = FigureCanvasTkAgg(self.qtable_fig, self.qtable_tab)
        self.qtable_canvas.get_tk_widget().pack(fill="both", expand=True)

        # Initialize an empty Q-table visualization
        self.update_qtable_chart()

    def calculate_score(self):
        """Calculate the memorizing score based on inputs"""
        try:
            # Get input values
            attempts = self.vars["attempts"].get()
            content_match = self.vars["content_match"].get()
            time_slots = self.vars["time_slots"].get()
            max_slots = self.vars["max_slots"].get()

            # Validate inputs
            if time_slots > max_slots:
                messagebox.showerror("Input Error", "Time slots used cannot exceed maximum time slots.")
                return

            # Calculate scores
            attempt_score = 100 * math.exp(-0.5 * (attempts - 1))
            content_score = content_match
            time_efficiency = max(0, 100 * (1 - (time_slots / max_slots)))

            # Calculate final score
            final_score = (0.5 * content_score) + (0.3 * attempt_score) + (0.2 * time_efficiency)

            # Update result displays
            self.result_vars["final_score"].set(f"{final_score:.2f}/100")
            self.result_vars["content_score"].set(f"{content_score:.2f}/100 (50% weight)")
            self.result_vars["attempt_score"].set(f"{attempt_score:.2f}/100 (30% weight)")
            self.result_vars["time_score"].set(f"{time_efficiency:.2f}/100 (20% weight)")

            # Update breakdown
            content_contribution = 0.5 * content_score
            attempt_contribution = 0.3 * attempt_score
            time_contribution = 0.2 * time_efficiency

            self.breakdown_var.set(
                f"Content: {content_contribution:.2f} pts + "
                f"Attempts: {attempt_contribution:.2f} pts + "
                f"Time: {time_contribution:.2f} pts = {final_score:.2f} pts"
            )

            # Store current score for potential saving
            self.current_score = {
                "attempts": attempts,
                "content_match": content_match,
                "time_slots": time_slots,
                "max_slots": max_slots,
                "final_score": final_score,
                "content_score": content_score,
                "attempt_score": attempt_score,
                "time_efficiency": time_efficiency,
                "strategy": self.strategy_var.get() if self.strategy_var.get() else "Not Selected",
                "breakdown": {
                    "content": content_contribution,
                    "attempts": attempt_contribution,
                    "time": time_contribution
                }
            }

            # Save state for Q-learning
            closest_content = min(self.content_match_range, key=lambda x: abs(x - content_match))
            self.current_state = (attempts, closest_content, time_slots)

            # Update the chart
            self.update_breakdown_chart()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def update_breakdown_chart(self):
        """Update the breakdown pie chart"""
        if not hasattr(self, 'current_score'):
            return

        # Clear previous chart
        self.breakdown_chart.clear()

        # Create data for pie chart
        labels = ['Content Match (50%)', 'Attempts (30%)', 'Time Efficiency (20%)']
        sizes = [
            self.current_score["breakdown"]["content"],
            self.current_score["breakdown"]["attempts"],
            self.current_score["breakdown"]["time"]
        ]

        # Create pie chart
        self.breakdown_chart.pie(
            sizes,
            labels=labels,
            autopct='%1.1f%%',
            startangle=90,
            shadow=True,
            explode=(0.1, 0, 0)
        )
        self.breakdown_chart.axis('equal')
        self.breakdown_chart.set_title(f'Score Breakdown: {self.current_score["final_score"]:.2f}/100')

        # Refresh canvas
        self.breakdown_canvas.draw()

    def save_and_train(self):
        """Save current score to history and update Q-learning model"""
        if hasattr(self, 'current_score') and hasattr(self, 'current_state'):
            # Make sure a strategy is selected
            if not self.strategy_var.get():
                messagebox.showerror("Error", "Please select a study strategy first.")
                return

            # Set the current action for Q-learning
            self.current_action = self.strategy_var.get()

            # Update score history with strategy
            self.score_history.append(self.current_score)

            # Add score to training data
            self.training_data.append({
                "state": self.current_state,
                "action": self.current_action,
                "reward": self.current_score["final_score"]
            })

            # Update history display
            self.history_listbox.insert(
                tk.END,
                f"Score: {self.current_score['final_score']:.2f} - "
                f"Strategy: {self.current_action} - "
                f"Attempts: {self.current_score['attempts']}, "
                f"Match: {self.current_score['content_match']}%"
            )

            # Update training data size display
            self.train_size_var.set(str(len(self.training_data)))

            # Train the Q-learning model with new data
            self.train_qlearning()

            messagebox.showinfo("Success", "Score saved and Q-learning model updated.")
        else:
            messagebox.showwarning("Warning", "Calculate a score first before saving.")

    def train_qlearning(self):
        """Train the Q-learning model with current data"""
        if len(self.training_data) < 1:
            self.status_var.set("Need more data for training")
            return

        # Update each state-action pair in Q-table based on rewards
        for data_point in self.training_data:
            state = data_point["state"]
            action = data_point["action"]
            reward = data_point["reward"]

            # Find best next state value (simplified as we don't have explicit transitions)
            best_next_q = max(self.q_table.get(state, {}).values()) if state in self.q_table else 0

            # Q-learning update formula
            if state in self.q_table and action in self.q_table[state]:
                self.q_table[state][action] = (1 - self.alpha) * self.q_table[state][action] + \
                                              self.alpha * (reward + self.gamma * best_next_q)

        # Update status
        self.status_var.set(f"Trained with {len(self.training_data)} data points")

        # Update Q-table visualization
        self.update_qtable_chart()

    def manual_train(self):
        """Manually trigger Q-learning training"""
        if len(self.training_data) < 1:
            messagebox.showwarning("Warning", "No training data available. Add some scores first.")
            return

        self.train_qlearning()
        messagebox.showinfo("Training Complete", f"Model trained with {len(self.training_data)} data points")

    def get_recommended_strategy(self):
        """Get the best strategy for current state based on Q-table"""
        try:
            # Get current parameters
            attempts = self.vars["attempts"].get()
            content_match = self.vars["content_match"].get()
            time_slots = self.vars["time_slots"].get()

            # Find closest content match in our discrete space
            closest_content = min(self.content_match_range, key=lambda x: abs(x - content_match))

            # Create state
            state = (attempts, closest_content, time_slots)

            if len(self.training_data) < 3:
                self.recommendation_var.set("Need more training data")
                return

            # Check if state exists in Q-table
            if state in self.q_table:
                # Get best action from Q-table
                q_values = self.q_table[state]
                best_action = max(q_values, key=q_values.get)
                best_value = q_values[best_action]

                if best_value > 0:
                    self.recommendation_var.set(f"{best_action} (Q-value: {best_value:.2f})")
                else:
                    # Not enough data for this state
                    self.recommendation_var.set("Explore different strategies")
            else:
                # State not in Q-table, give general recommendation
                self.recommendation_var.set("Try any strategy and provide feedback")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def update_qtable_chart(self):
        """Update the Q-table heatmap visualization"""
        self.qtable_chart.clear()

        if len(self.training_data) < 1:
            self.qtable_chart.text(0.5, 0.5, "No training data available yet",
                                   ha='center', va='center', fontsize=12)
            self.qtable_canvas.draw()
            return

        # Extract Q-values for visualization
        # We'll take average Q-value for each action across states
        action_values = {action: [] for action in self.actions}

        for state, actions in self.q_table.items():
            for action, value in actions.items():
                if value > 0:  # Only consider trained values
                    action_values[action].append(value)

        # Calculate average Q-value for each action
        action_avg = {}
        for action, values in action_values.items():
            if values:
                action_avg[action] = sum(values) / len(values)
            else:
                action_avg[action] = 0

        # Sort actions by average Q-value
        sorted_actions = sorted(action_avg.items(), key=lambda x: x[1], reverse=True)

        # Prepare data for bar chart
        actions = [a[0] for a in sorted_actions]
        values = [a[1] for a in sorted_actions]

        # Create bar chart
        bars = self.qtable_chart.bar(actions, values, color='skyblue')

        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                self.qtable_chart.text(bar.get_x() + bar.get_width() / 2., height + 0.1,
                                       f'{height:.2f}', ha='center', va='bottom', rotation=0)

        self.qtable_chart.set_title('Strategy Effectiveness (Average Q-Values)')
        self.qtable_chart.set_ylabel('Q-Value')
        self.qtable_chart.set_ylim(0, max(values) * 1.2 if values and max(values) > 0 else 10)

        # Rotate x-axis labels for better readability
        plt.setp(self.qtable_chart.get_xticklabels(), rotation=45, ha='right')

        self.qtable_fig.tight_layout()
        self.qtable_canvas.draw()

    def clear_history(self):
        """Clear the score history"""
        self.score_history = []
        self.history_listbox.delete(0, tk.END)
        messagebox.showinfo("Success", "History cleared.")


def setup_styles():
    """Set up custom styles for the application"""
    style = ttk.Style()

    # Configure styles
    style.configure("TLabel", font=("Arial", 10))
    style.configure("TButton", font=("Arial", 10))
    style.configure("Accent.TButton", font=("Arial", 10, "bold"))
    style.configure("TLabelframe", font=("Arial", 11, "bold"))
    style.configure("TLabelframe.Label", font=("Arial", 11, "bold"))


if __name__ == "__main__":
    root = tk.Tk()
    setup_styles()
    app = MemorizingQLearningApp(root)
    root.mainloop()
