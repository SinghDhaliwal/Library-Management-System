# controller.py

from models import (
    Student, Faculty, Book, Magazine, DVD, 
    Transaction, Fine, IDGenerator, LibraryItem, Reservation
)
from datetime import date
from data import SQLiteManager

class LibraryController:
    """
    The central controller managing application flow, business logic, 
    and interaction between the UI and data layers.
    """
    def __init__(self, db_manager: SQLiteManager):
        self.db_manager = db_manager 
        self.id_generator = IDGenerator()
        
        # Core data storage
        self.users = {}
        self.items = {}
        self.transactions = {}
        self.fines = {}
        self.reservations = {}
        
        self._load_initial_data()

    def _load_initial_data(self):
        """Loads all persisted objects from the database into memory."""
        print("Starting initial data load...")
        
        loaded_users = self.db_manager.load_data("User")
        for user in loaded_users:
            self.users[user.user_id] = user
            
        loaded_items = self.db_manager.load_data("Item")
        for item in loaded_items:
            self.items[item.item_id] = item

        loaded_transactions = self.db_manager.load_data("Transaction")
        for trans in loaded_transactions:
            self.transactions[trans.transaction_id] = trans

        loaded_fines = self.db_manager.load_data("Fine")
        for fine in loaded_fines:
            self.fines[fine.fine_id] = fine
        
        print(f"Data load complete: {len(self.users)} Users, {len(self.items)} Items loaded.")

    # --- User Management Methods ---
    
    def add_new_user(self, user_type: str, name: str, age: int, email: str, dept_or_id: str = ""):
        """Creates a new User object, saves it, and returns the user object."""
        try:
            age = int(age)
        except ValueError:
            return None
            
        if user_type == "Student":
            new_id = self.id_generator.generate_user_id(Student)
            new_user = Student(name, age, email, new_id)
        elif user_type == "Faculty":
            new_id = self.id_generator.generate_user_id(Faculty)
            department = dept_or_id if dept_or_id else "General"
            new_user = Faculty(name, age, email, new_id, department)
        else:
            return None

        self.users[new_id] = new_user
        self.db_manager.save_data([new_user], "User")
        return new_user

    def get_all_users(self):
        """Returns a list of all user objects."""
        return list(self.users.values())

    def get_user_by_id(self, user_id: str):
        """Returns a specific user by ID."""
        return self.users.get(user_id)

    def update_user_email(self, user_id: str, new_email: str):
        """Updates a user's email address."""
        user = self.users.get(user_id)
        if user:
            user.update_contact_info(new_email)
            self.db_manager.save_data([user], "User")
            return True
        return False

    def delete_user(self, user_id: str):
        """Deletes a user from the system."""
        if user_id in self.users:
            user = self.users[user_id]
            if len(user.borrowed_items) > 0:
                return False, "Cannot delete user with borrowed items"
            del self.users[user_id]
            return True, "User deleted successfully"
        return False, "User not found"

    # --- Item Management Methods ---

    def add_new_item(self, item_type: str, title: str, author_or_director: str, 
                     pub_year: int, copies: int, extra_data: str = ""):
        """Creates a new Item object and adds it to the catalog."""
        try:
            pub_year = int(pub_year)
            copies = int(copies)
        except ValueError:
            return None
            
        new_item = None
        
        if item_type == "Book":
            new_id = self.id_generator.generate_item_id(Book)
            genre = extra_data if extra_data else "General"
            new_item = Book(title, new_id, pub_year, copies, author_or_director, genre, 300)
        elif item_type == "Magazine":
            new_id = self.id_generator.generate_item_id(Magazine)
            try:
                issue_num = int(extra_data) if extra_data else 1
            except ValueError:
                issue_num = 1
            new_item = Magazine(title, new_id, pub_year, copies, issue_num)
        elif item_type == "DVD":
            new_id = self.id_generator.generate_item_id(DVD)
            new_item = DVD(title, new_id, pub_year, copies, 90, author_or_director)
        else:
            return None
            
        self.items[new_id] = new_item
        self.db_manager.save_data([new_item], "Item")
        return new_item

    def get_all_items(self):
        """Returns a list of all item objects."""
        return list(self.items.values())

    def get_item_by_id(self, item_id: str):
        """Returns a specific item by ID."""
        return self.items.get(item_id)

    def search_items(self, query: str):
        """Searches for items by title or author."""
        query_lower = query.lower()
        results = []
        for item in self.items.values():
            if query_lower in item.title.lower():
                results.append(item)
            elif hasattr(item, 'author') and query_lower in item.author.lower():
                results.append(item)
            elif hasattr(item, 'director') and query_lower in item.director.lower():
                results.append(item)
        return results

    def update_item_copies(self, item_id: str, new_copies: int):
        """Updates the number of copies for an item."""
        item = self.items.get(item_id)
        if item:
            item.set_availability(new_copies)
            self.db_manager.save_data([item], "Item")
            return True
        return False

    def delete_item(self, item_id: str):
        """Deletes an item from the catalog."""
        if item_id in self.items:
            item = self.items[item_id]
            # Check if item is currently borrowed
            for trans in self.transactions.values():
                if trans.item.item_id == item_id and trans.return_date is None:
                    return False, "Cannot delete item that is currently borrowed"
            del self.items[item_id]
            return True, "Item deleted successfully"
        return False, "Item not found"

    # --- Transaction/Borrowing Methods ---

    def issue_item(self, user_id: str, item_id: str):
        """Processes the borrowing of an item."""
        user = self.users.get(user_id)
        item = self.items.get(item_id)
        
        if not user:
            return "Error: User not found."
        if not item:
            return "Error: Item not found in catalog."
        if not isinstance(user, (Student, Faculty)):
            return "Error: Only students and faculty can borrow items."

        if not item.is_available():
            return "Error: Item is currently unavailable."
        
        if user.borrow_item(item):
            item.set_availability(item.copies_available - 1)
            
            trans_id = self.id_generator.generate_transaction_id()
            new_transaction = Transaction(trans_id, user, item, date.today())
            self.transactions[trans_id] = new_transaction
            
            self.db_manager.save_data([item], "Item")
            self.db_manager.save_data([new_transaction], "Transaction")
            
            return f"Success: {item.title} issued to {user.name} ({user_id})."
        else:
            return f"Error: {user.name} cannot borrow more items. Limit is {user.max_borrow_items}."

    def return_item(self, user_id: str, item_id: str):
        """Processes the return of an item and checks for fines."""
        user = self.users.get(user_id)
        item = self.items.get(item_id)
        
        if not user or not item:
            return "Error: User or item not found."

        active_trans = next((t for t in self.transactions.values() 
                             if t.user.user_id == user_id and t.item.item_id == item_id 
                             and t.return_date is None), None)

        if not active_trans:
            return "Error: Active borrow transaction not found for this user/item combination."
        
        user.return_item(item)
        item.set_availability(item.copies_available + 1)
        active_trans.complete_return(date.today())
        
        is_overdue, days_overdue = active_trans.check_due_status(date.today())
        
        if is_overdue:
            fine_amount = user.calculate_fine(days_overdue)
            fine_id = self.id_generator.generate_fine_id()
            new_fine = Fine(fine_id, user, active_trans.transaction_id, fine_amount)
            self.fines[fine_id] = new_fine
            self.db_manager.save_data([new_fine], "Fine")

            return f"Return successful. Overdue by {days_overdue} days. Fine of ${fine_amount:.2f} created."
        
        self.db_manager.save_data([active_trans], "Transaction")
        self.db_manager.save_data([item], "Item")
        
        return "Return successful. No fine incurred."

    def get_user_borrowed_items(self, user_id: str):
        """Returns list of items currently borrowed by user."""
        user = self.users.get(user_id)
        if user:
            return user.borrowed_items
        return []

    def get_all_transactions(self):
        """Returns all transactions."""
        return list(self.transactions.values())

    def get_active_transactions(self):
        """Returns only active (not returned) transactions."""
        return [t for t in self.transactions.values() if t.return_date is None]

    # --- Fine Management Methods ---

    def get_all_fines(self):
        """Returns all fines."""
        return list(self.fines.values())

    def get_unpaid_fines(self):
        """Returns only unpaid fines."""
        return [f for f in self.fines.values() if not f.is_paid]

    def get_user_fines(self, user_id: str):
        """Returns all fines for a specific user."""
        return [f for f in self.fines.values() if f.user.user_id == user_id]

    def pay_fine(self, fine_id: str):
        """Marks a fine as paid."""
        fine = self.fines.get(fine_id)
        if fine:
            fine.pay_fine()
            self.db_manager.save_data([fine], "Fine")
            return True, f"Fine {fine_id} paid successfully"
        return False, "Fine not found"

    # --- Reservation Methods ---

    def create_reservation(self, user_id: str, item_id: str):
        """Creates a reservation for an item."""
        user = self.users.get(user_id)
        item = self.items.get(item_id)
        
        if not user or not item:
            return None, "User or item not found"
            
        res_id = self.id_generator.generate_reservation_id()
        new_reservation = Reservation(res_id, user, item, date.today())
        self.reservations[res_id] = new_reservation
        
        return new_reservation, "Reservation created successfully"

    def cancel_reservation(self, reservation_id: str):
        """Cancels a reservation."""
        if reservation_id in self.reservations:
            reservation = self.reservations[reservation_id]
            reservation.cancel_reservation()
            del self.reservations[reservation_id]
            return True, "Reservation cancelled"
        return False, "Reservation not found"

    def get_all_reservations(self):
        """Returns all reservations."""
        return list(self.reservations.values())