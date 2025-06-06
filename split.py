import customtkinter as ctk
import fitz  # PyMuPDF
from PIL import ImageTk, Image
import io
import os

def open_split_screen(parent, pdf_path):
    # Hide the parent window
    parent.withdraw()

    # Create a new toplevel window
    split_win = ctk.CTkToplevel()
    split_win.title("Split PDF")
    split_win.configure(bg="#2b2b2b")

    # Get screen dimensions and center the window
    window_width = 1300
    window_height = 768
    screen_width = split_win.winfo_screenwidth()
    screen_height = split_win.winfo_screenheight()
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2
    split_win.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    # Create main frame
    main_frame = ctk.CTkFrame(split_win)
    main_frame.pack(expand=True, fill="both", padx=10, pady=10)

    # Create a frame for tabs
    tabs_frame = ctk.CTkFrame(main_frame)
    tabs_frame.pack(fill="x", padx=5, pady=5)

    # Create a frame for the content
    content_frame = ctk.CTkFrame(main_frame)
    content_frame.pack(expand=True, fill="both", padx=5, pady=5)

    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    
    # Calculate tab dimensions and spacing
    tab_width = 150
    tab_height = 200
    tab_spacing = 10
    tabs_per_row = (window_width - 40) // (tab_width + tab_spacing)
    
    # Dictionary to store page content frames
    page_frames = {}
    
    # Create tabs for each page
    for page_num in range(len(pdf_document)):
        # Calculate row and column position
        row = page_num // tabs_per_row
        col = page_num % tabs_per_row
        
        # Create a frame for the tab button
        tab_frame = ctk.CTkFrame(tabs_frame, width=tab_width, height=tab_height)
        tab_frame.grid(row=row, column=col, padx=tab_spacing, pady=tab_spacing)
        tab_frame.grid_propagate(False)  # Maintain fixed size
        
        # Get the page
        page = pdf_document[page_num]
        
        # Convert page to image for preview
        pix = page.get_pixmap(matrix=fitz.Matrix(0.3, 0.3))  # Smaller scale for preview
        img_data = pix.tobytes("png")
        
        # Create PIL Image
        img = Image.open(io.BytesIO(img_data))
        
        # Resize image to fit the tab while maintaining aspect ratio
        img.thumbnail((tab_width - 20, tab_height - 40), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(img)
        
        # Create label to display the preview image
        preview_label = ctk.CTkLabel(tab_frame, image=photo, text="")
        preview_label.image = photo  # Keep a reference
        preview_label.pack(pady=(5, 0))
        
        # Create page number label
        page_label = ctk.CTkLabel(tab_frame, text=f"Page {page_num + 1}")
        page_label.pack(pady=(0, 5))
        
        # Create content frame for this page
        page_frame = ctk.CTkFrame(content_frame)
        page_frames[page_num] = page_frame
        
        # Convert page to full-size image for content
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        
        # Resize image to fit the window while maintaining aspect ratio
        max_width = window_width - 40
        max_height = window_height - 150
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        full_photo = ImageTk.PhotoImage(img)
        
        # Create label to display the full image
        image_label = ctk.CTkLabel(page_frame, image=full_photo, text="")
        image_label.image = full_photo  # Keep a reference
        image_label.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Make the tab frame clickable
        tab_frame.bind("<Button-1>", lambda e, p=page_num: show_page(p))
        preview_label.bind("<Button-1>", lambda e, p=page_num: show_page(p))
        page_label.bind("<Button-1>", lambda e, p=page_num: show_page(p))
        
        # Hide all pages initially except the first one
        if page_num == 0:
            page_frame.pack(expand=True, fill="both")
            tab_frame.configure(fg_color=("gray75", "gray25"))  # Highlight selected tab
        else:
            page_frame.pack_forget()

    def show_page(page_num):
        # Hide all pages
        for frame in page_frames.values():
            frame.pack_forget()
        # Show selected page
        page_frames[page_num].pack(expand=True, fill="both")
        
        # Update tab highlighting
        for i, child in enumerate(tabs_frame.winfo_children()):
            if i == page_num:
                child.configure(fg_color=("gray75", "gray25"))
            else:
                child.configure(fg_color=("gray70", "gray30"))

    def on_close():
        pdf_document.close()
        split_win.destroy()
        parent.deiconify()

    split_win.protocol("WM_DELETE_WINDOW", on_close)
