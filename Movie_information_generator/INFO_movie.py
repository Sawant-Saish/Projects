import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import requests
import json
import random
import os
from io import BytesIO

# -------------------- API CONFIG --------------------
OMDB_API_KEY = "e60dd778"
OMDB_API_URL = "http://www.omdbapi.com/"
HISTORY_FILE = "search_history.json"
FAVORITES_FILE = "favorites.json"

# -------------------- THEME VARIABLES --------------------
BG_MAIN = "#1e1e1e"
BG_FRAME = "#2c2c2c"
FG_TEXT = "#ffffff"
ENTRY_BG = "#333333"
BTN_BG = "#3da58a"
BTN_HOVER = "#50c2a4"
BTN_FG = "#ffffff"
TEXT_BG = "#252525"
TEXT_FG = "#ffffff"
ACCENT_COLOR = "#ff8cbf"
current_dark_mode = True

# -------------------- MOVIE FUNCTIONS --------------------
def fetch_movie_details(title):
    params = {"t": title, "apikey": OMDB_API_KEY}
    try:
        response = requests.get(OMDB_API_URL, params=params)
        return response.json()
    except requests.RequestException as e:
        messagebox.showerror("Network Error", f"Failed to fetch data: {e}")
        return {}

def save_to_history(movie_data):
    if not movie_data.get("Title"):
        return
    history = load_history()
    if not any(m.get("imdbID") == movie_data.get("imdbID") for m in history):
        history.append(movie_data)
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=4)

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def get_unique_genres():
    history = load_history()
    genre_set = set()
    for movie in history:
        genres = movie.get("Genre", "")
        for g in genres.split(","):
            g_clean = g.strip().lower()
            if g_clean:
                genre_set.add(g_clean)
    return sorted(genre_set)

