import tkinter as tk
from tkinter import ttk


class AutocompleteEntry(ttk.Entry):
    def __init__(self, master=None, suggestions=None, **kwargs):
        super().__init__(master, **kwargs)
        self.suggestions = suggestions or []
        self.var = tk.StringVar()
        self.configure(textvariable=self.var)

        self.var.trace_add("write", self.on_var_change)
        self.ignore_var_change = False

        self._listbox = None
        self._listbox_toplevel = None

        self.bind("<Up>", self._on_arrow_key)
        self.bind("<Down>", self._on_arrow_key)
        self.bind("<Return>", self._on_enter_key)
        self.bind("<Escape>", lambda e: self._hide_listbox())
        self.bind("<FocusOut>", lambda e: self._hide_listbox())

    def on_var_change(self, *args):
        if self.ignore_var_change:
            return

        typed_text = self.var.get().strip()
        if not typed_text:
            self._hide_listbox()
            return

        matches = [
            s for s in self.suggestions if s.lower().startswith(typed_text.lower())
        ]

        if matches:
            self._show_listbox(matches)
        else:
            self._hide_listbox()

    def set_text(self, text):
        self.ignore_var_change = True
        self.var.set(text)
        self.icursor(tk.END)
        self.ignore_var_change = False

    def clear(self):
        self.ignore_var_change = True
        self.var.set("")
        self.ignore_var_change = False

    def _show_listbox(self, matches):
        if not self._listbox_toplevel:

            self._listbox_toplevel = tk.Toplevel(self)
            self._listbox_toplevel.overrideredirect(True)
            self._listbox_toplevel.attributes("-topmost", True)

            self._listbox = tk.Listbox(
                self._listbox_toplevel, selectmode=tk.SINGLE, font=("Segoe UI", 10)
            )
            self._listbox.pack(expand=True, fill="both")
            self._listbox.bind("<ButtonRelease-1>", self._on_listbox_select)
            self._listbox.bind("<Return>", self._on_enter_key)

        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        width = self.winfo_width()
        self._listbox_toplevel.geometry(f"{width}x100+{x}+{y}")

        self._listbox.delete(0, tk.END)
        for match in matches:
            self._listbox.insert(tk.END, match)

        self._listbox.selection_set(0)

    def _hide_listbox(self):
        if self._listbox_toplevel:
            self._listbox_toplevel.destroy()
            self._listbox_toplevel = None
            self._listbox = None

    def _on_listbox_select(self, event):
        if self._listbox and self._listbox.curselection():
            selection = self._listbox.get(self._listbox.curselection())
            self.set_text(selection)
            self._hide_listbox()
            self.focus()

    def _on_enter_key(self, event):
        if self._listbox and self._listbox.curselection():
            self._on_listbox_select(event)
            return "break"

    def _on_arrow_key(self, event):
        if not self._listbox:
            return

        current_selection = self._listbox.curselection()
        if not current_selection:
            new_index = 0
        else:
            current_index = current_selection[0]
            if event.keysym == "Down":
                new_index = min(current_index + 1, self._listbox.size() - 1)
            else:
                new_index = max(current_index - 1, 0)

        self._listbox.selection_clear(0, tk.END)
        self._listbox.selection_set(new_index)
        self._listbox.activate(new_index)
        self._listbox.see(new_index)
        return "break"
