import os
import time
from collections import defaultdict
from tkinter import filedialog
from pathlib import Path
import wmi
import tkinter as tk
from tkinter import ttk, messagebox

w = wmi.WMI()
WIDTH, HEIGHT = 900, 700

# Modern color scheme
BG_COLOR = "#f0f0f0"
PRIMARY_COLOR = "#4a6fa5"
SECONDARY_COLOR = "#166088"
ACCENT_COLOR = "#ff6b6b"
TEXT_COLOR = "#2d3436"
BUTTON_COLOR = "#4a6fa5"
BUTTON_HOVER = "#3a5a80"
SUCCESS_COLOR = "#00b894"
DANGER_COLOR = "#e17055"


class Game:
    def __init__(self, title, exePath, folderPath, notePath):
        self.title = title
        self.exePath = exePath
        self.folderPath = folderPath
        self.notePath = notePath
        self._root = None

    def is_note_running(self) -> bool:
        for proc in w.Win32_Process():
            if proc.Name.lower() == "notepad.exe" and self.notePath.lower() in proc.CommandLine.lower():
                return True
        return False

    def is_game_running(self) -> bool:
        exe_name = os.path.basename(self.exePath).lower()
        for proc in w.Win32_Process():
            if proc.Name.lower() == exe_name:
                return True
        return False

    def start(self, root=None):
        """Entry point to start the sequence"""
        self._root = root
        try:
            os.startfile(self.notePath)
            self.wait_until_closed(self.is_note_running, "notes", self._after_notes_closed)
        except Exception as e:
            messagebox.showerror("Error", f"Could not start notes: {e}")

    def _after_notes_closed(self):
        try:
            os.startfile(self.exePath)
            self.wait_until_closed(self.is_game_running, "game", self._after_game_closed)
        except Exception as e:
            messagebox.showerror("Error", f"Could not start game: {e}")

    def _after_game_closed(self):
        try:
            os.startfile(self.notePath)
        except Exception as e:
            messagebox.showerror("Error", f"Could not reopen notes: {e}")

    def wait_until_closed(self, check_func, name, callback):
        if check_func():
            self._root.after(1000, lambda: self.wait_until_closed(check_func, name, callback))
        else:
            print(f"{name} closed")
            callback()


def getScriptPath():
    home = Path.home()
    document = home / "Documents"
    path = document / "GameScripts"
    path.mkdir(parents=True, exist_ok=True)
    return path


games = {}

