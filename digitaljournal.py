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
            return json.load(file)
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

        # Treeview for displaying journal entries
        self.entry_tree = ttk.Treeview(self.root, columns=("Title", "Date"), show='headings', height=10)
        self.entry_tree.heading("Title", text="Title")
        self.entry_tree.heading("Date", text="Date")
        self.entry_tree.column("Title", anchor="w", width=300)  # Left align Title
        self.entry_tree.column("Date", anchor="w", width=120)  # Left align Date
        self.entry_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.entry_tree.bind("<ButtonRelease-1>", self.display_entry)  # Change to single click

        # Scrolled text area to show selected journal entry
        self.entry_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=50, height=10, state=tk.DISABLED,
                                                    bg="#ffffff", font=("Helvetica", 12))
        self.entry_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.entry_text.pack_forget()  # Hide initially

        # Store the full list of entries for displaying
        self.entries = load_entries()
        self.search_results = []  # To store search results
        self.refresh_treeview()

    def refresh_treeview(self):
        """Refresh the list of entries displayed in the treeview and manage placeholder text."""
        self.entry_tree.delete(*self.entry_tree.get_children())

        if not self.entries:
            # Show placeholder text
            self.entry_tree.insert("", "end", values=("No journal entries available.", ""))
            self.entry_text.pack_forget()  # Hide the text area if no entries available
        else:
            # Insert entry titles and dates
            for entry in self.entries:
                self.entry_tree.insert("", "end", values=(entry['title'], entry['timestamp']))

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
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            self.entries.append(entry)  # Append to the local entries
            save_entries(self.entries)
            messagebox.showinfo("Entry Added", "Your entry has been added successfully.")
            self.refresh_treeview()
            dialog.destroy()

        tk.Button(dialog, text="Save Entry", command=save_and_close, bg="#4CAF50", fg="white",
                  font=("Helvetica", 12)).grid(row=2, column=1, padx=10, pady=10)
        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)

    def edit_entry(self):
        """Edit the selected journal entry."""
        selected_item = self.entry_tree.selection()
        if not selected_item:
            messagebox.showwarning("Select Entry", "Please select an entry to edit.")
            return

        # Retrieve the entry from search results or original entries
        entry_index = self.entry_tree.index(selected_item)
        entry = self.search_results[entry_index] if self.search_results else self.entries[entry_index]

        # Create a dialog for editing the entry
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Entry")

        tk.Label(dialog, text="Edit Title:", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=10)
        title_entry = tk.Entry(dialog, width=40, font=("Helvetica", 12))
        title_entry.insert(0, entry['title'])  # Set current title
        title_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(dialog, text="Edit Content:", font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=10)
        content_text = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, width=40, height=10, font=("Helvetica", 12))
        content_text.insert(tk.END, entry['content'])  # Set current content
        content_text.grid(row=1, column=1, padx=10, pady=10)

        def save_changes():
            new_title = title_entry.get().strip()
            new_content = content_text.get(1.0, tk.END).strip()
            if not new_title:
                messagebox.showerror("Error", "Title cannot be empty.")
                return
            # Update entry and save to file
            entry['title'] = new_title
            entry['content'] = new_content
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
        """Display the content of the selected entry or hide the entry box if nothing is selected."""
        selected_item = self.entry_tree.selection()
        if not selected_item:
            self.entry_text.pack_forget()  # Hide if nothing is selected
            return

        entry_index = self.entry_tree.index(selected_item)
        selected_entry = self.search_results[entry_index] if self.search_results else self.entries[entry_index]

        # Display the selected entry's details
        self.entry_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.entry_text.config(state=tk.NORMAL)
        self.entry_text.delete(1.0, tk.END)
        self.entry_text.insert(tk.END, f"Title: {selected_entry['title']}\n")
        self.entry_text.insert(tk.END, f"Date: {selected_entry['timestamp']}\n\n")
        self.entry_text.insert(tk.END, selected_entry['content'])
        self.entry_text.config(state=tk.DISABLED)

    def delete_entry(self):
        """Delete the selected entry."""
        selected_item = self.entry_tree.selection()
        if not selected_item:
            messagebox.showwarning("Select Entry", "Please select an entry to delete.")
            return

        entry_index = self.entry_tree.index(selected_item)
        deleted_entry = self.search_results.pop(entry_index) if self.search_results else self.entries.pop(entry_index)
        save_entries(self.entries)

        messagebox.showinfo("Entry Deleted", f"Deleted entry: {deleted_entry['title']}")
        self.refresh_treeview()

        # Clear the entry text box if no entries remain
        if not self.entries:
            self.entry_text.pack_forget()
        else:
            self.entry_text.config(state=tk.NORMAL)
            self.entry_text.delete(1.0, tk.END)
            self.entry_text.config(state=tk.DISABLED)

    def search_entries(self):
        """Search entries by title."""
        query = self.search_entry.get().strip().lower()
        self.entry_tree.delete(*self.entry_tree.get_children())
        self.search_results = [entry for entry in self.entries if query in entry['title'].lower()]

        if self.search_results:
            for entry in self.search_results:
                self.entry_tree.insert("", "end", values=(entry['title'], entry['timestamp']))
        else:
            self.entry_tree.insert("", "end", values=("No matching entries found.", ""))

        self.entry_text.pack_forget()

    def reset_search(self):
        """Reset the search field and display all entries."""
        self.search_entry.delete(0, tk.END)  # Clear search entry
        self.search_results.clear()  # Clear search results
        self.entries = load_entries()  # Reload original entries
        self.refresh_treeview()  # Show all entries


def main():
    root = tk.Tk()
    app = DigitalJournalApp(root)
    root.geometry("600x600")  # Increased height for better display
    root.resizable(True, True)  # Allow the window to be resizable
    root.mainloop()


if __name__ == "__main__":
    main()
