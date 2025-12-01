import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext
from controller import LibraryController
from datetime import date

class LibraryGUI(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.title("Library Management System")
        self.geometry("1000x700")
        self.controller = controller 
        
        self._create_widgets()

    def _create_widgets(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, padx=10, expand=True, fill="both")

        # Create frames for each section
        self.user_frame = UserFrame(self.notebook, self.controller)
        self.item_frame = ItemFrame(self.notebook, self.controller)
        self.transaction_frame = TransactionFrame(self.notebook, self.controller)
        self.fine_frame = FineFrame(self.notebook, self.controller)
        self.search_frame = SearchFrame(self.notebook, self.controller)

        self.notebook.add(self.user_frame, text="User Management")
        self.notebook.add(self.item_frame, text="Item Catalog")
        self.notebook.add(self.transaction_frame, text="Borrow/Return")
        self.notebook.add(self.fine_frame, text="Fines")
        self.notebook.add(self.search_frame, text="Search & Reports")
        
        print("GUI structure initialized.")
        
    def run_app(self):
        self.mainloop()
        print("Application closing.")


class UserFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_layout()
        self._populate_user_list()

    def _setup_layout(self):
        # Add User Section
        add_frame = ttk.LabelFrame(self, text="Add New User", padding=10)
        add_frame.pack(fill='x', padx=10, pady=5)
        
        self.name_entry = self._create_input_field(add_frame, "Name:")
        self.age_entry = self._create_input_field(add_frame, "Age:")
        self.email_entry = self._create_input_field(add_frame, "Email:")
        
        type_frame = ttk.Frame(add_frame)
        type_frame.pack(fill='x', padx=5, pady=2)
        ttk.Label(type_frame, text="Type:", width=10).pack(side='left')
        self.user_type_var = tk.StringVar(value="Student")
        ttk.Radiobutton(type_frame, text="Student", variable=self.user_type_var, 
                       value="Student").pack(side='left', padx=5)
        ttk.Radiobutton(type_frame, text="Faculty", variable=self.user_type_var, 
                       value="Faculty").pack(side='left', padx=5)
        
        self.dept_entry = self._create_input_field(add_frame, "Department (Faculty only):")
        
        ttk.Button(add_frame, text="Add User", command=self._add_user_command).pack(pady=10)
        
        # User List Section
        list_frame = ttk.LabelFrame(self, text="Existing Users", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.user_listbox = tk.Listbox(list_frame, width=100, height=15)
        self.user_listbox.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.user_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.user_listbox.config(yscrollcommand=scrollbar.set)
        
        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', padx=10, pady=5)
        ttk.Button(btn_frame, text="View Details", command=self._view_user_details).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Delete User", command=self._delete_user).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Refresh List", command=self._populate_user_list).pack(side='left', padx=5)

    def _create_input_field(self, parent, label_text):
        frame = ttk.Frame(parent)
        frame.pack(fill='x', padx=5, pady=2)
        ttk.Label(frame, text=label_text, width=20).pack(side='left')
        entry = ttk.Entry(frame, width=40)
        entry.pack(side='left', fill='x', expand=True)
        return entry

    def _add_user_command(self):
        name = self.name_entry.get()
        age = self.age_entry.get()
        email = self.email_entry.get()
        user_type = self.user_type_var.get()
        dept = self.dept_entry.get()
        
        if not name or not age or not email:
            messagebox.showerror("Error", "Name, age, and email are required.")
            return

        new_user = self.controller.add_new_user(user_type, name, age, email, dept)
        
        if new_user:
            messagebox.showinfo("Success", f"New {user_type} added: {new_user.name} ({new_user.user_id})")
            self._clear_fields()
            self._populate_user_list()
        else:
            messagebox.showerror("Error", "Failed to add user. Check input values.")
            
    def _clear_fields(self):
        self.name_entry.delete(0, 'end')
        self.age_entry.delete(0, 'end')
        self.email_entry.delete(0, 'end')
        self.dept_entry.delete(0, 'end')

    def _populate_user_list(self):
        self.user_listbox.delete(0, 'end')
        users = self.controller.get_all_users()
        
        for user in users:
            display_text = f"[{user.__class__.__name__}] ID: {user.user_id} - {user.name} | Email: {user.email} | Borrowed: {len(user.borrowed_items)}"
            self.user_listbox.insert(tk.END, display_text)

    def _view_user_details(self):
        selection = self.user_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user")
            return
        
        users = self.controller.get_all_users()
        user = users[selection[0]]
        
        details = user.display_info()
        details += f"\n\nBorrowed Items ({len(user.borrowed_items)}):\n"
        for item in user.borrowed_items:
            details += f"  - {item.title}\n"
        
        messagebox.showinfo(f"User Details - {user.name}", details)

    def _delete_user(self):
        selection = self.user_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user to delete")
            return
        
        users = self.controller.get_all_users()
        user = users[selection[0]]
        
        confirm = messagebox.askyesno("Confirm Delete", 
                                      f"Are you sure you want to delete {user.name}?")
        if confirm:
            success, message = self.controller.delete_user(user.user_id)
            if success:
                messagebox.showinfo("Success", message)
                self._populate_user_list()
            else:
                messagebox.showerror("Error", message)


class ItemFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_layout()
        self._populate_item_list()

    def _setup_layout(self):
        # Add Item Section
        add_frame = ttk.LabelFrame(self, text="Add New Item", padding=10)
        add_frame.pack(fill='x', padx=10, pady=5)
        
        self.title_entry = self._create_input_field(add_frame, "Title:")
        self.author_entry = self._create_input_field(add_frame, "Author/Director:")
        self.year_entry = self._create_input_field(add_frame, "Publication Year:")
        self.copies_entry = self._create_input_field(add_frame, "Copies Available:")
        self.extra_entry = self._create_input_field(add_frame, "Genre/Issue/Duration:")
        
        type_frame = ttk.Frame(add_frame)
        type_frame.pack(fill='x', padx=5, pady=2)
        ttk.Label(type_frame, text="Type:", width=20).pack(side='left')
        self.item_type_var = tk.StringVar(value="Book")
        ttk.Radiobutton(type_frame, text="Book", variable=self.item_type_var, 
                       value="Book").pack(side='left', padx=5)
        ttk.Radiobutton(type_frame, text="Magazine", variable=self.item_type_var, 
                       value="Magazine").pack(side='left', padx=5)
        ttk.Radiobutton(type_frame, text="DVD", variable=self.item_type_var, 
                       value="DVD").pack(side='left', padx=5)
        
        ttk.Button(add_frame, text="Add Item", command=self._add_item_command).pack(pady=10)
        
        # Item List Section
        list_frame = ttk.LabelFrame(self, text="Catalog Items", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.item_listbox = tk.Listbox(list_frame, width=100, height=15)
        self.item_listbox.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.item_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.item_listbox.config(yscrollcommand=scrollbar.set)
        
        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', padx=10, pady=5)
        ttk.Button(btn_frame, text="View Details", command=self._view_item_details).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Update Copies", command=self._update_copies).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Delete Item", command=self._delete_item).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Refresh List", command=self._populate_item_list).pack(side='left', padx=5)

    def _create_input_field(self, parent, label_text):
        frame = ttk.Frame(parent)
        frame.pack(fill='x', padx=5, pady=2)
        ttk.Label(frame, text=label_text, width=20).pack(side='left')
        entry = ttk.Entry(frame, width=40)
        entry.pack(side='left', fill='x', expand=True)
        return entry

    def _add_item_command(self):
        title = self.title_entry.get()
        author = self.author_entry.get()
        year = self.year_entry.get()
        copies = self.copies_entry.get()
        extra = self.extra_entry.get()
        item_type = self.item_type_var.get()
        
        if not title or not year or not copies:
            messagebox.showerror("Error", "Title, year, and copies are required.")
            return

        new_item = self.controller.add_new_item(item_type, title, author, year, copies, extra)
        
        if new_item:
            messagebox.showinfo("Success", f"New {item_type} added: {new_item.title} ({new_item.item_id})")
            self._clear_fields()
            self._populate_item_list()
        else:
            messagebox.showerror("Error", "Failed to add item. Check input values.")
            
    def _clear_fields(self):
        self.title_entry.delete(0, 'end')
        self.author_entry.delete(0, 'end')
        self.year_entry.delete(0, 'end')
        self.copies_entry.delete(0, 'end')
        self.extra_entry.delete(0, 'end')

    def _populate_item_list(self):
        self.item_listbox.delete(0, 'end')
        items = self.controller.get_all_items()
        
        for item in items:
            status = "Available" if item.is_available() else "Unavailable"
            display_text = f"[{item.__class__.__name__}] ID: {item.item_id} - {item.title} | Copies: {item.copies_available} | Status: {status}"
            self.item_listbox.insert(tk.END, display_text)

    def _view_item_details(self):
        selection = self.item_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item")
            return
        
        items = self.controller.get_all_items()
        item = items[selection[0]]
        
        details = item.get_details()
        messagebox.showinfo(f"Item Details - {item.title}", details)

    def _update_copies(self):
        selection = self.item_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item")
            return
        
        items = self.controller.get_all_items()
        item = items[selection[0]]
        
        new_copies = tk.simpledialog.askinteger("Update Copies", 
                                                f"Enter new number of copies for {item.title}:",
                                                initialvalue=item.copies_available)
        if new_copies is not None:
            if self.controller.update_item_copies(item.item_id, new_copies):
                messagebox.showinfo("Success", "Copies updated successfully")
                self._populate_item_list()

    def _delete_item(self):
        selection = self.item_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to delete")
            return
        
        items = self.controller.get_all_items()
        item = items[selection[0]]
        
        confirm = messagebox.askyesno("Confirm Delete", 
                                      f"Are you sure you want to delete {item.title}?")
        if confirm:
            success, message = self.controller.delete_item(item.item_id)
            if success:
                messagebox.showinfo("Success", message)
                self._populate_item_list()
            else:
                messagebox.showerror("Error", message)


class TransactionFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_layout()
        self._populate_active_transactions()

    def _setup_layout(self):
        # Borrow Section
        borrow_frame = ttk.LabelFrame(self, text="Borrow Item", padding=10)
        borrow_frame.pack(fill='x', padx=10, pady=5)
        
        self.borrow_user_entry = self._create_input_field(borrow_frame, "User ID:")
        self.borrow_item_entry = self._create_input_field(borrow_frame, "Item ID:")
        ttk.Button(borrow_frame, text="Issue Item", command=self._issue_item).pack(pady=5)
        
        # Return Section
        return_frame = ttk.LabelFrame(self, text="Return Item", padding=10)
        return_frame.pack(fill='x', padx=10, pady=5)
        
        self.return_user_entry = self._create_input_field(return_frame, "User ID:")
        self.return_item_entry = self._create_input_field(return_frame, "Item ID:")
        ttk.Button(return_frame, text="Return Item", command=self._return_item).pack(pady=5)
        
        # Active Transactions
        trans_frame = ttk.LabelFrame(self, text="Active Transactions", padding=10)
        trans_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.trans_listbox = tk.Listbox(trans_frame, width=100, height=15)
        self.trans_listbox.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(trans_frame, orient='vertical', command=self.trans_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.trans_listbox.config(yscrollcommand=scrollbar.set)
        
        ttk.Button(self, text="Refresh Transactions", 
                  command=self._populate_active_transactions).pack(pady=5)

    def _create_input_field(self, parent, label_text):
        frame = ttk.Frame(parent)
        frame.pack(fill='x', padx=5, pady=2)
        ttk.Label(frame, text=label_text, width=15).pack(side='left')
        entry = ttk.Entry(frame, width=30)
        entry.pack(side='left', fill='x', expand=True)
        return entry

    def _issue_item(self):
        user_id = self.borrow_user_entry.get()
        item_id = self.borrow_item_entry.get()
        
        if not user_id or not item_id:
            messagebox.showerror("Error", "Both User ID and Item ID are required.")
            return
        
        result = self.controller.issue_item(user_id, item_id)
        
        if result.startswith("Success"):
            messagebox.showinfo("Success", result)
            self.borrow_user_entry.delete(0, 'end')
            self.borrow_item_entry.delete(0, 'end')
            self._populate_active_transactions()
        else:
            messagebox.showerror("Error", result)

    def _return_item(self):
        user_id = self.return_user_entry.get()
        item_id = self.return_item_entry.get()
        
        if not user_id or not item_id:
            messagebox.showerror("Error", "Both User ID and Item ID are required.")
            return
        
        result = self.controller.return_item(user_id, item_id)
        
        if result.startswith("Return successful"):
            messagebox.showinfo("Success", result)
            self.return_user_entry.delete(0, 'end')
            self.return_item_entry.delete(0, 'end')
            self._populate_active_transactions()
        else:
            messagebox.showerror("Error", result)

    def _populate_active_transactions(self):
        self.trans_listbox.delete(0, 'end')
        transactions = self.controller.get_active_transactions()
        
        for trans in transactions:
            due_date = trans.borrow_date + timedelta(days=trans.due_days)
            days_left = (due_date - date.today()).days
            status = f"Due in {days_left} days" if days_left > 0 else f"OVERDUE by {abs(days_left)} days"
            
            display_text = f"ID: {trans.transaction_id} | User: {trans.user.name} ({trans.user.user_id}) | Item: {trans.item.title} ({trans.item.item_id}) | {status}"
            self.trans_listbox.insert(tk.END, display_text)


class FineFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_layout()
        self._populate_fine_list()

    def _setup_layout(self):
        # Fine List
        list_frame = ttk.LabelFrame(self, text="All Fines", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.fine_listbox = tk.Listbox(list_frame, width=100, height=20)
        self.fine_listbox.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.fine_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.fine_listbox.config(yscrollcommand=scrollbar.set)
        
        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', padx=10, pady=5)
        ttk.Button(btn_frame, text="Pay Fine", command=self._pay_fine).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Show Unpaid Only", command=self._show_unpaid).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Show All", command=self._populate_fine_list).pack(side='left', padx=5)

    def _populate_fine_list(self):
        self.fine_listbox.delete(0, 'end')
        fines = self.controller.get_all_fines()
        
        total_unpaid = 0
        for fine in fines:
            status = fine.get_status()
            display_text = f"ID: {fine.fine_id} | User: {fine.user.name} ({fine.user.user_id}) | Amount: ${fine.amount:.2f} | Status: {status}"
            self.fine_listbox.insert(tk.END, display_text)
            if not fine.is_paid:
                total_unpaid += fine.amount
        
        self.fine_listbox.insert(tk.END, f"\n--- Total Unpaid Fines: ${total_unpaid:.2f} ---")

    def _show_unpaid(self):
        self.fine_listbox.delete(0, 'end')
        fines = self.controller.get_unpaid_fines()
        
        total = 0
        for fine in fines:
            display_text = f"ID: {fine.fine_id} | User: {fine.user.name} ({fine.user.user_id}) | Amount: ${fine.amount:.2f} | Status: UNPAID"
            self.fine_listbox.insert(tk.END, display_text)
            total += fine.amount
        
        self.fine_listbox.insert(tk.END, f"\n--- Total Unpaid: ${total:.2f} ---")

    def _pay_fine(self):
        selection = self.fine_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a fine to pay")
            return
        
        fines = self.controller.get_all_fines()
        if selection[0] >= len(fines):
            messagebox.showwarning("Warning", "Invalid selection")
            return
            
        fine = fines[selection[0]]
        
        if fine.is_paid:
            messagebox.showinfo("Info", "This fine is already paid")
            return
        
        confirm = messagebox.askyesno("Confirm Payment", 
                                      f"Pay fine of ${fine.amount:.2f} for {fine.user.name}?")
        if confirm:
            success, message = self.controller.pay_fine(fine.fine_id)
            if success:
                messagebox.showinfo("Success", message)
                self._populate_fine_list()


class SearchFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_layout()

    def _setup_layout(self):
        search_frame = ttk.LabelFrame(self, text="Search Items", padding=10)
        search_frame.pack(fill='x', padx=10, pady=5)
        
        input_frame = ttk.Frame(search_frame)
        input_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(input_frame, text="Search Query:").pack(side='left')
        self.search_entry = ttk.Entry(input_frame, width=40)
        self.search_entry.pack(side='left', fill='x', expand=True, padx=5)
        ttk.Button(input_frame, text="Search", command=self._search_items).pack(side='left')
        
        result_frame = ttk.LabelFrame(self, text="Search Results", padding=10)
        result_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.result_text = scrolledtext.ScrolledText(result_frame, width=100, height=20)
        self.result_text.pack(fill='both', expand=True)
        
        report_frame = ttk.LabelFrame(self, text="Generate Reports", padding=10)
        report_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(report_frame, text="All Users Report", 
                  command=self._generate_users_report).pack(side='left', padx=5)
        ttk.Button(report_frame, text="All Items Report", 
                  command=self._generate_items_report).pack(side='left', padx=5)
        ttk.Button(report_frame, text="Active Transactions Report", 
                  command=self._generate_trans_report).pack(side='left', padx=5)

    def _search_items(self):
        query = self.search_entry.get()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search query")
            return
        
        results = self.controller.search_items(query)
        
        self.result_text.delete(1.0, tk.END)
        if results:
            self.result_text.insert(tk.END, f"Found {len(results)} item(s):\n\n")
            for item in results:
                self.result_text.insert(tk.END, item.get_details() + "\n" + "-"*50 + "\n\n")
        else:
            self.result_text.insert(tk.END, "No items found matching your query.")

    def _generate_users_report(self):
        users = self.controller.get_all_users()
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "="*60 + "\n")
        self.result_text.insert(tk.END, "USER REPORT\n")
        self.result_text.insert(tk.END, "="*60 + "\n\n")
        self.result_text.insert(tk.END, f"Total Users: {len(users)}\n\n")
        
        for user in users:
            self.result_text.insert(tk.END, user.display_info() + "\n")
            self.result_text.insert(tk.END, f"Borrowed Items: {len(user.borrowed_items)}\n")
            self.result_text.insert(tk.END, "-"*60 + "\n\n")

    def _generate_items_report(self):
        items = self.controller.get_all_items()
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "="*60 + "\n")
        self.result_text.insert(tk.END, "ITEM CATALOG REPORT\n")
        self.result_text.insert(tk.END, "="*60 + "\n\n")
        self.result_text.insert(tk.END, f"Total Items: {len(items)}\n\n")
        
        for item in items:
            self.result_text.insert(tk.END, item.get_details() + "\n")
            self.result_text.insert(tk.END, "-"*60 + "\n\n")

    def _generate_trans_report(self):
        transactions = self.controller.get_active_transactions()
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "="*60 + "\n")
        self.result_text.insert(tk.END, "ACTIVE TRANSACTIONS REPORT\n")
        self.result_text.insert(tk.END, "="*60 + "\n\n")
        self.result_text.insert(tk.END, f"Total Active Transactions: {len(transactions)}\n\n")
        
        for trans in transactions:
            self.result_text.insert(tk.END, f"Transaction ID: {trans.transaction_id}\n")
            self.result_text.insert(tk.END, f"User: {trans.user.name} ({trans.user.user_id})\n")
            self.result_text.insert(tk.END, f"Item: {trans.item.title} ({trans.item.item_id})\n")
            self.result_text.insert(tk.END, f"Borrow Date: {trans.borrow_date}\n")
            self.result_text.insert(tk.END, f"Due Date: {trans.borrow_date + timedelta(days=trans.due_days)}\n")
            self.result_text.insert(tk.END, "-"*60 + "\n\n")


from datetime import timedelta
import tkinter.simpledialog