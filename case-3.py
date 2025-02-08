import tkinter as tk
from tkinter import messagebox
import datetime

###############################################################################
# GLOBAL VARIABLES
###############################################################################
# PARKING_SLOTS stores bookings for each slot as a list of tuples:
# (start_time, end_time, name, duration_in_seconds)
PARKING_SLOTS = {i: [] for i in range(1, 7)}
# Predefined positions for each slot in the parking lot view
slot_positions = {
    1: (100, 100),
    2: (250, 100),
    3: (400, 100),
    4: (100, 300),
    5: (250, 300),
    6: (400, 300)
}
# Dictionary for visual elements in the parking lot view:
# {slot: (timer_label_widget, leave_button_widget)}
cars = {}
# Buttons in the booking interface for each slot
slot_buttons = {}
# Running timers for active bookings (in seconds)
running_timers = {}
# Fine amounts (in INR) for each slot
fines = {}
# Notification flags for warning when 10 seconds remain
notifications = {}
# Flags to ensure that continuous fine is applied repeatedly after time expires
fines_applied = {}
# Ticket generation counter
ticket_number = 1001

###############################################################################
# TKINTER WINDOW REFERENCES
###############################################################################
root = None
booking_root = None
parking_root = None
canvas = None
selected_slot = None


###############################################################################
# UTILITY FUNCTIONS
###############################################################################
def get_free_slot():
    """Return the first free slot (i.e. with no bookings) or None if none available."""
    for i in range(1, 7):
        if not PARKING_SLOTS[i]:
            return i
    return None


def reassign_waiting_booking(slot):
    """
    If there is a waiting booking (i.e. more than one booking) for the given slot
    and the active booking's timer has reached 0 (i.e. the car hasn't left),
    then attempt to reassign the waiting booking to a free slot.
    Returns True if reassignment happened, False otherwise.
    """
    if len(PARKING_SLOTS[slot]) < 2:
        return False  # No waiting booking exists.
    waiting_booking = PARKING_SLOTS[slot][1]  # Second booking is waiting.
    free_slot = get_free_slot()
    if free_slot is not None:
        PARKING_SLOTS[slot].pop(1)
        PARKING_SLOTS[free_slot].append(waiting_booking)
        running_timers[free_slot] = waiting_booking[3]  # Set timer from the booking tuple.
        fines[free_slot] = 0
        notifications[free_slot] = False
        fines_applied[free_slot] = False
        messagebox.showinfo("Slot Reallocated",
                            f"Your booking has been reallocated to slot {free_slot} as slot {slot} is still occupied.")
        countdown(free_slot)
        update_slot_buttons()
        update_parking_lot()
        return True
    else:
        return False


###############################################################################
# MAIN SCREEN INTERFACE
###############################################################################
def main_screen_interface():
    global root
    root = tk.Tk()
    root.title("Smart Parking System")
    root.geometry("800x500")
    root.configure(bg="#0A0A0A")

    tk.Label(root, text="🚗 Smart Parking System", font=("Arial", 22, "bold"),
             bg="#0A0A0A", fg="white").pack(pady=20)

    tk.Button(root, text="🅿️ Book a Slot", font=("Arial", 16), command=booking_interface,
              width=20, height=2, bg="#007BFF", fg="white").pack(pady=10)

    tk.Button(root, text="🅿️ Open Parking Lot", font=("Arial", 16), command=parking_lot_interface,
              width=20, height=2, bg="#FF5733", fg="white").pack(pady=10)

    root.mainloop()


###############################################################################
# UPDATE SLOT BUTTONS (BOOKING INTERFACE)
###############################################################################
def update_slot_buttons():
    for i in range(1, 7):
        if i in slot_buttons:
            slot_buttons[i].destroy()
        color = "red" if PARKING_SLOTS[i] else "green"
        state = "disabled" if color == "red" else "normal"
        btn = tk.Button(booking_root, text=f"Slot {i}", font=("Arial", 14, "bold"),
                        width=10, height=2, bg=color, fg="white",
                        command=lambda s=i: selected_slot.set(s), state=state)
        btn.pack(pady=5)
        slot_buttons[i] = btn


