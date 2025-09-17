import time
import tkinter as tk
import win32gui
import subprocess
import os
import threading
import queue
import sys
import main

# -------------------------
# Get active window title
# -------------------------
def get_active_window_title():
    window = win32gui.GetForegroundWindow()
    return win32gui.GetWindowText(window)

# -------------------------
# Run main.py and capture output
# -------------------------
def run_mainpy(output_queue):
    process = subprocess.Popen(
        [sys.executable, "main.py"],  # use venv python
        cwd=os.path.dirname(__file__),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    for line in iter(process.stdout.readline, ''):
        output_queue.put(line.strip())
    process.stdout.close()
    process.wait()

# -------------------------
# Show popup with live output
# -------------------------
def show_popup(output_queue):
    def popup():
        root = tk.Tk()
        root.title("Smart Assistant")
        root.geometry("400x300")

        label = tk.Label(root, text="⚠️ Google detected! Running main.py...", font=("Arial", 12))
        label.pack(pady=5)

        text_box = tk.Text(root, wrap="word", state="disabled")
        text_box.pack(expand=True, fill="both", padx=10, pady=10)

        def update_output():
            while not output_queue.empty():
                line = output_queue.get_nowait()
                text_box.config(state="normal")
                text_box.insert("end", line + "\n")
                text_box.see("end")
                text_box.config(state="disabled")
            root.after(200, update_output)

        update_output()
        root.mainloop()

    threading.Thread(target=popup, daemon=True).start()

# -------------------------
# Main watcher loop
# -------------------------
def main():
    print("🔎 Monitoring for Google in Chrome...")
    already_launched = False  
    output_queue = queue.Queue()

    while True:
        title = get_active_window_title()

        if "Google" in title and "Chrome" in title:
            if not already_launched:  
                print("🚀 Google detected! Launching main.py and popup...")

                # Start main.py with live output
                threading.Thread(target=run_mainpy, args=(output_queue,), daemon=True).start()

                # Show popup
                show_popup(output_queue)

                already_launched = True
        else:
            already_launched = False  

        time.sleep(2)

if __name__ == "__main__":
    main()
