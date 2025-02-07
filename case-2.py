import tkinter as tk
from tkinter import messagebox

# Global Variables
PARKING_SLOTS = {i: {"status": "Available", "timer": None, "fine": 0} for i in range(1, 7)}
BOOKED_SLOTS = {}  # Stores active bookings {slot: time_left}
slot_positions = {1: (100, 100), 2: (250, 100), 3: (400, 100), 4: (100, 300), 5: (250, 300), 6: (400, 300)}
cars = {}  # {slot: (car_id, timer_text, leave_button, fine_text)}
slot_buttons = {}

# Tkinter Windows
root = None
booking_root = None
parking_root = None
canvas = None
selected_slot = None
ticket_number = 1001  # Ticket generation number


# Main Screen Interface
def main_screen_interface():
    global root
    root = tk.Tk()
    root.title("Smart Parking System")
    root.geometry("800x500")
    root.configure(bg="#0A0A0A")

    tk.Label(root, text="🚗 Smart Parking System", font=("Arial", 22, "bold"), bg="#0A0A0A", fg="white").pack(pady=20)

    tk.Button(root, text="🅿️ Book a Slot", font=("Arial", 16), command=booking_interface,
              width=20, height=2, bg="#007BFF", fg="white").pack(pady=10)

    tk.Button(root, text="🅿️ Open Parking Lot", font=("Arial", 16), command=parking_lot_interface,
              width=20, height=2, bg="#FF5733", fg="white").pack(pady=10)

    root.mainloop()


# Update Slot Buttons for Booking Interface
def update_slot_buttons():
    for i in range(1, 7):
        if i in slot_buttons:
            slot_buttons[i].destroy()

        color = "red" if PARKING_SLOTS[i]["status"] == "Booked" else "green"
        state = "disabled" if color == "red" else "normal"

        btn = tk.Button(booking_root, text=f"Slot {i}", font=("Arial", 14, "bold"), width=10, height=2, bg=color,
                        fg="white", command=lambda s=i: selected_slot.set(s), state=state)
        btn.pack(pady=5)
        slot_buttons[i] = btn


# Booking Interface
def booking_interface():
    global booking_root, selected_slot
    booking_root = tk.Toplevel(root)
    booking_root.title("🚗 Parking Slot Booking")
    booking_root.geometry("800x600")
    booking_root.configure(bg="#1A1A1A")

    selected_slot = tk.IntVar()

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

        duration = int(duration) * 60

        PARKING_SLOTS[slot]["status"] = "Booked"
        PARKING_SLOTS[slot]["timer"] = duration
        PARKING_SLOTS[slot]["fine"] = 0
        BOOKED_SLOTS[slot] = duration

        update_slot_buttons()
        update_parking_lot()

        update_timer(slot)
        apply_fine(slot)

        global ticket_number
        ticket_number += 1
        messagebox.showinfo("Ticket Generated", f"Ticket Number: {ticket_number-1}\nCar Details:\nName: {name}\nSlot: {slot}\nDuration: {duration//60} minutes")

    tk.Button(booking_root, text="📥 Book Now", font=("Arial", 14, "bold"), command=generate_ticket, bg="#007BFF",
              fg="white").pack(pady=20)


# Parking Lot Interface
def parking_lot_interface():
    global parking_root, canvas
    parking_root = tk.Toplevel(root)
    parking_root.title("🅿️ Virtual Parking Lot")
    parking_root.geometry("800x600")
    parking_root.configure(bg="#2F2F2F")

    canvas = tk.Canvas(parking_root, width=800, height=500, bg="black")
    canvas.pack()

    update_parking_lot()


# Update Parking Lot View
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
            timer_text = canvas.create_text(x + 50, y - 10, text=f"{BOOKED_SLOTS[i]}s", fill="white",
                                            font=("Arial", 14, "bold"))
            fine_text = canvas.create_text(x + 50, y + 130, text=f"₹{PARKING_SLOTS[i]['fine']}", fill="white",
                                           font=("Arial", 14, "bold"))

            leave_button = tk.Button(parking_root, text="Leave", font=("Arial", 12), bg="#FF5733",
                                     fg="white", command=lambda s=i: leave_car(s))
            leave_button.place(x=x + 25, y=y + 120)

            cars[i] = (car, timer_text, leave_button, fine_text)


# Update Timer for Booked Slots
def update_timer(slot):
    if slot in BOOKED_SLOTS and BOOKED_SLOTS[slot] > 0:
        BOOKED_SLOTS[slot] -= 1

        if slot in cars:
            _, timer_text, _, _ = cars[slot]
            canvas.itemconfig(timer_text, text=f"{BOOKED_SLOTS[slot]}s")

        root.after(1000, update_timer, slot)
    else:
        messagebox.showwarning("Time's Up!", f"Time for car in slot {slot} has run out! Please move your car.")
        # After showing the warning, we will start applying fine every 10 seconds
        root.after(10000, apply_fine, slot)


# Apply Fine for Overstay
def apply_fine(slot):
    if slot in BOOKED_SLOTS and BOOKED_SLOTS[slot] == 0:
        PARKING_SLOTS[slot]["fine"] += 10
        if slot in cars:
            _, _, _, fine_text = cars[slot]
            canvas.itemconfig(fine_text, text=f"₹{PARKING_SLOTS[slot]['fine']}")

        if PARKING_SLOTS[slot]["fine"] > 0:
            messagebox.showwarning("Overstay Warning", f"Car in Slot {slot} has overstayed! Fine: ₹{PARKING_SLOTS[slot]['fine']}")

        # Reapply fine every 10 seconds if the car hasn't left
        root.after(10000, apply_fine, slot)


# Leave Car and Clean Up Slot
def leave_car(slot):
    PARKING_SLOTS[slot] = {"status": "Available", "timer": None, "fine": 0}
    BOOKED_SLOTS.pop(slot, None)

    if slot in cars:
        for item in cars[slot]:
            if isinstance(item, tk.Button):
                item.destroy()  # Destroy the leave button
            else:
                canvas.delete(item)  # Delete other elements like car, timer text, fine text
        del cars[slot]

    update_parking_lot()
    update_slot_buttons()


# Start the Application
if __name__ == "__main__":
    main_screen_interface()