if __name__ == "__main__":

    def show_frame(frame):
        if frame == frame1:
            loadGames()
            reload_gameFrame()
        frame.tkraise()


    def open_file():
        filepath = filedialog.askopenfilename(
            title="Select a file",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if filepath:
            return filepath


    def browse_exe():
        path = filedialog.askopenfilename(
            title="Select Game Executable",
            filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")]
        )
        if path:
            exe_var.set(path)


    def browse_folder():
        path = filedialog.askdirectory(title="Select Game Folder")
        if path:
            folder_var.set(path)


    def add_game(title, gamePath, folderPath, notePath):
        text = f"{title}\n{gamePath}\n{folderPath}\n{notePath}"
        path = getScriptPath()
        filePath = path / f"{title}.txt"

        with open(filePath, "w") as f:
            f.write(text)
        if title not in games:
            games[title] = Game(title, gamePath, folderPath, notePath)


    def create_game(title, gamePath, gameFolderPath):
        notePath = Path(gameFolderPath) / f"{title}.txt"
        with open(notePath, "w") as f:
            f.write(f"This is {title}")
        add_game(title, gamePath, gameFolderPath, str(notePath))


    def submit():
        title = title_var.get().strip()
        exe = exe_var.get().strip()
        folder = folder_var.get().strip()

        if not title or not exe or not folder:
            messagebox.showerror("Error", "Please fill in all fields")
            return

        if not Path(exe).exists():
            messagebox.showerror("Error", "Game executable not found")
            return

        if not Path(folder).exists():
            messagebox.showerror("Error", "Game folder not found")
            return

        try:
            create_game(title, exe, folder)
            title_var.set("")
            exe_var.set("")
            folder_var.set("")
            messagebox.showinfo("Success", f"Game '{title}' added successfully!")
            show_frame(frame1)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add game: {e}")


    def getGameTexts():
        folder = getScriptPath()
        txt_files = list(folder.glob("*.txt"))
        return txt_files


    def loadGames():
        txt_files = getGameTexts()
        for txt_file in txt_files:
            try:
                with open(txt_file, "r") as f:
                    lines = [line.rstrip() for line in f]
                    if len(lines) == 4:
                        games[lines[0]] = Game(lines[0], lines[1], lines[2], lines[3])
                    else:
                        print(f"wrong format for game file {txt_file}")
            except Exception as e:
                print(f"Error reading game file {txt_file}: {e}")


    def deleteGame(title):
        result = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{title}'?")
        if result:
            if title in games:
                del games[title]
            try:
                path = getScriptPath() / f"{title}.txt"
                if path.exists():
                    path.unlink()
                reload_gameFrame()
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting game: {e}")


    # Create main window
    window = tk.Tk()
    window.title("Game Notation")
    window.minsize(WIDTH, HEIGHT)
    window.configure(bg=BG_COLOR)

    # Configure styles
    style = ttk.Style()
    style.theme_use('clam')

    # Custom fonts
    title_font = ('Segoe UI', 16, 'bold')
    subtitle_font = ('Segoe UI', 12)
    normal_font = ('Segoe UI', 10)

    # Create frames
    frame1 = tk.Frame(window, width=WIDTH, height=HEIGHT, bg=BG_COLOR)
    frame2 = tk.Frame(window, width=WIDTH, height=HEIGHT, bg=BG_COLOR)

    # Frame 1 - Main Dashboard
    frame1.grid(row=0, column=0, sticky="nsew")
    frame1.grid_columnconfigure(0, weight=1)

    # Header
    header_frame = tk.Frame(frame1, bg=PRIMARY_COLOR, height=80)
    header_frame.grid(row=0, column=0, sticky="ew")
    header_frame.grid_columnconfigure(0, weight=1)

    title_label = tk.Label(header_frame, text="🎮 Game Notation",
                           font=title_font, bg=PRIMARY_COLOR, fg="white")
    title_label.grid(row=0, column=0, pady=20, padx=20, sticky="w")

    # Main content
    content_frame = tk.Frame(frame1, bg=BG_COLOR)
    content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
    content_frame.grid_columnconfigure(0, weight=1)

    # Welcome section
    welcome_frame = tk.Frame(content_frame, bg="white", relief="raised", bd=1)
    welcome_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
    welcome_frame.grid_columnconfigure(0, weight=1)

    welcome_label = tk.Label(welcome_frame, text="Welcome to Game Notation!",
                             font=subtitle_font, bg="white", fg=TEXT_COLOR)
    welcome_label.grid(row=0, column=0, pady=15, padx=20, sticky="w")

    desc_label = tk.Label(welcome_frame, text="Launch your games with integrated notes and tracking",
                          font=normal_font, bg="white", fg=TEXT_COLOR)
    desc_label.grid(row=1, column=0, pady=(0, 15), padx=20, sticky="w")

    # Add game button
    add_game_btn = tk.Button(welcome_frame, text="➕ Add New Game",
                             command=lambda: show_frame(frame2),
                             bg=SUCCESS_COLOR, fg="white", font=subtitle_font,
                             relief="flat", padx=20, pady=10, cursor="hand2")
    add_game_btn.grid(row=0, column=1, rowspan=2, pady=15, padx=20, sticky="e")

    # Games list section
    games_label = tk.Label(content_frame, text="Your Games",
                           font=subtitle_font, bg=BG_COLOR, fg=TEXT_COLOR)
    games_label.grid(row=1, column=0, sticky="w", pady=(0, 10))

    # Scrollable games frame
    games_container = tk.Frame(content_frame, bg=BG_COLOR)
    games_container.grid(row=2, column=0, sticky="nsew")
    games_container.grid_columnconfigure(0, weight=1)

    # Canvas for scrolling
    games_canvas = tk.Canvas(games_container, bg=BG_COLOR, highlightthickness=0)
    games_scrollbar = ttk.Scrollbar(games_container, orient="vertical", command=games_canvas.yview)
    games_frame = tk.Frame(games_canvas, bg=BG_COLOR)

    games_frame.bind(
        "<Configure>",
        lambda e: games_canvas.configure(scrollregion=games_canvas.bbox("all"))
    )

    games_canvas.create_window((0, 0), window=games_frame, anchor="nw")
    games_canvas.configure(yscrollcommand=games_scrollbar.set)

    games_canvas.grid(row=0, column=0, sticky="nsew")
    games_scrollbar.grid(row=0, column=1, sticky="ns")

    games_container.grid_rowconfigure(0, weight=1)


    def reload_gameFrame():
        # Clear old buttons
        for widget in games_frame.winfo_children():
            widget.destroy()

        if not games:
            empty_label = tk.Label(games_frame, text="No games added yet. Click 'Add New Game' to get started!",
                                   font=normal_font, bg=BG_COLOR, fg=TEXT_COLOR)
            empty_label.pack(pady=50)
            return

        # Rebuild buttons
        for i, gameName in enumerate(sorted(games.keys())):
            game = games[gameName]

            game_card = tk.Frame(games_frame, bg="white", relief="raised", bd=1)
            game_card.pack(fill="x", pady=5, padx=10)
            game_card.grid_columnconfigure(0, weight=1)

            # Game info
            info_frame = tk.Frame(game_card, bg="white")
            info_frame.grid(row=0, column=0, sticky="w", padx=15, pady=15)

            game_title = tk.Label(info_frame, text=game.title, font=subtitle_font,
                                  bg="white", fg=TEXT_COLOR)
            game_title.pack(anchor="w")

            game_path = tk.Label(info_frame, text=game.exePath, font=("Segoe UI", 9),
                                 bg="white", fg="#666666")
            game_path.pack(anchor="w", pady=(2, 0))

            # Buttons
            buttons_frame = tk.Frame(game_card, bg="white")
            buttons_frame.grid(row=0, column=1, padx=15, pady=15)

            play_btn = tk.Button(buttons_frame, text="▶ Play",
                                 command=lambda g=game: g.start(window),
                                 bg=SUCCESS_COLOR, fg="white", font=normal_font,
                                 relief="flat", padx=15, pady=5, cursor="hand2")
            play_btn.pack(side="left", padx=(0, 5))

            delete_btn = tk.Button(buttons_frame, text="🗑️ Delete",
                                   command=lambda title=game.title: deleteGame(title),
                                   bg=DANGER_COLOR, fg="white", font=normal_font,
                                   relief="flat", padx=15, pady=5, cursor="hand2")
            delete_btn.pack(side="left")


    # Frame 2 - Add Game Form
    frame2.grid(row=0, column=0, sticky="nsew")
    frame2.grid_columnconfigure(0, weight=1)

    # Header
    header_frame2 = tk.Frame(frame2, bg=PRIMARY_COLOR, height=80)
    header_frame2.grid(row=0, column=0, sticky="ew")
    header_frame2.grid_columnconfigure(0, weight=1)

    title_label2 = tk.Label(header_frame2, text="➕ Add New Game",
                            font=title_font, bg=PRIMARY_COLOR, fg="white")
    title_label2.grid(row=0, column=0, pady=20, padx=20, sticky="w")

    # Back button
    back_btn = tk.Button(header_frame2, text="← Back",
                         command=lambda: show_frame(frame1),
                         bg=SECONDARY_COLOR, fg="white", font=normal_font,
                         relief="flat", padx=15, pady=5, cursor="hand2")
    back_btn.grid(row=0, column=1, pady=20, padx=20, sticky="e")

    # Form content
    form_frame = tk.Frame(frame2, bg=BG_COLOR)
    form_frame.grid(row=1, column=0, sticky="nsew", padx=50, pady=30)
    form_frame.grid_columnconfigure(1, weight=1)

    # Variables
    title_var = tk.StringVar()
    exe_var = tk.StringVar()
    folder_var = tk.StringVar()

    # Form fields with modern styling
    # Title
    tk.Label(form_frame, text="Game Title:", font=subtitle_font,
             bg=BG_COLOR, fg=TEXT_COLOR).grid(row=0, column=0, sticky="w", pady=15)
    title_entry = tk.Entry(form_frame, textvariable=title_var, font=normal_font,
                           width=40, relief="solid", bd=1)
    title_entry.grid(row=0, column=1, sticky="ew", padx=(20, 0), pady=15)

    # Game EXE
    tk.Label(form_frame, text="Game EXE:", font=subtitle_font,
             bg=BG_COLOR, fg=TEXT_COLOR).grid(row=1, column=0, sticky="w", pady=15)
    exe_frame = tk.Frame(form_frame, bg=BG_COLOR)
    exe_frame.grid(row=1, column=1, sticky="ew", padx=(20, 0), pady=15)
    exe_frame.grid_columnconfigure(0, weight=1)

    exe_entry = tk.Entry(exe_frame, textvariable=exe_var, font=normal_font,
                         width=30, relief="solid", bd=1)
    exe_entry.grid(row=0, column=0, sticky="ew")

    browse_exe_btn = tk.Button(exe_frame, text="Browse", command=browse_exe,
                               bg=BUTTON_COLOR, fg="white", font=normal_font,
                               relief="flat", padx=15, cursor="hand2")
    browse_exe_btn.grid(row=0, column=1, padx=(10, 0))

    # Game Folder
    tk.Label(form_frame, text="Game Folder:", font=subtitle_font,
             bg=BG_COLOR, fg=TEXT_COLOR).grid(row=2, column=0, sticky="w", pady=15)
    folder_frame = tk.Frame(form_frame, bg=BG_COLOR)
    folder_frame.grid(row=2, column=1, sticky="ew", padx=(20, 0), pady=15)
    folder_frame.grid_columnconfigure(0, weight=1)

    folder_entry = tk.Entry(folder_frame, textvariable=folder_var, font=normal_font,
                            width=30, relief="solid", bd=1)
    folder_entry.grid(row=0, column=0, sticky="ew")

    browse_folder_btn = tk.Button(folder_frame, text="Browse", command=browse_folder,
                                  bg=BUTTON_COLOR, fg="white", font=normal_font,
                                  relief="flat", padx=15, cursor="hand2")
    browse_folder_btn.grid(row=0, column=1, padx=(10, 0))

    # Submit button
    submit_btn = tk.Button(form_frame, text="💾 Save Game", command=submit,
                           bg=SUCCESS_COLOR, fg="white", font=subtitle_font,
                           relief="flat", padx=30, pady=10, cursor="hand2")
    submit_btn.grid(row=3, column=1, pady=30, padx=(20, 0), sticky="e")

    # Start with frame 1
    show_frame(frame1)

    # Configure window grid
    window.grid_rowconfigure(0, weight=1)
    window.grid_columnconfigure(0, weight=1)


    # Add mousewheel scrolling
    def _on_mousewheel(event):
        games_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


    games_canvas.bind_all("<MouseWheel>", _on_mousewheel)

    window.mainloop()
