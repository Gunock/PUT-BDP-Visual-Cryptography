"""Contains window application"""

import tkinter as tk


class PrimeGeneratorApplication(tk.Frame):
    """Application for prime generator"""

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self._create_widgets()

    def _create_widgets(self):
        self.save_var = False
        self.save_checkbox = tk.Checkbutton(text="save shares", variable=self.save_var)
        self.save_checkbox.pack()

        self.filename_frame = tk.LabelFrame(text="Image filename")
        self.filename_frame.pack()
        self.filename_input = tk.Entry(self.filename_frame, bd=5)
        self.filename_input.pack()

        self.encryption_visualization = tk.Button(self)
        self.encryption_visualization["text"] = "Visualize encryption"
        self.encryption_visualization["command"] = self._visualize_encryption
        self.encryption_visualization.pack()

    def _visualize_encryption(self):
        import os
        from application import visual_encrypter
        from tkinter import messagebox

        filename: str = self.filename_input.get()
        if not os.path.exists(filename) or not os.path.isfile(filename):
            messagebox.showinfo("Error", "Image file does not exist!")
            return

        visual_encrypter.visualize_encryption(filename, self.save_var)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Visual encryption")
    app = PrimeGeneratorApplication(master=root)
    app.mainloop()
