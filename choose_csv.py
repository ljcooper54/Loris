import tkinter as tk
from tkinter import filedialog, messagebox
import os

def choose_csv_file():
    """Prompt the user to select a CSV file.

    Returns the selected file path or None if cancelled.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    root.update()

    file_path = filedialog.askopenfilename(
        title="Order File (CSV)",
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
    )

    if not file_path:
        print("No file selected. Operation cancelled.")
        return None

    print(f"Selected file: {file_path}")

    # Count lines in the selected file
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            line_count = sum(1 for _ in f)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read file:\n{e}")
        root.destroy()
        return None

    show_done_dialog(root, os.path.basename(file_path), line_count)
    root.destroy()
    return file_path


def show_done_dialog(root: tk.Tk, filename: str, line_count: int) -> None:
    """Display a dialog reporting the line count with a Done button."""
    dialog = tk.Toplevel(root)
    dialog.title("File Line Count")

    label = tk.Label(dialog, text=f"{filename} has {line_count} lines")
    label.pack(padx=20, pady=10)

    done_button = tk.Button(dialog, text="Done", command=dialog.destroy)
    done_button.pack(pady=(0, 10))

    dialog.transient(root)
    dialog.grab_set()
    root.wait_window(dialog)


if __name__ == "__main__":
    choose_csv_file()
