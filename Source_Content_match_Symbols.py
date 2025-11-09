import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from difflib import SequenceMatcher
class AdvancedContentMatchingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Content Matching Score Calculator")
        self.root.geometry("900x700")

        # Configure style
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Result.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Score.TLabel', font=('Arial', 12))

        # Main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="Advanced Content Matching Score Calculator",
                                style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Reference text section
        ref_label = ttk.Label(main_frame, text="Reference Text:", style='Header.TLabel')
        ref_label.grid(row=1, column=0, sticky=(tk.W), pady=(0, 5))

        self.ref_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD,
                                                  width=40, height=10)
        self.ref_text.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S),
                           padx=(0, 10), pady=(0, 20))

        # Student text section
        student_label = ttk.Label(main_frame, text="Student Text:", style='Header.TLabel')
        student_label.grid(row=1, column=1, sticky=(tk.W), pady=(0, 5))

        self.student_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD,
                                                      width=40, height=10)
        self.student_text.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S),
                               padx=(10, 0), pady=(0, 20))

        # Configure row weight for text areas
        main_frame.rowconfigure(2, weight=1)

        # Symbol Helper Buttons
        symbols_frame = ttk.LabelFrame(main_frame, text="Symbols Helper", padding="5")
        symbols_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # Math Symbols Button
        self.math_btn = ttk.Button(symbols_frame, text="Math Symbols",
                                   command=self.show_math_symbols)
        self.math_btn.grid(row=0, column=0, padx=5, pady=5)

        # Chemistry Symbols Button
        self.chem_btn = ttk.Button(symbols_frame, text="Chemistry Symbols",
                                   command=self.show_chemistry_symbols)
        self.chem_btn.grid(row=0, column=1, padx=5, pady=5)

        # Physics Symbols Button
        self.physics_btn = ttk.Button(symbols_frame, text="Physics Symbols",
                                      command=self.show_physics_symbols)
        self.physics_btn.grid(row=0, column=2, padx=5, pady=5)

        # Example Equations Button
        self.eqn_btn = ttk.Button(symbols_frame, text="Example Equations",
                                  command=self.show_equation_examples)
        self.eqn_btn.grid(row=0, column=3, padx=5, pady=5)

        # Calculate button
        self.calculate_btn = ttk.Button(main_frame, text="Calculate Matching Score",
                                        command=self.calculate_score,
                                        style='AccentButton.TButton')
        self.calculate_btn.grid(row=4, column=0, columnspan=2, pady=(10, 20))

        # Result display frame
        result_frame = ttk.LabelFrame(main_frame, text="Detailed Results", padding="10")
        result_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E),
                          pady=(0, 10))

        # Overall score label
        self.overall_score_label = ttk.Label(result_frame, text="Overall Score: --",
                                             style='Result.TLabel')
        self.overall_score_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))

        # Individual scores frame
        scores_frame = ttk.Frame(result_frame)
        scores_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))

        # Create labels for different matching algorithms
        self.exact_match_label = ttk.Label(scores_frame, text="Exact Match: --",
                                           style='Score.TLabel')
        self.exact_match_label.grid(row=0, column=0, sticky=(tk.W), padx=(0, 30), pady=2)

        self.sequence_match_label = ttk.Label(scores_frame, text="Sequence Match: --",
                                              style='Score.TLabel')
        self.sequence_match_label.grid(row=0, column=1, sticky=(tk.W), padx=(0, 30), pady=2)

        self.word_match_label = ttk.Label(scores_frame, text="Word Overlap: --",
                                          style='Score.TLabel')
        self.word_match_label.grid(row=1, column=0, sticky=(tk.W), padx=(0, 30), pady=2)

        self.char_match_label = ttk.Label(scores_frame, text="Character Match: --",
                                          style='Score.TLabel')
        self.char_match_label.grid(row=1, column=1, sticky=(tk.W), padx=(0, 30), pady=2)

        # Add new symbol match label
        self.symbol_match_label = ttk.Label(scores_frame, text="Symbol Match: --",
                                            style='Score.TLabel')
        self.symbol_match_label.grid(row=2, column=0, sticky=(tk.W), padx=(0, 30), pady=2)

        # Progress bar for visual representation
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(result_frame, variable=self.progress_var,
                                            maximum=100, length=400)
        self.progress_bar.grid(row=2, column=0, columnspan=2, pady=(15, 10))

        # Grade label
        self.grade_label = ttk.Label(result_frame, text="Grade: --",
                                     style='Result.TLabel')
        self.grade_label.grid(row=3, column=0, columnspan=2, pady=(5, 0))

        # Clear and Example buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=(10, 0))

        self.clear_btn = ttk.Button(button_frame, text="Clear All",
                                    command=self.clear_all)
        self.clear_btn.grid(row=0, column=0, padx=5)

        self.example_btn = ttk.Button(button_frame, text="Load Example",
                                      command=self.load_example)
        self.example_btn.grid(row=0, column=1, padx=5)

        # Define scientific symbols dictionaries
        self.setup_scientific_symbols()

    def setup_scientific_symbols(self):
        """Define the scientific symbols for matching"""
        # Math symbols
        self.math_symbols = {
            '±': 'plus-minus',
            '∓': 'minus-plus',
            '×': 'multiplication',
            '÷': 'division',
            '√': 'square root',
            '∛': 'cube root',
            '∞': 'infinity',
            '∑': 'summation',
            '∏': 'product',
            '∫': 'integral',
            '∂': 'partial derivative',
            '∇': 'nabla/del',
            '∆': 'delta/change',
            '≠': 'not equal',
            '≈': 'approximately equal',
            '≤': 'less than or equal',
            '≥': 'greater than or equal',
            '∝': 'proportional to',
            '∈': 'element of',
            '∉': 'not element of',
            '⊂': 'subset of',
            '⊃': 'superset of',
            '∩': 'intersection',
            '∪': 'union',
            '∠': 'angle',
            'π': 'pi',
            'θ': 'theta',
            'α': 'alpha',
            'β': 'beta',
            'γ': 'gamma',
            'δ': 'delta',
            'ε': 'epsilon',
            'λ': 'lambda',
            'μ': 'mu',
            'σ': 'sigma',
            'Σ': 'capital sigma',
            'Π': 'capital pi',
            '∀': 'for all',
            '∃': 'there exists',
            '∄': 'there does not exist',
            '⇒': 'implies',
            '⇔': 'if and only if',
            '⊕': 'direct sum',
            '⊗': 'tensor product'
        }

        # Chemistry symbols
        self.chemistry_symbols = {
            '→': 'reaction arrow',
            '⇌': 'equilibrium',
            '↑': 'gas evolution',
            '↓': 'precipitation',
            'Δ': 'heat',
            '⊝': 'negative charge',
            '⊕': 'positive charge',
            '∘': 'degree',
            '°': 'degree celsius',
            'ρ': 'density',
            'φ': 'quantum yield',
            'η': 'viscosity',
            'λ': 'wavelength',
            'ν': 'frequency',
            '⇋': 'resonance',
            '⇄': 'reversible reaction',
            '≐': 'equal by definition',
            '≡': 'identical to',
            '₁': 'subscript 1',
            '₂': 'subscript 2',
            '₃': 'subscript 3',
            '₄': 'subscript 4',
            '⁰': 'superscript 0',
            '¹': 'superscript 1',
            '²': 'superscript 2',
            '³': 'superscript 3',
            '⁴': 'superscript 4',
            '⁺': 'superscript plus',
            '⁻': 'superscript minus'
        }

        # Physics symbols
        self.physics_symbols = {
            'α': 'alpha particle',
            'β': 'beta particle',
            'γ': 'gamma radiation',
            'λ': 'wavelength',
            'μ': 'coefficient of friction',
            'ω': 'angular velocity',
            'τ': 'torque',
            'ρ': 'density',
            'σ': 'stress',
            'ε': 'strain',
            'η': 'efficiency',
            'θ': 'angle',
            'Φ': 'magnetic flux',
            '∂': 'partial derivative',
            '∇': 'nabla/del',
            '∆': 'change in',
            '∑': 'sum',
            '∏': 'product',
            '∫': 'integral',
            '∮': 'closed integral',
            '∞': 'infinity',
            'Ω': 'ohm',
            '→': 'vector',
            '⊥': 'perpendicular',
            '∥': 'parallel',
            '≈': 'approximately equal',
            '≠': 'not equal',
            '≡': 'identical to',
            '≤': 'less than or equal',
            '≥': 'greater than or equal'
        }

        # Combined symbols for matching
        self.all_symbols = {}
        self.all_symbols.update(self.math_symbols)
        self.all_symbols.update(self.chemistry_symbols)
        self.all_symbols.update(self.physics_symbols)

        # Example equations
        self.example_equations = [
            "E = mc²",
            "F = ma",
            "PV = nRT",
            "C₆H₁₂O₆ + 6O₂ → 6CO₂ + 6H₂O",
            "∫₀^π sin(x) dx = 2",
            "∇ × B = μ₀J + μ₀ε₀∂E/∂t",
            "2H₂ + O₂ → 2H₂O",
            "pH = -log₁₀[H⁺]"
        ]

    def show_math_symbols(self):
        """Display math symbols in a new window"""
        symbols_window = tk.Toplevel(self.root)
        symbols_window.title("Math Symbols")
        symbols_window.geometry("500x400")

        # Create a frame for the symbols
        frame = ttk.Frame(symbols_window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        # Create a scrollable text widget
        symbols_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=60, height=20)
        symbols_text.pack(fill=tk.BOTH, expand=True)

        # Insert symbols and their descriptions
        for symbol, description in self.math_symbols.items():
            symbols_text.insert(tk.END, f"{symbol} : {description}\n")

        # Make the text widget read-only
        symbols_text.config(state=tk.DISABLED)

        # Add a copy button for convenience
        def copy_selected():
            selected_text = symbols_text.selection_get()
            if selected_text:
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)

        copy_btn = ttk.Button(frame, text="Copy Selected", command=copy_selected)
        copy_btn.pack(pady=10)

    def show_chemistry_symbols(self):
        """Display chemistry symbols in a new window"""
        symbols_window = tk.Toplevel(self.root)
        symbols_window.title("Chemistry Symbols")
        symbols_window.geometry("500x400")

        # Create a frame for the symbols
        frame = ttk.Frame(symbols_window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        # Create a scrollable text widget
        symbols_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=60, height=20)
        symbols_text.pack(fill=tk.BOTH, expand=True)

        # Insert symbols and their descriptions
        for symbol, description in self.chemistry_symbols.items():
            symbols_text.insert(tk.END, f"{symbol} : {description}\n")

        # Make the text widget read-only
        symbols_text.config(state=tk.DISABLED)

        # Add a copy button for convenience
        def copy_selected():
            selected_text = symbols_text.selection_get()
            if selected_text:
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)

        copy_btn = ttk.Button(frame, text="Copy Selected", command=copy_selected)
        copy_btn.pack(pady=10)

    def show_physics_symbols(self):
        """Display physics symbols in a new window"""
        symbols_window = tk.Toplevel(self.root)
        symbols_window.title("Physics Symbols")
        symbols_window.geometry("500x400")

        # Create a frame for the symbols
        frame = ttk.Frame(symbols_window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        # Create a scrollable text widget
        symbols_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=60, height=20)
        symbols_text.pack(fill=tk.BOTH, expand=True)

        # Insert symbols and their descriptions
        for symbol, description in self.physics_symbols.items():
            symbols_text.insert(tk.END, f"{symbol} : {description}\n")

        # Make the text widget read-only
        symbols_text.config(state=tk.DISABLED)

        # Add a copy button for convenience
        def copy_selected():
            selected_text = symbols_text.selection_get()
            if selected_text:
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)

        copy_btn = ttk.Button(frame, text="Copy Selected", command=copy_selected)
        copy_btn.pack(pady=10)

    def show_equation_examples(self):
        """Display example equations in a new window"""
        examples_window = tk.Toplevel(self.root)
        examples_window.title("Example Equations")
        examples_window.geometry("500x400")

        # Create a frame for the examples
        frame = ttk.Frame(examples_window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        # Create a scrollable text widget
        examples_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=60, height=20)
        examples_text.pack(fill=tk.BOTH, expand=True)

        # Insert example equations
        examples_text.insert(tk.END, "Example Scientific Equations:\n\n")
        for i, equation in enumerate(self.example_equations, 1):
            examples_text.insert(tk.END, f"{i}. {equation}\n\n")

        # Add a button to use the selected equation
        def use_selected():
            try:
                selected_text = examples_text.selection_get()
                # Insert the selected equation into the active text area
                focused_widget = self.root.focus_get()
                if focused_widget == self.ref_text or focused_widget == self.student_text:
                    focused_widget.insert(tk.INSERT, selected_text)
                else:
                    # If no text area is focused, default to reference text
                    self.ref_text.insert(tk.INSERT, selected_text)
            except:
                pass  # No selection

        use_btn = ttk.Button(frame, text="Use Selected Equation", command=use_selected)
        use_btn.pack(pady=10)

    def preprocess_text(self, text):
        """Preprocess text for comparison"""
        # Convert to lowercase
        text = text.lower()

        # Remove extra whitespace
        text = ' '.join(text.split())

        return text

    def exact_match_comparison(self, reference_text, student_text):
        """Calculate exact match percentage"""
        ref_processed = self.preprocess_text(reference_text)
        student_processed = self.preprocess_text(student_text)

        if ref_processed == student_processed:
            return 100.0
        else:
            # Instead of returning 0, calculate partial match
            return self.calculate_partial_match(ref_processed, student_processed)

    def calculate_partial_match(self, ref_text, student_text):
        """Calculate partial match using multiple algorithms"""
        scores = {}

        # 1. Sequence Matcher (similar to difflib)
        sequence_ratio = SequenceMatcher(None, ref_text, student_text).ratio()
        scores['sequence'] = sequence_ratio * 100

        # 2. Word-level overlap
        ref_words = set(ref_text.split())
        student_words = set(student_text.split())

        if ref_words:
            word_overlap = len(ref_words.intersection(student_words)) / len(ref_words)
            scores['word'] = word_overlap * 100
        else:
            scores['word'] = 0

        # 3. Character-level similarity
        ref_chars = set(ref_text.replace(' ', ''))
        student_chars = set(student_text.replace(' ', ''))

        if ref_chars:
            char_overlap = len(ref_chars.intersection(student_chars)) / len(ref_chars)
            scores['char'] = char_overlap * 100
        else:
            scores['char'] = 0

        # 4. Symbol matching score
        symbol_score = self.calculate_symbol_match(ref_text, student_text)
        scores['symbol'] = symbol_score

        # 5. Weighted average for overall score
        # Adjust weights based on symbol content
        symbol_content = self.has_scientific_symbols(ref_text)

        if symbol_content:
            # If scientific symbols are present, give more weight to symbol matching
            weights = {
                'sequence': 0.35,
                'word': 0.25,
                'char': 0.15,
                'symbol': 0.25  # Higher weight for symbol matching
            }
        else:
            # Standard weights if no symbols
            weights = {
                'sequence': 0.5,
                'word': 0.3,
                'char': 0.2,
                'symbol': 0.0  # No weight if no symbols
            }

        overall_score = sum(scores[key] * weights[key] for key in scores)

        return overall_score, scores

    def has_scientific_symbols(self, text):
        """Check if the text contains any scientific symbols"""
        for symbol in self.all_symbols.keys():
            if symbol in text:
                return True
        return False

    def calculate_symbol_match(self, ref_text, student_text):
        """Calculate symbol matching score based on scientific symbols"""
        ref_symbols = []
        student_symbols = []

        # Extract symbols from reference text
        for symbol in self.all_symbols.keys():
            if symbol in ref_text:
                ref_symbols.append(symbol)

        # Extract symbols from student text
        for symbol in self.all_symbols.keys():
            if symbol in student_text:
                student_symbols.append(symbol)

        # If no symbols in reference text, return full score
        if not ref_symbols:
            return 100.0

        # Calculate symbol overlap
        symbols_in_both = set(ref_symbols).intersection(set(student_symbols))
        symbol_score = len(symbols_in_both) / len(ref_symbols) * 100

        return symbol_score

    def calculate_detailed_scores(self, reference_text, student_text):
        """Calculate detailed matching scores"""
        ref_processed = self.preprocess_text(reference_text)
        student_processed = self.preprocess_text(student_text)

        # Check for exact match first
        if ref_processed == student_processed:
            return {
                'overall': 100.0,
                'exact': 100.0,
                'sequence': 100.0,
                'word': 100.0,
                'char': 100.0,
                'symbol': 100.0
            }

        # Calculate partial matches
        overall_score, partial_scores = self.calculate_partial_match(ref_processed,
                                                                     student_processed)

        # Calculate raw symbol matching (not preprocessed for case sensitivity)
        symbol_score = self.calculate_symbol_match(reference_text, student_text)

        return {
            'overall': overall_score,
            'exact': 0.0,  # Not an exact match
            'sequence': partial_scores['sequence'],
            'word': partial_scores['word'],
            'char': partial_scores['char'],
            'symbol': symbol_score
        }

    def get_grade(self, score):
        """Convert percentage score to letter grade"""
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "B+"
        elif score >= 80:
            return "B"
        elif score >= 75:
            return "C+"
        elif score >= 70:
            return "C"
        elif score >= 65:
            return "D"
        else:
            return "F"

    def calculate_score(self):
        """Calculate the matching score when button is clicked"""
        # Get text from text areas
        ref_text = self.ref_text.get("1.0", tk.END).strip()
        student_text = self.student_text.get("1.0", tk.END).strip()

        # Check if both texts are provided
        if not ref_text or not student_text:
            messagebox.showwarning("Input Error",
                                   "Please provide both reference and student text.")
            return

        # Calculate detailed scores
        scores = self.calculate_detailed_scores(ref_text, student_text)

        # Update display
        self.overall_score_label.config(text=f"Overall Score: {scores['overall']:.1f}%")
        self.exact_match_label.config(text=f"Exact Match: {scores['exact']:.1f}%")
        self.sequence_match_label.config(text=f"Sequence Match: {scores['sequence']:.1f}%")
        self.word_match_label.config(text=f"Word Overlap: {scores['word']:.1f}%")
        self.char_match_label.config(text=f"Character Match: {scores['char']:.1f}%")
        self.symbol_match_label.config(text=f"Symbol Match: {scores['symbol']:.1f}%")

        # Update progress bar
        self.progress_var.set(scores['overall'])

        # Update grade
        grade = self.get_grade(scores['overall'])
        self.grade_label.config(text=f"Grade: {grade}")

        # Show appropriate message
        if scores['overall'] == 100.0:
            messagebox.showinfo("Perfect Match!",
                                "The student text perfectly matches the reference text!")
        elif scores['overall'] >= 80:
            messagebox.showinfo("Great Match!",
                                f"Very good match!\nOverall Score: {scores['overall']:.1f}%")
        elif scores['overall'] >= 60:
            messagebox.showinfo("Good Match",
                                f"Reasonable match.\nOverall Score: {scores['overall']:.1f}%")
        else:
            messagebox.showinfo("Poor Match",
                                f"Low match score.\nOverall Score: {scores['overall']:.1f}%")

    def clear_all(self):
        """Clear all text fields and results"""
        self.ref_text.delete("1.0", tk.END)
        self.student_text.delete("1.0", tk.END)
        self.overall_score_label.config(text="Overall Score: --")
        self.exact_match_label.config(text="Exact Match: --")
        self.sequence_match_label.config(text="Sequence Match: --")
        self.word_match_label.config(text="Word Overlap: --")
        self.char_match_label.config(text="Character Match: --")
        self.symbol_match_label.config(text="Symbol Match: --")
        self.grade_label.config(text="Grade: --")
        self.progress_var.set(0)

    def load_example(self):
        """Load example texts for demonstration"""
        examples = [
            # Plain text examples
            {
                "ref": "The quick brown fox jumps over the lazy dog.",
                "student": "The quick brown fox jumps over the lazy dog."  # 100% match
            },
            {
                "ref": "The quick brown fox jumps over the lazy dog.",
                "student": "A quick brown fox jumped over the lazy dog."  # ~85% match
            },
            # Math examples
            {
                "ref": "The area of a circle is A = πr².",
                "student": "Area of circle equals π×r²."  # Symbol match
            },
            # Chemistry example
            {
                "ref": "2H₂ + O₂ → 2H₂O",
                "student": "2H₂+O₂ → 2H₂O"  # Chemistry symbols
            },
            # Physics example
            {
                "ref": "F = ma where F is force, m is mass, and a is acceleration.",
                "student": "Force equals mass × acceleration (F=ma)."  # Physics concept
            },
            # Complex equation
            {
                "ref": "∫₀^π sin(x) dx = 2",
                "student": "The integral of sin(x) from 0 to π equals 2."  # Math symbols
            },
            # Multiple scientific symbols
            {
                "ref": "PV = nRT where P is pressure, V is volume, n is moles, R is gas constant, T is temperature.",
                "student": "For ideal gases, P×V = n×R×T"  # Physics/chemistry
            }
        ]

        # Randomly select an example
        import random
        example = random.choice(examples)

        self.clear_all()
        self.ref_text.insert("1.0", example["ref"])
        self.student_text.insert("1.0", example["student"])


def main():
    import tkinter as tk
    from tkinter import ttk, scrolledtext, messagebox
    from difflib import SequenceMatcher

    root = tk.Tk()
    app = AdvancedContentMatchingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
