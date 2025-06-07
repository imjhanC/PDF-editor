import customtkinter as ctk
import fitz  # PyMuPDF
from PIL import ImageTk, Image
import io
import os
import math
import tkinter as tk
from tkinter import filedialog, messagebox


def open_split_screen(parent, pdf_path):
    # Hide the parent window
    parent.withdraw()

    # Create a new toplevel window
    split_win = ctk.CTkToplevel()
    split_win.title("Split PDF")
    split_win.configure(bg="#2b2b2b")

    # Create menu bar with dark theme
    menu_bar = tk.Menu(split_win, 
                      bg='#2b2b2b',
                      fg='white',
                      activebackground='#404040',
                      activeforeground='white')
    split_win.config(menu=menu_bar)

    # File menu
    file_menu = tk.Menu(menu_bar, 
                       tearoff=0,
                       bg='#2b2b2b',
                       fg='white',
                       activebackground='#404040',
                       activeforeground='white')
    menu_bar.add_cascade(label="File", menu=file_menu)
    
    def save_as():
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save PDF As"
        )
        if file_path:
            try:
                # Create a new PDF document
                new_doc = fitz.open()
                
                # Use the current_page_order which tracks the swaps
                print(f"Saving PDF with page order: {current_page_order}")
                
                # Add pages in the current swapped order
                for original_page_num in current_page_order:
                    new_doc.insert_pdf(pdf_document, from_page=original_page_num, to_page=original_page_num)
                
                # Save the new PDF
                new_doc.save(file_path)
                new_doc.close()
                
                messagebox.showinfo("Success", f"PDF saved successfully with {len(current_page_order)} pages!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save PDF: {str(e)}")


    # Add Save As to File menu
    file_menu.add_command(label="Save As", command=save_as)

    # New menu
    def new_pdf():
        messagebox.showinfo("New", "New PDF functionality will be implemented soon!")
    menu_bar.add_command(label="New", command=new_pdf)

    # Exit menu
    menu_bar.add_command(label="Exit", command=split_win.destroy)

    # Configure menu colors
    menu_bar.configure(
        bg='#2b2b2b',
        fg='white',
        activebackground='#404040',
        activeforeground='white',
        relief='flat'
    )

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

    # Create right side panel (initially hidden)
    right_panel_width = window_width
    right_panel = ctk.CTkFrame(main_container, width=right_panel_width)
    right_panel_visible = False

    # Create overlay label for semi-transparent effect
    overlay_label = ctk.CTkLabel(main_frame, text="", fg_color=("gray60", "gray30"))
    
    def show_right_panel():
        nonlocal right_panel_visible
        if not right_panel_visible:
            main_frame.pack_forget()
            right_panel.pack(fill="both", expand=True)
            right_panel.configure(width=right_panel_width)
            
            overlay_label.place(relx=0, rely=0, relwidth=1, relheight=1)
            overlay_label.configure(fg_color=("gray70", "gray40"))
            overlay_label.lift()
            
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
            main_frame.pack(side="left", expand=True, fill="both", padx=(0, 5))
            right_panel_visible = False

    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    num_pages = len(pdf_document)
    current_page_order = list(range(num_pages))

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
        zoom_slider.set(1.0)
        
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
            scale = max(0.5, min(3.0, scale))
            zoom_slider.set(scale)
            
            zoom_label.configure(text=f"{int(scale * 100)}%")
            
            pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale))
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            photo = ImageTk.PhotoImage(img)
            page_image_label.configure(image=photo)
            page_image_label.image = photo
            
            page_scroll_frame.update_idletasks()
            page_scroll_frame._parent_canvas.configure(scrollregion=page_scroll_frame._parent_canvas.bbox("all"))
        
        def on_mousewheel(event):
            page_scroll_frame._parent_canvas.yview_scroll(int(-10 * (event.delta / 120)), "units")
        
        page_scroll_frame.bind_all("<MouseWheel>", on_mousewheel)
        
        def cleanup_binding():
            page_scroll_frame.unbind_all("<MouseWheel>")
        
        right_panel.bind("<Unmap>", lambda e: cleanup_binding())
        
        update_zoom(1.0)

    # Dynamic tab layout
    tab_spacing = 10
    min_tab_width = 130
    
    def get_available_width():
        if right_panel_visible:
            return int(window_width * 0.25) - 40
        else:
            return window_width - 40
    
    available_width = get_available_width()
    columns = max(1, available_width // (min_tab_width + tab_spacing))
    columns = min(num_pages, columns)
    rows = math.ceil(num_pages / columns)
    
    actual_tab_width = int((available_width - ((columns + 1) * tab_spacing)) / columns)
    actual_tab_height = int((window_height - ((rows + 1) * tab_spacing)) / rows)
    
    max_aspect = 1.4
    if actual_tab_height > actual_tab_width * max_aspect:
        actual_tab_height = int(actual_tab_width * max_aspect)

    # Variables for enhanced drag effects
    is_dragging = False
    drag_shadow = None
    drop_zone_indicator = None
    original_positions = {}
    current_animation = None

    # Create tabs for each page
    for page_num in range(num_pages):
        row = page_num // columns
        col = page_num % columns

        tab_frame = ctk.CTkFrame(tabs_frame, width=actual_tab_width, height=actual_tab_height)
        tab_frame.grid(row=row, column=col, padx=tab_spacing, pady=tab_spacing, sticky="nsew")
        tab_frame.grid_propagate(False)
        tab_frame.page_num = page_num

        page = pdf_document[page_num]
        pix = page.get_pixmap(matrix=fitz.Matrix(0.3, 0.3))
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        img.thumbnail((actual_tab_width - 20, actual_tab_height - 40), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)

        preview_label = ctk.CTkLabel(tab_frame, image=photo, text="")
        preview_label.image = photo
        preview_label.pack(pady=(5, 0))

        page_label = ctk.CTkLabel(tab_frame, text=f"Page {page_num + 1}")
        page_label.pack(pady=(0, 5))

        def on_drag_start(event, frame=tab_frame):
            nonlocal is_dragging, drag_shadow, original_positions, current_animation
            
            if is_dragging or current_animation:
                return
                
            is_dragging = True
            original_positions[frame] = {
                'row': frame.grid_info()['row'],
                'column': frame.grid_info()['column']
            }
            
            frame._drag_start_x = event.x
            frame._drag_start_y = event.y
            
            if drag_shadow:
                drag_shadow.destroy()
                drag_shadow = None
            
            drag_shadow = ctk.CTkFrame(
                tabs_frame, 
                width=actual_tab_width, 
                height=actual_tab_height,
                fg_color=("gray40", "gray60"),
                border_width=3,
                border_color=("#3B8ED0", "#3B8ED0")
            )
            
            shadow_img_label = ctk.CTkLabel(drag_shadow, image=frame.winfo_children()[0].cget("image"), text="")
            shadow_img_label.pack(pady=(5, 0))
            shadow_page_label = ctk.CTkLabel(drag_shadow, text=frame.winfo_children()[1].cget("text"))
            shadow_page_label.pack(pady=(0, 5))
            
            drag_shadow.place(x=frame.winfo_x(), y=frame.winfo_y())
            drag_shadow.lift()
            
            frame.configure(fg_color=("gray80", "gray20"), corner_radius=10)
            
            for child in tabs_frame.winfo_children():
                if child != frame and hasattr(child, 'page_num'):
                    child.configure(border_width=1, border_color=("gray70", "gray50"))

        def on_drag_motion(event, frame=tab_frame):
            nonlocal drag_shadow, drop_zone_indicator
            
            if not is_dragging or drag_shadow is None:
                return
                
            x = frame.winfo_x() - frame._drag_start_x + event.x
            y = frame.winfo_y() - frame._drag_start_y + event.y
            
            if drag_shadow.winfo_exists():
                drag_shadow.place(x=x, y=y)
            
            new_col = max(0, min(columns - 1, int(x / (actual_tab_width + tab_spacing))))
            new_row = max(0, min(rows - 1, int(y / (actual_tab_height + tab_spacing))))
            
            if drop_zone_indicator:
                drop_zone_indicator.destroy()
                drop_zone_indicator = None
            
            target_pos = new_row * columns + new_col
            if 0 <= target_pos < num_pages:
                target_x = new_col * (actual_tab_width + tab_spacing) + tab_spacing
                target_y = new_row * (actual_tab_height + tab_spacing) + tab_spacing
                
                drop_zone_indicator = ctk.CTkFrame(
                    tabs_frame,
                    width=actual_tab_width,
                    height=actual_tab_height,
                    fg_color="transparent",
                    border_width=3,
                    border_color=("#1f538d", "#42a2d6"),
                    corner_radius=15
                )
                drop_zone_indicator.place(x=target_x, y=target_y)
                
                pulse_label = ctk.CTkLabel(
                    drop_zone_indicator, 
                    text="Drop Here",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=("#1f538d", "#42a2d6")
                )
                pulse_label.place(relx=0.5, rely=0.5, anchor="center")

        def on_drag_release(event, frame=tab_frame):
            nonlocal is_dragging, drag_shadow, drop_zone_indicator, original_positions, current_animation
            
            if not is_dragging:
                return
                
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
            
            for child in tabs_frame.winfo_children():
                if hasattr(child, 'page_num'):
                    child.configure(
                        fg_color=("gray60", "gray30"), 
                        border_width=0,
                        corner_radius=6
                    )
            
            new_col = max(0, min(columns - 1, int(final_x / (actual_tab_width + tab_spacing))))
            new_row = max(0, min(rows - 1, int(final_y / (actual_tab_height + tab_spacing))))
            target_pos = new_row * columns + new_col
            
            if 0 <= target_pos < num_pages:
                current_page = frame.page_num
                target_frame = None
                for child in tabs_frame.winfo_children():
                    if hasattr(child, 'page_num') and child.page_num == target_pos:
                        target_frame = child
                        break
                
                if target_frame and target_frame != frame:
                    animate_swap(frame, target_frame, current_page, target_pos)
                else:
                    animate_return_to_original(frame)
            else:
                animate_return_to_original(frame)

        def animate_swap(frame1, frame2, pos1, pos2):
            nonlocal current_animation, current_page_order
            
            if current_animation:
                split_win.after_cancel(current_animation)
                current_animation = None
            
            # Swap the pages in our tracking array
            current_page_order[pos1], current_page_order[pos2] = current_page_order[pos2], current_page_order[pos1]
            
            grid1 = frame1.grid_info()
            grid2 = frame2.grid_info()
            
            target1_x = grid2['column'] * (actual_tab_width + tab_spacing) + tab_spacing
            target1_y = grid2['row'] * (actual_tab_height + tab_spacing) + tab_spacing
            target2_x = grid1['column'] * (actual_tab_width + tab_spacing) + tab_spacing
            target2_y = grid1['row'] * (actual_tab_height + tab_spacing) + tab_spacing
            
            start1_x, start1_y = frame1.winfo_x(), frame1.winfo_y()
            start2_x, start2_y = frame2.winfo_x(), frame2.winfo_y()
            
            frame1.grid_forget()
            frame2.grid_forget()
            frame1.place(x=start1_x, y=start1_y)
            frame2.place(x=start2_x, y=start2_y)
            
            animation_duration = 200
            animation_steps = 8
            step_duration = animation_duration // animation_steps
            current_step = 0
            
            def animate_step():
                nonlocal current_step, current_animation
                
                if not (frame1.winfo_exists() and frame2.winfo_exists()):
                    current_animation = None
                    return
                
                if current_step <= animation_steps:
                    progress = current_step / animation_steps
                    ease_progress = 1 - (1 - progress) ** 2
                    
                    frame1_x = start1_x + (target1_x - start1_x) * ease_progress
                    frame1_y = start1_y + (target1_y - start1_y) * ease_progress
                    frame2_x = start2_x + (target2_x - start2_x) * ease_progress
                    frame2_y = start2_y + (target2_y - start2_y) * ease_progress
                    
                    frame1.place(x=int(frame1_x), y=int(frame1_y))
                    frame2.place(x=int(frame2_x), y=int(frame2_y))
                    
                    current_step += 1
                    current_animation = split_win.after(step_duration, animate_step)
                else:
                    current_animation = None
                    frame1.place_forget()
                    frame2.place_forget()
                    
                    frame1.grid(row=grid2['row'], column=grid2['column'], 
                            padx=tab_spacing, pady=tab_spacing, sticky="nsew")
                    frame2.grid(row=grid1['row'], column=grid1['column'], 
                            padx=tab_spacing, pady=tab_spacing, sticky="nsew")
                    
                    # Update the frame positions but keep original page_num for reference
                    frame1.page_num = pos2
                    frame2.page_num = pos1
                    
                    # Update labels to show new logical page numbers
                    frame1.winfo_children()[1].configure(text=f"Page {pos2 + 1}")
                    frame2.winfo_children()[1].configure(text=f"Page {pos1 + 1}")
                    
                    frame1.configure(fg_color=("#4a9eff", "#4a9eff"))
                    frame2.configure(fg_color=("#4a9eff", "#4a9eff"))
                    split_win.after(100, lambda: (
                        frame1.configure(fg_color=("gray60", "gray30")) if frame1.winfo_exists() else None,
                        frame2.configure(fg_color=("gray60", "gray30")) if frame2.winfo_exists() else None
                    ))
            
            animate_step()

        def animate_return_to_original(frame):
            nonlocal current_animation
            
            if current_animation:
                split_win.after_cancel(current_animation)
                current_animation = None
            
            if frame in original_positions and frame.winfo_exists():
                orig_pos = original_positions[frame]
                target_x = orig_pos['column'] * (actual_tab_width + tab_spacing) + tab_spacing
                target_y = orig_pos['row'] * (actual_tab_height + tab_spacing) + tab_spacing
                
                start_x, start_y = frame.winfo_x(), frame.winfo_y()
                frame.grid_forget()
                frame.place(x=start_x, y=start_y)
                
                animation_duration = 150
                animation_steps = 6
                step_duration = animation_duration // animation_steps
                current_step = 0
                
                def animate_step():
                    nonlocal current_step, current_animation
                    
                    if not frame.winfo_exists():
                        current_animation = None
                        return
                    
                    if current_step <= animation_steps:
                        progress = current_step / animation_steps
                        ease_progress = 1 - (1 - progress) ** 2
                        
                        x = start_x + (target_x - start_x) * ease_progress
                        y = start_y + (target_y - start_y) * ease_progress
                        
                        frame.place(x=int(x), y=int(y))
                        
                        current_step += 1
                        current_animation = split_win.after(step_duration, animate_step)
                    else:
                        current_animation = None
                        frame.place_forget()
                        frame.grid(row=orig_pos['row'], column=orig_pos['column'], 
                                  padx=tab_spacing, pady=tab_spacing, sticky="nsew")
                
                animate_step()

        tab_frame.bind("<Button-1>", on_drag_start)
        tab_frame.bind("<B1-Motion>", on_drag_motion)
        tab_frame.bind("<ButtonRelease-1>", on_drag_release)
        
        def make_double_click_handler(page_idx):
            def on_double_click(event):
                if not is_dragging and not current_animation:
                    show_page_detail(page_idx)
            return on_double_click

        double_click_handler = make_double_click_handler(page_num)
        tab_frame.bind("<Double-Button-1>", double_click_handler)
        preview_label.bind("<Double-Button-1>", double_click_handler)
        page_label.bind("<Double-Button-1>", double_click_handler)

    for col in range(columns):
        tabs_frame.grid_columnconfigure(col, weight=1)
    for row in range(rows):
        tabs_frame.grid_rowconfigure(row, weight=1)

    def on_close():
        nonlocal current_animation
        if current_animation:
            split_win.after_cancel(current_animation)
        pdf_document.close()
        split_win.destroy()
        parent.deiconify()

    split_win.protocol("WM_DELETE_WINDOW", on_close)