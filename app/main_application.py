import tkinter as tk
from tkinter import ttk # Themed Tkinter widgets
from tkinter import messagebox, filedialog # For showinfo and file dialogs
from .app_logic import AppLogic
from .utils import generate_unique_id
from .ui_components import TextBlockFrame

class TextBlockEditorApp(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Text Block Editor - Python")

        # Configure padding for the main frame
        self.configure(padx=10, pady=10)

        self.app_logic = AppLogic()
        self._create_widgets()

        # Pack the main application frame to fill the root window
        self.pack(fill=tk.BOTH, expand=True)

    def _create_widgets(self):
        # Main application header
        header_label = tk.Label(self, text="Text Block Editor", font=("Arial", 16, "bold"))
        header_label.pack(pady=(0, 10)) # Add some padding below the header

        # Global Action Buttons Frame
        global_actions_frame = tk.Frame(self)
        global_actions_frame.pack(fill=tk.X, pady=(0, 10))

        btn_open = tk.Button(global_actions_frame, text="Open File", command=self._handle_open_file)
        btn_open.pack(side=tk.LEFT, padx=(0, 5))

        btn_save = tk.Button(global_actions_frame, text="Save File", command=self._handle_save_file)
        btn_save.pack(side=tk.LEFT, padx=(0, 5))

        btn_expand_all = tk.Button(global_actions_frame, text="Expand All")
        btn_expand_all.pack(side=tk.LEFT, padx=(0, 5))

        btn_collapse_all = tk.Button(global_actions_frame, text="Collapse All", command=self._handle_collapse_all)
        btn_collapse_all.pack(side=tk.LEFT, padx=(0, 5))

        btn_expand_all = tk.Button(global_actions_frame, text="Expand All", command=self._handle_expand_all)
        btn_expand_all.pack(side=tk.LEFT, padx=(0, 5))

        btn_clear_all_document = tk.Button(global_actions_frame, text="Clear All Document", command=self._handle_clear_all_document)
        btn_clear_all_document.pack(side=tk.LEFT, padx=(0, 5))


        # Main layout: PanedWindow for resizable left and right panels
        main_paned_window = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        main_paned_window.pack(fill=tk.BOTH, expand=True)

        # Left Panel (Editor Area)
        left_panel_frame = tk.Frame(main_paned_window, bd=1, relief=tk.SUNKEN)
        main_paned_window.add(left_panel_frame, stretch="always", width=self.master.winfo_screenwidth() // 2) # Give it an initial width

        # Left panel will be divided vertically
        # Top: Original Text Area + Controls
        original_text_frame = tk.Frame(left_panel_frame)
        original_text_frame.pack(fill=tk.X, pady=(5,5))

        lbl_original_text = tk.Label(original_text_frame, text="Original Text:")
        lbl_original_text.pack(side=tk.LEFT, padx=(0,5))

        self.original_text_area = tk.Text(original_text_frame, height=10)
        self.original_text_area.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))

        original_text_controls_frame = tk.Frame(original_text_frame)
        original_text_controls_frame.pack(side=tk.LEFT, fill=tk.Y)

        btn_create_paragraphs = tk.Button(original_text_controls_frame, text="Create Paragraphs", command=self._handle_create_paragraphs)
        btn_create_paragraphs.pack(fill=tk.X, pady=(0,2))

        btn_paste_original = tk.Button(original_text_controls_frame, text="Paste")
        btn_paste_original.pack(fill=tk.X, pady=(0,2))

        btn_clear_original = tk.Button(original_text_controls_frame, text="Clear")
        btn_clear_original.pack(fill=tk.X)

        # Middle: Editable Blocks Area (Scrollable)
        editable_blocks_container = tk.Frame(left_panel_frame)
        editable_blocks_container.pack(fill=tk.BOTH, expand=True, pady=(5,5))

        canvas_frame = tk.Frame(editable_blocks_container)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.blocks_canvas = tk.Canvas(canvas_frame, borderwidth=0, background="#ffffff")
        self.scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=self.blocks_canvas.yview)
        self.scrollable_blocks_frame = tk.Frame(self.blocks_canvas, background="#ffffff")

        self.scrollable_blocks_frame.bind(
            "<Configure>",
            lambda e: self.blocks_canvas.configure(
                scrollregion=self.blocks_canvas.bbox("all")
            )
        )

        self.blocks_canvas.create_window((0, 0), window=self.scrollable_blocks_frame, anchor="nw")
        self.blocks_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.blocks_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Mouse wheel scrolling for the canvas
        self.blocks_canvas.bind_all("<MouseWheel>", self._on_mousewheel) # For Windows and MacOS
        self.blocks_canvas.bind_all("<Button-4>", self._on_mousewheel) # For Linux (scroll up)
        self.blocks_canvas.bind_all("<Button-5>", self._on_mousewheel) # For Linux (scroll down)


        btn_add_empty_paragraph = tk.Button(left_panel_frame, text="Add Empty Paragraph Below", command=self._handle_add_empty_paragraph)
        btn_add_empty_paragraph.pack(pady=(5,5))


        # Bottom: Stats Panel
        self.stats_panel_frame = tk.Frame(left_panel_frame, height=120, bd=1, relief=tk.SUNKEN)
        self.stats_panel_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(5,0), ipady=5)

        stats_title_label = tk.Label(self.stats_panel_frame, text="--- Statistics ---", font=("Arial", 10, "bold"))
        stats_title_label.pack(pady=(0,5))

        self.stats_total_blocks_label = tk.Label(self.stats_panel_frame, text="Total Blocks: 0")
        self.stats_total_blocks_label.pack(anchor=tk.W, padx=10)

        self.stats_visible_blocks_label = tk.Label(self.stats_panel_frame, text="Visible Blocks: 0")
        self.stats_visible_blocks_label.pack(anchor=tk.W, padx=10)

        self.stats_titles_label = tk.Label(self.stats_panel_frame, text="Titles (visible): 0")
        self.stats_titles_label.pack(anchor=tk.W, padx=10)

        self.stats_paragraphs_label = tk.Label(self.stats_panel_frame, text="Paragraphs (visible): 0")
        self.stats_paragraphs_label.pack(anchor=tk.W, padx=10)

        self.stats_words_label = tk.Label(self.stats_panel_frame, text="Words (visible): 0")
        self.stats_words_label.pack(anchor=tk.W, padx=10)

        self._update_stats_panel_ui() # Initialize stats panel on creation


        # Right Panel (Outline Area)
        right_panel_frame = tk.Frame(main_paned_window, bd=1, relief=tk.SUNKEN)
        main_paned_window.add(right_panel_frame, stretch="always", width=self.master.winfo_screenwidth() // 4) # Give it an initial width

        lbl_outline_panel = tk.Label(right_panel_frame, text="Outline Panel", font=("Arial", 12, "bold"))
        lbl_outline_panel.pack(pady=5, fill=tk.X)

        self.outline_listbox = tk.Listbox(right_panel_frame, selectmode=tk.SINGLE)
        self.outline_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0,5))
        self.outline_listbox.bind("<<ListboxSelect>>", self._handle_outline_select)
        self.outline_items_map = {} # To map listbox index to block_id


    def _handle_create_paragraphs(self):
        """
        Handles the "Create Paragraphs" button click.
        Processes the text from the original_text_area.
        """
        text_content = self.original_text_area.get("1.0", tk.END).strip()
        if not text_content:
            messagebox.showwarning("Empty Input", "Original text area is empty. Please paste or type some text.")
            return

        self.app_logic.process_original_text(text_content)

        # For now, print to console and show a message box
        # Later, this will trigger a UI update for the editable blocks and outline
        print("--- Processed Text Blocks ---")
        for block in self.app_logic.text_blocks:
            print(block)
        print("-----------------------------")

        messagebox.showinfo("Success", f"Text processed! {len(self.app_logic.text_blocks)} blocks created. Check console for details.")


        messagebox.showinfo("Success", f"Text processed! {len(self.app_logic.text_blocks)} blocks created and displayed.")
        self._redraw_text_blocks_ui()
        self._update_outline_panel_ui() # Update outline as well

    def _redraw_text_blocks_ui(self):
        """
        Clears and redraws all text block frames in the scrollable area.
        """
        # Persist text from any focused widget before redrawing
        focused_widget = self.focus_get()
        if isinstance(focused_widget, tk.Text) and isinstance(focused_widget.master, TextBlockFrame):
            focused_widget.master._on_text_focus_out() # Call the update method

        for widget in self.scrollable_blocks_frame.winfo_children():
            widget.destroy()

        for block_data in self.app_logic.text_blocks:
            if block_data.get('visible', True): # Check visibility
                frame = TextBlockFrame(
                    self.scrollable_blocks_frame,
                    block_data,
                    delete_callback=self._handle_delete_block,
                    update_text_callback=self._handle_update_block_text,
                    toggle_title_callback=self._handle_toggle_title_status,
                    expansion_toggle_callback=self._handle_expansion_toggle, # Pass expansion callback
                    collapsed_ids_set=self.app_logic.collapsed_title_ids # Pass set of collapsed IDs
                )
                frame.pack(fill=tk.X, pady=2, padx=2)

        # Update canvas scroll region after adding new frames
        self.scrollable_blocks_frame.update_idletasks() # Ensure layout is updated
        self.blocks_canvas.configure(scrollregion=self.blocks_canvas.bbox("all"))
        self._update_outline_panel_ui() # Update outline after redrawing blocks
        self._update_stats_panel_ui() # Update stats panel


    def _handle_add_empty_paragraph(self):
        """
        Handles adding a new empty paragraph.
        """
        self.app_logic.add_empty_paragraph() # Adds to the end by default
        self._redraw_text_blocks_ui()
        self._update_outline_panel_ui()
        # Scroll to the bottom to show the new paragraph
        self.blocks_canvas.update_idletasks()
        self.blocks_canvas.yview_moveto(1.0)


    def _handle_delete_block(self, block_id: str):
        """
        Handles deletion of a text block.
        """
        self.app_logic.delete_block(block_id)
        self._redraw_text_blocks_ui()
        self._update_outline_panel_ui()

    def _handle_update_block_text(self, block_id: str, new_text: str):
        """
        Handles updating the text of a block.
        """
        self.app_logic.update_block_text(block_id, new_text)
        # print(f"Block {block_id} updated to: {new_text}") # Debugging
        self._update_outline_panel_ui()
        self._update_stats_panel_ui() # Explicitly update stats after text change

    def _handle_toggle_title_status(self, block_id: str, is_title: bool):
        """
        Handles toggling the title status of a block.
        """
        self.app_logic.toggle_block_title_status(block_id, is_title)
        self._redraw_text_blocks_ui() # Redraw to reflect numbering and style changes
        # _redraw_text_blocks_ui already calls _update_outline_panel_ui

    def _handle_expansion_toggle(self, title_id: str):
        """
        Handles toggling the expansion state of a title block.
        """
        self.app_logic.toggle_title_expansion(title_id)
        self._redraw_text_blocks_ui()
        # _redraw_text_blocks_ui already calls _update_outline_panel_ui

    def _handle_expand_all(self):
        """
        Handles expanding all title blocks.
        """
        self.app_logic.expand_all()
        self._redraw_text_blocks_ui()

    def _handle_collapse_all(self):
        """
        Handles collapsing all title blocks.
        """
        self.app_logic.collapse_all()
        self._redraw_text_blocks_ui()

    def _update_outline_panel_ui(self):
        """
        Updates the outline panel Listbox based on current text blocks.
        """
        # Persist text from any focused TextBlockFrame's Text widget
        # This is important if a title's text is changed and outline is updated immediately
        focused_widget = self.focus_get()
        if isinstance(focused_widget, tk.Text) and isinstance(focused_widget.master, TextBlockFrame):
             if focused_widget.master.block_data.get('is_title'):
                focused_widget.master._on_text_focus_out()


        self.outline_listbox.delete(0, tk.END)
        self.outline_items_map.clear() # Clear the old mapping

        for list_idx, block_data in enumerate(self.app_logic.text_blocks):
            if block_data.get('is_title'):
                is_collapsed = block_data['id'] in self.app_logic.collapsed_title_ids
                prefix = "[+] " if is_collapsed else "[-] "

                display_text = f"{prefix}{block_data.get('display_number', 'T')}: {block_data.get('text', '')[:30]}"
                if len(block_data.get('text', '')) > 30:
                    display_text += "..."

                self.outline_listbox.insert(tk.END, display_text)
                self.outline_items_map[self.outline_listbox.size() - 1] = block_data['id']

    def _handle_outline_select(self, event):
        """
        Handles selection changes in the outline listbox.
        Scrolls to the selected block in the editor.
        If a collapsed title is clicked, it expands it.
        """
        selected_indices = self.outline_listbox.curselection()
        if not selected_indices:
            return

        listbox_idx = selected_indices[0]
        block_id = self.outline_items_map.get(listbox_idx)

        if not block_id:
            return

        # If the selected title was collapsed, expand it first
        if block_id in self.app_logic.collapsed_title_ids:
            self.app_logic.toggle_title_expansion(block_id)
            self._redraw_text_blocks_ui() # This will also update outline and listbox selection
            # Try to re-select the item in the listbox after redraw
            # This is a bit complex as IDs might not map to same index if some items become visible/invisible
            # For now, the redraw might clear selection, user might need to click again if it was collapsed.
            # A better way would be to find the new index of block_id and re-select.

            # Find new listbox index for block_id
            new_listbox_idx = -1
            for k, v in self.outline_items_map.items():
                if v == block_id:
                    new_listbox_idx = k
                    break
            if new_listbox_idx != -1:
                self.outline_listbox.selection_set(new_listbox_idx)
                self.outline_listbox.activate(new_listbox_idx)
                self.outline_listbox.see(new_listbox_idx)


        # Scroll to the block in the editor area
        target_frame_widget = None
        for child_widget in self.scrollable_blocks_frame.winfo_children():
            if isinstance(child_widget, TextBlockFrame) and child_widget.block_id == block_id:
                target_frame_widget = child_widget
                break

        if target_frame_widget:
            self.blocks_canvas.update_idletasks() # Ensure geometry is up-to-date

            frame_y = target_frame_widget.winfo_y()
            frame_height = target_frame_widget.winfo_height()
            canvas_height = self.blocks_canvas.winfo_height()
            scrollable_content_height = self.scrollable_blocks_frame.winfo_height()

            # Calculate position to scroll to (fraction from 0.0 to 1.0)
            # Try to position it somewhat in the middle if possible
            scroll_pos = (frame_y - canvas_height / 3) / scrollable_content_height
            scroll_pos = max(0.0, min(scroll_pos, 1.0)) # Clamp between 0 and 1

            if scrollable_content_height > canvas_height: # Only scroll if content is larger than canvas
                 self.blocks_canvas.yview_moveto(scroll_pos)

            # Brief highlight (optional)
            original_bg = target_frame_widget.cget("background")
            target_frame_widget.configure(background="lightyellow")
            self.after(500, lambda: target_frame_widget.configure(background=original_bg if tk.Tcl().eval(f"winfo exists {target_frame_widget}") else None) )


    def _on_mousewheel(self, event):
        """Handles mouse wheel scrolling for the canvas."""
        # Determine the direction and amount of scrolling
        if event.num == 4:  # Linux scroll up
            delta = -1
        elif event.num == 5:  # Linux scroll down
            delta = 1
        elif event.delta > 0:  # Windows and macOS scroll up
            delta = -1
        elif event.delta < 0:  # Windows and macOS scroll down
            delta = 1
        else:
            delta = 0

        if delta != 0 :
             # Check if the canvas can be scrolled
            current_y_top, current_y_bottom = self.blocks_canvas.yview()
            if (delta < 0 and current_y_top > 0.0) or \
               (delta > 0 and current_y_bottom < 1.0):
                self.blocks_canvas.yview_scroll(delta, "units")

    def _update_stats_panel_ui(self):
        """
        Updates the statistics panel labels with the latest data from app_logic.
        """
        stats_data = self.app_logic.calculate_stats()

        self.stats_total_blocks_label.config(text=f"Total Blocks: {stats_data.get('total_blocks', 0)}")
        self.stats_visible_blocks_label.config(text=f"Visible Blocks: {stats_data.get('visible_blocks', 0)}")
        self.stats_titles_label.config(text=f"Titles (visible): {stats_data.get('titles', 0)}")
        self.stats_paragraphs_label.config(text=f"Paragraphs (visible): {stats_data.get('paragraphs', 0)}")
        self.stats_words_label.config(text=f"Words (visible): {stats_data.get('words', 0)}")

    def _handle_open_file(self):
        """
        Handles opening a text file and loading its content into the original text area.
        """
        filepath = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("Markdown Files", "*.md"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                file_content = f.read()

            self.original_text_area.delete("1.0", tk.END)
            self.original_text_area.insert("1.0", file_content)

            # Automatically process the opened file
            self._handle_create_paragraphs()

            messagebox.showinfo("File Opened", f"File '{filepath}' loaded and processed.")

        except Exception as e:
            messagebox.showerror("Error Opening File", f"Failed to read or process file: {e}")

    def _handle_save_file(self):
        """
        Handles saving the processed text blocks to a file.
        Saves only visible and non-empty blocks.
        """
        content_to_save = self.app_logic.get_text_for_saving()

        if not content_to_save.strip():
            messagebox.showwarning("Nothing to Save", "There is no visible text content to save.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("Markdown Files", "*.md"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content_to_save)
            messagebox.showinfo("File Saved", f"Content saved to '{filepath}'.")
        except Exception as e:
            messagebox.showerror("Error Saving File", f"Failed to save file: {e}")

    def _handle_clear_all_document(self):
        """
        Clears all content from the application after user confirmation.
        """
        if not messagebox.askyesno("Confirm Clear All",
                                     "Are you sure you want to clear all content?\n"
                                     "- Original text area will be cleared.\n"
                                     "- All processed text blocks will be removed.\n\n"
                                     "This action cannot be undone."):
            return

        self.app_logic.clear_all_data()
        self.original_text_area.delete("1.0", tk.END)

        # Redraw will clear block frames, update outline, and update stats
        self._redraw_text_blocks_ui()

        messagebox.showinfo("Cleared", "All content has been cleared.")


if __name__ == '__main__':
    # This is for testing the App class directly if needed
    # but the main execution will be from main.py
    root = tk.Tk()
    app = TextBlockEditorApp(master=root)
    root.mainloop()