# -------------------- FAVORITES FUNCTIONS --------------------
def load_favorites():
    if not os.path.exists(FAVORITES_FILE):
        return []
    with open(FAVORITES_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_to_favorites(movie_data):
    if not movie_data.get("Title"):
        return
    favorites = load_favorites()
    if not any(m.get("imdbID") == movie_data.get("imdbID") for m in favorites):
        favorites.append(movie_data)
        with open(FAVORITES_FILE, "w") as f:
            json.dump(favorites, f, indent=4)
        messagebox.showinfo("Added to Favorites", f"{movie_data.get('Title')} was added to your favorites.")
    else:
        messagebox.showinfo("Already in Favorites", f"{movie_data.get('Title')} is already in your favorites.")

def show_favorites():
    favorites = load_favorites()
    if not favorites:
        messagebox.showinfo("Favorites", "No favorite movies yet.")
        return
    fav_text = "\n\n".join([f"❤️ {f['Title']} ({f['Year']}) - {f['Genre']}" for f in favorites])
    text_result.delete("1.0", tk.END)
    text_result.insert(tk.END, f"⭐ Favorites List:\n\n{fav_text}")
    poster_label.configure(image="")
    poster_label.image = None

def remove_from_favorites():
    title = entry_movie.get().strip().lower()
    if not title:
        messagebox.showwarning("Input Error", "Enter a movie title to remove.")
        return

    favorites = load_favorites()
    new_favorites = [m for m in favorites if m.get("Title", "").strip().lower() != title]

    if len(new_favorites) == len(favorites):
        messagebox.showinfo("Not Found", f"'{title}' was not found in your favorites.")
    else:
        with open(FAVORITES_FILE, "w") as f:
            json.dump(new_favorites, f, indent=4)
        messagebox.showinfo("Removed", f"'{title}' was removed from your favorites.")


# -------------------- EVENT FUNCTIONS --------------------
def search_movie():
    title = entry_movie.get().strip()
    if not title:
        messagebox.showwarning("Input Error", "Please enter a movie title.")
        return
    data = fetch_movie_details(title)
    if data.get("Response") == "True":
        display_movie_info(data)
        save_to_history(data)
        update_genre_options()
    else:
        messagebox.showerror("Error", f"Movie not found: {data.get('Error')}")

def display_movie_info(data):
    info = (
        f"\n🎬 Title: {data.get('Title')}\n"
        f"📅 Year: {data.get('Year')}\n"
        f"⭐ Rating: {data.get('imdbRating')}\n"
        f"🎭 Genre: {data.get('Genre')}\n"
        f"🎬 Director: {data.get('Director')}\n"
        f"📝 Plot: {data.get('Plot')}\n"
    )
    text_result.delete("1.0", tk.END)
    text_result.insert(tk.END, info)

    poster_url = data.get("Poster")
    if poster_url and poster_url != "N/A":
        try:
            img_data = requests.get(poster_url).content
            img = Image.open(BytesIO(img_data)).resize((140, 200))
            poster_img = ImageTk.PhotoImage(img)
            poster_label.configure(image=poster_img)
            poster_label.image = poster_img
        except:
            poster_label.configure(image="")
            poster_label.image = None
    else:
        poster_label.configure(image="")
        poster_label.image = None

def show_history():
    history = load_history()
    if not history:
        messagebox.showinfo("History", "No search history found.")
        return
    history_text = "\n\n".join([f"🎬 {h['Title']} ({h['Year']}) - {h['Genre']}" for h in history])
    text_result.delete("1.0", tk.END)
    text_result.insert(tk.END, f"📜 Search History:\n\n{history_text}")
    poster_label.configure(image="")
    poster_label.image = None

def recommend_movie():
    selected_genre = genre_combobox.get().strip().lower()
    if not selected_genre:
        messagebox.showinfo("No Genre", "Please select a genre from the dropdown.")
        return

    history = load_history()
    genre_filtered = []

    for movie in history:
        genres = movie.get("Genre", "")
        genre_list = [g.strip().lower() for g in genres.split(",")]
        if selected_genre in genre_list:
            genre_filtered.append(movie)

    if genre_filtered:
        movie = random.choice(genre_filtered)
        display_movie_info(movie)
    else:
        messagebox.showinfo("No Match", f"No movies found with genre: {selected_genre}")

def update_genre_options():
    genres = get_unique_genres()
    genre_combobox["values"] = genres
    if genres:
        genre_combobox.set("")

def delete_history():
    if not os.path.exists(HISTORY_FILE) or not load_history():
        messagebox.showinfo("No History", "There is no history to delete.")
        return

    confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the entire search history?")
    if confirm:
        with open(HISTORY_FILE, "w") as f:
            json.dump([], f)
        messagebox.showinfo("Deleted", "Search history deleted successfully.")
        text_result.delete("1.0", tk.END)
        poster_label.configure(image="")
        poster_label.image = None
        genre_combobox.set("")
        genre_combobox["values"] = []

# -------------------- Hover Animation --------------------
def on_enter(e):
    e.widget.config(bg=BTN_HOVER)
    e.widget.config(font=("Segoe UI", 11, "bold"))

def on_leave(e):
    e.widget.config(bg=BTN_BG)
    e.widget.config(font=("Segoe UI", 10, "bold"))

# ----------------- Theme Switch -----------------
def apply_theme(dark_mode):
    global BG_MAIN, BG_FRAME, FG_TEXT, ENTRY_BG, BTN_BG, BTN_HOVER, BTN_FG, TEXT_BG, TEXT_FG, ACCENT_COLOR, current_dark_mode
    current_dark_mode = dark_mode

    if dark_mode:
        BG_MAIN = "#1e1e1e"
        BG_FRAME = "#2c2c2c"
        FG_TEXT = "#ffffff"
        ENTRY_BG = "#333333"
        BTN_BG = "#3da58a"
        BTN_HOVER = "#50c2a4"
        BTN_FG = "#ffffff"
        TEXT_BG = "#252525"
        TEXT_FG = "#ffffff"
        ACCENT_COLOR = "#ff8cbf"
    else:
        BG_MAIN = "#fdf6f0"
        BG_FRAME = "#f8e8e4"
        FG_TEXT = "#000000"
        ENTRY_BG = "#ffffff"
        BTN_BG = "#b5ead7"
        BTN_HOVER = "#9de7c7"
        BTN_FG = "#000000"
        TEXT_BG = "#fffaf0"
        TEXT_FG = "#000000"
        ACCENT_COLOR = "#ff69b4"

    root.configure(bg=BG_MAIN)
    frame_top.configure(bg=BG_FRAME, fg=ACCENT_COLOR)
    tk.Label(frame_top, text="🎬 Title:", bg=BG_FRAME, fg=FG_TEXT).grid(row=0, column=0, padx=5, sticky="e")
    entry_movie.configure(bg=ENTRY_BG, fg=FG_TEXT, insertbackground=FG_TEXT, highlightcolor=ACCENT_COLOR)

    frame_buttons.configure(bg=BG_MAIN)
    tk.Label(frame_buttons, text="🎭 Recommend Genre:", font=("Segoe UI", 11, "bold"), bg=BG_MAIN, fg=ACCENT_COLOR).grid(row=1, column=0, pady=15)

    for btn in [btn_search, btn_history, btn_delete, btn_recommend, btn_favorite, btn_show_favs, btn_remove_fav, theme_switch_button]:
        btn.configure(bg=BTN_BG, fg=BTN_FG, activebackground=BTN_HOVER)

    style.configure("TLabel", background=BG_FRAME, foreground=FG_TEXT, font=("Segoe UI", 12, "bold"))
    style.configure("TButton", background=BTN_BG, foreground=BTN_FG, font=("Segoe UI", 10, "bold"))
    style.configure("Dark.TCombobox",
                    fieldbackground=ENTRY_BG,
                    background=ENTRY_BG,
                    foreground=FG_TEXT,
                    arrowcolor=ACCENT_COLOR)
    genre_combobox.configure(style="Dark.TCombobox")

    frame_result.configure(bg=BG_FRAME, fg=ACCENT_COLOR)
    frame_inner.configure(bg=BG_FRAME)
    poster_label.configure(bg=BG_FRAME)
    text_result.configure(bg=TEXT_BG, fg=TEXT_FG, insertbackground=FG_TEXT)

    theme_switch_button.config(text="Light Mode" if dark_mode else "Dark Mode")

def toggle_theme():
    apply_theme(not current_dark_mode)

# ----------------- GUI -----------------
root = tk.Tk()
root.title("🎥 Movie Search App")
root.geometry("800x600")

style = ttk.Style()
style.theme_use("default")

# Top frame for movie search
frame_top = tk.LabelFrame(root, text="🔎 Movie Search", padx=10, pady=10,
                          font=("Segoe UI", 13, "bold"))
frame_top.pack(pady=20, fill="x", padx=25)

tk.Label(frame_top, text="🎬 Title:").grid(row=0, column=0, padx=5, sticky="e")
entry_movie = tk.Entry(frame_top, font=("Segoe UI", 12),
                       highlightthickness=1, relief="flat")
entry_movie.grid(row=0, column=1, padx=5, pady=5, columnspan=3, sticky="we")

# Buttons and Genre
frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=10)

