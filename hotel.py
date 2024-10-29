import streamlit as st
import sqlite3
from datetime import datetime

# Connect to the SQLite database (this will create a new file if it doesn't exist)
conn = sqlite3.connect('hotel.db')
c = conn.cursor()

# Create tables for guests, rooms, and reservations
def create_tables():
    c.execute('''CREATE TABLE IF NOT EXISTS guests (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT,
                 phone TEXT,
                 email TEXT
                 )''')
    c.execute('''CREATE TABLE IF NOT EXISTS rooms (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 room_number INTEGER UNIQUE,
                 room_type TEXT,
                 price_per_night REAL,
                 status TEXT
                 )''')
    c.execute('''CREATE TABLE IF NOT EXISTS reservations (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 guest_id INTEGER,
                 room_id INTEGER,
                 check_in DATE,
                 check_out DATE,
                 FOREIGN KEY (guest_id) REFERENCES guests (id),
                 FOREIGN KEY (room_id) REFERENCES rooms (id)
                 )''')
    conn.commit()

# Initialize database tables
create_tables()

# Streamlit app title
st.title("Hotel Management System")

# Sidebar for navigation
menu = st.sidebar.selectbox("Menu", ["Add Guest", "Add Room", "Make Reservation", "View Guests", "View Rooms", "View Reservations"])

# Function to add a guest
def add_guest():
    st.subheader("Add New Guest")
    name = st.text_input("Guest Name")
    phone = st.text_input("Phone Number")
    email = st.text_input("Email")
    if st.button("Add Guest"):
        c.execute("INSERT INTO guests (name, phone, email) VALUES (?, ?, ?)", (name, phone, email))
        conn.commit()
        st.success(f"Guest {name} added successfully")

# Function to add a room
def add_room():
    st.subheader("Add New Room")
    room_number = st.number_input("Room Number", min_value=1, step=1)
    room_type = st.selectbox("Room Type", ["Single", "Double", "Suite"])
    price_per_night = st.number_input("Price per Night", min_value=0.0, step=0.01)
    if st.button("Add Room"):
        try:
            c.execute("INSERT INTO rooms (room_number, room_type, price_per_night, status) VALUES (?, ?, ?, ?)", 
                      (room_number, room_type, price_per_night, "Available"))
            conn.commit()
            st.success(f"Room {room_number} added successfully")
        except sqlite3.IntegrityError:
            st.error("Room number already exists!")

# Function to make a reservation
def make_reservation():
    st.subheader("Make Reservation")
    guests = c.execute("SELECT id, name FROM guests").fetchall()
    rooms = c.execute("SELECT id, room_number FROM rooms WHERE status = 'Available'").fetchall()
    
    if guests and rooms:
        guest_id = st.selectbox("Select Guest", guests, format_func=lambda x: x[1])
        room_id = st.selectbox("Select Room", rooms, format_func=lambda x: f"Room {x[1]}")
        check_in = st.date_input("Check-in Date", min_value=datetime.today())
        check_out = st.date_input("Check-out Date", min_value=check_in)
        
        if st.button("Reserve"):
            if check_out > check_in:
                c.execute("INSERT INTO reservations (guest_id, room_id, check_in, check_out) VALUES (?, ?, ?, ?)",
                          (guest_id[0], room_id[0], check_in, check_out))
                c.execute("UPDATE rooms SET status = 'Occupied' WHERE id = ?", (room_id[0],))
                conn.commit()
                st.success(f"Reservation for Room {room_id[1]} made successfully for Guest {guest_id[1]}")
            else:
                st.error("Check-out date must be after check-in date!")
    else:
        st.error("No available rooms or guests found. Please add them first.")

# Function to view guests
def view_guests():
    st.subheader("List of Guests")
    guests = c.execute("SELECT * FROM guests").fetchall()
    for guest in guests:
        st.write(f"ID: {guest[0]}, Name: {guest[1]}, Phone: {guest[2]}, Email: {guest[3]}")

# Function to view rooms
def view_rooms():
    st.subheader("List of Rooms")
    rooms = c.execute("SELECT * FROM rooms").fetchall()
    for room in rooms:
        st.write(f"Room Number: {room[1]}, Type: {room[2]}, Price: ${room[3]:.2f}, Status: {room[4]}")

# Function to view reservations
def view_reservations():
    st.subheader("List of Reservations")
    reservations = c.execute('''SELECT guests.name, rooms.room_number, reservations.check_in, reservations.check_out 
                                FROM reservations
                                JOIN guests ON reservations.guest_id = guests.id
                                JOIN rooms ON reservations.room_id = rooms.id''').fetchall()
    for res in reservations:
        st.write(f"Guest: {res[0]}, Room: {res[1]}, Check-in: {res[2]}, Check-out: {res[3]}")

# Display content based on the selected menu option
if menu == "Add Guest":
    add_guest()
elif menu == "Add Room":
    add_room()
elif menu == "Make Reservation":
    make_reservation()
elif menu == "View Guests":
    view_guests()
elif menu == "View Rooms":
    view_rooms()
elif menu == "View Reservations":
    view_reservations()

# Close the connection when app stops
conn.close()
