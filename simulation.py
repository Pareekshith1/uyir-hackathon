import tkinter as tk
from tkinter import messagebox, ttk
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


def main_screen_interface():
    global main_screen
    main_screen = tk.Tk()
    main_screen.title("Test Case Selection")
    main_screen.geometry("800x500")
    main_screen.configure(bg="#0A0A0A")

    tk.Label(main_screen, text="🛠️ Select Test Case", font=("Arial", 22, "bold"), bg="#0A0A0A", fg="white").pack(pady=20)

    tk.Button(main_screen, text="🚗 Test Case 1: Smart Parking System", font=("Arial", 16), command=test_case_1,
              width=40, height=2, bg="#007BFF", fg="white").pack(pady=10)

    main_screen.mainloop()


def test_case_1():
    global root, selected_slot
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

    # ----------------- Destination Selection -----------------
    tk.Label(booking_root, text="📍 Select Destination:", font=("Arial", 12), bg="#1A1A1A", fg="white").pack(pady=5)
    destination_values = ["Brookfield Mall", "Prozone Mall", "Funmall", "City Centre", "Plaza Mall"]
    destination_combo = ttk.Combobox(booking_root, values=destination_values, font=("Arial", 12))
    destination_combo.set(destination_values[0])
    destination_combo.pack(pady=5)

    tk.Label(booking_root, text="🅿️ Select Slot:", font=("Arial", 18, "bold"), bg="#1A1A1A", fg="white").pack(pady=10)

    update_slot_buttons()

    def generate_ticket():
        name = name_entry.get()
        slot = selected_slot.get()
        duration = duration_entry.get()
        destination = destination_combo.get().strip()

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
        display_ticket(name, slot, duration,destination)

    tk.Button(booking_root, text="📥 Book Now", font=("Arial", 14, "bold"), command=generate_ticket, bg="#007BFF", fg="white").pack(pady=20)


def display_ticket(name, slot, duration,destination):
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
            timer_text = canvas.create_text(x + 50, y - 10, text=f"{BOOKED_SLOTS[i]}s", fill="white", font=("Arial", 14, "bold"))
            cars[i] = (car, timer_text)

    parking_root.after(1000, update_timer)


def update_timer():
    to_remove = []
    for slot in list(BOOKED_SLOTS.keys()):
        BOOKED_SLOTS[slot] -= 1
        if BOOKED_SLOTS[slot] <= 0:
            to_remove.append(slot)
        else:
            canvas.itemconfig(cars[slot][1], text=f"{BOOKED_SLOTS[slot]}s")

    for slot in to_remove:
        del BOOKED_SLOTS[slot]
        PARKING_SLOTS[slot]["status"] = "Available"
        update_slot_buttons()
        update_parking_lot()

    parking_root.after(1000, update_timer)


main_screen_interface()