###############################################################################
# BOOKING INTERFACE
###############################################################################
def booking_interface():
    global booking_root, selected_slot
    booking_root = tk.Toplevel(root)
    booking_root.title("🚗 Parking Slot Booking")
    booking_root.geometry("800x600")
    booking_root.configure(bg="#1A1A1A")

    selected_slot = tk.IntVar()

    tk.Label(booking_root, text="📌 Enter Your Details", font=("Arial", 18, "bold"),
             bg="#1A1A1A", fg="white").pack(pady=10)
    tk.Label(booking_root, text="👤 Name:", font=("Arial", 12), bg="#1A1A1A", fg="white").pack(pady=5)
    name_entry = tk.Entry(booking_root, font=("Arial", 12))
    name_entry.pack(pady=5)
    tk.Label(booking_root, text="🕒 Start Time (HH:MM):", font=("Arial", 12), bg="#1A1A1A", fg="white").pack(pady=5)
    start_time_entry = tk.Entry(booking_root, font=("Arial", 12))
    start_time_entry.pack(pady=5)
    tk.Label(booking_root, text="⌛ Duration (Minutes):", font=("Arial", 12), bg="#1A1A1A", fg="white").pack(pady=5)
    duration_entry = tk.Entry(booking_root, font=("Arial", 12))
    duration_entry.pack(pady=5)
    tk.Label(booking_root, text="🅿️ Select Slot:", font=("Arial", 18, "bold"),
             bg="#1A1A1A", fg="white").pack(pady=10)

    update_slot_buttons()

    def check_availability(slot, start_time, end_time):
        for (existing_start, existing_end, _, _) in PARKING_SLOTS[slot]:
            if start_time < existing_end and end_time > existing_start:
                return False
        return True

    def generate_ticket():
        global ticket_number
        name = name_entry.get()
        slot = selected_slot.get()
        start_time_str = start_time_entry.get()
        duration_str = duration_entry.get()

        if not (name and slot and start_time_str and duration_str.isdigit()):
            messagebox.showerror("Error", "Please enter valid details!")
            return

        try:
            start_time = datetime.datetime.strptime(start_time_str, "%H:%M").time()
            duration = int(duration_str)
            end_time = (datetime.datetime.combine(datetime.date.today(), start_time) +
                        datetime.timedelta(minutes=duration)).time()
        except ValueError:
            messagebox.showerror("Error", "Invalid time format! Use HH:MM.")
            return

        if not check_availability(slot, start_time, end_time):
            messagebox.showerror("Error",
                                 f"Slot {slot} is already booked for this time. Please choose another time or slot.")
            return

        # Book the slot: append the booking details.
        PARKING_SLOTS[slot].append((start_time, end_time, name, duration * 60))
        running_timers[slot] = duration * 60  # Set timer in seconds
        fines[slot] = 0
        notifications[slot] = False
        fines_applied[slot] = False
        update_slot_buttons()
        update_parking_lot()
        countdown(slot)

        ticket_number += 1
        messagebox.showinfo("Ticket Generated",
                            f"Ticket Number: {ticket_number - 1}\nCar Details:\nName: {name}\nSlot: {slot}\nTime: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")

    tk.Button(booking_root, text="📥 Book Now", font=("Arial", 14, "bold"),
              command=generate_ticket, bg="#007BFF", fg="white").pack(pady=20)


###############################################################################
# PARKING LOT INTERFACE
###############################################################################
def parking_lot_interface():
    global parking_root, canvas
    parking_root = tk.Toplevel(root)
    parking_root.title("🅿️ Virtual Parking Lot")
    parking_root.geometry("800x600")
    parking_root.configure(bg="#2F2F2F")

    canvas = tk.Canvas(parking_root, width=800, height=500, bg="black")
    canvas.pack()
    update_parking_lot()


###############################################################################
# UPDATE PARKING LOT VIEW
###############################################################################
def update_parking_lot():
    if not canvas:
        return
    canvas.delete("all")
    for i in range(1, 7):
        x, y = slot_positions[i]
        color = "red" if PARKING_SLOTS[i] else "green"
        canvas.create_rectangle(x, y, x + 100, y + 150, fill=color, outline="white", width=3)
        canvas.create_text(x + 50, y + 20, text=f"Slot {i}", fill="white", font=("Arial", 12, "bold"))
        # If a running timer exists, display countdown and yellow car indicator, plus a leave button.
        if i in running_timers:
            remaining = running_timers[i]
            minutes, seconds = divmod(remaining, 60)
            timer_message = f"{minutes:02}:{seconds:02}"
            canvas.create_text(x + 50, y + 5, text=timer_message, fill="white", font=("Arial", 10, "bold"))
            canvas.create_rectangle(x + 25, y + 40, x + 75, y + 100, fill="yellow", outline="black")
            leave_btn = tk.Button(parking_root, text="Leave", font=("Arial", 12, "bold"),
                                  bg="#FF5733", fg="white", command=lambda s=i: leave_car(s))
            canvas.create_window(x + 50, y + 120, window=leave_btn)
        # Display the total fine at the bottom of the slot.
        fine_amount = fines.get(i, 0)
        canvas.create_text(x + 50, y + 140, text=f"Fine: ₹{fine_amount}", fill="white", font=("Arial", 10, "bold"))
    parking_root.update_idletasks()


###############################################################################
# COUNTDOWN TIMER & CONTINUOUS FINE LOGIC
###############################################################################
def countdown(slot):
    if slot in running_timers and running_timers[slot] > 0:
        running_timers[slot] -= 1
        update_parking_lot()
        if running_timers[slot] == 10 and not notifications.get(slot, False):
            messagebox.showwarning("Time Running Out", f"Only 10 seconds remaining for the car in slot {slot}.")
            notifications[slot] = True
        root.after(1000, countdown, slot)
    elif running_timers.get(slot, 0) == 0:
        # Timer expired: if a waiting booking exists, try to reassign.
        if len(PARKING_SLOTS[slot]) > 1:
            if reassign_waiting_booking(slot):
                messagebox.showinfo("Slot Reallocation",
                                    f"A waiting booking for slot {slot} has been reallocated to another available slot.")
        if not fines_applied.get(slot, False):
            messagebox.showwarning("Time's Up!", f"Time for car in slot {slot} has run out! Please move your car.")
            fines_applied[slot] = True
        apply_fine_continuous(slot)


def apply_fine_continuous(slot):
    if slot in running_timers and running_timers[slot] == 0:
        fines[slot] = fines.get(slot, 0) + 10
        messagebox.showinfo("Fine Applied",
                            f"A fine of ₹10 has been applied to the car in slot {slot}. Total fine: ₹{fines[slot]}")
        root.after(10000, apply_fine_continuous, slot)


###############################################################################
# CAR LEAVE FUNCTION
###############################################################################
def leave_car(slot):
    if slot in PARKING_SLOTS and PARKING_SLOTS[slot]:
        PARKING_SLOTS[slot].pop(0)
    running_timers.pop(slot, None)
    fines.pop(slot, None)
    notifications.pop(slot, None)
    fines_applied.pop(slot, None)
    update_parking_lot()
    update_slot_buttons()
    messagebox.showinfo("Car Left", f"Car in slot {slot} has been removed.")


###############################################################################
# START THE APPLICATION
###############################################################################
if __name__ == "__main__":
    main_screen_interface()