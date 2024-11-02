import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

# File to store the journal entries
JOURNAL_FILE = 'journal_entries.json'


def load_entries():
    """Load journal entries from the JSON file and ensure all have date_modified."""
    if os.path.exists(JOURNAL_FILE):
        with open(JOURNAL_FILE, 'r') as file:
            entries = json.load(file)
            # Ensure all entries have 'date_modified' field
            for entry in entries:
                if 'date_modified' not in entry:
                    entry['date_modified'] = entry['timestamp']
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

        # Treeview for displaying journal entries with sortable headers
        columns = ("Title", "Date Created", "Date Modified")
        self.entry_tree = ttk.Treeview(self.root, columns=columns, show='headings', height=10)
        for col in columns:
            self.entry_tree.heading(col, text=col, command=lambda _col=col: self.sort_by_column(_col, False))

        self.entry_tree.column("Title", anchor="w", width=200)
        self.entry_tree.column("Date Created", anchor="w", width=150)
        self.entry_tree.column("Date Modified", anchor="w", width=150)
        self.entry_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Bind single-click to display entry content
        self.entry_tree.bind("<ButtonRelease-1>", self.display_entry)

        # Scrolled text area to show selected journal entry
        self.entry_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=50, height=10, state=tk.DISABLED,
                                                    bg="#ffffff", font=("Helvetica", 12))
        self.entry_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.entry_text.pack_forget()  # Hide initially

        # Store the full list of entries for displaying
        self.entries = load_entries()
        self.search_results = []
        self.sort_orders = {col: False for col in columns}  # Track sort order for each column
        self.refresh_treeview()

    def refresh_treeview(self):
        """Refresh the list of entries displayed in the treeview."""
        self.entry_tree.delete(*self.entry_tree.get_children())
        if not self.entries:
            self.entry_tree.insert("", "end", values=("No journal entries available.", "", ""))
            self.entry_text.pack_forget()
        else:
            for entry in self.entries:
                self.entry_tree.insert("", "end", values=(entry['title'], entry['timestamp'], entry['date_modified']))

    def add_entry(self):
        """Add a new journal entry via a custom dialog box."""
        # Implementation here for adding an entry dialog and saving

    def edit_entry(self):
        """Edit the selected journal entry."""
        selected_item = self.entry_tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select an entry to edit.")
            return
        entry_index = self.entry_tree.index(selected_item[0])
        entry = self.search_results[entry_index] if self.search_results else self.entries[entry_index]

        # Implement editing logic here

    def search_entries(self):
        """Search entries based on partial match with the search term."""
        search_term = self.search_entry.get().strip().lower()
        self.search_results = [entry for entry in self.entries if search_term in entry['title'].lower()]

        # Update the display to show search results
        self.refresh_treeview_with_results(self.search_results)

    def reset_search(self):
        """Reset the search and show all entries."""
        self.search_entry.delete(0, tk.END)
        self.search_results = []
        self.refresh_treeview()

    def refresh_treeview_with_results(self, results):
        """Helper to refresh treeview with specific results."""
        self.entry_tree.delete(*self.entry_tree.get_children())
        if not results:
            self.entry_tree.insert("", "end", values=("No matching entries found.", "", ""))
            self.entry_text.pack_forget()
        else:
            for entry in results:
                self.entry_tree.insert("", "end", values=(entry['title'], entry['timestamp'], entry['date_modified']))

    def display_entry(self, event):
        """Display the content of the selected entry or hide the entry box if nothing is selected."""
        selected_item = self.entry_tree.selection()
        if not selected_item:
            self.entry_text.pack_forget()
            return

        entry_index = self.entry_tree.index(selected_item[0])
        entry = self.search_results[entry_index] if self.search_results else self.entries[entry_index]

        # Display the selected entry's details
        self.entry_text.config(state=tk.NORMAL)
        self.entry_text.delete(1.0, tk.END)
        self.entry_text.insert(tk.END, f"Title: {entry['title']}\n")
        self.entry_text.insert(tk.END, f"Date: {entry['timestamp']}\n")
        self.entry_text.insert(tk.END, f"Last Modified: {entry['date_modified']}\n\n")
        self.entry_text.insert(tk.END, entry['content'])
        self.entry_text.config(state=tk.DISABLED)

    def sort_by_column(self, column, reverse):
        """Sort the treeview by column and toggle the sort order."""
        if column == "Title":
            self.entries.sort(key=lambda x: x['title'], reverse=reverse)
        elif column == "Date Created":
            self.entries.sort(key=lambda x: x['timestamp'], reverse=reverse)
        elif column == "Date Modified":
            self.entries.sort(key=lambda x: x['date_modified'], reverse=reverse)

        self.sort_orders[column] = not reverse  # Toggle the sort order
        self.refresh_treeview()

    def delete_entry(self):
        """Delete an entry by selecting it from the listbox."""
        # Implement delete logic here


def main():
    root = tk.Tk()
    app = DigitalJournalApp(root)
    root.geometry("700x600")
    root.resizable(True, True)
    root.mainloop()


if __name__ == "__main__":
    main()
