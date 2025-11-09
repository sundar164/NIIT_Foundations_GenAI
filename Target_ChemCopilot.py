import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import matplotlib.patches as patches
from matplotlib.patches import Circle
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time
import sys
import platform

# Voice packages
try:
    import speech_recognition as sr
    import pyttsx3

    VOICE_AVAILABLE = True
    print("✅ Voice packages loaded successfully!")
except ImportError as e:
    VOICE_AVAILABLE = False
    print(f"❌ Voice packages not available: {e}")


class MolecularCopilot:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Interactive Molecular Visualization with Voice AI Copilot")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')

        # Animation control
        self.animation_running = True
        self.current_angle = 0

        # Annotation system - simplified approach
        self.annotations = []
        self.annotation_mode = False
        self.click_points = []
        self.current_annotation_id = 0

        # Voice AI system
        self.voice_enabled = False
        if VOICE_AVAILABLE:
            self.setup_voice_ai()

        self.setup_ui()
        self.setup_molecule()
        self.start_animation()

    def setup_voice_ai(self):
        """Initialize voice recognition and text-to-speech with better error handling"""
        try:
            print("Setting up voice AI...")

            # Initialize speech recognition
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()

            # Initialize text-to-speech with platform-specific settings
            self.tts_engine = pyttsx3.init()

            # Configure TTS engine
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Try to set a voice (prefer female voice if available)
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
                else:
                    self.tts_engine.setProperty('voice', voices[0].id)

            # Set speech rate and volume
            self.tts_engine.setProperty('rate', 180)  # Speed of speech
            self.tts_engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)

            # Test TTS
            print("Testing text-to-speech...")

            # Adjust microphone for ambient noise
            print("Adjusting microphone for ambient noise...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)

            self.voice_enabled = True
            print("✅ Voice AI setup complete!")

            # Test voice on startup
            threading.Thread(target=lambda: self.speak("Voice AI ready!"), daemon=True).start()

        except Exception as e:
            print(f"❌ Voice setup failed: {e}")
            self.voice_enabled = False

    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Top control panel
        control_panel = ttk.Frame(main_frame)
        control_panel.pack(fill=tk.X, pady=(0, 10))

        # Voice/AI Button
        if self.voice_enabled:
            self.ai_btn = ttk.Button(control_panel, text="🎤 Voice AI (Click & Speak)",
                                     command=self.start_voice_interaction, style="Accent.TButton")
            self.ai_status = ttk.Label(control_panel, text="🔊 Voice AI Ready", foreground="green")
        else:
            self.ai_btn = ttk.Button(control_panel, text="💬 Text AI Chat",
                                     command=self.open_text_chat, style="Accent.TButton")
            self.ai_status = ttk.Label(control_panel, text="💬 Text AI Ready", foreground="blue")

        self.ai_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.ai_status.pack(side=tk.LEFT, padx=(0, 20))

        # Test Voice Button (if voice enabled)
        if self.voice_enabled:
            self.test_voice_btn = ttk.Button(control_panel, text="🔊 Test Voice",
                                             command=self.test_voice)
            self.test_voice_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Animation controls
        self.pause_btn = ttk.Button(control_panel, text="⏸️ Pause", command=self.toggle_animation)
        self.pause_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.reset_btn = ttk.Button(control_panel, text="🔄 Reset View", command=self.reset_view)
        self.reset_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Annotation controls
        self.annotate_btn = ttk.Button(control_panel, text="✏️ Click to Annotate",
                                       command=self.toggle_annotation_mode)
        self.annotate_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.clear_annotations_btn = ttk.Button(control_panel, text="🗑️ Clear Annotations",
                                                command=self.clear_annotations)
        self.clear_annotations_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Status label
        self.status_label = ttk.Label(control_panel, text="Ready - Click atoms or use voice commands")
        self.status_label.pack(side=tk.RIGHT)

        # Content frame
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Left side - 3D visualization
        viz_frame = ttk.LabelFrame(content_frame, text="3D Molecular Structure - Click on Atoms to Annotate",
                                   padding=10)
        viz_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Create matplotlib figure
        self.fig = plt.Figure(figsize=(10, 8), facecolor='white')
        self.ax = self.fig.add_subplot(111, projection='3d')

        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, viz_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Right side - Information panel
        info_frame = ttk.LabelFrame(content_frame, text="Molecular Information & AI Responses", padding=10)
        info_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        info_frame.configure(width=400)

        # Molecular info
        self.info_text = scrolledtext.ScrolledText(info_frame, height=18, width=50, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # AI Response area
        ai_type = "Voice AI 🔊" if self.voice_enabled else "Text AI 💬"
        response_label = ttk.Label(info_frame, text=f"🤖 {ai_type} Responses:")
        response_label.pack(anchor=tk.W)

        self.response_text = scrolledtext.ScrolledText(info_frame, height=14, width=50, wrap=tk.WORD,
                                                       bg='#e8f4fd', fg='#2c3e50')
        self.response_text.pack(fill=tk.BOTH, expand=True)

        # Load initial molecular information
        self.load_molecular_info()

        # Bottom panel for quick actions
        bottom_panel = ttk.Frame(main_frame)
        bottom_panel.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(bottom_panel, text="Quick Actions:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

        quick_actions = [
            ("🔬 Explain Carbonyl", lambda: self.quick_explain("carbonyl")),
            ("⚛️ Show Mechanism", lambda: self.quick_explain("mechanism")),
            ("📊 Properties", lambda: self.quick_explain("properties")),
            ("🧬 Biology", lambda: self.quick_explain("biology"))
        ]

        for text, command in quick_actions:
            ttk.Button(bottom_panel, text=text, command=command).pack(side=tk.LEFT, padx=(10, 0))

        # Setup mouse events for annotation
        self.setup_click_events()

    def setup_click_events(self):
        """Setup mouse click events for atom selection"""
        self.canvas.mpl_connect('button_press_event', self.on_atom_click)

    def on_atom_click(self, event):
        """Handle mouse clicks on atoms"""
        if not self.annotation_mode or not event.inaxes:
            return

        if event.xdata is None or event.ydata is None:
            return

        # Find the closest atom to the click
        click_point = np.array([event.xdata, event.ydata])
        min_distance = float('inf')
        closest_atom = None

        # Get current rotated atom positions (2D projection)
        rotation_matrix = np.array([
            [np.cos(self.current_angle), -np.sin(self.current_angle), 0],
            [np.sin(self.current_angle), np.cos(self.current_angle), 0],
            [0, 0, 1]
        ])

        for name, pos in self.atoms.items():
            rotated_pos = rotation_matrix @ pos
            # Use only x, y coordinates for distance calculation
            atom_2d = np.array([rotated_pos[0], rotated_pos[1]])
            distance = np.linalg.norm(click_point - atom_2d)

            if distance < min_distance and distance < 0.8:  # Threshold for click detection
                min_distance = distance
                closest_atom = name

        if closest_atom:
            self.annotate_atom(closest_atom)

    def annotate_atom(self, atom_name):
        """Annotate a specific atom"""
        atom_type = self.get_atom_type(atom_name)

        # Create annotation marker
        annotation = {
            'atom': atom_name,
            'type': atom_type,
            'id': self.current_annotation_id
        }

        self.annotations.append(annotation)
        self.current_annotation_id += 1

        # Provide AI response
        self.analyze_atom_click(atom_name, atom_type)

        # Update status
        self.status_label.config(text=f"Annotated {atom_name} ({atom_type})")

        # Redraw molecule with annotation
        self.plot_molecule(self.current_angle)

    def analyze_atom_click(self, atom_name, atom_type):
        """Provide AI analysis of clicked atom"""
        responses = []

        if atom_type == 'C':
            if atom_name in ['C2']:  # Carbonyl carbon
                responses = [
                    f"🎯 You clicked on {atom_name} - a carbonyl carbon!",
                    "This carbon is highly electrophilic due to the C=O double bond.",
                    "It's a key reactive site for nucleophilic attacks.",
                    "The electron-withdrawing oxygen makes this carbon δ+ (partially positive)."
                ]
            else:
                responses = [
                    f"🎯 You clicked on {atom_name} - a carbon atom!",
                    "Carbon forms the backbone of organic molecules.",
                    "This carbon participates in the molecular framework.",
                    "It can form up to 4 covalent bonds with other atoms."
                ]

        elif atom_type == 'O':
            responses = [
                f"🎯 You clicked on {atom_name} - an oxygen atom!",
                "Oxygen is highly electronegative and pulls electron density.",
                "In C=O bonds, oxygen is nucleophilic and can accept protons.",
                "This creates the polar character of the carbonyl group."
            ]

        elif atom_type == 'N':
            responses = [
                f"🎯 You clicked on {atom_name} - a nitrogen atom!",
                "Nitrogen can act as a base due to its lone pair electrons.",
                "In amide bonds, nitrogen's basicity is reduced by resonance.",
                "This stabilizes the peptide structure significantly."
            ]

        elif atom_type == 'S':
            responses = [
                f"🎯 You clicked on {atom_name} - a sulfur atom!",
                "Sulfur provides flexibility to the molecular structure.",
                "It can form disulfide bridges with other sulfur atoms.",
                "Thioether linkages are important in protein chemistry."
            ]

        # Add responses and speak them
        for response in responses:
            self.add_ai_response(response)

        if self.voice_enabled:
            combined_response = " ".join(responses)
            threading.Thread(target=lambda: self.speak(combined_response), daemon=True).start()

    def setup_molecule(self):
        # Define atomic coordinates for the molecule
        self.atoms = {
            'C1': np.array([0, 0, 0]),
            'C2': np.array([1.5, 0, 0]),  # Carbonyl carbon
            'O1': np.array([2.5, 0, 0.5]),  # Carbonyl oxygen
            'N1': np.array([1.5, -1.2, 0]),
            'C3': np.array([0, -1.5, 0.5]),
            'C4': np.array([-1, -0.8, 0.2]),
            'S1': np.array([-2.2, -1.2, 0.8]),  # Sulfur
            'C5': np.array([-3, 0, 0.5]),
            'C6': np.array([-3.5, 1, 1.2]),
            'N2': np.array([-4.5, 1.5, 1.5]),  # Second nitrogen
            'O2': np.array([-4.8, 2.5, 1.8]),  # Second oxygen
            'C7': np.array([0.75, 1.3, 0]),
            'C8': np.array([-0.5, 1.8, 0.3]),
            'C9': np.array([2.5, -1.5, -0.5]),
        }

        self.bonds = [
            ('C1', 'C2'), ('C2', 'O1'), ('C2', 'N1'), ('N1', 'C3'),
            ('C3', 'C4'), ('C4', 'S1'), ('S1', 'C5'), ('C5', 'C6'),
            ('C6', 'N2'), ('N2', 'O2'), ('C1', 'C7'), ('C1', 'C8'),
            ('N1', 'C9'), ('C3', 'C1')
        ]

        self.atom_colors = {
            'C': '#404040', 'O': '#FF0000', 'N': '#0000FF', 'S': '#FFFF00'
        }

        self.atom_sizes = {
            'C': 150, 'O': 180, 'N': 160, 'S': 200  # Larger sizes for easier clicking
        }

    def get_atom_type(self, atom_name):
        return atom_name[0]

    def plot_molecule(self, angle=0):
        self.ax.clear()

        # Rotate the molecule
        rotation_matrix = np.array([
            [np.cos(angle), -np.sin(angle), 0],
            [np.sin(angle), np.cos(angle), 0],
            [0, 0, 1]
        ])

        rotated_atoms = {}
        for name, pos in self.atoms.items():
            rotated_atoms[name] = rotation_matrix @ pos

        # Plot bonds
        for bond in self.bonds:
            atom1, atom2 = bond
            pos1 = rotated_atoms[atom1]
            pos2 = rotated_atoms[atom2]

            if (self.get_atom_type(atom1) == 'C' and self.get_atom_type(atom2) == 'O') or \
                    (self.get_atom_type(atom1) == 'O' and self.get_atom_type(atom2) == 'C'):
                self.ax.plot([pos1[0], pos2[0]], [pos1[1], pos2[1]], [pos1[2], pos2[2]],
                             'r-', linewidth=5, alpha=0.8)
            else:
                self.ax.plot([pos1[0], pos2[0]], [pos1[1], pos2[1]], [pos1[2], pos2[2]],
                             'k-', linewidth=3, alpha=0.6)

        # Plot atoms with larger sizes for easier clicking
        for name, pos in rotated_atoms.items():
            atom_type = self.get_atom_type(name)
            color = self.atom_colors[atom_type]
            size = self.atom_sizes[atom_type]

            # Check if this atom is annotated
            is_annotated = any(ann['atom'] == name for ann in self.annotations)
            if is_annotated:
                # Add a white border for annotated atoms
                self.ax.scatter(pos[0], pos[1], pos[2], c='white', s=size * 1.5, alpha=1.0, edgecolors='red',
                                linewidth=3)

            self.ax.scatter(pos[0], pos[1], pos[2], c=color, s=size, alpha=0.9, edgecolors='black', linewidth=2)
            self.ax.text(pos[0], pos[1], pos[2], f'  {name}', fontsize=10, fontweight='bold', alpha=0.8)

        # Set axis properties
        self.ax.set_xlim([-5, 3])
        self.ax.set_ylim([-3, 4])
        self.ax.set_zlim([-1, 3])
        self.ax.set_xlabel('X', fontsize=12)
        self.ax.set_ylabel('Y', fontsize=12)
        self.ax.set_zlabel('Z', fontsize=12)

        title_suffix = "🔊 Voice Enabled" if self.voice_enabled else "💬 Text Mode"
        self.ax.set_title(f'Interactive 3D Molecular Structure - {title_suffix}\nClick on atoms to annotate!',
                          fontsize=14, fontweight='bold')
        self.ax.grid(True, alpha=0.3)

        # Make atoms more visible
        self.ax.view_init(elev=20, azim=angle * 180 / np.pi)

        self.canvas.draw()

    def start_animation(self):
        """Start the animation in a separate thread"""

        def animate():
            while True:
                if self.animation_running:
                    self.current_angle += 0.02  # Slower rotation for easier clicking
                    self.root.after_idle(lambda: self.plot_molecule(self.current_angle))
                time.sleep(0.1)

        self.animation_thread = threading.Thread(target=animate, daemon=True)
        self.animation_thread.start()

    def toggle_animation(self):
        self.animation_running = not self.animation_running
        if self.animation_running:
            self.pause_btn.config(text="⏸️ Pause")
            self.status_label.config(text="Animation running - pause for easier clicking")
        else:
            self.pause_btn.config(text="▶️ Play")
            self.status_label.config(text="Animation paused - easier to click atoms")

    def reset_view(self):
        self.current_angle = 0
        self.plot_molecule(0)

    def toggle_annotation_mode(self):
        self.annotation_mode = not self.annotation_mode
        if self.annotation_mode:
            self.annotate_btn.config(text="🚫 Exit Annotate")
            self.status_label.config(text="Annotation mode: Click on atoms to learn about them")
            self.add_ai_response("🎯 Annotation mode enabled! Click on any atom to learn about it.")
            if self.voice_enabled:
                threading.Thread(
                    target=lambda: self.speak("Annotation mode enabled. Click on atoms to learn about them."),
                    daemon=True).start()
        else:
            self.annotate_btn.config(text="✏️ Click to Annotate")
            self.status_label.config(text="Annotation mode disabled")
            self.add_ai_response("📝 Annotation mode disabled.")

    def clear_annotations(self):
        self.annotations.clear()
        self.current_annotation_id = 0
        self.plot_molecule(self.current_angle)
        self.add_ai_response("📝 All annotations cleared!")
        if self.voice_enabled:
            threading.Thread(target=lambda: self.speak("All annotations cleared."), daemon=True).start()

    def test_voice(self):
        """Test the voice system"""
        if self.voice_enabled:
            test_message = "Voice system is working! You can now use voice commands."
            self.add_ai_response(f"🔊 Testing voice: {test_message}")
            threading.Thread(target=lambda: self.speak(test_message), daemon=True).start()
        else:
            messagebox.showwarning("Voice Not Available", "Voice system is not properly initialized.")

    def start_voice_interaction(self):
        """Start voice recognition"""
        if not self.voice_enabled:
            messagebox.showwarning("Voice Not Available", "Voice system not initialized properly.")
            return

        def listen_and_respond():
            try:
                self.ai_status.config(text="🎤 Listening...", foreground="red")
                self.ai_btn.config(text="🎤 Listening... (Speak now)")

                with self.microphone as source:
                    print("Listening for speech...")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)

                self.ai_status.config(text="🔄 Processing...", foreground="orange")
                self.ai_btn.config(text="🔄 Processing...")

                # Recognize speech
                text = self.recognizer.recognize_google(audio).lower()
                print(f"Recognized: {text}")
                self.add_ai_response(f"🗣️ You said: '{text}'")

                # Generate and speak response
                response = self.generate_ai_response(text)
                self.add_ai_response(f"🤖 {response}")
                threading.Thread(target=lambda: self.speak(response), daemon=True).start()

            except sr.WaitTimeoutError:
                self.add_ai_response("⏰ No speech detected. Try again!")
                print("No speech detected")
            except sr.UnknownValueError:
                self.add_ai_response("❓ Could not understand speech. Please try again.")
                print("Could not understand speech")
            except sr.RequestError as e:
                self.add_ai_response(f"❌ Speech service error: {e}")
                print(f"Speech service error: {e}")
            except Exception as e:
                self.add_ai_response(f"❌ Error: {e}")
                print(f"Voice error: {e}")

            finally:
                self.ai_status.config(text="🔊 Voice AI Ready", foreground="green")
                self.ai_btn.config(text="🎤 Voice AI (Click & Speak)")

        threading.Thread(target=listen_and_respond, daemon=True).start()

    def speak(self, text):
        """Convert text to speech with better error handling"""
        if not self.voice_enabled:
            print(f"Voice disabled, would say: {text}")
            return

        try:
            print(f"Speaking: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            print("Speech completed")
        except Exception as e:
            print(f"TTS Error: {e}")
            self.add_ai_response(f"🔇 Voice output failed: {e}")

    def open_text_chat(self):
        """Open text input for AI questions"""
        question = simpledialog.askstring("Ask AI",
                                          "What would you like to know about this molecule?\n\n" +
                                          "Try asking:\n" +
                                          "• 'What is the carbonyl group?'\n" +
                                          "• 'Explain the nitrogen atom'\n" +
                                          "• 'How does this molecule react?'\n" +
                                          "• 'What makes it stable?'")
        if question:
            self.add_ai_response(f"❓ You asked: '{question}'")
            response = self.generate_ai_response(question.lower())
            self.add_ai_response(f"🤖 {response}")
            if self.voice_enabled:
                threading.Thread(target=lambda: self.speak(response), daemon=True).start()

    def quick_explain(self, topic):
        """Quick explanation for topics"""
        explanations = {
            "carbonyl": "The carbonyl group contains a carbon-oxygen double bond. The carbon is electrophilic and attracts nucleophiles, making it highly reactive in organic reactions.",
            "mechanism": "Key mechanisms include nucleophilic addition to carbonyls, where nucleophiles attack the electron-deficient carbon, and hydrolysis reactions that break amide bonds.",
            "properties": "This cyclic dipeptide has multiple functional groups including carbonyls, amides, and thioethers. The ring structure provides enhanced stability compared to linear peptides.",
            "biology": "The cyclic structure provides metabolic stability and resistance to enzymatic degradation. This makes it similar to hormone-like peptides with extended biological activity."
        }

        if topic in explanations:
            response = explanations[topic]
            self.add_ai_response(f"🤖 {response}")
            if self.voice_enabled:
                threading.Thread(target=lambda: self.speak(response), daemon=True).start()

    def generate_ai_response(self, user_input):
        """Generate AI response based on input"""
        input_lower = user_input.lower()

        if any(word in input_lower for word in ['carbonyl', 'carbon oxygen', 'double bond', 'c=o']):
            return (
                "The carbonyl group is highly electrophilic due to the electronegativity difference between carbon and oxygen. This creates a partial positive charge on carbon, making it susceptible to nucleophilic attack.")

        elif any(word in input_lower for word in ['nitrogen', 'amine', 'basic', 'n']):
            return (
                "Nitrogen atoms have lone pair electrons that can act as bases or nucleophiles. In amide bonds, the nitrogen's basicity is reduced due to resonance with the carbonyl group.")

        elif any(word in input_lower for word in ['sulfur', 'thioether', 'disulfide', 's']):
            return (
                "The sulfur atom provides molecular flexibility and can participate in disulfide bridge formation. Thioether linkages are important for protein structure and stability.")

        elif any(word in input_lower for word in ['stable', 'stability', 'cyclic', 'ring']):
            return (
                "The cyclic structure enhances metabolic stability by protecting the peptide bonds from enzymatic cleavage. This cyclization is a common strategy in drug design.")

        elif any(word in input_lower for word in ['reaction', 'mechanism', 'react', 'how']):
            return (
                "Key reactions include nucleophilic addition to carbonyls, hydrolysis of amide bonds, and potential cyclization reactions. Each involves specific electron movements and intermediate formations.")

        elif any(word in input_lower for word in ['biological', 'hormone', 'activity', 'biology']):
            return (
                "This molecule resembles hormone-like peptides with potential receptor binding activity. The cyclic structure enhances biological specificity and extends duration of action.")

        elif any(word in input_lower for word in ['oxygen', 'o']):
            return (
                "Oxygen atoms are highly electronegative and create polar bonds. In carbonyl groups, oxygen acts as a nucleophilic center and can accept protons in acidic conditions.")

        else:
            return (
                "That's an interesting question! This cyclic dipeptide contains carbonyls, amides, and thioethers. Try clicking on specific atoms to learn more, or ask about particular functional groups!")

    def add_ai_response(self, message):
        """Add response to the AI response area"""
        self.response_text.insert(tk.END, f"{message}\n\n")
        self.response_text.see(tk.END)
        self.root.update_idletasks()  # Force UI update

    def load_molecular_info(self):
        """Load molecular information"""
        voice_status = "🔊 Voice AI Enabled!" if self.voice_enabled else "💬 Text Mode Only"

        info_content = f"""🧬 MOLECULAR INFORMATION

{voice_status}

SMILES: CC(C)C1C(=O)N[C@@H](CSCC(N)=O)C(=O)N1C

🔬 KEY FUNCTIONAL GROUPS:
• C=O (Carbonyl): Highly electrophilic carbon
• C-N (Amide): Partial double bond character  
• C-S (Thioether): Sulfur linkage
• Chiral centers: Stereochemistry important

⚛️ CARBON-OXYGEN DOUBLE BOND (C=O):
• Bond length: ~1.23 Å
• Bond strength: ~745 kJ/mol
• Highly polar (δ+C=Oδ-)

🎯 HOW TO INTERACT:
1. 🎤 Use Voice AI to ask questions
2. ✏️ Click "Click to Annotate" then click atoms
3. 📖 Use quick action buttons below
4. ⏸️ Pause animation for easier clicking

🎮 VOICE COMMANDS TO TRY:
• "What is the carbonyl group?"
• "Explain the nitrogen atom"
• "How does this molecule react?"
• "What makes it stable?"
• "Tell me about the sulfur"

💡 TIP: Click directly on atoms (the colored spheres)
   to get detailed explanations!

🔧 TROUBLESHOOTING:
• Pause animation for easier atom clicking
• Use "Test Voice" button to check audio
• Try text mode if voice issues persist
"""

        self.info_text.insert(tk.END, info_content)
        self.info_text.config(state=tk.DISABLED)

    def run(self):
        """Start the application"""
        self.plot_molecule(0)

        if self.voice_enabled:
            welcome_msg = "🤖 Welcome! Voice AI ready. Click atoms or use voice commands to explore!"
            threading.Thread(target=lambda: self.speak(
                "Welcome! Voice AI ready. Click on atoms or ask questions to explore the molecule."),
                             daemon=True).start()
        else:
            welcome_msg = "🤖 Welcome! Click atoms or use text chat to explore the molecule!"

        self.add_ai_response(welcome_msg)
        self.root.mainloop()


# Create and run the application
if __name__ == "__main__":
    print("=" * 60)
    print("🧬 MOLECULAR COPILOT STARTING...")
    print("=" * 60)

    if VOICE_AVAILABLE:
        print("✅ Voice packages found!")
        print("🔧 Initializing voice system...")
    else:
        print("❌ Voice packages not available")
        print("📦 Install with: pip install SpeechRecognition pyttsx3")

    print("🚀 Starting application...")
    print("=" * 60)

    try:
        app = MolecularCopilot()
        app.run()
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()
