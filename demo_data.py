from supabase_client import (
    create_announcement,
    create_class,
    create_exam,
    create_fee_record,
    create_inventory_item,
    create_library_book,
    create_parent,
    create_student,
    create_teacher,
    create_timetable_entry,
    create_transport_route,
    register_user,
)


def seed_demo_data() -> None:
    try:
        register_user("Admin User", "admin", "admin@example.com", "StrongPass123!", "5550000000", role="admin")
    except ValueError:
        pass

    create_student("Alice Johnson", "STU001", "Grade 9", "alice@example.com", "5551112222", "James Johnson", "12 Oak Street", "No allergies")
    create_student("Brian Smith", "STU002", "Grade 10", "brian@example.com", "5552223333", "Sarah Smith", "88 Pine Avenue", "Asthma")
    create_teacher("Mina Patel", "TCH001", "Science", "MSc", "Physics", "mina@example.com", "5553334444", 98000)
    create_parent("James Johnson", "james@example.com", "5554445555", "Engineer", "5555556666")
    create_class("Grade 9A", "Mina Patel", "Physics,Math", "A", "Room 12", 30)
    create_exam("Midterm", "Physics", "2026-10-15", "Hall 1")
    create_fee_record("STU001", "Monthly", 2500, "Paid")
    create_timetable_entry("Monday", "08:00", "Physics", "Mina Patel", "Room 12")
    create_announcement("School Holiday", "School will be closed next Friday for sports day.", "All")
    create_library_book("Algorithms", "Jane Doe", "Computer Science", 5)
    create_transport_route("Route A", "Daniel Cruz", "North Loop", 40)
    create_inventory_item("Chromebook", "Technology", 25, "Lab 1")


if __name__ == "__main__":
    seed_demo_data()
