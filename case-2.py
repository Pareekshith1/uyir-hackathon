import tkinter as tk
from tkinter import messagebox
import random
import qrcode
from PIL import Image, ImageTk

# Global Variables
PARKING_SLOTS = {i: {"status": "Available", "timer": None} for i in range(1, 7)}
BOOKED_SLOTS = {}  # Stores active bookings {slot: time_left}
slot_positions = {1: (100, 100), 2: (250, 100), 3: (400, 100), 4: (100, 300), 5: (250, 300), 6: (400, 300)}
cars = {}  # {slot: (car_id, timer_text)}
slot_buttons = {}

# Tkinter Windows
root = None
main_screen = None
booking_root = None
parking_root = None
canvas = None
selected_slot = None
case_2_mode = False  # To switch between Case 1 and Case 2


def main_screen_interface():
    global main_screen
    main_screen = tk.Tk()
    main_screen.title("Test Case Selection")
    main_screen.geometry("800x500")
    main_screen.configure(bg="#0A0A0A")

    tk.Label(main_screen, text="🛠️ Select Test Case", font=("Arial", 22, "bold"), bg="#0A0A0A", fg="white").pack(pady=20)

    tk.Button(main_screen, text="🚗 Test Case 1: Smart Parking System", font=("Arial", 16), command=test_case_1,
              width=40, height=2, bg="#007BFF", fg="white").pack(pady=10)

    tk.Button(main_screen, text="🚗 Test Case 2: Smart Parking with Fine", font=("Arial", 16), command=test_case_2,
              width=40, height=2, bg="#007BFF", fg="white").pack(pady=10)

    main_screen.mainloop()


def test_case_1():
    global root, selected_slot, case_2_mode
    case_2_mode = False
    main_screen.destroy()

    root = tk.Tk()
    root.title("Futuristic Parking System")
    root.geometry("800x500")
    root.configure(bg="#0A0A0A")

    selected_slot = tk.IntVar()

    tk.Label(root, text="🚗 Smart Parking Hub 🚀", font=("Arial", 22, "bold"), bg="#0A0A0A", fg="white").pack(pady=20)

    tk.Button(root, text="🅿️ Book a Slot", font=("Arial", 16), command=booking_interface,
              width=20, height=2, bg="#007BFF", fg="white").pack(pady=10)

    tk.Button(root, text="🅿️ Open Parking Lot", font=("Arial", 16), command=parking_lot_interface,
              width=20, height=2, bg="#FF5733", fg="white").pack(pady=10)

    root.mainloop()


def test_case_2():
    global root, selected_slot, case_2_mode
    case_2_mode = True
    main_screen.destroy()

    root = tk.Tk()
    root.title("Futuristic Parking System")
    root.geometry("800x500")
    root.configure(bg="#0A0A0A")

    selected_slot = tk.IntVar()

    tk.Label(root, text="🚗 Smart Parking Hub 🚀", font=("Arial", 22, "bold"), bg="#0A0A0A", fg="white").pack(pady=20)

    tk.Button(root, text="🅿️ Book a Slot", font=("Arial", 16), command=booking_interface,
              width=20, height=2, bg="#007BFF", fg="white").pack(pady=10)

    tk.Button(root, text="🅿️ Open Parking Lot", font=("Arial", 16), command=parking_lot_interface,
              width=20, height=2, bg="#FF5733", fg="white").pack(pady=10)

    root.mainloop()


def update_slot_buttons():
    for i in range(1, 7):
        if i in slot_buttons:
            slot_buttons[i].destroy()
        color = "red" if PARKING_SLOTS[i]["status"] == "Booked" else "green"
        btn = tk.Button(booking_root, text=f"Slot {i}", font=("Arial", 14, "bold"), width=10, height=2, bg=color,
                        fg="white", command=lambda s=i: selected_slot.set(s),
                        state=("disabled" if color == "red" else "normal"))
        btn.pack(pady=5)
        slot_buttons[i] = btn


