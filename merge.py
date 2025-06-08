import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD
import tkinter as tk
from tkinter import messagebox, filedialog
import os
from PIL import Image, ImageTk
import fitz  # PyMuPDF

def open_merge_screen(parent, pdf_path, show_pdf_screen):
    # Hide the parent window
    parent.withdraw()

    # Create a new toplevel window
    merge_win = ctk.CTkToplevel()
    merge_win.title("Merge PDF")
    merge_win.configure(bg="#2b2b2b")

    # Get screen dimensions
    screen_width = merge_win.winfo_screenwidth()
    screen_height = merge_win.winfo_screenheight()

    # Calculate position for center of the screen
    window_width = 1300
    window_height = 768
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2

    # Set window size and position
    merge_win.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    # Create menu bar with dark theme
    menu_bar = tk.Menu(merge_win, 
                      bg='#2b2b2b',
                      fg='white',
                      activebackground='#404040',
                      activeforeground='white')
    merge_win.config(menu=menu_bar)

    # File menu
    file_menu = tk.Menu(menu_bar, 
                       tearoff=0,
                       bg='#2b2b2b',
                       fg='white',
                       activebackground='#404040',
                       activeforeground='white')
    menu_bar.add_cascade(label="File", menu=file_menu)

    # New menu
    def new_pdf():
        # Create custom confirmation dialog
        confirm_dialog = ctk.CTkToplevel(merge_win)
        confirm_dialog.title("Confirm New")
        confirm_dialog.geometry("400x200")
        confirm_dialog.transient(merge_win)
        confirm_dialog.grab_set()

        # Center the dialog
        confirm_dialog.update_idletasks()
        x = merge_win.winfo_x() + (merge_win.winfo_width() - confirm_dialog.winfo_width()) // 2
        y = merge_win.winfo_y() + (merge_win.winfo_height() - confirm_dialog.winfo_height()) // 2
        confirm_dialog.geometry(f"+{x}+{y}")

        # Add message
        msg_label = ctk.CTkLabel(
            confirm_dialog,
            text="Do you want to discard changes and start a new PDF?",
            wraplength=350,
            font=ctk.CTkFont(size=14)
        )
        msg_label.pack(pady=(30, 20))

        # Add buttons
        button_frame = ctk.CTkFrame(confirm_dialog)
        button_frame.pack(pady=(0, 20))

        def on_confirm():
            confirm_dialog.destroy()
            # Close the current window
            merge_win.destroy()
            # Show the parent window
            parent.deiconify()
            # Reset the main screen by recreating it
            show_pdf_screen(None)  # Pass None to indicate we want to show the initial screen

        def on_cancel():
            confirm_dialog.destroy()

        confirm_btn = ctk.CTkButton(
            button_frame,
            text="Yes, Start New",
            command=on_confirm
        )
        confirm_btn.pack(side="left", padx=10)

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=on_cancel
        )
        cancel_btn.pack(side="left", padx=10)

        # Wait for dialog to close
        merge_win.wait_window(confirm_dialog)

    menu_bar.add_command(label="New", command=new_pdf)

    # Exit menu
    def exit_app():
        # Create custom confirmation dialog
        confirm_dialog = ctk.CTkToplevel(merge_win)
        confirm_dialog.title("Confirm Exit")
        confirm_dialog.geometry("400x200")
        confirm_dialog.transient(merge_win)
        confirm_dialog.grab_set()

        # Center the dialog
        confirm_dialog.update_idletasks()
        x = merge_win.winfo_x() + (merge_win.winfo_width() - confirm_dialog.winfo_width()) // 2
        y = merge_win.winfo_y() + (merge_win.winfo_height() - confirm_dialog.winfo_height()) // 2
        confirm_dialog.geometry(f"+{x}+{y}")

        # Add message
        msg_label = ctk.CTkLabel(
            confirm_dialog,
            text="Are you sure you want to exit the application?",
            wraplength=350,
            font=ctk.CTkFont(size=14)
        )
        msg_label.pack(pady=(30, 20))

        # Add buttons
        button_frame = ctk.CTkFrame(confirm_dialog)
        button_frame.pack(pady=(0, 20))

        def on_confirm():
            confirm_dialog.destroy()
            # Close the merge screen window
            merge_win.destroy()
            # Close the parent window (main application)
            parent.destroy()

        def on_cancel():
            confirm_dialog.destroy()

        confirm_btn = ctk.CTkButton(
            button_frame,
            text="Yes, Exit",
            command=on_confirm
        )
        confirm_btn.pack(side="left", padx=10)

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=on_cancel
        )
        cancel_btn.pack(side="left", padx=10)

        # Wait for dialog to close
        merge_win.wait_window(confirm_dialog)

    menu_bar.add_command(label="Exit", command=exit_app)

    # Configure menu colors
    menu_bar.configure(
        bg='#2b2b2b',
        fg='white',
        activebackground='#404040',
        activeforeground='white',
        relief='flat'
    )

    # Create main container
    main_container = ctk.CTkFrame(merge_win)
    main_container.pack(expand=True, fill="both", padx=10, pady=10)

    # Create a frame for the drop area
    drop_frame = ctk.CTkFrame(main_container)
    drop_frame.pack(expand=True, fill="both", padx=20, pady=20)

    # Create a label to show drop area
    drop_label = ctk.CTkLabel(drop_frame, text="Drag and drop PDF files here to merge", font=("Arial", 20))
    drop_label.pack(expand=True)

    # Add a button to manually attach PDF files
    def select_pdfs():
        file_paths = filedialog.askopenfilenames(
            filetypes=[("PDF files", "*.pdf")],
            title="Select PDF files to merge"
        )
        if file_paths:
            # TODO: Handle multiple PDF files for merging
            pass

    attach_button = ctk.CTkButton(drop_frame, text="Or select PDFs to merge", command=select_pdfs)
    attach_button.pack(pady=(0, 250))

    # Enable drag and drop
    drop_frame.drop_target_register(DND_FILES)
    
    def handle_drop(event):
        file_paths = event.data.strip('{}').split('} {')
        # TODO: Handle multiple PDF files for merging
        pass
    
    drop_frame.dnd_bind('<<Drop>>', handle_drop)

    def on_close():
        merge_win.destroy()
        parent.deiconify()

    merge_win.protocol("WM_DELETE_WINDOW", on_close)
