import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD
import tkinter as tk
from tkinter import messagebox, filedialog
import os
from PIL import Image, ImageTk
import fitz  # PyMuPDF
import math
import io

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

    # Create frames for left and right PDFs
    left_frame = ctk.CTkFrame(main_container)
    left_frame.pack(side="left", expand=True, fill="both", padx=(0, 5))
    
    right_frame = ctk.CTkFrame(main_container)
    right_frame.pack(side="right", expand=True, fill="both", padx=(5, 0))

    # Variables to store PDF paths
    left_pdf_path = [pdf_path]  # Use the original PDF path
    right_pdf_path = [None]

    # Function to show all pages in tabs
    def show_all_pages():
        # Clear the main container
        for widget in main_container.winfo_children():
            widget.destroy()

        # Create tabview
        tabview = ctk.CTkTabview(main_container)
        tabview.pack(expand=True, fill="both", padx=10, pady=10)

        # Open both PDFs
        doc1 = fitz.open(left_pdf_path[0])
        doc2 = fitz.open(right_pdf_path[0])

        # Create tabs for first PDF
        for page_num in range(len(doc1)):
            page = doc1[page_num]
            tab_name = f"PDF1 - Page {page_num + 1}"
            tabview.add(tab_name)
            
            # Create frame for the page
            page_frame = ctk.CTkFrame(tabview.tab(tab_name))
            page_frame.pack(expand=True, fill="both", padx=10, pady=10)
            
            # Convert page to image
            pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            photo = ImageTk.PhotoImage(img)
            
            # Create label for the page
            page_label = ctk.CTkLabel(page_frame, image=photo, text="")
            page_label.image = photo  # Keep a reference
            page_label.pack(expand=True, fill="both")

        # Create tabs for second PDF
        for page_num in range(len(doc2)):
            page = doc2[page_num]
            tab_name = f"PDF2 - Page {page_num + 1}"
            tabview.add(tab_name)
            
            # Create frame for the page
            page_frame = ctk.CTkFrame(tabview.tab(tab_name))
            page_frame.pack(expand=True, fill="both", padx=10, pady=10)
            
            # Convert page to image
            pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            photo = ImageTk.PhotoImage(img)
            
            # Create label for the page
            page_label = ctk.CTkLabel(page_frame, image=photo, text="")
            page_label.image = photo  # Keep a reference
            page_label.pack(expand=True, fill="both")

    # Function to show PDF preview
    def show_pdf_preview(frame, pdf_path, path_var):
        # Clear the frame
        for widget in frame.winfo_children():
            widget.destroy()

        if pdf_path:
            # Show PDF icon
            pdf_icon_label = ctk.CTkLabel(frame, text="📄", font=("Arial", 40))
            pdf_icon_label.pack(pady=(20, 10))

            # Show PDF file name
            file_name = os.path.basename(pdf_path)
            file_label = ctk.CTkLabel(frame, text=file_name, font=("Arial", 14))
            file_label.pack(pady=(0, 10))

            # Create preview area
            preview_frame = ctk.CTkFrame(frame)
            preview_frame.pack(expand=True, fill="both", padx=10, pady=10)

            # Open PDF and show first page
            doc = fitz.open(pdf_path)
            page = doc[0]
            pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            photo = ImageTk.PhotoImage(img)

            # Create label for preview
            preview_label = ctk.CTkLabel(preview_frame, image=photo, text="")
            preview_label.image = photo  # Keep a reference
            preview_label.pack(expand=True, fill="both")

            # Add page navigation
            nav_frame = ctk.CTkFrame(preview_frame)
            nav_frame.pack(fill="x", pady=5)

            def prev_page():
                nonlocal page, photo
                if page.number > 0:
                    page = doc[page.number - 1]
                    pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    photo = ImageTk.PhotoImage(img)
                    preview_label.configure(image=photo)
                    preview_label.image = photo
                    # Update page counter
                    page_label.configure(text=f"Page {page.number + 1} of {len(doc)}")

            def next_page():
                nonlocal page, photo
                if page.number < len(doc) - 1:
                    page = doc[page.number + 1]
                    pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    photo = ImageTk.PhotoImage(img)
                    preview_label.configure(image=photo)
                    preview_label.image = photo
                    # Update page counter
                    page_label.configure(text=f"Page {page.number + 1} of {len(doc)}")

            prev_btn = ctk.CTkButton(nav_frame, text="←", width=30, command=prev_page)
            prev_btn.pack(side="left", padx=5)

            page_label = ctk.CTkLabel(nav_frame, text=f"Page {page.number + 1} of {len(doc)}")
            page_label.pack(side="left", expand=True)

            next_btn = ctk.CTkButton(nav_frame, text="→", width=30, command=next_page)
            next_btn.pack(side="right", padx=5)

            # Add remove button only for the right frame
            if frame == right_frame:
                # Create a frame for buttons
                button_frame = ctk.CTkFrame(frame)
                button_frame.pack(pady=10)

                def remove_pdf():
                    path_var[0] = None
                    show_drop_area(frame, path_var)
                    # Hide confirm button if it exists
                    if hasattr(button_frame, 'confirm_button'):
                        button_frame.confirm_button.pack_forget()

                remove_btn = ctk.CTkButton(button_frame, text="Remove PDF", command=remove_pdf)
                remove_btn.pack(side="left", padx=5)

                # Show confirm button if both PDFs are present
                if left_pdf_path[0] and right_pdf_path[0]:
                    if not hasattr(button_frame, 'confirm_button'):
                        confirm_button = ctk.CTkButton(
                            button_frame,
                            text="Confirm",
                            command=show_all_pages,
                            fg_color=("red", "red"),
                            hover_color=("darkred", "darkred")
                        )
                        confirm_button.pack(side="left", padx=5)
                        button_frame.confirm_button = confirm_button

    # Function to show drop area
    def show_drop_area(frame, path_var):
        # Clear the frame
        for widget in frame.winfo_children():
            widget.destroy()

        # Create drop area
        drop_label = ctk.CTkLabel(frame, text="Drag and drop PDF here", font=("Arial", 16))
        drop_label.pack(expand=True)

        # Add select button
        def select_pdf():
            file_path = filedialog.askopenfilename(
                filetypes=[("PDF files", "*.pdf")],
                title="Select a PDF file"
            )
            if file_path:
                path_var[0] = file_path
                show_pdf_preview(frame, file_path, path_var)

        select_btn = ctk.CTkButton(frame, text="Or select PDF", command=select_pdf)
        select_btn.pack(pady=(0, 20))

        # Enable drag and drop
        frame.drop_target_register(DND_FILES)
        
        def handle_drop(event):
            file_path = event.data.strip('{}')
            if file_path.lower().endswith('.pdf'):
                path_var[0] = file_path
                show_pdf_preview(frame, file_path, path_var)
            else:
                messagebox.showwarning("Invalid File", "Please drop a PDF file")
        
        frame.dnd_bind('<<Drop>>', handle_drop)

    # Initialize frames
    show_pdf_preview(left_frame, pdf_path, left_pdf_path)  # Show original PDF on left
    show_drop_area(right_frame, right_pdf_path)  # Show drop area on right

    def on_close():
        merge_win.destroy()
        parent.deiconify()

    merge_win.protocol("WM_DELETE_WINDOW", on_close)
