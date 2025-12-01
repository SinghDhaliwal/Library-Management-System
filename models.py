from datetime import timedelta, date
from abc import ABC, abstractmethod

class Person:
    def __init__(self, name, age, email):
        self.name = name
        self.age = age
        self.email = email

    def display_info(self):
        return f"Name: {self.name}\nAge: {self.age}\nEmail: {self.email}"

    def update_contact_info(self, new_email):
        self.email = new_email
        print(f"Contact info for {self.name} updated succsessfully.") # Spelling mistake 1

#Abstract Base Class for Library User

class LibraryUser(Person, ABC):
    def __init__(self, name, age, email, user_id, borrowed_items=None):
        super().__init__(name, age, email)
        self.user_id = user_id
        self.borrowed_items = borrowed_items if borrowed_items is not None else []
        self.max_borrow_items = 5 # Default limit

#abstract method for calculating fine
    @abstractmethod
    def calculate_fine(self, days_overdue):
        pass

    def borrow_item(self, item):
        if len(self.borrowed_items) < self.max_borrow_items:
            self.borrowed_items.append(item)
            return True
        else:
            print("Cannot borrow more items. Max limit reached.")
            return False

    def return_item(self, item):
        if item in self.borrowed_items:
            self.borrowed_items.remove(item)
            print(f"{item.title} returned by {self.name}.")
            return True
        return False

class Student(LibraryUser):
    def __init__(self, name, age, email, student_id):
        super().__init__(name, age, email, student_id)
        self.student_id = student_id
        self.max_borrow_items = 4

#polymorphism on calculating fine

    def calculate_fine(self, days_overdue):
        return days_overdue * 0.50

    def display_info(self):
        base_info = super().display_info()
        return f"{base_info}\nUser Type: Student\nID: {self.student_id}"

class Faculty(LibraryUser):
    def __init__(self, name, age, email, employee_id, department):
        super().__init__(name, age, email, employee_id)
        self.employee_id = employee_id
        self.department = department
        self.max_borrow_items = 10

#polymorphism on calculating fine

    def calculate_fine(self, days_overdue):
        return days_overdue * 0.10 # $0.10 per day

    def display_info(self):
        base_info = super().display_info()
        return f"{base_info}\nUser Type: Faculty\nDepartment: {self.department}"

class Librarian(Person):
    def __init__(self, name, age, email, employee_id, access_level):
        super().__init__(name, age, email)
        self.employee_id = employee_id
        self.access_level = access_level

    def issue_item(self, item, user):
        if user.borrow_item(item):
            print(f"Item '{item.title}' issued to {user.name}.")
            return True
        return False

    def add_item(self, item, library_catalog):
        library_catalog.append(item)
        print(f"Item '{item.title}' added to catalog.")

    def register_user(self, user, user_database):
        user_database.append(user)
        print(f"User '{user.name}' registered.")


class LibraryItem:
    def __init__(self, title, item_id, publication_year, copies_available):
        self.title = title
        self.item_id = item_id
        self.publication_year = publication_year
        self.copies_available = copies_available

#method to be overridden

    def get_details(self):
        return f"Title: {self.title}\nYear: {self.publication_year}\nCopies: {self.copies_available}"

    def set_availability(self, copies):
        self.copies_available = copies
        print(f"Availability for {self.title} set to {copies}.")

    def is_available(self):
        return self.copies_available > 0      

class Book(LibraryItem):
    def __init__(self, title, item_id, publication_year, copies_available, author, genre, page_count):
        super().__init__(title, item_id, publication_year, copies_available)
        self.author = author
        self.genre = genre
        self.page_count = page_count

#overrided method

    def get_details(self):
        base_details = super().get_details()
        return f"{base_details}\nAuthor: {self.author}\nGenre: {self.genre}\nPages: {self.page_count}"

class Magazine(LibraryItem):
    def __init__(self, title, item_id, publication_year, copies_available, issue_number):
        super().__init__(title, item_id, publication_year, copies_available)
        self.issue_number = issue_number

#method overriding

    def get_details(self):
        base_details = super().get_details()
        return f"{base_details}\nIssue No.: {self.issue_number}"

class DVD(LibraryItem):
    def __init__(self, title, item_id, publication_year, copies_available, duration_minutes, director):
        super().__init__(title, item_id, publication_year, copies_available)
        self.duration_minutes = duration_minutes
        self.director = director

    def get_details(self):
        base_details = super().get_details()
        return f"{base_details}\nDirector: {self.director}\nDuration: {self.duration_minutes} min"