btn_remove_fav = tk.Button(frame_buttons, text="🗑️ Remove from Favorites",
                           command=remove_from_favorites, font=("Segoe UI", 10, "bold"),
                           cursor="hand2")
btn_remove_fav.grid(row=2, column=3, pady=10)
btn_remove_fav.bind("<Enter>", on_enter)
btn_remove_fav.bind("<Leave>", on_leave)


btn_search = tk.Button(frame_buttons, text="🔍 Search", command=search_movie, cursor="hand2", font=("Segoe UI", 10, "bold"))
btn_search.grid(row=0, column=0, padx=10, ipadx=10, ipady=5)

btn_history = tk.Button(frame_buttons, text="📜 History", command=show_history, cursor="hand2", font=("Segoe UI", 10, "bold"))
btn_history.grid(row=0, column=1, padx=10, ipadx=10, ipady=5)

btn_delete = tk.Button(frame_buttons, text="🗑️ Delete History", command=delete_history, cursor="hand2", font=("Segoe UI", 10, "bold"))
btn_delete.grid(row=0, column=2, padx=10, ipadx=10, ipady=5)

for btn in [btn_search, btn_history, btn_delete]:
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

tk.Label(frame_buttons, text="🎭 Recommend Genre:", font=("Segoe UI", 11, "bold")).grid(row=1, column=0, pady=15)
genre_combobox = ttk.Combobox(frame_buttons, width=20, font=("Segoe UI", 10), state="readonly")
genre_combobox.grid(row=1, column=1)

btn_recommend = tk.Button(frame_buttons, text="🎲 Recommend", command=recommend_movie, font=("Segoe UI", 10, "bold"), cursor="hand2")
btn_recommend.grid(row=1, column=2, padx=10, ipadx=10, ipady=5)

btn_favorite = tk.Button(frame_buttons, text="❤️ Add to Favorites", command=lambda: save_to_favorites(fetch_movie_details(entry_movie.get())), font=("Segoe UI", 10, "bold"), cursor="hand2")
btn_favorite.grid(row=1, column=3, padx=10, ipadx=10, ipady=5)

for btn in [btn_recommend, btn_favorite]:
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

theme_switch_button = tk.Button(frame_buttons, text="Light Mode", command=toggle_theme, font=("Segoe UI", 10, "bold"), cursor="hand2")
theme_switch_button.grid(row=2, column=1, pady=10)

btn_show_favs = tk.Button(frame_buttons, text="⭐ Show Favorites", command=show_favorites, font=("Segoe UI", 10, "bold"), cursor="hand2")
btn_show_favs.grid(row=2, column=2, pady=10)

for btn in [theme_switch_button, btn_show_favs]:
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

# Movie Info Output
frame_result = tk.LabelFrame(root, text="📋 Movie Info", padx=10, pady=10,
                             font=("Segoe UI", 13, "bold"))
frame_result.pack(padx=25, pady=15, fill="both", expand=True)

frame_inner = tk.Frame(frame_result)
frame_inner.pack(fill="both", expand=True)

poster_label = tk.Label(frame_inner)
poster_label.pack(side="left", padx=10)

text_result = tk.Text(frame_inner, wrap="word", height=15, font=("Consolas", 11),
                      relief="flat", borderwidth=2)
text_result.pack(side="left", fill="both", expand=True, padx=5, pady=5)

apply_theme(dark_mode=True)
update_genre_options()
root.mainloop()
