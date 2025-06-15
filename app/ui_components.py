import tkinter as tk

class TextBlockFrame(tk.Frame):
    def __init__(self, master, block_data: dict, delete_callback, update_text_callback, toggle_title_callback, expansion_toggle_callback, collapsed_ids_set: set):
        super().__init__(master, borderwidth=1, relief=tk.SOLID, padx=5, pady=5)
        self.master = master # Keep a reference to the master for later use if needed
        self.block_data = block_data
        self.delete_callback = delete_callback
        self.update_text_callback = update_text_callback
        self.toggle_title_callback = toggle_title_callback
        self.expansion_toggle_callback = expansion_toggle_callback
        self.collapsed_ids_set = collapsed_ids_set # Store for checking collapse state

        self.block_id = block_data['id']

        self._create_widgets()

    def _create_widgets(self):
        left_controls_frame = tk.Frame(self)
        left_controls_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))

        if self.block_data.get('is_title', False):
            # Determine initial button text based on collapsed state
            button_text = "[+]" if self.block_id in self.collapsed_ids_set else "[-]"
            self.expand_button = tk.Button(left_controls_frame, text=button_text, command=self._handle_expansion_toggle, width=3)
            self.expand_button.pack(side=tk.TOP, pady=(0,2))

        lbl_display_number = tk.Label(left_controls_frame, text=self.block_data.get('display_number', 'N/A'), width=10, anchor='w')
        lbl_display_number.pack(side=tk.TOP)

        # Title Toggle Checkbutton
        self.is_title_var = tk.BooleanVar(value=self.block_data.get('is_title', False))
        title_toggle_check = tk.Checkbutton(
            left_controls_frame,
            text="Title",
            variable=self.is_title_var,
            command=self._handle_toggle_title
        )
        title_toggle_check.pack(side=tk.BOTTOM)


        # Main content text widget
        self.text_widget = tk.Text(self, height=3, wrap=tk.WORD, borderwidth=1, relief=tk.SUNKEN)
        self.text_widget.insert(tk.END, self.block_data.get('text', ''))
        self.text_widget.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        # Bind events
        self.text_widget.bind("<FocusOut>", self._on_text_focus_out)
        # Consider adding a small delay or specific event if FocusOut fires too often
        # self.text_widget.bind("<KeyRelease>", self._on_text_changed_live) # Example for live updates

        # Delete button
        btn_delete = tk.Button(self, text="Del", command=self._handle_delete, background="salmon", foreground="white", width=3)
        btn_delete.pack(side=tk.RIGHT, fill=tk.Y)

    def _handle_delete(self):
        if self.delete_callback:
            self.delete_callback(self.block_id)

    def _on_text_focus_out(self, event=None): # event=None if called manually
        current_text = self.text_widget.get("1.0", tk.END).strip()
        if current_text != self.block_data.get('text', ''):
            self.block_data['text'] = current_text # Update local cache
            if self.update_text_callback:
                self.update_text_callback(self.block_id, current_text)

    def _handle_toggle_title(self):
        new_is_title_status = self.is_title_var.get()
        # Update local data immediately to prevent race conditions if UI redraws fast
        self.block_data['is_title'] = new_is_title_status
        if self.toggle_title_callback:
            self.toggle_title_callback(self.block_id, new_is_title_status)

    def _handle_expansion_toggle(self):
        if self.expansion_toggle_callback:
            self.expansion_toggle_callback(self.block_id)
            # The button text will be updated when _redraw_text_blocks_ui recreates this frame.

    def update_display(self, new_block_data, new_collapsed_ids_set):
        """
        Updates the frame's displayed content if external changes occurred (e.g., re-numbering).
        Also updates the knowledge of collapsed_ids for the expand button.
        """
        self.block_data = new_block_data
        self.collapsed_ids_set = new_collapsed_ids_set # Update internal state

        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert(tk.END, self.block_data.get('text', ''))

        # Update display number label
        # Assumes left_controls_frame is the first child, and label is its second child (if expand_button exists) or first.
        # This is getting fragile; direct reference would be better if possible.
        left_controls_children = self.winfo_children()[0].winfo_children()

        display_label_widget = None
        if self.block_data.get('is_title'):
            if len(left_controls_children) > 1 and isinstance(left_controls_children[1], tk.Label):
                 display_label_widget = left_controls_children[1]
            # Update expand button text
            if hasattr(self, 'expand_button'):
                button_text = "[+]" if self.block_id in self.collapsed_ids_set else "[-]"
                self.expand_button.config(text=button_text)
        else: # Paragraph or other non-title
            if len(left_controls_children) > 0 and isinstance(left_controls_children[0], tk.Label):
                 display_label_widget = left_controls_children[0]

        if display_label_widget:
            display_label_widget.config(text=self.block_data.get('display_number', 'N/A'))

        self.is_title_var.set(self.block_data.get('is_title', False))


    def get_current_text(self):
        """Returns the current text from the text widget."""
        return self.text_widget.get("1.0", tk.END).strip()

    def destroy(self):
        # Ensure FocusOut is triggered if the widget has focus before destroying
        if self.focus_get() == self.text_widget:
            self._on_text_focus_out()
        super().destroy()
