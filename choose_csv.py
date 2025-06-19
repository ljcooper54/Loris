import tkinter as tk
from tkinter import filedialog

def choose_csv_file():
    """Prompt the user to select a CSV file.

    Returns the selected file path or None if cancelled.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    root.update()

    file_path = filedialog.askopenfilename(
        title="Select Order CSV",
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
    )

    if not file_path:
        print("No file selected. Operation cancelled.")
        return None

    print(f"Selected file: {file_path}")
    return file_path


if __name__ == "__main__":
    choose_csv_file()
