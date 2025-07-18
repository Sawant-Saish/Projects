import tkinter as tk
from tkinter import ttk, messagebox
import requests
import pyperclip
import random

# Mood to keyword mapping
mood_keywords = {
    "Happy": "happiness",
    "Sad": "hope",
    "Angry": "peace",
    "Anxious": "calm",
    "Motivated": "success",
    "Tired": "inspiration",
    "Lonely": "life",
    "Love": "love"
}

# Light/Dark Theme Colors
themes = {
    "light": {
        "bg": "#f5f5f5", "fg": "#000000", "button": "#e0e0e0", "entry": "#ffffff"
    },
    "dark": {
        "bg": "#1e1e1e", "fg": "#ffffff", "button": "#333333", "entry": "#2e2e2e"
    }
}

class QuoteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mood-Based Quote Generator")
        self.root.geometry("600x400")
        self.current_theme = "light"

        self.style = ttk.Style()
        self.set_theme()

        self.create_widgets()

    def set_theme(self):
        theme = themes[self.current_theme]
        self.root.configure(bg=theme["bg"])
        self.style.configure("TLabel", background=theme["bg"], foreground=theme["fg"])
        self.style.configure("TButton", background=theme["button"], foreground=theme["fg"])
        self.style.configure("TCombobox", fieldbackground=theme["entry"], background=theme["entry"], foreground=theme["fg"])

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.set_theme()
        self.create_widgets()

    def create_widgets(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        ttk.Label(self.root, text="Select Your Mood:", font=("Helvetica", 14)).pack(pady=10)

        self.mood_var = tk.StringVar()
        self.mood_dropdown = ttk.Combobox(self.root, textvariable=self.mood_var, state="readonly", values=list(mood_keywords.keys()))
        self.mood_dropdown.current(0)
        self.mood_dropdown.pack(pady=10)

        ttk.Button(self.root, text="Get Quote", command=self.get_quote).pack(pady=10)
        self.quote_text = tk.Text(self.root, wrap="word", height=6, width=60, font=("Helvetica", 12), bg=themes[self.current_theme]["entry"], fg=themes[self.current_theme]["fg"])
        self.quote_text.pack(pady=10)

        button_frame = tk.Frame(self.root, bg=themes[self.current_theme]["bg"])
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Copy to Clipboard", command=self.copy_quote).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Save to Favorites", command=self.save_quote).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Toggle Theme", command=self.toggle_theme).pack(side="left", padx=10)

    def get_quote(self):
        mood = self.mood_var.get()
        keyword = mood_keywords.get(mood, "inspiration")

        try:
            response = requests.get("https://zenquotes.io/api/quotes/")
            quotes = response.json()

            matched = [q for q in quotes if keyword in q["q"].lower() or keyword in q["a"].lower()]
            quote = random.choice(matched if matched else quotes)
            self.full_quote = f'"{quote["q"]}" — {quote["a"]}'

            self.quote_text.delete("1.0", tk.END)
            self.quote_text.insert(tk.END, self.full_quote)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch quote.\n{e}")

    def copy_quote(self):
        if hasattr(self, "full_quote"):
            pyperclip.copy(self.full_quote)
            messagebox.showinfo("Copied", "Quote copied to clipboard!")

    def save_quote(self):
        if hasattr(self, "full_quote"):
            with open("favorites.txt", "a", encoding="utf-8") as file:
                file.write(self.full_quote + "\n\n")
            messagebox.showinfo("Saved", "Quote saved to favorites.txt!")


if __name__ == "__main__":
    root = tk.Tk()
    app = QuoteApp(root)
    root.mainloop()
