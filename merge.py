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
    window_height = 800
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
                       activeforeground='black')

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

    # Global variables for page management
    left_pages = []  # Will store page data for left PDF
    right_pages = []  # Will store page data for right PDF
    selected_pages = []  # Store selected pages

    def toggle_page_selection(page_data, var):
        """Toggle page selection and update the selected_pages list"""
        if var.get():
            selected_pages.append(page_data)
        else:
            if page_data in selected_pages:
                selected_pages.remove(page_data)

    # Function to handle arrow button click
    def handle_arrow_click():
        """Handle the arrow button click - check if pages are selected"""
        if not selected_pages:
            # Show message box if no pages are selected
            messagebox.showwarning(
                "No Pages Selected", 
                "Please select at least one PDF page before proceeding.",
                parent=merge_win
            )
        else:
            # TODO: Add your logic here for what happens when pages are selected
            # For now, just show a message with the count of selected pages
            from merge_final import open_merge_final_screen
            open_merge_final_screen(merge_win, selected_pages.copy())

    # Function to create draggable page thumbnail
    def create_page_thumbnail(page, scale=0.2):
        pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        return ImageTk.PhotoImage(img)

    # Function to show pages in horizontal grid layout
    def show_pages_in_tabs():
        # Clear the main container
        for widget in main_container.winfo_children():
            widget.destroy()

        # Recreate left and right frames
        left_main_frame = ctk.CTkFrame(main_container)
        left_main_frame.pack(side="left", expand=True, fill="both", padx=(0, 5))
        
        right_main_frame = ctk.CTkFrame(main_container)
        right_main_frame.pack(side="right", expand=True, fill="both", padx=(5, 0))

        # Add titles
        left_title_frame = ctk.CTkFrame(left_main_frame, fg_color="transparent")
        left_title_frame.pack(fill="x", pady=(10, 5))

        # Use a sub-frame to center the title and button for PDF 1
        center_frame_pdf1 = ctk.CTkFrame(left_title_frame, fg_color="transparent")
        center_frame_pdf1.pack(expand=True)

        left_title = ctk.CTkLabel(center_frame_pdf1, text="PDF 1", font=ctk.CTkFont(size=16, weight="bold"))
        left_title.pack(side="left", padx=(0, 10))

        def replace_pdf1():
            # Create confirmation dialog
            confirm_dialog = ctk.CTkToplevel(merge_win)
            confirm_dialog.title("Confirm Replace")
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
                text="Do you want to replace the current PDF 1?",
                wraplength=350,
                font=ctk.CTkFont(size=14)
            )
            msg_label.pack(pady=(30, 20))

            # Add buttons
            button_frame = ctk.CTkFrame(confirm_dialog)
            button_frame.pack(pady=(0, 20))

            def on_confirm():
                confirm_dialog.destroy()
                # Open file dialog to select new PDF
                file_path = filedialog.askopenfilename(
                    filetypes=[
                        ("PDF and Image files", "*.pdf;*.png;*.jpg;*.jpeg;*.bmp;*.gif"),
                        ("PDF files", "*.pdf"),
                        ("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")
                    ],
                    title="Select a PDF or Image file"
                )
                if file_path:
                    if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                        # Convert image to PDF
                        pdf_bytes = convert_image_to_pdf(file_path)
                        if pdf_bytes:
                            left_pdf_path[0] = file_path
                            show_pages_in_tabs()  # Reload the view with new PDF
                    else:
                        left_pdf_path[0] = file_path
                        show_pages_in_tabs()  # Reload the view with new PDF

            def on_cancel():
                confirm_dialog.destroy()

            confirm_btn = ctk.CTkButton(
                button_frame,
                text="Yes, Replace",
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

        replace_btn_pdf1 = ctk.CTkButton(
            center_frame_pdf1,
            text="Replace PDF",
            width=100,
            command=replace_pdf1
        )
        replace_btn_pdf1.pack(side="left")
        
        right_title_frame = ctk.CTkFrame(right_main_frame, fg_color="transparent")
        right_title_frame.pack(fill="x", pady=(10, 5))
        
        # Use a sub-frame to center the title and button
        center_frame = ctk.CTkFrame(right_title_frame, fg_color="transparent")
        center_frame.pack(expand=True)
        
        right_title = ctk.CTkLabel(center_frame, text="PDF 2", font=ctk.CTkFont(size=16, weight="bold"))
        right_title.pack(side="left", padx=(0, 10))
        
        def replace_pdf2():
            # Create confirmation dialog
            confirm_dialog = ctk.CTkToplevel(merge_win)
            confirm_dialog.title("Confirm Replace")
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
                text="Do you want to replace the current PDF 2?",
                wraplength=350,
                font=ctk.CTkFont(size=14)
            )
            msg_label.pack(pady=(30, 20))

            # Add buttons
            button_frame = ctk.CTkFrame(confirm_dialog)
            button_frame.pack(pady=(0, 20))

            def on_confirm():
                confirm_dialog.destroy()
                # Open file dialog to select new PDF
                file_path = filedialog.askopenfilename(
                    filetypes=[
                        ("PDF and Image files", "*.pdf;*.png;*.jpg;*.jpeg;*.bmp;*.gif"),
                        ("PDF files", "*.pdf"),
                        ("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")
                    ],
                    title="Select a PDF or Image file"
                )
                if file_path:
                    if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                        # Convert image to PDF
                        pdf_bytes = convert_image_to_pdf(file_path)
                        if pdf_bytes:
                            right_pdf_path[0] = file_path
                            show_pages_in_tabs()  # Reload the view with new PDF
                    else:
                        right_pdf_path[0] = file_path
                        show_pages_in_tabs()  # Reload the view with new PDF

            def on_cancel():
                confirm_dialog.destroy()

            confirm_btn = ctk.CTkButton(
                button_frame,
                text="Yes, Replace",
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

        replace_btn = ctk.CTkButton(
            center_frame,
            text="Replace PDF",
            width=100,
            command=replace_pdf2
        )
        replace_btn.pack(side="left")

        # Create scrollable frames for page thumbnails
        left_scroll = ctk.CTkScrollableFrame(left_main_frame)
        left_scroll.pack(expand=True, fill="both", padx=10, pady=10)
        
        right_scroll = ctk.CTkScrollableFrame(right_main_frame)
        right_scroll.pack(expand=True, fill="both", padx=10, pady=10)

        # Open both PDFs and load pages
        if isinstance(left_pdf_path[0], str) and left_pdf_path[0].lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            # Convert image to PDF if it's an image file
            rotation = getattr(left_frame, 'rotation_state', 0)  # Get rotation state from frame
            pdf_bytes = convert_image_to_pdf(left_pdf_path[0], rotation)
            if pdf_bytes:
                doc1 = fitz.open(stream=pdf_bytes, filetype="pdf")
        else:
            doc1 = fitz.open(left_pdf_path[0])

        if isinstance(right_pdf_path[0], str) and right_pdf_path[0].lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            # Convert image to PDF if it's an image file
            rotation = getattr(right_frame, 'rotation_state', 0)  # Get rotation state from frame
            pdf_bytes = convert_image_to_pdf(right_pdf_path[0], rotation)
            if pdf_bytes:
                doc2 = fitz.open(stream=pdf_bytes, filetype="pdf")
        else:
            doc2 = fitz.open(right_pdf_path[0])

        # Clear previous page data only if it's empty (first time loading)
        if not left_pages:
            for page_num in range(len(doc1)):
                left_pages.append({
                    'doc': doc1, 
                    'page_num': page_num, 
                    'original_pdf': 'left',
                    'display_index': len(left_pages)  # Track display order
                })
        
        if not right_pages:
            for page_num in range(len(doc2)):
                right_pages.append({
                    'doc': doc2, 
                    'page_num': page_num, 
                    'original_pdf': 'right',
                    'display_index': len(right_pages)  # Track display order
                })

        # Calculate grid layout parameters
        thumbnail_width = 170 #120
        thumbnail_height = 190  # Increased height to accommodate page number  190
        padding = 10 #10
        
        # Get the width of the scrollable frame to calculate columns
        left_scroll.update_idletasks()
        available_width = left_scroll.winfo_width() - 40  # Account for padding
        columns_per_row = max(1, available_width // (thumbnail_width + padding))

        # Create horizontal grid layout for left PDF
        current_row_frame = None
        current_column = 0
        
        for display_index, page_data in enumerate(left_pages):
            page = page_data['doc'][page_data['page_num']]
            
            # Create new row frame if needed
            if current_column == 0:
                current_row_frame = ctk.CTkFrame(left_scroll, fg_color="transparent")
                current_row_frame.pack(fill="x", pady=2)
            
            # Create page frame
            page_frame = ctk.CTkFrame(current_row_frame, width=thumbnail_width, height=thumbnail_height)
            page_frame.pack(side="left", padx=padding//2, pady=5)
            page_frame.pack_propagate(False)  # Maintain fixed size
            
            # Create thumbnail
            thumbnail = create_page_thumbnail(page)
            
            # Create image label
            image_label = ctk.CTkLabel(
                page_frame, 
                image=thumbnail, 
                text="",
            )
            image_label.image = thumbnail  # Keep reference
            image_label.pack(expand=True, fill="both", pady=(5,0))
            
            # Create page number label - Show original page number
            page_number_label = ctk.CTkLabel(
                page_frame, 
                text=f"Page {page_data['page_num'] + 1}",
                font=ctk.CTkFont(size=10)
            )
            page_number_label.pack(pady=(0,5))

            # Add checkbox for page selection
            is_selected = ctk.BooleanVar(value=page_data in selected_pages)
            checkbox = ctk.CTkCheckBox(
                page_frame,
                text="",
                variable=is_selected,
                command=lambda pd=page_data, var=is_selected: toggle_page_selection(pd, var),
                width=20,
                height=20
            )
            checkbox.place(relx=1.0, rely=0.0, anchor="ne", x=-2, y=2)

            current_column += 1
            if current_column >= columns_per_row:
                current_column = 0

        # Create horizontal grid layout for right PDF
        current_row_frame = None
        current_column = 0
        
        for display_index, page_data in enumerate(right_pages):
            page = page_data['doc'][page_data['page_num']]
            
            # Create new row frame if needed
            if current_column == 0:
                current_row_frame = ctk.CTkFrame(right_scroll, fg_color="transparent")
                current_row_frame.pack(fill="x", pady=2)
            
            # Create page frame
            page_frame = ctk.CTkFrame(current_row_frame, width=thumbnail_width, height=thumbnail_height)
            page_frame.pack(side="left", padx=padding//2, pady=5)
            page_frame.pack_propagate(False)  # Maintain fixed size
            
            # Create thumbnail
            thumbnail = create_page_thumbnail(page)
            
            # Create image label
            image_label = ctk.CTkLabel(
                page_frame, 
                image=thumbnail, 
                text="",
            )
            image_label.image = thumbnail  # Keep reference
            image_label.pack(expand=True, fill="both", pady=(5,0))
            
            # Create page number label - Show original page number
            page_number_label = ctk.CTkLabel(
                page_frame, 
                text=f"Page {page_data['page_num'] + 1}",
                font=ctk.CTkFont(size=10)
            )
            page_number_label.pack(pady=(0,5))

            # Add checkbox for page selection
            is_selected = ctk.BooleanVar(value=page_data in selected_pages)
            checkbox = ctk.CTkCheckBox(
                page_frame,
                text="",
                variable=is_selected,
                command=lambda pd=page_data, var=is_selected: toggle_page_selection(pd, var),
                width=20,
                height=20
            )
            checkbox.place(relx=1.0, rely=0.0, anchor="ne", x=-2, y=2)

            current_column += 1
            if current_column >= columns_per_row:
                current_column = 0

        # Add the arrow button at bottom right corner overlapping PDF 2 frame
        arrow_button = ctk.CTkButton(
            right_main_frame,
            text="→",
            width=50,
            height=50,
            font=ctk.CTkFont(size=20, weight="bold"),
            command=handle_arrow_click,
            fg_color=("#1f538d", "#14375e"),
            hover_color=("#144870", "#1f538d")
        )
        # Place the button at bottom right corner with some padding from edges
        arrow_button.place(relx=1.0, rely=1.0, anchor="se", x=-30, y=-30)

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
            if isinstance(pdf_path, io.BytesIO):
                # For in-memory PDFs, use the original image path stored in path_var
                file_name = os.path.basename(path_var[0])
            else:
                file_name = os.path.basename(pdf_path)
            file_label = ctk.CTkLabel(frame, text=file_name, font=("Arial", 14))
            file_label.pack(pady=(0, 10))

            # Create preview area
            preview_frame = ctk.CTkFrame(frame)
            preview_frame.pack(expand=True, fill="both", padx=10, pady=10)

            # Open PDF and show first page
            if isinstance(pdf_path, io.BytesIO):
                doc = fitz.open(stream=pdf_path, filetype="pdf")
            else:
                doc = fitz.open(pdf_path)
            
            page = doc[0]
            pix = page.get_pixmap(matrix=fitz.Matrix(0.6, 0.6))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            photo = ImageTk.PhotoImage(img)

            # Create label for preview
            preview_label = ctk.CTkLabel(preview_frame, image=photo, text="")
            preview_label.image = photo  # Keep a reference
            preview_label.pack(expand=True, fill="both")

            # Create a container for all controls
            controls_frame = ctk.CTkFrame(frame)
            controls_frame.pack(fill="x", pady=10)

            # Add rotation controls if it's an image
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                rotation_frame = ctk.CTkFrame(controls_frame)
                rotation_frame.pack(fill="x", pady=(0, 5))

                # Initialize rotation state if not exists
                if not hasattr(frame, 'rotation_state'):
                    frame.rotation_state = 0

                def rotate_image(direction):
                    nonlocal doc, page, photo
                    # Update rotation angle
                    if direction == 'clockwise':
                        frame.rotation_state = (frame.rotation_state + 90) % 360
                    else:
                        frame.rotation_state = (frame.rotation_state - 90) % 360

                    # Convert image to PDF with new rotation
                    pdf_bytes = convert_image_to_pdf(path_var[0], frame.rotation_state)
                    if pdf_bytes:
                        # Update preview
                        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                        page = doc[0]
                        pix = page.get_pixmap(matrix=fitz.Matrix(0.6, 0.6))
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        photo = ImageTk.PhotoImage(img)
                        preview_label.configure(image=photo)
                        preview_label.image = photo

                # Add rotation buttons
                rotate_left_btn = ctk.CTkButton(rotation_frame, text="↺", width=30, command=lambda: rotate_image('anticlockwise'))
                rotate_left_btn.pack(side="left", padx=5)

                rotate_right_btn = ctk.CTkButton(rotation_frame, text="↻", width=30, command=lambda: rotate_image('clockwise'))
                rotate_right_btn.pack(side="right", padx=5)

            # Add page navigation
            nav_frame = ctk.CTkFrame(controls_frame)
            nav_frame.pack(fill="x", pady=(0, 5))

            def prev_page():
                nonlocal page, photo
                if page.number > 0:
                    page = doc[page.number - 1]
                    pix = page.get_pixmap(matrix=fitz.Matrix(0.6, 0.6))
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    photo = ImageTk.PhotoImage(img)
                    preview_label.configure(image=photo)
                    preview_label.image = photo
                    # Update page counter
                    page_number_label.configure(text=f"Page {page.number + 1} of {len(doc)}")

            def next_page():
                nonlocal page, photo
                if page.number < len(doc) - 1:
                    page = doc[page.number + 1]
                    pix = page.get_pixmap(matrix=fitz.Matrix(0.6, 0.6))
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    photo = ImageTk.PhotoImage(img)
                    preview_label.configure(image=photo)
                    preview_label.image = photo
                    # Update page counter
                    page_number_label.configure(text=f"Page {page.number + 1} of {len(doc)}")

            prev_btn = ctk.CTkButton(nav_frame, text="←", width=30, command=prev_page)
            prev_btn.pack(side="left", padx=5)

            page_number_label = ctk.CTkLabel(nav_frame, text=f"Page {page.number + 1} of {len(doc)}")
            page_number_label.pack(side="left", expand=True)

            next_btn = ctk.CTkButton(nav_frame, text="→", width=30, command=next_page)
            next_btn.pack(side="right", padx=5)

            # Add action buttons (remove and confirm)
            if frame == right_frame:
                # Create a separate frame for action buttons with more padding
                action_frame = ctk.CTkFrame(frame)
                action_frame.pack(fill="x", pady=0)  # Increased top padding

                def remove_pdf():
                    path_var[0] = None
                    show_drop_area(frame, path_var)

                # Create a container for the buttons
                button_container = ctk.CTkFrame(action_frame, fg_color="transparent")
                button_container.pack(expand=True, pady=2)

                remove_btn = ctk.CTkButton(button_container, text="Remove PDF", command=remove_pdf)
                remove_btn.pack(side="left", padx=20)

                # Show confirm button if both PDFs are present
                if left_pdf_path[0] and right_pdf_path[0]:
                    confirm_button = ctk.CTkButton(
                        button_container,
                        text="Confirm",
                        command=show_pages_in_tabs,
                        fg_color=("green", "green"),
                        hover_color=("darkgreen", "darkgreen"),
                        width=120,
                        height=40
                    )
                    confirm_button.pack(side="right", padx=20)

    # Function to show drop area
    def show_drop_area(frame, path_var):
        # Clear the frame
        for widget in frame.winfo_children():
            widget.destroy()

        # Create drop area
        drop_label = ctk.CTkLabel(frame, text="Drag and drop PDF or Image here", font=("Arial", 16))
        drop_label.pack(expand=True)

        # Add select button
        def select_file():
            file_path = filedialog.askopenfilename(
                filetypes=[
                    ("PDF and Image files", "*.pdf;*.png;*.jpg;*.jpeg;*.bmp;*.gif"),
                    ("PDF files", "*.pdf"),
                    ("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")
                ],
                title="Select a PDF or Image file"
            )
            if file_path:
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    # Convert image to PDF
                    pdf_bytes = convert_image_to_pdf(file_path)
                    if pdf_bytes:
                        path_var[0] = file_path  # Store original image path
                        show_pdf_preview(frame, pdf_bytes, path_var)
                else:
                    path_var[0] = file_path
                    show_pdf_preview(frame, file_path, path_var)

        select_btn = ctk.CTkButton(frame, text="Or select file", command=select_file)
        select_btn.pack(pady=(0, 20))

        # Enable drag and drop
        frame.drop_target_register(DND_FILES)
        
        def handle_drop(event):
            file_path = event.data.strip('{}')
            if file_path.lower().endswith('.pdf'):
                path_var[0] = file_path
                show_pdf_preview(frame, file_path, path_var)
            elif file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                # Convert image to PDF
                pdf_bytes = convert_image_to_pdf(file_path)
                if pdf_bytes:
                    path_var[0] = file_path  # Store original image path
                    show_pdf_preview(frame, pdf_bytes, path_var)
            else:
                messagebox.showwarning("Invalid File", "Please drop a PDF or image file (PNG, JPG, JPEG, BMP, GIF)")
        
        frame.dnd_bind('<<Drop>>', handle_drop)

    def convert_image_to_pdf(image_path, rotation=0):
        try:
            # Open the image
            img = Image.open(image_path)
            
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Rotate image if needed
            if rotation != 0:
                img = img.rotate(rotation, expand=True, resample=Image.Resampling.BICUBIC)
            
            # Define standard A4 size in pixels at 300 DPI
            A4_WIDTH = 2480  # 8.27 inches * 300 DPI
            A4_HEIGHT = 3508  # 11.69 inches * 300 DPI
            
            # Calculate scaling factor to fit image within A4 size while maintaining aspect ratio
            width_ratio = A4_WIDTH / img.width
            height_ratio = A4_HEIGHT / img.height
            scale_factor = min(width_ratio, height_ratio)
            
            # Calculate new dimensions
            new_width = int(img.width * scale_factor)
            new_height = int(img.height * scale_factor)
            
            # Resize image
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Create a new white background image of A4 size
            background = Image.new('RGB', (A4_WIDTH, A4_HEIGHT), (255, 255, 255))
            
            # Calculate position to center the image
            x_offset = (A4_WIDTH - new_width) // 2
            y_offset = (A4_HEIGHT - new_height) // 2
            
            # Paste the resized image onto the white background
            background.paste(img, (x_offset, y_offset))
            
            # Create PDF in memory
            pdf_bytes = io.BytesIO()
            background.save(pdf_bytes, 'PDF', resolution=300.0)
            pdf_bytes.seek(0)
            
            return pdf_bytes
        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert image to PDF: {str(e)}")
            return None

    # Initialize frames
    show_pdf_preview(left_frame, pdf_path, left_pdf_path)  # Show original PDF on left
    show_drop_area(right_frame, right_pdf_path)  # Show drop area on right

    def on_close():
        merge_win.destroy()
        parent.deiconify()

    merge_win.protocol("WM_DELETE_WINDOW", on_close)