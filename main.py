import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD
import tkinter as tk
from tkinter import messagebox, filedialog
import os
from PIL import Image, ImageTk
from split import open_split_screen

# Set the appearance mode and default color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Create the main window with TkinterDnD support
app = TkinterDnD.Tk()
app.title("CustomTkinter Window")
app.configure(bg="#2b2b2b")

# Get screen dimensions
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()

# Calculate position for center of the screen
window_width = 1300
window_height = 768
x_position = (screen_width - window_width) // 2
y_position = (screen_height - window_height) // 2

# Set window size and position
app.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

# Create a frame for the drop area
drop_frame = ctk.CTkFrame(app)
drop_frame.pack(expand=True, fill="both", padx=20, pady=20)

# Create a label to show drop area
drop_label = ctk.CTkLabel(drop_frame, text="Drag and drop PDF files here", font=("Arial", 20))
drop_label.pack(expand=True)

# Add a button to manually attach a PDF file
def select_pdf():
    file_path = filedialog.askopenfilename(
        filetypes=[("PDF files", "*.pdf")],
        title="Select a PDF file"
    )
    if file_path:
        if file_path.lower().endswith('.pdf'):
            show_pdf_screen(file_path)
        else:
            messagebox.showwarning("Invalid File", "Please select a PDF file")

attach_button = ctk.CTkButton(drop_frame, text="Or attach PDF here", command=select_pdf)
attach_button.pack(pady=(0, 250))

# Enable drag and drop
drop_frame.drop_target_register(DND_FILES)
drop_frame.dnd_bind('<<Drop>>', lambda e: handle_drop(e))

# Function to show the PDF screen
def show_pdf_screen(pdf_path):
    # Clear the drop_frame
    for widget in drop_frame.winfo_children():
        widget.destroy()

    # Show PDF icon (using emoji as placeholder)
    pdf_icon_label = ctk.CTkLabel(drop_frame, text="📄", font=("Arial", 80))
    pdf_icon_label.pack(pady=(40, 10))

    # Show PDF file name
    file_name = os.path.basename(pdf_path)
    file_label = ctk.CTkLabel(drop_frame, text=file_name, font=("Arial", 18))
    file_label.pack(pady=(0, 30))

    # Split and Merge buttons in a horizontal frame
    button_frame = ctk.CTkFrame(drop_frame, fg_color="transparent")
    button_frame.pack(pady=(0, 10), fill="x", padx=40)
    split_button = ctk.CTkButton(button_frame, text="Split", command=lambda: open_split_screen(app, pdf_path))
    split_button.pack(side="left", expand=True, fill="x", padx=(0, 10))
    merge_button = ctk.CTkButton(button_frame, text="Merge")
    merge_button.pack(side="right", expand=True, fill="x", padx=(10, 0))

# Update handlers to show the PDF screen
def handle_drop(event):
    file_path = event.data.strip('{}')
    if file_path.lower().endswith('.pdf'):
        show_pdf_screen(file_path)
    else:
        messagebox.showwarning("Invalid File", "Please drop a PDF file")

# Start the main event loop
app.mainloop()
