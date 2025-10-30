import time
import tkinter as tk
import win32gui
import subprocess
import os
import threading
import queue
import sys

sys.stdout.reconfigure(encoding="utf-8")

# -------------------------
# Get active window title
# -------------------------
def get_active_window_title():
    window = win32gui.GetForegroundWindow()
    return win32gui.GetWindowText(window)

# -------------------------
# Run main.py and capture output (live)
# -------------------------
def run_mainpy(output_queue):
    """Run main.py as a subprocess and stream stdout lines to a queue."""
    process = subprocess.Popen(
        [sys.executable, "-u", "main.py"],
        cwd=os.path.dirname(__file__),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1
    )

    def reader_thread(proc, q):
        for line in iter(proc.stdout.readline, b''):
            text = line.decode("utf-8", errors="replace").rstrip()
            if text:
                q.put(text)
        proc.stdout.close()
        proc.wait()
        q.put("[Program finished]")

    threading.Thread(target=reader_thread, args=(process, output_queue), daemon=True).start()

# -------------------------
# Create popup window
# -------------------------
def create_popup(root, output_queue):
    """Create or update popup to display streaming output."""
    popup = tk.Toplevel(root)
    popup.title("🧠 Smart Assistant")
    popup.geometry("600x400")
    popup.configure(bg="#1e1e1e")

    title_label = tk.Label(
        popup, 
        text="⚙️ Smart Assistant Running (main.py)",
        font=("Segoe UI", 12, "bold"), 
        bg="#1e1e1e", 
        fg="#00ff88"
    )
    title_label.pack(pady=6)

    # Text area with scrollbar
    frame = tk.Frame(popup, bg="#1e1e1e")
    frame.pack(expand=True, fill="both", padx=10, pady=5)

    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side="right", fill="y")

    text_box = tk.Text(
        frame, wrap="word", state="disabled", 
        yscrollcommand=scrollbar.set, bg="#1e1e1e", fg="#ffffff", 
        insertbackground="white", font=("Consolas", 10)
    )
    text_box.pack(expand=True, fill="both")
    scrollbar.config(command=text_box.yview)

    # Periodic update loop
    def update_output():
        while not output_queue.empty():
            line = output_queue.get_nowait()
            text_box.config(state="normal")
            text_box.insert("end", line + "\n")
            text_box.see("end")
            text_box.config(state="disabled")
        popup.after(200, update_output)

    update_output()
    return popup

# -------------------------
# Watcher function
# -------------------------
def watcher(output_queue, root):
    print("🔎 Monitoring for Google Chrome launch...")
    main_launched = False
    popup = None

    while True:
        title = get_active_window_title()

        if "Google" in title and "Chrome" in title:
            if not main_launched:
                print("🚀 Chrome detected → launching main.py and popup")

                run_mainpy(output_queue)
                main_launched = True

                # Must create popup in the Tkinter thread
                root.after(0, lambda: create_popup(root, output_queue))

        # If main.py prints something that contains "REMINDER", popup reappears
        if not output_queue.empty():
            try:
                line = output_queue.queue[-1]
                if "REMINDER" in line.upper():
                    root.after(0, lambda: create_popup(root, output_queue))
            except IndexError:
                pass

        time.sleep(2)

# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    output_queue = queue.Queue()
    root = tk.Tk()
    root.withdraw()  # hide main window

    threading.Thread(target=watcher, args=(output_queue, root), daemon=True).start()

    print("✅ Smart Assistant watcher started.")
    root.mainloop()
