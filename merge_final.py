import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD
import tkinter as tk
from tkinter import messagebox, filedialog
import os
from PIL import Image, ImageTk
import fitz  # PyMuPDF
import math
import io

def open_merge_final_screen(parent, selected_pages):
    # Hide the parent merge window
    parent.withdraw()
    
    # Create a new toplevel window
    final_win = ctk.CTkToplevel()
    final_win.title("Final PDF Merge")
    final_win.configure(bg="#2b2b2b")

    # Get screen dimensions
    screen_width = final_win.winfo_screenwidth()
    screen_height = final_win.winfo_screenheight()

    # Calculate position for center of the screen
    window_width = 1300
    window_height = 768
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2

    # Set window size and position
    final_win.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    # Global variables for drag and drop (enhanced)
    is_dragging = False
    drag_shadow = None
    drop_zone_indicator = None
    original_positions = {}
    current_animation = None
    pages_order = selected_pages.copy()  # Maintain order of pages

    # Create menu bar with dark theme
    menu_bar = tk.Menu(final_win, 
                      bg='#2b2b2b',
                      fg='white',
                      activebackground='#404040',
                      activeforeground='white')
    final_win.config(menu=menu_bar)

    # File menu
    file_menu = tk.Menu(menu_bar, 
                       tearoff=0,
                       bg='#2b2b2b',
                       fg='white',
                       activebackground='#404040',
                       activeforeground='white')
    menu_bar.add_cascade(label="File", menu=file_menu)

    # Save menu
    def save_pdf():
        if not pages_order:
            messagebox.showwarning(
                "No Pages", 
                "No pages to save.",
                parent=final_win
            )
            return

        # Open save dialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save merged PDF as"
        )
        
        if file_path:
            try:
                # Create new PDF document
                new_doc = fitz.open()
                
                # Add each page in the current order
                for page_data in pages_order:
                    # Get the source document and page
                    source_doc = page_data['doc']
                    page_num = page_data['page_num']
                    
                    # Insert the page into the new document
                    new_doc.insert_pdf(source_doc, from_page=page_num, to_page=page_num)
                
                # Save the new document
                new_doc.save(file_path)
                new_doc.close()
                
                messagebox.showinfo(
                    "Success", 
                    f"PDF saved successfully as:\n{file_path}",
                    parent=final_win
                )
                
            except Exception as e:
                messagebox.showerror(
                    "Error", 
                    f"Failed to save PDF:\n{str(e)}",
                    parent=final_win
                )

    menu_bar.add_command(label="Save PDF", command=save_pdf)

    # Back menu
    def go_back():
        nonlocal current_animation
        if current_animation:
            final_win.after_cancel(current_animation)
        final_win.destroy()
        parent.deiconify()  # Show the merge window again

    menu_bar.add_command(label="Back", command=go_back)

    # Configure menu colors
    menu_bar.configure(
        bg='#2b2b2b',
        fg='white',
        activebackground='#404040',
        activeforeground='white',
        relief='flat'
    )

    # Create main container
    main_container = ctk.CTkFrame(final_win)
    main_container.pack(expand=True, fill="both", padx=10, pady=10)

    # Add title
    title_frame = ctk.CTkFrame(main_container, fg_color="transparent")
    title_frame.pack(fill="x", pady=(10, 5))

    title_label = ctk.CTkLabel(
        title_frame, 
        text="Selected Pages for Final PDF", 
        font=ctk.CTkFont(size=20, weight="bold")
    )
    title_label.pack()

    # Add page count info
    info_label = ctk.CTkLabel(
        title_frame, 
        text=f"Total pages selected: {len(pages_order)}", 
        font=ctk.CTkFont(size=14)
    )
    info_label.pack(pady=(5, 0))

    # Add legend for PDF colors
    legend_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
    legend_frame.pack(pady=(10, 0))

    pdf1_legend = ctk.CTkLabel(
        legend_frame,
        text="● PDF 1",
        font=ctk.CTkFont(size=12),
        text_color="#4CAF50"  # Green for PDF 1
    )
    pdf1_legend.pack(side="left", padx=20)

    pdf2_legend = ctk.CTkLabel(
        legend_frame,
        text="● PDF 2",
        font=ctk.CTkFont(size=12),
        text_color="#2196F3"  # Blue for PDF 2
    )
    pdf2_legend.pack(side="left", padx=20)

    # Create scrollable frame for page thumbnails
    scroll_frame = ctk.CTkScrollableFrame(main_container)
    scroll_frame.pack(expand=True, fill="both", padx=10, pady=10)

    # Function to create page thumbnail
    def create_page_thumbnail(page, scale=0.15):
        pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        return ImageTk.PhotoImage(img)

    # Calculate grid layout parameters - FIXED VALUES
    thumbnail_width = 170 # 140
    thumbnail_height = 180
    padding = 18 #12
    columns = 6  # Fixed number of columns for consistent layout
    
    # Function to get grid position from coordinates
    def get_grid_position(x, y):
        # Account for scroll frame padding
        scroll_x = max(0, x - padding)
        scroll_y = max(0, y - padding)
        
        col = min(columns - 1, max(0, int(scroll_x // (thumbnail_width + 2 * padding))))
        row = max(0, int(scroll_y // (thumbnail_height + 2 * padding)))
        
        return row, col
    
    # Function to get pixel coordinates from grid position
    def get_pixel_position(row, col):
        x = col * (thumbnail_width + 2 * padding) + padding
        y = row * (thumbnail_height + 2 * padding) + padding
        return x, y
    
    # Function to refresh the page display
    def refresh_pages():
        nonlocal info_label
        
        # Clear the scroll frame
        for widget in scroll_frame.winfo_children():
            widget.destroy()

        # Update page count
        info_label.configure(text=f"Total pages selected: {len(pages_order)}")
        
        # Configure grid weights for even distribution
        for col in range(columns):
            scroll_frame.grid_columnconfigure(col, weight=1, uniform="column")

        # Create grid layout for all pages
        for display_index, page_data in enumerate(pages_order):
            row = display_index // columns
            col = display_index % columns
            
            page = page_data['doc'][page_data['page_num']]
            
            # Determine colors based on PDF source
            if page_data['original_pdf'] == 'left':
                border_color = "#4CAF50"  # Green for PDF 1
                text_color = "#4CAF50"
            else:
                border_color = "#2196F3"  # Blue for PDF 2
                text_color = "#2196F3"
            
            # Create page frame with colored border
            page_frame = ctk.CTkFrame(
                scroll_frame, 
                width=thumbnail_width, 
                height=thumbnail_height,
                border_width=3,
                border_color=border_color
            )
            page_frame.grid(
                row=row, 
                column=col, 
                padx=padding, 
                pady=padding, 
                sticky="nsew"
            )
            page_frame.grid_propagate(False)
            
            # Store page data and position in the frame
            page_frame.page_data = page_data
            page_frame.display_index = display_index
            
            # Create thumbnail
            thumbnail = create_page_thumbnail(page)
            
            # Create image label
            image_label = ctk.CTkLabel(
                page_frame, 
                image=thumbnail, 
                text="",
            )
            image_label.image = thumbnail
            image_label.pack(expand=True, fill="both", pady=(5,0))
            
            # Create page info label with colored text
            pdf_source = "PDF 1" if page_data['original_pdf'] == 'left' else "PDF 2"
            page_info_label = ctk.CTkLabel(
                page_frame, 
                text=f"{pdf_source} - P{page_data['page_num'] + 1}",
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=text_color
            )
            page_info_label.pack(pady=(0,2))

            # Add order number in top-left corner
            order_label = ctk.CTkLabel(
                page_frame,
                text=str(display_index + 1),
                font=ctk.CTkFont(size=10, weight="bold"),
                fg_color=("#1f538d", "#14375e"),
                corner_radius=8,
                width=20,
                height=20
            )
            order_label.place(relx=0.0, rely=0.0, anchor="nw", x=2, y=2)

            # Add remove button in top-right corner
            remove_btn = ctk.CTkButton(
                page_frame,
                text="×",
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=("#ff4444", "#cc3333"),
                hover_color=("#ff6666", "#ff4444"),
                corner_radius=8,
                width=20,
                height=20,
                command=lambda idx=display_index: remove_page(idx)
            )
            remove_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-2, y=2)

            # Bind enhanced drag events
            bind_drag_events(page_frame, image_label, page_info_label)

    # Function to remove a page
    def remove_page(index):
        if 0 <= index < len(pages_order):
            pages_order.pop(index)
            refresh_pages()

    # Enhanced drag and drop functions with FIXED positioning
    def bind_drag_events(page_frame, image_label, page_info_label):
        def on_drag_start(event):
            nonlocal is_dragging, drag_shadow, original_positions, current_animation
            
            if is_dragging or current_animation:
                return
                
            try:
                # Check if frame still exists and is managed by grid
                if not page_frame.winfo_exists() or not page_frame.grid_info():
                    return
                    
                is_dragging = True
                original_positions[page_frame] = {
                    'row': page_frame.grid_info()['row'],
                    'column': page_frame.grid_info()['column']
                }
                
                page_frame._drag_start_x = event.x
                page_frame._drag_start_y = event.y
                
                if drag_shadow:
                    drag_shadow.destroy()
                    drag_shadow = None
                
                # Create drag shadow
                drag_shadow = ctk.CTkFrame(
                    scroll_frame, 
                    width=thumbnail_width, 
                    height=thumbnail_height,
                    fg_color=("gray40", "gray60"),
                    border_width=3,
                    border_color=("#3B8ED0", "#3B8ED0")
                )
                
                # Copy content to shadow
                shadow_img_label = ctk.CTkLabel(drag_shadow, image=image_label.cget("image"), text="")
                shadow_img_label.pack(pady=(5, 0))
                shadow_page_label = ctk.CTkLabel(drag_shadow, text=page_info_label.cget("text"))
                shadow_page_label.pack(pady=(0, 5))
                
                drag_shadow.place(x=page_frame.winfo_x(), y=page_frame.winfo_y())
                drag_shadow.lift()
                
                # Highlight original frame
                page_frame.configure(fg_color=("gray80", "gray20"), corner_radius=10)
                
                # Add visual feedback to other frames
                for child in scroll_frame.winfo_children():
                    if child != page_frame and hasattr(child, 'page_data'):
                        child.configure(border_width=1, border_color=("gray70", "gray50"))
            except Exception as e:
                is_dragging = False
                if drag_shadow and drag_shadow.winfo_exists():
                    drag_shadow.destroy()
                drag_shadow = None
                print(f"Failed to start drag: {str(e)}")

        def on_drag_motion(event):
            nonlocal drag_shadow, drop_zone_indicator
            
            if not is_dragging or drag_shadow is None or not page_frame.winfo_exists():
                return
                
            try:
                # Calculate new position for drag shadow
                x = page_frame.winfo_x() - page_frame._drag_start_x + event.x
                y = page_frame.winfo_y() - page_frame._drag_start_y + event.y
                
                if drag_shadow.winfo_exists():
                    drag_shadow.place(x=x, y=y)
                
                # Calculate target grid position using FIXED grid calculation
                target_row, target_col = get_grid_position(x, y)
                target_pos = target_row * columns + target_col
                
                # Clean up previous drop zone indicator
                if drop_zone_indicator:
                    drop_zone_indicator.destroy()
                    drop_zone_indicator = None
                
                # Show drop zone indicator if valid position
                if 0 <= target_pos < len(pages_order):
                    # Get exact pixel position for the target grid cell
                    target_x, target_y = get_pixel_position(target_row, target_col)
                    
                    # Create drop zone indicator at exact grid position
                    drop_zone_indicator = ctk.CTkFrame(
                        scroll_frame,
                        width=thumbnail_width,
                        height=thumbnail_height,
                        fg_color="transparent",
                        border_width=3,
                        border_color=("#1f538d", "#42a2d6"),
                        corner_radius=15
                    )
                    drop_zone_indicator.place(x=target_x, y=target_y)
                    
                    pulse_label = ctk.CTkLabel(
                        drop_zone_indicator, 
                        text="Drop Here",
                        font=ctk.CTkFont(size=12, weight="bold"),
                        text_color=("#1f538d", "#42a2d6")
                    )
                    pulse_label.place(relx=0.5, rely=0.5, anchor="center")
                    
            except Exception as e:
                if drop_zone_indicator and drop_zone_indicator.winfo_exists():
                    drop_zone_indicator.destroy()
                drop_zone_indicator = None

        def on_drag_release(event):
            nonlocal is_dragging, drag_shadow, drop_zone_indicator, original_positions, current_animation
            
            if not is_dragging or not page_frame.winfo_exists():
                return
                
            try:
                is_dragging = False
                
                final_x = final_y = 0
                if drag_shadow and drag_shadow.winfo_exists():
                    final_x = drag_shadow.winfo_x()
                    final_y = drag_shadow.winfo_y()
                    drag_shadow.destroy()
                    drag_shadow = None
                
                if drop_zone_indicator and drop_zone_indicator.winfo_exists():
                    drop_zone_indicator.destroy()
                    drop_zone_indicator = None
                
                # Reset all frame colors
                for child in scroll_frame.winfo_children():
                    if hasattr(child, 'page_data'):
                        if child.page_data['original_pdf'] == 'left':
                            border_color = "#4CAF50"
                        else:
                            border_color = "#2196F3"
                        child.configure(
                            fg_color=("gray60", "gray30"), 
                            border_width=3,
                            border_color=border_color,
                            corner_radius=6
                        )
                
                # Calculate target position using FIXED grid calculation
                target_row, target_col = get_grid_position(final_x, final_y)
                target_pos = target_row * columns + target_col
                
                if 0 <= target_pos < len(pages_order):
                    # Get the current position of the dragged frame
                    current_pos = page_frame.display_index
                    
                    if current_pos != target_pos:
                        # Perform the swap in pages_order
                        page_to_move = pages_order.pop(current_pos)
                        pages_order.insert(target_pos, page_to_move)
                        
                        # Animate the swap and refresh
                        animate_swap_and_refresh(page_frame, current_pos, target_pos)
                    else:
                        animate_return_to_original(page_frame)
                else:
                    animate_return_to_original(page_frame)
            except Exception as e:
                if drag_shadow and drag_shadow.winfo_exists():
                    drag_shadow.destroy()
                if drop_zone_indicator and drop_zone_indicator.winfo_exists():
                    drop_zone_indicator.destroy()
                print(f"Failed to complete drag: {str(e)}")

        # Bind events to frame and its children
        page_frame.bind("<Button-1>", on_drag_start)
        page_frame.bind("<B1-Motion>", on_drag_motion)
        page_frame.bind("<ButtonRelease-1>", on_drag_release)
        
        image_label.bind("<Button-1>", on_drag_start)
        image_label.bind("<B1-Motion>", on_drag_motion)
        image_label.bind("<ButtonRelease-1>", on_drag_release)
        
        page_info_label.bind("<Button-1>", on_drag_start)
        page_info_label.bind("<B1-Motion>", on_drag_motion)
        page_info_label.bind("<ButtonRelease-1>", on_drag_release)

    def animate_swap_and_refresh(frame, current_pos, target_pos):
        nonlocal current_animation
        
        if current_animation:
            final_win.after_cancel(current_animation)
            current_animation = None
        
        try:
            # Highlight the moved frame briefly
            frame.configure(fg_color=("#4a9eff", "#4a9eff"))
            
            def finish_animation():
                nonlocal current_animation
                current_animation = None
                if frame.winfo_exists():
                    if frame.page_data['original_pdf'] == 'left':
                        border_color = "#4CAF50"
                    else:
                        border_color = "#2196F3"
                    frame.configure(fg_color=("gray60", "gray30"), border_color=border_color)
                # Refresh the entire display to show new positions
                refresh_pages()
            
            current_animation = final_win.after(200, finish_animation)
        except Exception as e:
            print(f"Failed to animate swap: {str(e)}")
            refresh_pages()

    def animate_return_to_original(frame):
        nonlocal current_animation
        
        if current_animation:
            final_win.after_cancel(current_animation)
            current_animation = None
        
        if frame in original_positions and frame.winfo_exists():
            try:
                if frame.page_data['original_pdf'] == 'left':
                    border_color = "#4CAF50"
                else:
                    border_color = "#2196F3"
                frame.configure(fg_color=("gray60", "gray30"), border_color=border_color)
            except:
                pass

    # Create bottom button frame
    button_frame = ctk.CTkFrame(main_container, fg_color="transparent")
    button_frame.pack(fill="x", pady=(10, 0))

    # Add instruction text
    instruction_label = ctk.CTkLabel(
        button_frame,
        text="Click and drag pages to reorder • Click × to remove pages",
        font=ctk.CTkFont(size=12),
        text_color="gray60"
    )
    instruction_label.pack(pady=(0, 10))

    # Button container
    btn_container = ctk.CTkFrame(button_frame, fg_color="transparent")
    btn_container.pack()

    # Add back button
    back_button = ctk.CTkButton(
        btn_container,
        text="← Back",
        width=120,
        height=40,
        font=ctk.CTkFont(size=14, weight="bold"),
        command=go_back
    )
    back_button.pack(side="left", padx=20)

    # Add save button
    save_button = ctk.CTkButton(
        btn_container,
        text="Save PDF",
        width=120,
        height=40,
        font=ctk.CTkFont(size=14, weight="bold"),
        command=save_pdf,
        fg_color=("#4CAF50", "#45a049"),
        hover_color=("#45a049", "#4CAF50")
    )
    save_button.pack(side="left", padx=20)

    # Initialize the page display
    refresh_pages()

    # Handle window close event
    def on_close():
        nonlocal current_animation
        if current_animation:
            final_win.after_cancel(current_animation)
        final_win.destroy()
        parent.deiconify()  # Show the merge window again

    final_win.protocol("WM_DELETE_WINDOW", on_close)