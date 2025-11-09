import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import pyttsx3
import threading
from difflib import SequenceMatcher
import json
import random
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import numpy as np
import os


class MemorizingCoachApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Memorizing AI Agent Coach")
        self.root.geometry("900x700")

        # Initialize text-to-speech engine
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)  # Speech rate
        self.tts_engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)

        # Get available voices
        voices = self.tts_engine.getProperty('voices')
        if voices:
            self.tts_engine.setProperty('voice', voices[1].id)

        # Coach script with expected responses
        self.script = [
            {"message": "Hi Welcome to this Memorizing AI Agent coach", "type": "greeting", "expected": None},
            {"message": "Choose the topic from your chapter", "type": "input", "expected": "topic"},
            {"message": "Choose your depth level as 1, 2 or 3", "type": "input", "expected": ["1", "2", "3"]},
            {"message": "Now open the app to start your Memorizing activity", "type": "info", "expected": None},
            {"message": "Give your input parameters and check your score", "type": "test", "expected": "parameters"},
            {"message": "Your score was low choose a different Memorizing strategy and check your score",
             "type": "strategy", "expected": "strategy"},
            {"message": "Post it for review to your Teacher and parent using the canvas.", "type": "canvas_info",
             "expected": "feedback"},
            {"message": "If you still need help I will guide you with below questions", "type": "guide",
             "expected": "help"}
        ]

        # Memorizing content for testing
        self.memorizing_content = {
            "history": ["World War II ended in 1945", "The Renaissance began in Italy",
                        "The Great Wall of China was built over centuries"],
            "science": ["Water boils at 100 degrees Celsius", "The Earth revolves around the Sun",
                        "Photosynthesis converts light to energy"],
            "math": ["Pi equals 3.14159...", "Pythagorean theorem: a² + b² = c²",
                     "The quadratic formula solves ax² + bx + c = 0"]
        }

        self.current_index = 0
        self.is_speaking = False
        self.user_data = {
            "topic": None,
            "depth": None,
            "score": 0,
            "strategy": None,
            "test_content": None,
            "attempts": []
        }

        # Initialize session history filename
        self.session_file = 'session_history.json'

        # Style configuration
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Coach.TLabel', font=('Arial', 12))
        style.configure('Action.TButton', font=('Arial', 11))
        style.configure('Score.TLabel', font=('Arial', 11, 'bold'))

        # Main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Title
        title_label = ttk.Label(main_frame, text="Memorizing AI Agent Coach", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Score display
        score_frame = ttk.Frame(main_frame)
        score_frame.grid(row=1, column=0, columnspan=3, pady=(0, 10))
        ttk.Label(score_frame, text="Current Score:", style='Score.TLabel').grid(row=0, column=0, padx=(0, 10))
        self.score_label = ttk.Label(score_frame, text="0%", style='Score.TLabel')
        self.score_label.grid(row=0, column=1)

        # Coach display area
        self.coach_frame = ttk.LabelFrame(main_frame, text="Coach Says:", padding="10")
        self.coach_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))

        self.coach_label = ttk.Label(self.coach_frame, text="", style='Coach.TLabel', wraplength=800)
        self.coach_label.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Speaking indicator
        self.speaking_label = ttk.Label(self.coach_frame, text="", font=('Arial', 10, 'italic'))
        self.speaking_label.grid(row=1, column=0, sticky=(tk.W), pady=(5, 0))

        # Test content display (for memorization)
        self.test_frame = ttk.LabelFrame(main_frame, text="Content to Memorize:", padding="10")
        self.test_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        self.test_frame.grid_remove()  # Hidden initially

        self.test_label = ttk.Label(self.test_frame, text="", font=('Arial', 11), wraplength=800)
        self.test_label.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # User input area
        input_frame = ttk.LabelFrame(main_frame, text="Your Response:", padding="10")
        input_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))

        self.user_input = ttk.Entry(input_frame, font=('Arial', 11), width=60)
        self.user_input.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.user_input.bind('<Return>', lambda e: self.submit_response())

        submit_btn = ttk.Button(input_frame, text="Submit", command=self.submit_response, style='Action.TButton')
        submit_btn.grid(row=0, column=1)

        # Feedback label
        self.feedback_label = ttk.Label(input_frame, text="", font=('Arial', 10, 'italic'))
        self.feedback_label.grid(row=1, column=0, columnspan=2, pady=(5, 0))

        # History area
        history_frame = ttk.LabelFrame(main_frame, text="Conversation History:", padding="10")
        history_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))

        self.history_text = scrolledtext.ScrolledText(history_frame, wrap=tk.WORD, height=8, font=('Arial', 10))
        self.history_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.history_text.config(state=tk.DISABLED)

        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=6, column=0, columnspan=3, pady=(10, 0))

        self.start_btn = ttk.Button(control_frame, text="Start Session", command=self.start_session,
                                    style='Action.TButton')
        self.start_btn.grid(row=0, column=0, padx=5)

        self.next_btn = ttk.Button(control_frame, text="Next", command=self.next_message, state=tk.DISABLED,
                                   style='Action.TButton')
        self.next_btn.grid(row=0, column=1, padx=5)

        self.show_answer_btn = ttk.Button(control_frame, text="Show Answer", command=self.show_answer,
                                          state=tk.DISABLED, style='Action.TButton')
        self.show_answer_btn.grid(row=0, column=2, padx=5)

        self.mute_btn = ttk.Button(control_frame, text="Mute", command=self.toggle_mute, style='Action.TButton')
        self.mute_btn.grid(row=0, column=3, padx=5)

        self.restart_btn = ttk.Button(control_frame, text="Restart", command=self.restart_session, state=tk.DISABLED,
                                      style='Action.TButton')
        self.restart_btn.grid(row=0, column=4, padx=5)

        # Add Show Progress button
        self.progress_btn = ttk.Button(control_frame, text="Show Progress", command=self.show_progress,
                                       style='Action.TButton')
        self.progress_btn.grid(row=0, column=5, padx=5)

        self.quit_btn = ttk.Button(control_frame, text="Quit", command=self.on_quit, style='Action.TButton')
        self.quit_btn.grid(row=0, column=6, padx=5)

        # Volume control
        volume_frame = ttk.Frame(main_frame)
        volume_frame.grid(row=7, column=0, columnspan=3, pady=(10, 0))

        ttk.Label(volume_frame, text="Volume:").grid(row=0, column=0, padx=(0, 5))

        # Create volume label first
        self.volume_label = ttk.Label(volume_frame, text="90%")
        self.volume_label.grid(row=0, column=2, padx=(5, 0))

        # Then create the scale with command
        self.volume_scale = ttk.Scale(volume_frame, from_=0, to=100, orient=tk.HORIZONTAL, length=200,
                                      command=self.change_volume)
        self.volume_scale.set(90)
        self.volume_scale.grid(row=0, column=1)

        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        input_frame.columnconfigure(0, weight=1)

        self.is_muted = False

    def speak_text(self, text):
        """Speak the given text using text-to-speech in a separate thread"""

        def speak_in_thread():
            self.is_speaking = True
            self.speaking_label.config(text="🔊 Speaking...")

            if not self.is_muted:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()

            self.is_speaking = False
            self.speaking_label.config(text="")

        thread = threading.Thread(target=speak_in_thread, daemon=True)
        thread.start()

    def start_session(self):
        """Start the coaching session"""
        self.current_index = 0
        current_item = self.script[self.current_index]
        self.coach_label.config(text=current_item["message"])
        self.add_to_history(f"Coach: {current_item['message']}")
        self.speak_text(current_item["message"])

        self.start_btn.config(state=tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL)
        self.restart_btn.config(state=tk.NORMAL)
        self.user_input.focus()

    def prepare_memorization_test(self):
        """Prepare content for memorization test based on topic and depth"""
        topic = self.user_data["topic"].lower()
        depth = int(self.user_data["depth"])

        # Select content based on topic (simplified for demo)
        content_pool = self.memorizing_content.get(topic, self.memorizing_content["science"])

        # Number of items based on depth
        num_items = depth
        selected_content = random.sample(content_pool, min(num_items, len(content_pool)))

        self.user_data["test_content"] = selected_content

        # Display content to memorize
        self.test_frame.grid()
        self.test_label.config(text="\n\n".join(selected_content))
        self.add_to_history(f"Content to memorize:\n{chr(10).join(selected_content)}")

        # Hide after some time based on depth
        display_time = 3000 * depth  # 3, 6, or 9 seconds
        self.root.after(display_time, self.hide_test_content)

    def hide_test_content(self):
        """Hide the test content and ask user to recall"""
        self.test_frame.grid_remove()
        self.coach_label.config(text="Now recall what you memorized and type it below:")
        self.add_to_history("Coach: Now recall what you memorized and type it below:")
        self.speak_text("Now recall what you memorized and type it below:")
        self.show_answer_btn.config(state=tk.NORMAL)

    def calculate_similarity(self, text1, text2):
        """Calculate similarity between two texts"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    def evaluate_response(self, response):
        """Evaluate user's response and calculate score"""
        current_item = self.script[self.current_index]

        if current_item["type"] == "test" and self.user_data["test_content"]:
            # For memorization test
            total_score = 0
            for content in self.user_data["test_content"]:
                similarity = self.calculate_similarity(response, content)
                total_score += similarity

            score = (total_score / len(self.user_data["test_content"])) * 100
            self.user_data["score"] = score
            self.score_label.config(text=f"{score:.1f}%")

            feedback = f"Your memorization score: {score:.1f}%"
            if score < 50:
                feedback += " - Try a different strategy!"
            elif score < 80:
                feedback += " - Good effort, but there's room for improvement."
            else:
                feedback += " - Excellent memorization!"

            self.feedback_label.config(text=feedback)
            return score

        elif current_item["expected"]:
            # For specific expected responses
            if isinstance(current_item["expected"], list):
                if response in current_item["expected"]:
                    self.feedback_label.config(text="✓ Valid response")
                    return 100
                else:
                    self.feedback_label.config(text=f"Please choose from: {', '.join(current_item['expected'])}")
                    return 0
            else:
                # Store user data
                self.user_data[current_item["expected"]] = response
                self.feedback_label.config(text="✓ Response recorded")
                return 100

        return None

    def submit_response(self):
        """Handle user response submission"""
        response = self.user_input.get().strip()
        if response:
            self.add_to_history(f"You: {response}")

            # Evaluate response
            score = self.evaluate_response(response)

            # Store attempt
            self.user_data["attempts"].append({
                "index": self.current_index,
                "response": response,
                "score": score
            })

            self.user_input.delete(0, tk.END)

            # Handle special cases
            current_item = self.script[self.current_index]
            if current_item["type"] == "input" and current_item["expected"] == "depth":
                # Start memorization test after depth is selected
                if response in ["1", "2", "3"]:
                    self.root.after(1000, self.prepare_memorization_test)

            # Check if we're at the end or near the end of the script
            if self.current_index >= len(self.script) - 2:
                # Save session data when we reach the canvas_info or guide steps
                if self.user_data.get('score', 0) > 0:
                    self.save_current_session()

            # Automatically move to next message after user input
            if self.current_index < len(self.script) - 1:
                self.root.after(1500, self.next_message)

    def show_answer(self):
        """Show the correct answer for memorization test"""
        if self.user_data["test_content"]:
            self.test_frame.grid()
            self.root.after(3000, lambda: self.test_frame.grid_remove())

    def next_message(self):
        """Display the next message from the coach"""
        self.feedback_label.config(text="")
        self.show_answer_btn.config(state=tk.DISABLED)

        if self.current_index < len(self.script) - 1:
            self.current_index += 1
            current_item = self.script[self.current_index]
            self.coach_label.config(text=current_item["message"])
            self.add_to_history(f"Coach: {current_item['message']}")
            self.speak_text(current_item["message"])
            self.user_input.focus()
        else:
            self.show_final_report()
            self.next_btn.config(state=tk.DISABLED)

    def show_final_report(self):
        """Show final report with scores and strategies"""
        # Only save if we have actual data
        if self.user_data.get('topic') and self.user_data.get('score', 0) > 0:
            self.save_current_session()

        report = f"""Session Complete!

Topic: {self.user_data.get('topic', 'Not selected')}
Depth Level: {self.user_data.get('depth', 'Not selected')}
Final Score: {self.user_data.get('score', 0):.1f}%
Strategy Used: {self.user_data.get('strategy', 'Not specified')}

Total Attempts: {len(self.user_data['attempts'])}
        """

        messagebox.showinfo("Session Report", report)

    def save_current_session(self):
        """Save current session data to history file"""
        # Make sure we have valid data before saving
        if not self.user_data.get('topic') or self.user_data.get('score', 0) == 0:
            print("No valid session data to save")
            return

        session_data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M'),
            'topic': self.user_data.get('topic', 'Unknown'),
            'depth': int(self.user_data.get('depth', 0)) if self.user_data.get('depth') else 0,
            'score': float(self.user_data.get('score', 0)),
            'strategy': self.user_data.get('strategy', 'Unknown'),
            'attempts': len(self.user_data.get('attempts', []))
        }

        print(f"Saving session data: {session_data}")  # Debug print

        # Load existing data
        history = self.load_session_data_from_file()
        history.append(session_data)

        # Save updated data
        self.save_session_data(history)
        print(f"Session saved. Total sessions: {len(history)}")  # Debug print

    def save_session_data(self, session_data):
        """Save session data to JSON file"""
        with open(self.session_file, 'w') as f:
            json.dump(session_data, f, indent=2)

    def load_session_data_from_file(self):
        """Load session data from JSON file"""
        try:
            with open(self.session_file, 'r') as f:
                data = json.load(f)
                print(f"Loaded {len(data)} sessions from {self.session_file}")  # Debug print
                return data
        except FileNotFoundError:
            print(f"Session file {self.session_file} not found. Starting with empty history.")
            return []
        except json.JSONDecodeError:
            print(f"Error reading {self.session_file}. Starting with empty history.")
            return []

    def generate_sample_data(self):
        """Generate sample session data for testing/demonstration"""
        sample_sessions = []
        topics = ['history', 'science', 'math']
        strategies = ['repetition', 'visualization', 'association', 'chunking']

        # Generate 30 days of sample data
        start_date = datetime.now() - timedelta(days=30)

        for day in range(30):
            current_date = start_date + timedelta(days=day)

            # Random number of sessions per day (0-3)
            num_sessions = random.randint(0, 3)

            for session in range(num_sessions):
                topic = random.choice(topics)
                depth = random.choice([1, 2, 3])
                score = random.uniform(40, 100)
                strategy = random.choice(strategies)

                sample_sessions.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'time': (current_date + timedelta(hours=random.randint(8, 20))).strftime('%H:%M'),
                    'topic': topic,
                    'depth': depth,
                    'score': score,
                    'strategy': strategy,
                    'attempts': random.randint(1, 3)
                })

        # Save sample data
        self.save_session_data(sample_sessions)
        messagebox.showinfo("Sample Data", "Generated 30 days of sample data for demonstration.")

    def show_progress(self):
        """Display performance plots in a new window"""
        history = self.load_session_data_from_file()

        if not history:
            # Offer to generate sample data
            response = messagebox.askyesno(
                "No Data Available",
                "No session data found. Would you like to generate sample data for demonstration?"
            )
            if response:
                self.generate_sample_data()
                history = self.load_session_data_from_file()
            else:
                return

        # Create a new window for progress display
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Performance Progress")
        progress_window.geometry("1000x800")

        # Create notebook for tabs
        notebook = ttk.Notebook(progress_window)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Create daily performance tab
        daily_frame = ttk.Frame(notebook)
        notebook.add(daily_frame, text="Daily Performance")
        daily_fig = self.create_daily_performance_plots(history)
        daily_canvas = FigureCanvasTkAgg(daily_fig, master=daily_frame)
        daily_canvas.draw()
        daily_canvas.get_tk_widget().pack(fill="both", expand=True)

        # Create topic performance tab
        topic_frame = ttk.Frame(notebook)
        notebook.add(topic_frame, text="Topic Performance")
        topic_fig = self.create_topic_performance_plot(history)
        topic_canvas = FigureCanvasTkAgg(topic_fig, master=topic_frame)
        topic_canvas.draw()
        topic_canvas.get_tk_widget().pack(fill="both", expand=True)

        # Add close button
        close_btn = ttk.Button(progress_window, text="Close",
                               command=progress_window.destroy)
        close_btn.pack(pady=10)

    def create_daily_performance_plots(self, sessions):
        """Create multiple subplots showing different aspects of daily performance"""

        # Process data for plotting
        daily_stats = {}

        for session in sessions:
            date = session['date']
            if date not in daily_stats:
                daily_stats[date] = {
                    'scores': [],
                    'topics': [],
                    'depths': [],
                    'strategies': [],
                    'attempts': []
                }

            if session['score'] > 0:  # Only include sessions with actual scores
                daily_stats[date]['scores'].append(session['score'])
                daily_stats[date]['topics'].append(session['topic'])
                daily_stats[date]['depths'].append(int(session['depth']) if session['depth'] else 0)
                daily_stats[date]['strategies'].append(session['strategy'])
                daily_stats[date]['attempts'].append(session['attempts'])

        # Prepare data for plotting
        dates = sorted(daily_stats.keys())
        date_objects = [datetime.strptime(d, '%Y-%m-%d') for d in dates]

        # Calculate daily metrics
        avg_scores = []
        max_scores = []
        min_scores = []
        session_counts = []
        avg_depths = []
        total_attempts = []

        for date in dates:
            scores = daily_stats[date]['scores']
            if scores:
                avg_scores.append(np.mean(scores))
                max_scores.append(max(scores))
                min_scores.append(min(scores))
                session_counts.append(len(scores))
                depths = [d for d in daily_stats[date]['depths'] if d > 0]
                avg_depths.append(np.mean(depths) if depths else 0)
                total_attempts.append(sum(daily_stats[date]['attempts']))
            else:
                avg_scores.append(0)
                max_scores.append(0)
                min_scores.append(0)
                session_counts.append(0)
                avg_depths.append(0)
                total_attempts.append(0)

        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('Memorizing Coach - Daily Performance Analysis', fontsize=16, fontweight='bold')

        # Plot 1: Daily average scores with range
        ax1.plot(date_objects, avg_scores, 'b-', linewidth=2, label='Average Score')
        ax1.fill_between(date_objects, min_scores, max_scores, alpha=0.3, color='lightblue', label='Score Range')
        ax1.set_title('Daily Score Performance')
        ax1.set_ylabel('Score (%)')
        ax1.set_ylim(0, 100)
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: Number of sessions per day
        ax2.bar(date_objects, session_counts, color='green', alpha=0.7)
        ax2.set_title('Daily Session Count')
        ax2.set_ylabel('Number of Sessions')
        ax2.grid(True, alpha=0.3)

        # Plot 3: Average depth level per day
        ax3.bar(date_objects, avg_depths, color='orange', alpha=0.7)
        ax3.set_title('Average Depth Level by Day')
        ax3.set_ylabel('Depth Level')
        ax3.set_ylim(0, 3.5)
        ax3.grid(True, alpha=0.3)

        # Plot 4: Total attempts per day
        ax4.plot(date_objects, total_attempts, 'r-', linewidth=2, marker='o')
        ax4.set_title('Total Daily Attempts')
        ax4.set_ylabel('Number of Attempts')
        ax4.grid(True, alpha=0.3)

        # Format x-axis for all subplots
        for ax in [ax1, ax2, ax3, ax4]:
            if date_objects:  # Only format if we have dates
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
                ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(date_objects) // 10)))
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

        plt.tight_layout()
        return fig

    def create_topic_performance_plot(self, sessions):
        """Create a plot showing performance by topic over time"""

        # Process data by topic
        topic_data = {'history': [], 'science': [], 'math': []}
        topic_dates = {'history': [], 'science': [], 'math': []}

        for session in sessions:
            if session['score'] > 0:  # Only include sessions with actual scores
                date = datetime.strptime(session['date'], '%Y-%m-%d')
                topic = session['topic'].lower()
                score = session['score']

                if topic in topic_data:
                    topic_data[topic].append(score)
                    topic_dates[topic].append(date)

        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))

        colors = {'history': 'blue', 'science': 'green', 'math': 'red'}

        for topic in ['history', 'science', 'math']:
            if topic_dates[topic]:
                ax.scatter(topic_dates[topic], topic_data[topic],
                           color=colors[topic], alpha=0.6, label=topic.capitalize(), s=50)

                # Add trend line if we have enough data points
                if len(topic_dates[topic]) > 1:
                    dates_numeric = mdates.date2num(topic_dates[topic])
                    z = np.polyfit(dates_numeric, topic_data[topic], 1)
                    p = np.poly1d(z)
                    ax.plot(topic_dates[topic], p(dates_numeric),
                            color=colors[topic], linestyle='--', alpha=0.8)

        ax.set_title('Performance by Topic Over Time', fontsize=14, fontweight='bold')
        ax.set_ylabel('Score (%)')
        ax.set_ylim(0, 100)
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Format x-axis only if we have data
        if any(topic_dates.values()):
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

        plt.tight_layout()
        return fig

    def add_to_history(self, text):
        """Add text to the conversation history"""
        self.history_text.config(state=tk.NORMAL)
        self.history_text.insert(tk.END, text + "\n\n")
        self.history_text.see(tk.END)
        self.history_text.config(state=tk.DISABLED)

    def restart_session(self):
        """Restart the coaching session"""
        self.tts_engine.stop()

        self.current_index = 0
        self.user_data = {
            "topic": None,
            "depth": None,
            "score": 0,
            "strategy": None,
            "test_content": None,
            "attempts": []
        }

        self.coach_label.config(text="")
        self.speaking_label.config(text="")
        self.feedback_label.config(text="")
        self.score_label.config(text="0%")
        self.test_frame.grid_remove()

        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        self.history_text.config(state=tk.DISABLED)
        self.user_input.delete(0, tk.END)

        self.start_btn.config(state=tk.NORMAL)
        self.next_btn.config(state=tk.DISABLED)
        self.restart_btn.config(state=tk.DISABLED)
        self.show_answer_btn.config(state=tk.DISABLED)

    def toggle_mute(self):
        """Toggle mute for text-to-speech"""
        self.is_muted = not self.is_muted
        self.mute_btn.config(text="Unmute" if self.is_muted else "Mute")

    def change_volume(self, value):
        """Change the volume of text-to-speech"""
        volume = float(value) / 100
        self.tts_engine.setProperty('volume', volume)
        self.volume_label.config(text=f"{int(float(value))}%")

    def on_quit(self):
        """Handle quit button - stop speech and close window"""
        self.tts_engine.stop()
        self.root.quit()


def main():
    root = tk.Tk()
    app = MemorizingCoachApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