def booking_interface():
    global booking_root
    booking_root = tk.Toplevel(root)
    booking_root.title("🚗 Parking Slot Booking")
    booking_root.geometry("800x600")
    booking_root.configure(bg="#1A1A1A")

    tk.Label(booking_root, text="📌 Enter Your Details", font=("Arial", 18, "bold"), bg="#1A1A1A", fg="white").pack(pady=10)

    tk.Label(booking_root, text="👤 Name:", font=("Arial", 12), bg="#1A1A1A", fg="white").pack(pady=5)
    name_entry = tk.Entry(booking_root, font=("Arial", 12))
    name_entry.pack(pady=5)

    tk.Label(booking_root, text="⌛ Duration (Minutes):", font=("Arial", 12), bg="#1A1A1A", fg="white").pack(pady=5)
    duration_entry = tk.Entry(booking_root, font=("Arial", 12))
    duration_entry.pack(pady=5)

    tk.Label(booking_root, text="🅿️ Select Slot:", font=("Arial", 18, "bold"), bg="#1A1A1A", fg="white").pack(pady=10)

    update_slot_buttons()

    def generate_ticket():
        name = name_entry.get()
        slot = selected_slot.get()
        duration = duration_entry.get()

        if not (name and slot and duration.isdigit()):
            messagebox.showerror("Error", "Please enter valid details!")
            return

        if PARKING_SLOTS[slot]["status"] == "Booked":
            messagebox.showerror("Error", "Slot already booked. Please choose another.")
            return

        duration = int(duration) * 60
        PARKING_SLOTS[slot]["status"] = "Booked"
        PARKING_SLOTS[slot]["timer"] = duration
        BOOKED_SLOTS[slot] = duration

        update_slot_buttons()
        update_parking_lot()
        display_ticket(name, slot, duration)

    tk.Button(booking_root, text="📥 Book Now", font=("Arial", 14, "bold"), command=generate_ticket, bg="#007BFF", fg="white").pack(pady=20)


def display_ticket(name, slot, duration):
    ticket_window = tk.Toplevel(root)
    ticket_window.title("🎟 Parking Ticket")
    ticket_window.geometry("400x300")
    ticket_window.configure(bg="#2F2F2F")

    tk.Label(ticket_window, text="🎟 Parking Ticket", font=("Arial", 18, "bold"), bg="#2F2F2F", fg="white").pack(pady=10)
    tk.Label(ticket_window, text=f"👤 Name: {name}", font=("Arial", 14), bg="#2F2F2F", fg="white").pack(pady=5)
    tk.Label(ticket_window, text=f"🅿️ Slot: {slot}", font=("Arial", 14), bg="#2F2F2F", fg="white").pack(pady=5)
    tk.Label(ticket_window, text=f"⌛ Duration: {duration // 60} min", font=("Arial", 14), bg="#2F2F2F", fg="white").pack(pady=5)


def parking_lot_interface():
    global parking_root, canvas
    if parking_root and tk.Toplevel.winfo_exists(parking_root):
        return

    parking_root = tk.Toplevel(root)
    parking_root.title("🅿️ Virtual Parking Lot")
    parking_root.geometry("800x600")
    parking_root.configure(bg="#2F2F2F")

    canvas = tk.Canvas(parking_root, width=800, height=500, bg="black")
    canvas.pack()

    update_parking_lot()


def update_parking_lot():
    if not canvas:
        return

    canvas.delete("all")

    for i in range(1, 7):
        x, y = slot_positions[i]
        color = "red" if PARKING_SLOTS[i]["status"] == "Booked" else "green"

        canvas.create_rectangle(x, y, x + 100, y + 150, fill=color, outline="white", width=3)
        if i in BOOKED_SLOTS:
            car = canvas.create_rectangle(x + 25, y + 40, x + 75, y + 100, fill="yellow")
            timer_text = canvas.create_text(x + 50, y - 10, text=f"{BOOKED_SLOTS[i] // 60}s", fill="white", font=("Arial", 14, "bold"))
            cars[i] = (car, timer_text)
            update_timer(i)  # Update the countdown for the slot
            if case_2_mode:
                leave_button = tk.Button(parking_root, text="Leave", font=("Arial", 14, "bold"), bg="#FF5733",
                                         fg="white", command=lambda s=i: leave_car(s))
                leave_button.place(x=x + 25, y=y + 120)


def update_timer(slot):
    if slot in BOOKED_SLOTS and BOOKED_SLOTS[slot] > 0:
        BOOKED_SLOTS[slot] -= 1  # Decrease the timer by 1 second
        _, timer_text = cars[slot]
        canvas.itemconfig(timer_text, text=f"{BOOKED_SLOTS[slot] // 60}s")  # Update the displayed timer
        root.after(1000, update_timer, slot)  # Call this function again after 1 second
    else:
        if slot in BOOKED_SLOTS:
            del BOOKED_SLOTS[slot]
            PARKING_SLOTS[slot]["status"] = "Available"
        update_slot_buttons()
        update_parking_lot()


def leave_car(slot):
    if slot in BOOKED_SLOTS:
        del BOOKED_SLOTS[slot]
        PARKING_SLOTS[slot]["status"] = "Available"
        update_slot_buttons()
        update_parking_lot()


if __name__ == "__main__":
    main_screen_interface()
