from models import Student, Faculty, Book, Magazine, DVD, Transaction, Fine
from datetime import date, timedelta
from data import SQLiteManager
from controller import LibraryController
from ui import LibraryGUI

def main():
    print("="*60)
    print("LIBRARY MANAGEMENT SYSTEM - STARTING UP")
    print("="*60)
    
    DB_FILE_NAME = "library_system.db"
    db_manager = SQLiteManager(DB_FILE_NAME) 
    print(f"Data layer initiated for file: {DB_FILE_NAME}.")

    library_app = LibraryController(db_manager) 
    print("Application controller initiated and loaded initial data.")

    if len(library_app.users) == 0:
        print("\n--- Initializing with sample data ---")
        
        student1 = library_app.add_new_user("Student", "Aisha Sharma", "20", "aisha@email.com")
        student2 = library_app.add_new_user("Student", "Raj Patel", "22", "raj@email.com")
        faculty1 = library_app.add_new_user("Faculty", "Dr. Smith", "45", "smith@uni.edu", "Science")
        faculty2 = library_app.add_new_user("Faculty", "Dr. Johnson", "38", "johnson@uni.edu", "Literature")
        
        print(f"Added {len(library_app.users)} sample users.")
        
        book1 = library_app.add_new_item("Book", "OOP Fundamentals", "Author X", "2023", "5", "Computer Science")
        book2 = library_app.add_new_item("Book", "Data Structures", "Author Y", "2022", "3", "Computer Science")
        book3 = library_app.add_new_item("Book", "Python Programming", "Author Z", "2024", "4", "Programming")
        magazine1 = library_app.add_new_item("Magazine", "Tech Monthly", "Various", "2024", "10", "12")
        dvd1 = library_app.add_new_item("DVD", "Learning Python", "John Director", "2023", "2", "John Director")
        
        print(f"Added {len(library_app.items)} sample items to catalog.")
        print("Sample data initialization complete!\n")
    
    print("\n--- Testing Fine Calculation System ---")
    
    if library_app.users and library_app.items:
        test_user = list(library_app.users.values())[0]
        test_item = list(library_app.items.values())[0]
        
        # Create a test transaction that's overdue
        borrow_date = date.today() - timedelta(days=20)  # 20 days ago
        test_trans = Transaction("TEST_T001", test_user, test_item, borrow_date)
        
        is_overdue, days_overdue = test_trans.check_due_status(date.today())
        
        if is_overdue:
            fine_amount = test_user.calculate_fine(days_overdue)
            print(f"Test: Item '{test_item.title}' would be overdue by {days_overdue} days.")
            print(f"Fine for {test_user.__class__.__name__}: ${fine_amount:.2f}")
        else:
            print("Test transaction is not overdue.")
    
    print("\n" + "="*60)
    print("LAUNCHING GUI APPLICATION")
    print("="*60)
    print("\nInstructions:")
    print("1. User Management: Add students and faculty members")
    print("2. Item Catalog: Add books, magazines, and DVDs")
    print("3. Borrow/Return: Issue items to users and process returns")
    print("4. Fines: View and pay outstanding fines")
    print("5. Search & Reports: Search items and generate reports")
    print("\n")
    
    app = LibraryGUI(library_app) 
    app.run_app()
    
    db_manager.close()
    print("\nMain program termination complete.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nApplication closed; all processes terminated.")