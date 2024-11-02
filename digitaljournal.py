import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

# File to store the journal entries
JOURNAL_FILE = 'journal_entries.json'


def load_entries():
    """Load journal entries from the JSON file."""
    if os.path.exists(JOURNAL_FILE):
        with open(JOURNAL_FILE, 'r') as file:
            entries = json.load(file)
            return entries
    return []


def save_entries(entries):
    """Save journal entries to the JSON file."""
    with open(JOURNAL_FILE, 'w') as file:
        json.dump(entries, file, indent=4)


class DigitalJournalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Digital Journal")
        self.root.configure(bg="#f0f0f0")

        # Title Frame
        title_frame = tk.Frame(self.root, bg="#f0f0f0")
        title_frame.pack(pady=10)
        title_label = tk.Label(title_frame, text="My Digital Journal", font=("Helvetica", 24, "bold"), bg="#f0f0f0")
        title_label.pack()

        # Search Frame
        search_frame = tk.Frame(self.root, bg="#f0f0f0")
        search_frame.pack(pady=10)
        self.search_entry = tk.Entry(search_frame, width=30, font=("Helvetica", 14))
        self.search_entry.pack(side=tk.LEFT, padx=10)

        # Search and Reset buttons
        tk.Button(search_frame, text="Search", command=self.search_entries, bg="#2196F3", fg="white",
                  font=("Helvetica", 12)).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(search_frame, text="Reset", command=self.reset_search, bg="#FFC107", font=("Helvetica", 12)).pack(
            side=tk.LEFT)

        # Frame for Add, Delete, and Edit buttons
        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(pady=10)

        # Add, Edit, and Delete buttons
        tk.Button(button_frame, text="Add Entry", command=self.add_entry, bg="#4CAF50", fg="white",
                  font=("Helvetica", 12)).grid(row=0, column=0, padx=10)
        tk.Button(button_frame, text="Edit Entry", command=self.edit_entry, bg="#FF9800", fg="white",
                  font=("Helvetica", 12)).grid(row=0, column=1, padx=10)
        tk.Button(button_frame, text="Delete Entry", command=self.delete_entry, bg="#f44336", fg="white",
                  font=("Helvetica", 12)).grid(row=0, column=2, padx=10)

        # Treeview for displaying journal entries with Date Modified
        self.entry_tree = ttk.Treeview(self.root, columns=("Title", "Date Created", "Date Modified"), show='headings',
                                       height=10)
        self.entry_tree.heading("Title", text="Title", command=lambda: self.sort_entries("title"))
        self.entry_tree.heading("Date Created", text="Date Created", command=lambda: self.sort_entries("date_created"))
        self.entry_tree.heading("Date Modified", text="Date Modified",
                                command=lambda: self.sort_entries("date_modified"))
        self.entry_tree.column("Title", anchor="w", width=200)
        self.entry_tree.column("Date Created", anchor="w", width=120)
        self.entry_tree.column("Date Modified", anchor="w", width=120)
        self.entry_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.entry_tree.bind("<ButtonRelease-1>", self.display_entry)

        # Scrolled text area to show selected journal entry
        self.entry_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=50, height=10, state=tk.DISABLED,
                                                    bg="#ffffff", font=("Helvetica", 12))
        self.entry_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.entry_text.pack_forget()  # Hide initially

        # Store the full list of entries for displaying
        self.entries = load_entries()
        self.search_results = []
        self.refresh_treeview()
        self.sort_order = {"title": True, "date_created": True, "date_modified": True}  # Track sort order

    def refresh_treeview(self):
        """Refresh the list of entries displayed in the treeview."""
        self.entry_tree.delete(*self.entry_tree.get_children())

        # Choose the entries to display based on search results or all entries
        entries_to_display = self.search_results if self.search_results else self.entries

        if not entries_to_display:
            self.entry_tree.insert("", "end", values=("No journal entries available.", "", ""))
            self.entry_text.pack_forget()
        else:
            for entry in entries_to_display:
                self.entry_tree.insert("", "end", values=(entry['title'], entry['timestamp'], entry['date_modified']))

    def add_entry(self):
        """Add a new journal entry via a custom dialog box."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Entry")

        tk.Label(dialog, text="Enter Title:", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=10)
        title_entry = tk.Entry(dialog, width=40, font=("Helvetica", 12))
        title_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(dialog, text="Enter Content:", font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=10)
        content_text = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, width=40, height=10, font=("Helvetica", 12))
        content_text.grid(row=1, column=1, padx=10, pady=10)

        def save_and_close():
            title = title_entry.get().strip()
            content = content_text.get(1.0, tk.END).strip()
            if not title:
                messagebox.showerror("Error", "Title cannot be empty.")
                return
            entry = {
                'title': title,
                'content': content,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'date_modified': datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Add date modified
            }
            self.entries.append(entry)  # Append to the local entries
            save_entries(self.entries)

            # Refresh the treeview to show the new entry
            self.refresh_treeview()

            dialog.destroy()  # Close the dialog and return to main interface

        tk.Button(dialog, text="Save Entry", command=save_and_close, bg="#4CAF50", fg="white",
                  font=("Helvetica", 12)).grid(row=2, column=1, padx=10, pady=10)
        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)

    def edit_entry(self):
        """Edit the selected journal entry and update the date modified field."""
        selected_item = self.entry_tree.selection()
        if not selected_item:
            messagebox.showwarning("Select Entry", "Please select an entry to edit.")
            return

        entry_index = self.entry_tree.index(selected_item)
        entry = self.search_results[entry_index] if self.search_results else self.entries[entry_index]

        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Entry")

        tk.Label(dialog, text="Edit Title:", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=10)
        title_entry = tk.Entry(dialog, width=40, font=("Helvetica", 12))
        title_entry.insert(0, entry['title'])
        title_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(dialog, text="Edit Content:", font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=10)
        content_text = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, width=40, height=10, font=("Helvetica", 12))
        content_text.insert(tk.END, entry['content'])
        content_text.grid(row=1, column=1, padx=10, pady=10)

        def save_changes():
            new_title = title_entry.get().strip()
            new_content = content_text.get(1.0, tk.END).strip()
            if not new_title:
                messagebox.showerror("Error", "Title cannot be empty.")
                return
            entry['title'] = new_title
            entry['content'] = new_content
            entry['date_modified'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            save_entries(self.entries)
            messagebox.showinfo("Entry Updated", "Your entry has been updated successfully.")
            self.refresh_treeview()
            dialog.destroy()

        tk.Button(dialog, text="Save Changes", command=save_changes, bg="#FF9800", fg="white",
                  font=("Helvetica", 12)).grid(row=2, column=1, padx=10, pady=10)
        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)

    def display_entry(self, event):
        """Display the selected entry's content in the text area."""
        selected_item = self.entry_tree.selection()
        if not selected_item:
            return

        entry_index = self.entry_tree.index(selected_item)
        entry = self.search_results[entry_index] if self.search_results else self.entries[entry_index]

        self.entry_text.config(state=tk.NORMAL)
        self.entry_text.delete(1.0, tk.END)
        self.entry_text.insert(tk.END, entry['content'])
        self.entry_text.config(state=tk.DISABLED)
        self.entry_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def delete_entry(self):
        """Delete the selected entry from the list."""
        selected_item = self.entry_tree.selection()
        if not selected_item:
            messagebox.showwarning("Select Entry", "Please select an entry to delete.")
            return

        entry_index = self.entry_tree.index(selected_item)
        entry = self.search_results[entry_index] if self.search_results else self.entries[entry_index]

        confirm = messagebox.askyesno("Delete Entry", "Are you sure you want to delete this entry?")
        if confirm:
            self.entries.remove(entry)
            save_entries(self.entries)
            messagebox.showinfo("Entry Deleted", "The entry has been deleted successfully.")
            self.refresh_treeview()

    def search_entries(self):
        """Search entries by title and update the treeview."""
        search_text = self.search_entry.get().strip().lower()
        if search_text:
            self.search_results = [entry for entry in self.entries if search_text in entry['title'].lower()]
        else:
            self.search_results = []  # Reset if the search text is empty

        self.refresh_treeview()

    def reset_search(self):
        """Reset search and display all entries."""
        self.search_entry.delete(0, tk.END)
        self.search_results = []
        self.refresh_treeview()

    def sort_entries(self, key):
        """Sort entries based on the selected key and refresh the treeview."""
        self.sort_order[key] = not self.sort_order[key]  # Toggle sort order
        reverse = not self.sort_order[key]

        if key == "title":
            self.entries.sort(key=lambda entry: entry['title'].lower(), reverse=reverse)
        elif key == "date_created":
            self.entries.sort(key=lambda entry: entry['timestamp'], reverse=reverse)
        elif key == "date_modified":
            self.entries.sort(key=lambda entry: entry['date_modified'], reverse=reverse)

        self.refresh_treeview()


if __name__ == "__main__":
    root = tk.Tk()
    app = DigitalJournalApp(root)
    root.mainloop()
