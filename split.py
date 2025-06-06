import customtkinter as ctk
import fitz  # PyMuPDF
from PIL import ImageTk, Image
import io
import os
import math
import tkinter as tk

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

    # Create main container
    main_container = ctk.CTkFrame(split_win)
    main_container.pack(expand=True, fill="both", padx=10, pady=10)

    # Create main frame (left side)
    main_frame = ctk.CTkFrame(main_container)
    main_frame.pack(side="left", expand=True, fill="both", padx=(0, 5))

    # --- Scrollable Tabs Area ---
    scroll_frame = ctk.CTkFrame(main_frame)
    scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

    canvas = tk.Canvas(scroll_frame, bg="#2b2b2b", highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar = tk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Create a frame inside the canvas for tabs
    tabs_frame = ctk.CTkFrame(canvas)
    tabs_window = canvas.create_window((0, 0), window=tabs_frame, anchor="nw")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfig(tabs_window, width=canvas.winfo_width())
    tabs_frame.bind("<Configure>", on_frame_configure)

    def on_canvas_configure(event):
        canvas.itemconfig(tabs_window, width=event.width)
    canvas.bind("<Configure>", on_canvas_configure)

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # --- End Scrollable Tabs Area ---

    # Create right side panel (initially hidden) - Made wider
    right_panel_width = window_width  # Use full window width
    right_panel = ctk.CTkFrame(main_container, width=right_panel_width)
    right_panel_visible = False

    # Create overlay label for semi-transparent effect
    overlay_label = ctk.CTkLabel(main_frame, text="", fg_color=("gray60", "gray30"))
    
    def show_right_panel():
        nonlocal right_panel_visible
        if not right_panel_visible:
            # Hide the main frame completely
            main_frame.pack_forget()
            right_panel.pack(fill="both", expand=True)
            right_panel.configure(width=right_panel_width)
            
            # Show overlay with semi-transparent effect
            overlay_label.place(relx=0, rely=0, relwidth=1, relheight=1)
            overlay_label.configure(fg_color=("gray70", "gray40"))
            overlay_label.lift()
            
            # Disable interactions with tabs by binding click events to overlay
            def block_clicks(event):
                pass
            overlay_label.bind("<Button-1>", block_clicks)
            overlay_label.bind("<Double-Button-1>", block_clicks)
            
            right_panel_visible = True

    def hide_right_panel():
        nonlocal right_panel_visible
        if right_panel_visible:
            right_panel.pack_forget()
            overlay_label.place_forget()
            # Restore main frame
            main_frame.pack(side="left", expand=True, fill="both", padx=(0, 5))
            right_panel_visible = False

    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    num_pages = len(pdf_document)

    def show_page_detail(page_num):
        # Clear right panel
        for widget in right_panel.winfo_children():
            widget.destroy()
        
        # Show right panel
        show_right_panel()
        
        # Create header with back button
        header_frame = ctk.CTkFrame(right_panel)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        back_button = ctk.CTkButton(
            header_frame, 
            text="← Back", 
            command=hide_right_panel,
            width=80,
            height=30
        )
        back_button.pack(side="left", padx=5, pady=5)
        
        page_title = ctk.CTkLabel(
            header_frame, 
            text=f"Page {page_num + 1} of {num_pages}",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        page_title.pack(side="left", padx=20, pady=5)
        
        # Create a container frame for the page and zoom controls
        page_container = ctk.CTkFrame(right_panel)
        page_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create scrollable frame for the page image
        page_scroll_frame = ctk.CTkScrollableFrame(page_container)
        page_scroll_frame.pack(fill="both", expand=True)
        
        # Get the page and create high-quality image
        page = pdf_document[page_num]
        
        # Get page dimensions
        page_rect = page.rect
        page_width = page_rect.width
        page_height = page_rect.height
        
        # Create a frame for the zoom slider
        zoom_frame = ctk.CTkFrame(page_container)
        zoom_frame.pack(fill="x", pady=(10, 0))
        
        # Add zoom out button
        zoom_out_btn = ctk.CTkButton(
            zoom_frame,
            text="-",
            width=30,
            command=lambda: update_zoom(zoom_slider.get() - 0.1)
        )
        zoom_out_btn.pack(side="left", padx=(10, 5))
        
        # Add zoom slider
        zoom_slider = ctk.CTkSlider(
            zoom_frame,
            from_=0.5,
            to=3.0,
            number_of_steps=25,
            command=lambda x: update_zoom(x)
        )
        zoom_slider.pack(side="left", fill="x", expand=True, padx=5)
        zoom_slider.set(1.0)  # Set initial zoom level
        
        # Add zoom in button
        zoom_in_btn = ctk.CTkButton(
            zoom_frame,
            text="+",
            width=30,
            command=lambda: update_zoom(zoom_slider.get() + 0.1)
        )
        zoom_in_btn.pack(side="left", padx=(5, 10))
        
        # Add zoom percentage label
        zoom_label = ctk.CTkLabel(zoom_frame, text="100%")
        zoom_label.pack(side="left", padx=10)
        
        # Create a label to hold the page image
        page_image_label = ctk.CTkLabel(page_scroll_frame, text="")
        page_image_label.pack(pady=10)
        
        def update_zoom(scale):
            # Clamp the scale between 0.5 and 3.0
            scale = max(0.5, min(3.0, scale))
            zoom_slider.set(scale)
            
            # Update zoom percentage label
            zoom_label.configure(text=f"{int(scale * 100)}%")
            
            # Get the page and create high-quality image with new scale
            pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale))
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            photo = ImageTk.PhotoImage(img)
            page_image_label.configure(image=photo)
            page_image_label.image = photo  # Keep a reference
            
            # Update scroll region
            page_scroll_frame.update_idletasks()
            page_scroll_frame._parent_canvas.configure(scrollregion=page_scroll_frame._parent_canvas.bbox("all"))
        
        # Enable mouse wheel scrolling
        def on_mousewheel(event):
            # Increase scroll speed by multiplying the delta by 10
            page_scroll_frame._parent_canvas.yview_scroll(int(-10 * (event.delta / 120)), "units")
        
        page_scroll_frame.bind_all("<MouseWheel>", on_mousewheel)
        
        # Clean up binding when panel is hidden
        def cleanup_binding():
            page_scroll_frame.unbind_all("<MouseWheel>")
        
        right_panel.bind("<Unmap>", lambda e: cleanup_binding())
        
        # Initial render
        update_zoom(1.0)

    # Dynamic tab layout - updated to account for variable panel width
    tab_spacing = 10
    # Calculate columns based on current available width
    min_tab_width = 130
    def get_available_width():
        if right_panel_visible:
            return int(window_width * 0.25) - 40  # Account for padding when right panel is visible
        else:
            return window_width - 40  # Full width when right panel is hidden
    
    available_width = get_available_width()
    columns = max(1, available_width // (min_tab_width + tab_spacing))
    columns = min(num_pages, columns)
    rows = math.ceil(num_pages / columns)
    
    # Calculate actual tab dimensions
    actual_tab_width = int((available_width - ((columns + 1) * tab_spacing)) / columns)
    actual_tab_height = int((window_height - ((rows + 1) * tab_spacing)) / rows)
    
    # Keep aspect ratio reasonable (not too tall)
    max_aspect = 1.4
    if actual_tab_height > actual_tab_width * max_aspect:
        actual_tab_height = int(actual_tab_width * max_aspect)

    # Create tabs for each page
    for page_num in range(num_pages):
        row = page_num // columns
        col = page_num % columns

        # Create a frame for the tab button
        tab_frame = ctk.CTkFrame(tabs_frame, width=actual_tab_width, height=actual_tab_height)
        tab_frame.grid(row=row, column=col, padx=tab_spacing, pady=tab_spacing, sticky="nsew")
        tab_frame.grid_propagate(False)
        
        # Store the page number in the frame for reference
        tab_frame.page_num = page_num

        # Get the page
        page = pdf_document[page_num]

        # Convert page to image for preview
        pix = page.get_pixmap(matrix=fitz.Matrix(0.3, 0.3))
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        img.thumbnail((actual_tab_width - 20, actual_tab_height - 40), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)

        # Create label to display the preview image
        preview_label = ctk.CTkLabel(tab_frame, image=photo, text="")
        preview_label.image = photo
        preview_label.pack(pady=(5, 0))

        # Create page number label
        page_label = ctk.CTkLabel(tab_frame, text=f"Page {page_num + 1}")
        page_label.pack(pady=(0, 5))

        # Create a preview frame (initially hidden)
        preview_frame = ctk.CTkFrame(tabs_frame, width=actual_tab_width, height=actual_tab_height,
                                   fg_color=("gray70", "gray40"), border_width=2, border_color=("white", "gray"))
        preview_frame.place_forget()  # Initially hidden

        # Add drag and drop functionality
        def on_drag_start(event, frame=tab_frame, preview=preview_frame):
            # Store the starting position
            frame._drag_start_x = event.x
            frame._drag_start_y = event.y
            frame.lift()  # Bring to front while dragging
            frame.configure(fg_color=("gray70", "gray40"))  # Highlight while dragging
            # Show preview frame
            preview.lift()
            preview.place(x=frame.winfo_x(), y=frame.winfo_y())

        def on_drag_motion(event, frame=tab_frame, preview=preview_frame):
            # Calculate new position
            x = frame.winfo_x() - frame._drag_start_x + event.x
            y = frame.winfo_y() - frame._drag_start_y + event.y
            frame.place(x=x, y=y)
            
            # Calculate the potential new grid position
            new_col = max(0, min(columns - 1, int(x / (actual_tab_width + tab_spacing))))
            new_row = max(0, min(rows - 1, int(y / (actual_tab_height + tab_spacing))))
            
            # Calculate the position for the preview frame
            preview_x = new_col * (actual_tab_width + tab_spacing) + tab_spacing
            preview_y = new_row * (actual_tab_height + tab_spacing) + tab_spacing
            
            # Update preview frame position
            preview.place(x=preview_x, y=preview_y)

        def on_drag_release(event, frame=tab_frame, preview=preview_frame):
            # Hide preview frame
            preview.place_forget()
            
            # Reset appearance
            frame.configure(fg_color=("gray60", "gray30"))
            
            # Calculate the new grid position
            x = frame.winfo_x()
            y = frame.winfo_y()
            
            # Calculate new column and row
            new_col = max(0, min(columns - 1, int(x / (actual_tab_width + tab_spacing))))
            new_row = max(0, min(rows - 1, int(y / (actual_tab_height + tab_spacing))))
            
            # Get the target page number
            target_pos = new_row * columns + new_col
            if 0 <= target_pos < num_pages:
                # Get the current page number
                current_page = frame.page_num
                
                # Update the grid positions of all affected frames
                for i in range(num_pages):
                    if i == current_page:
                        continue
                    other_frame = tabs_frame.grid_slaves(row=i//columns, column=i%columns)[0]
                    if i == target_pos:
                        # Move the dragged frame to the target position
                        frame.grid(row=new_row, column=new_col)
                        # Move the target frame to the old position
                        other_frame.grid(row=current_page//columns, column=current_page%columns)
                        # Update page numbers
                        other_frame.page_num = current_page
                        frame.page_num = target_pos
                        # Update labels
                        other_frame.winfo_children()[1].configure(text=f"Page {current_page + 1}")
                        frame.winfo_children()[1].configure(text=f"Page {target_pos + 1}")
                        break
            
            # Reset the frame's position in the grid
            frame.grid(row=new_row, column=new_col)

        # Bind drag and drop events
        tab_frame.bind("<Button-1>", on_drag_start)
        tab_frame.bind("<B1-Motion>", on_drag_motion)
        tab_frame.bind("<ButtonRelease-1>", on_drag_release)
        
        # Bind double-click event to show page detail
        def make_double_click_handler(page_idx):
            def on_double_click(event):
                show_page_detail(page_idx)
            return on_double_click

        # Bind double-click to both the frame and its children
        double_click_handler = make_double_click_handler(page_num)
        tab_frame.bind("<Double-Button-1>", double_click_handler)
        preview_label.bind("<Double-Button-1>", double_click_handler)
        page_label.bind("<Double-Button-1>", double_click_handler)

    # Make columns expand equally
    for col in range(columns):
        tabs_frame.grid_columnconfigure(col, weight=1)
    for row in range(rows):
        tabs_frame.grid_rowconfigure(row, weight=1)

    def on_close():
        pdf_document.close()
        split_win.destroy()
        parent.deiconify()

    split_win.protocol("WM_DELETE_WINDOW", on_close)