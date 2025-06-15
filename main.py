import tkinter as tk
from app.main_application import TextBlockEditorApp

if __name__ == "__main__":
    root = tk.Tk()
    # Optional: Set a minimum size for the window
    root.minsize(800, 600)
    app = TextBlockEditorApp(master=root)
    # The title is set within TextBlockEditorApp's __init__ method.
    # If you need to set it here, it would be: root.title("Text Block Editor - Python")
    root.mainloop()