class Transaction:
    def __init__(self, transaction_id, user, item, borrow_date, return_date=None):
        self.transaction_id = transaction_id
        self.user = user
        self.item = item
        self.borrow_date = borrow_date
        self.return_date = return_date
        self.due_days = user.max_borrow_items * 3

    def check_due_status(self, current_date):
        due_date = self.borrow_date + timedelta(days=self.due_days)
        if self.return_date is None and current_date > due_date:
            days_overdue = (current_date - due_date).days
            return True, days_overdue
        return False, 0
    
    def complete_return(self, return_date):
        self.return_date = return_date
        print(f"Transactoin {self.transaction_id} is complete.")

class Reservation:
    def __init__(self, reservation_id, user, item, reservation_date):
        self.reservation_id = reservation_id
        self.user = user
        self.item = item
        self.reservation_date = reservation_date
        self.expiry_days = 7

    def cancel_reservation(self):
        print(f"Reservation {self.reservation_id} for {self.item.title} cancelled.")
        return True

    def notify_user(self):
        print(f"Notification sent to {self.user.name}: {self.item.title} is now available.")

    def extend_reservation(self, additional_days):
        self.expiry_days += additional_days
        print(f"Reservation extended by {additional_days} days.")

    def is_expired(self, current_date):
        expiry_date = self.reservation_date + timedelta(days=self.expiry_days)
        return current_date > expiry_date

class Fine:
    def __init__(self, fine_id, user, transaction_id, amount, is_paid=False):
        self.fine_id = fine_id
        self.user = user
        self.transaction_id = transaction_id
        self.amount = amount
        self.is_paid = is_paid

    def pay_fine(self):
        self.is_paid = True
        print(f"Fine {self.fine_id} of ${self.amount:.2f} paid by {self.user.name}.")
        return True
    
    def get_status(self):
        return "Paid" if self.is_paid else "Unpaid"

class ReportGenerator:
    def generate_user_report(self, user):
        report = f"--- User Report for {user.name} ({user.user_id}) ---\n"
        report += f"Borrowed Items: {[item.title for item in user.borrowed_items]}\n"
        report += "Status: Active"
        return report

    def generate_item_report(self, item):
        report = f"--- Item Report for {item.title} ---\n"
        report += f"Copies Available: {item.copies_available}\n"
        report += f"Total Copies: {item.copies_available + 1} (Placeholder)\n"
        return report

    def generate_transaction_report(self, transaction):
        report = f"--- Transaction {transaction.transaction_id} ---\n"
        report += f"User: {transaction.user.name}\n"
        report += f"Item: {transaction.item.title}\n"
        report += f"Borrow Date: {transaction.borrow_date}\n"
        report += f"Return Date: {transaction.return_date if transaction.return_date else 'N/A'}"
        return report

    def save_report(self, report, filename):
        with open(filename, 'w') as f:
            f.write(report)
        print(f"Report saved to {filename}")

class IDGenerator:
    def __init__(self, start_id=1000):
        self._next_user_id = start_id
        self._next_item_id = start_id
        self._next_trans_id = start_id
        self._next_res_id = start_id
        self._next_fine_id = start_id
        
    def generate_user_id(self, user_type):
        self._next_user_id += 1
        prefix = 'S' if isinstance(user_type, Student) else 'F' if isinstance(user_type, Faculty) else 'L'
        return f"{prefix}{self._next_user_id}"

    def generate_item_id(self, item_type):
        self._next_item_id += 1
        prefix = 'B' if isinstance(item_type, Book) else 'M' if isinstance(item_type, Magazine) else 'D'
        return f"{prefix}{self._next_item_id}"

    def generate_transaction_id(self):
        self._next_trans_id += 1
        return f"T{self._next_trans_id}"

    def generate_reservation_id(self):
        self._next_res_id += 1
        return f"R{self._next_res_id}"

    def generate_fine_id(self):
        self._next_fine_id += 1
        return f"F{self._next_fine_id}"

class DataAccessAbstract(ABC):
    @abstractmethod
    def save_data(self, data, data_type):
        """Abstract method to persist data."""
        pass

    @abstractmethod
    def load_data(self, data_type):
        """Abstract method to retrieve data."""
        pass

class SQLiteManager(DataAccessAbstract):
    def __init__(self, db_name):
        self.db_name = db_name

    def save_data(self, data, data_type):
        print(f"Saving {len(data)} {data_type} records to {self.db_name}...")
        return True

    def load_data(self, data_type):
        print(f"Loading {data_type} from {self.db_name}...")
        return []