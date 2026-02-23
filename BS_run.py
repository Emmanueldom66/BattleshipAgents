from GUI.bs_gui import BattleshipGUI
import tkinter as tk

if __name__ == "__main__":
    # Start the GUI application
    root = tk.Tk()
    app = BattleshipGUI(root)
    root.mainloop()