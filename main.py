import tkinter as tk
from tkinter import messagebox, ttk
import pygame
import qrcode
from PIL import Image, ImageTk
import random

# Global variables
PARKING_SLOTS = {i: "Available" for i in range(1, 7)}  # 6 slots (1-6), initially available
BOOKINGS = []  # (not used in this version; booking status is stored in PARKING_SLOTS)

# Initialize Pygame
pygame.init()


# ----------------------------------- MAIN INTERFACE -----------------------------------
def main_interface():
    global root
    root = tk.Tk()
    root.title("Futuristic Parking System")
    root.geometry("800x500")
    root.configure(bg="#0A0A0A")

    title = tk.Label(root, text="🚗 Smart Parking Hub 🚀", font=("Arial", 22, "bold"), bg="#0A0A0A", fg="white")
    title.pack(pady=20)

    # On hovering, change button color
    def on_enter(e):
        e.widget.config(bg="#0056b3")

    def on_leave(e):
        e.widget.config(bg="#007BFF")

    btn_booking = tk.Button(root, text="🅿️ Book a Slot", font=("Arial", 16), command=booking_interface,
                            width=20, height=2, bg="#007BFF", fg="white", relief="flat")
    btn_booking.pack(pady=10)
    btn_booking.bind("<Enter>", on_enter)
    btn_booking.bind("<Leave>", on_leave)

    # (Simulation interface button removed to directly open booking UI)

    root.mainloop()


# ----------------------------------- BOOKING INTERFACE -----------------------------------
def booking_interface():
    # Destroy main interface and open booking window
    root.destroy()
    global booking_root
    booking_root = tk.Tk()
    booking_root.title("🚗 Parking Slot Booking")
    booking_root.geometry("800x600")
    booking_root.configure(bg="#1A1A1A")

    # Data Entry Section
    tk.Label(booking_root, text="📌 Enter Your Details", font=("Arial", 18, "bold"), bg="#1A1A1A", fg="white").pack(
        pady=10)

    tk.Label(booking_root, text="👤 Enter Your Name:", font=("Arial", 12), bg="#1A1A1A", fg="white").pack(pady=5)
    name_entry = tk.Entry(booking_root, font=("Arial", 12))
    name_entry.pack(pady=5)

    tk.Label(booking_root, text="⏰ Select Start Time (12-hour format):", font=("Arial", 12), bg="#1A1A1A",
             fg="white").pack(pady=5)
    time_frame = tk.Frame(booking_root, bg="#1A1A1A")
    time_frame.pack(pady=5)

    hour_var = tk.StringVar()
    minute_var = tk.StringVar()
    am_pm_var = tk.StringVar(value="AM")

    hours = [str(i).zfill(2) for i in range(1, 13)]
    minutes = [str(i).zfill(2) for i in range(0, 60, 5)]

    hour_dropdown = ttk.Combobox(time_frame, values=hours, textvariable=hour_var, width=5, font=("Arial", 12))
    minute_dropdown = ttk.Combobox(time_frame, values=minutes, textvariable=minute_var, width=5, font=("Arial", 12))
    am_pm_dropdown = ttk.Combobox(time_frame, values=["AM", "PM"], textvariable=am_pm_var, width=5, font=("Arial", 12))

    hour_dropdown.grid(row=0, column=0, padx=5)
    tk.Label(time_frame, text=":", font=("Arial", 12), bg="#1A1A1A", fg="white").grid(row=0, column=1)
    minute_dropdown.grid(row=0, column=2, padx=5)
    am_pm_dropdown.grid(row=0, column=3, padx=5)

    tk.Label(booking_root, text="📏 Enter Duration (Hours):", font=("Arial", 12), bg="#1A1A1A", fg="white").pack(pady=5)
    duration_entry = tk.Entry(booking_root, font=("Arial", 12))
    duration_entry.pack(pady=5)

    # ----------------- Destination Selection -----------------
    tk.Label(booking_root, text="📍 Select Destination:", font=("Arial", 12), bg="#1A1A1A", fg="white").pack(pady=5)
    destination_values = ["Brookfield Mall", "Prozone Mall", "Funmall", "City Centre", "Plaza Mall"]
    destination_combo = ttk.Combobox(booking_root, values=destination_values, font=("Arial", 12))
    destination_combo.set(destination_values[0])
    destination_combo.pack(pady=5)

    # ----------------- Slot Selection (3x2 Grid) -----------------
    tk.Label(booking_root, text="🅿️ Select Your Parking Slot", font=("Arial", 18, "bold"), bg="#1A1A1A",
             fg="white").pack(pady=10)
    slot_frame = tk.Frame(booking_root, bg="#1A1A1A")
    slot_frame.pack(pady=10)

    global selected_slot
    selected_slot = tk.IntVar()

    def select_slot(slot):
        if PARKING_SLOTS[slot] == "Booked":
            messagebox.showerror("Error", "Slot already booked!")
            return
        selected_slot.set(slot)

    for i in range(1, 7):
        color = "red" if PARKING_SLOTS[i] == "Booked" else "green"
        btn = tk.Button(slot_frame, text=f"Slot {i}", font=("Arial", 14, "bold"), width=10, height=2, bg=color,
                        fg="white", command=lambda s=i: select_slot(s))
        btn.grid(row=(i - 1) // 3, column=(i - 1) % 3, padx=10, pady=10)

    def generate_ticket():
        name = name_entry.get()
        slot = selected_slot.get()
        hour = hour_var.get()
        minute = minute_var.get()
        am_pm = am_pm_var.get()
        duration = duration_entry.get()
        destination = destination_combo.get().strip()

        if not (name and slot and hour and minute and am_pm and duration.isdigit() and destination):
            messagebox.showerror("Error", "Please enter valid details!")
            return

        duration = int(duration)
        start_time = f"{hour}:{minute} {am_pm}"
        ticket_id = random.randint(1000, 9999)

        PARKING_SLOTS[slot] = "Booked"

        qr_data = f"Name: {name}\nTime: {start_time}\nSlot: {slot}\nDuration: {duration} hrs\nTicket ID: {ticket_id}\nDestination: {destination}"

        qr = qrcode.make(qr_data)
        qr.save("qr_ticket.png")

        ticket_window = tk.Toplevel(booking_root)
        ticket_window.title("🎟️ Your Parking Ticket")
        ticket_window.geometry("400x400")

        tk.Label(ticket_window, text="🚗 Parking Ticket 🎟️", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(ticket_window,
                 text=f"👤 Name: {name}\n⏰ Time: {start_time}\n🅿️ Slot: {slot}\n⌛ Duration: {duration} hrs\n"
                      f"🎟️ Ticket ID: {ticket_id}\n📍 Destination: {destination}",
                 font=("Arial", 12)).pack(pady=10)

        qr_img = Image.open("qr_ticket.png")
        qr_img = qr_img.resize((150, 150))
        qr_img = ImageTk.PhotoImage(qr_img)

        qr_label = tk.Label(ticket_window, image=qr_img)
        qr_label.image = qr_img
        qr_label.pack(pady=10)

    tk.Button(booking_root, text="📥 Book Now", font=("Arial", 14, "bold"), command=generate_ticket,
              bg="#007BFF", fg="white", relief="flat").pack(pady=20)

    booking_root.mainloop()


# ----------------------------------- SIMULATION INTERFACE -----------------------------------
def simulation_interface():
    # For this version, we open the booking UI directly.
    booking_interface()


# Start the app
main_interface()
