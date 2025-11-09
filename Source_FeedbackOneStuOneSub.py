import tkinter as tk
from tkinter import ttk, messagebox
import random


class PostCorrelationAnalysis:
    def __init__(self, root):
        self.root = root
        self.root.title("Post Correlation Analysis System")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f0f0f0')

        # Sample data for Alice - Mathematics subject with different topics
        self.sample_data = [
            {"Post1_ID": "P001", "Post2_ID": "P002", "Student": "Alice", "Subject": "Mathematics",
             "Topics": "Algebra - Quadratic Equations", "Correlation": 0.758, "Time_Gap": "1 days",
             "Status": "Filtered"},
            {"Post1_ID": "P001", "Post2_ID": "P003", "Student": "Alice", "Subject": "Mathematics",
             "Topics": "Algebra - Linear Equations", "Correlation": 0.642, "Time_Gap": "2 days", "Status": "Filtered"},
            {"Post1_ID": "P001", "Post2_ID": "P004", "Student": "Alice", "Subject": "Mathematics",
             "Topics": "Algebra - Polynomials", "Correlation": 0.589, "Time_Gap": "3 days", "Status": "Filtered"},
            {"Post1_ID": "P002", "Post2_ID": "P003", "Student": "Alice", "Subject": "Mathematics",
             "Topics": "Quadratic Equations - Linear Equations", "Correlation": 0.523, "Time_Gap": "1 days",
             "Status": "Filtered"},
            {"Post1_ID": "P002", "Post2_ID": "P004", "Student": "Alice", "Subject": "Mathematics",
             "Topics": "Quadratic Equations - Polynomials", "Correlation": 0.674, "Time_Gap": "2 days",
             "Status": "Filtered"},
            {"Post1_ID": "P003", "Post2_ID": "P004", "Student": "Alice", "Subject": "Mathematics",
             "Topics": "Linear Equations - Polynomials", "Correlation": 0.456, "Time_Gap": "1 days",
             "Status": "Filtered"}
        ]

        self.filtered_data = self.sample_data.copy()
        self.create_widgets()
        self.populate_data()

    def create_widgets(self):
        # Main title
        title_label = tk.Label(self.root, text="Student Post Correlation Analysis",
                               font=('Arial', 16, 'bold'), bg='#f0f0f0', fg='#333')
        title_label.pack(pady=10)

        # Analysis Controls Frame
        controls_frame = tk.LabelFrame(self.root, text="Analysis Controls", font=('Arial', 10, 'bold'),
                                       bg='white', fg='#333', padx=10, pady=10)
        controls_frame.pack(fill='x', padx=20, pady=10)

        # First row of controls
        first_row = tk.Frame(controls_frame, bg='white')
        first_row.pack(fill='x', pady=5)

        tk.Label(first_row, text="Time Window (days):", bg='white', font=('Arial', 9)).pack(side='left')
        self.time_window = tk.Entry(first_row, width=8, font=('Arial', 9))
        self.time_window.insert(0, "7")
        self.time_window.pack(side='left', padx=(5, 20))

        tk.Label(first_row, text="Correlation Threshold:", bg='white', font=('Arial', 9)).pack(side='left')
        self.correlation_threshold = tk.Entry(first_row, width=8, font=('Arial', 9))
        self.correlation_threshold.insert(0, "0.5")
        self.correlation_threshold.pack(side='left', padx=(5, 20))

        self.load_data_btn = tk.Button(first_row, text="Load Data", bg='#e0e0e0',
                                       font=('Arial', 9), command=self.load_data)
        self.load_data_btn.pack(side='left', padx=5)

        self.analyze_btn = tk.Button(first_row, text="Analyze Correlations", bg='#ffcccc',
                                     font=('Arial', 9), command=self.analyze_correlations)
        self.analyze_btn.pack(side='left', padx=5)

        self.find_gaps_btn = tk.Button(first_row, text="Find Gaps", bg='#e0e0e0',
                                       font=('Arial', 9), command=self.find_gaps)
        self.find_gaps_btn.pack(side='left', padx=5)

        # Subject info label
        subject_info = tk.Label(controls_frame, text="Subject: Mathematics | Student: Alice",
                                bg='white', font=('Arial', 9, 'italic'), fg='#666')
        subject_info.pack(anchor='w', pady=(5, 0))

        # Tabs frame
        tabs_frame = tk.Frame(self.root, bg='white')
        tabs_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(tabs_frame)
        self.notebook.pack(fill='both', expand=True)

        # Posts Data tab
        self.posts_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.posts_frame, text="Posts Data")

        # Other tabs (placeholders)
        correlations_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(correlations_frame, text="Correlations")

        gaps_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(gaps_frame, text="Correlation Gaps")

        stats_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(stats_frame, text="Statistics")

        # Filters section
        filters_frame = tk.Frame(self.posts_frame, bg='white')
        filters_frame.pack(fill='x', pady=5)

        tk.Label(filters_frame, text="Filters", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w')

        filter_controls = tk.Frame(filters_frame, bg='white')
        filter_controls.pack(fill='x', pady=5)

        tk.Label(filter_controls, text="Min Correlation Score:", bg='white', font=('Arial', 9)).pack(side='left')
        self.min_correlation = tk.Entry(filter_controls, width=8, font=('Arial', 9))
        self.min_correlation.insert(0, "0.3")
        self.min_correlation.pack(side='left', padx=(5, 10))

        self.apply_filter_btn = tk.Button(filter_controls, text="Apply Filter", bg='#ffcccc',
                                          font=('Arial', 9), command=self.apply_filter)
        self.apply_filter_btn.pack(side='left', padx=5)

        # Treeview for data display
        self.create_treeview()

    def create_treeview(self):
        # Frame for treeview and scrollbars
        tree_frame = tk.Frame(self.posts_frame, bg='white')
        tree_frame.pack(fill='both', expand=True, pady=10)

        # Define columns - modified for single subject
        columns = ("Post1_ID", "Post2_ID", "Student", "Subject", "Topics", "Correlation",
                   "Time Gap", "Status")

        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)

        # Define column headings and widths
        column_widths = {"Post1_ID": 80, "Post2_ID": 80, "Student": 80, "Subject": 100,
                         "Topics": 250, "Correlation": 100, "Time Gap": 80, "Status": 80}

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100), anchor='center')

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.tree.xview)

        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Pack scrollbars and treeview
        self.tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')

    def populate_data(self):
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add filtered data
        for row in self.filtered_data:
            self.tree.insert('', 'end', values=(
                row["Post1_ID"], row["Post2_ID"], row["Student"],
                row["Subject"], row["Topics"], f"{row['Correlation']:.3f}",
                row["Time_Gap"], row["Status"]
            ))

    def load_data(self):
        messagebox.showinfo("Load Data", "Mathematics topic correlation data for Alice loaded successfully!")
        self.populate_data()

    def analyze_correlations(self):
        # Show analysis complete dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Analysis Complete")
        dialog.geometry("350x150")
        dialog.configure(bg='white')
        dialog.transient(self.root)
        dialog.grab_set()

        # Center the dialog
        dialog.geometry("+{}+{}".format(
            self.root.winfo_rootx() + 425,
            self.root.winfo_rooty() + 200
        ))

        # Info icon and message
        info_frame = tk.Frame(dialog, bg='white')
        info_frame.pack(expand=True, fill='both', padx=20, pady=20)

        # Blue info icon (using text)
        icon_label = tk.Label(info_frame, text="ℹ", font=('Arial', 24),
                              fg='#0066cc', bg='white')
        icon_label.pack(pady=10)

        message_label = tk.Label(info_frame, text="Found 6 topic correlations in Mathematics",
                                 font=('Arial', 11), bg='white')
        message_label.pack(pady=5)

        ok_button = tk.Button(info_frame, text="OK", command=dialog.destroy,
                              bg='#e0e0e0', font=('Arial', 9), width=10)
        ok_button.pack(pady=10)

    def find_gaps(self):
        messagebox.showinfo("Find Gaps", "Topic correlation gap analysis completed for Mathematics!")

    def apply_filter(self):
        try:
            min_corr = float(self.min_correlation.get())
            self.filtered_data = [row for row in self.sample_data
                                  if row["Correlation"] >= min_corr]
            self.populate_data()
            messagebox.showinfo("Filter Applied",
                                f"Filter applied. Showing {len(self.filtered_data)} topic correlations.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid correlation threshold.")


def main():
    root = tk.Tk()
    app = PostCorrelationAnalysis(root)
    root.mainloop()


if __name__ == "__main__":
    main()
