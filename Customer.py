import tkinter as tk
import tkinter.font as tkFont
from tkinter import PhotoImage

from PIL import ImageFont, Image, ImageTk

#Admin Window
root = tk.Tk()
root.title("Cuddle Corner")
root.geometry("1200x700+140+60")
root.resizable(False, False)
root.configure(background="#F9FAFB")

#sidebar
sideBar = tk.Frame(root, bg="#F9D162", width=300, height=700)
sideBar.place(relx=0, rely=0)

#sidebar bg
side_path = PhotoImage(file=r"C:\Users\user\Pictures\project\sidebar.png")
bg_img = tk.Label(sideBar, image=side_path)
bg_img.place(x=0, y=0)

#font
font_pth = r"C:\Users\user\OneDrive\Documents\fonts\beachday.ttf"
try:
    pil_font = ImageFont.truetype(font_pth, 18)
    font_name = pil_font.getname()[0]  # Extract the font family name
    custom_font = tkFont.Font(family=font_name, size=23, weight="bold")
    pet_font = tkFont.Font(family=font_name, size=30, weight="bold")
except Exception as e:
    print("Could not load custom font:", e)
    custom_font = ("Arial", 18, "bold")
    pet_font = ("Arial", 12, "bold")

def load_icon(path, size=(30,30)):
    img = Image.open(path)
    img = img.resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(img)

#load all icons
user_icon = load_icon(r"C:\Users\user\Pictures\project\user.png")
pet_icon = load_icon(r"C:\Users\user\Pictures\project\pawprint.png")
product_icon = load_icon(r"C:\Users\user\Pictures\project\file-cabinet.png")
checkOut_icon = load_icon(r"C:\Users\user\Pictures\project\shopping-bag.png")
adoption_icon = load_icon(r"C:\Users\user\Pictures\project\share.png")
order_icon = load_icon(r"C:\Users\user\Pictures\project\order-history.png")
notification_icon = load_icon(r"C:\Users\user\Pictures\project\bell.png")
appointment_icon = load_icon(r"C:\Users\user\Pictures\project\appointment.png")

#section line whatever
line = tk.Frame(sideBar, bg="#F9FAFB", height=2, width=300)
line.place(x=0, y=80)

#user stff_btn
user_btn = tk.Button(sideBar, text="Customer", image=user_icon, compound="left", bg="#F1A842", fg="white",
                      font=("Arial", 12, "bold"), relief="flat", width=150, height=40, padx=10, anchor="w")
user_btn.img = user_icon
user_btn.place(x=40, y=100)

#section line whatever
line2 = tk.Frame(sideBar, bg="#F9FAFB", height=2, width=300)
line2.place(x=0, y=170)

#sidebar buttons
pet_btn = tk.Button(sideBar, text="Browse Pets", image=pet_icon, compound="left", bg="#F9D162", fg="#2D3436",
                      font=("Arial", 12, "bold"), relief="flat", width=180, height=40, padx=10, anchor="w")
pet_btn.img = pet_icon
pet_btn.place(x=40, y=180)

product_btn = tk.Button(sideBar, text="Browse Products", image=product_icon, compound="left", bg="#F9D162", fg="#2D3436",
                          font=("Arial", 12, "bold"), relief="flat", width=180, height=40, padx=10, anchor="w")
product_btn.img = product_icon
product_btn.place(x=40, y=230)

checkOut_btn = tk.Button(sideBar, text="Cart & Checkout", image=checkOut_icon, compound="left", bg="#F9D162", fg="#2D3436",
                      font=("Arial", 12, "bold"), relief="flat", width=180, height=40, padx=10, anchor="w")
checkOut_btn.img = checkOut_icon
checkOut_btn.place(x=40, y=280)

adoption_btn = tk.Button(sideBar, text="Adoption Request", image=adoption_icon, compound="left", bg="#F9D162", fg="#2D3436",
                      font=("Arial", 12, "bold"), relief="flat", width=180, height=40, padx=10, anchor="w")
adoption_btn.img = adoption_icon
adoption_btn.place(x=40, y=330)

order_btn = tk.Button(sideBar, text="Order History", image=order_icon, compound="left", bg="#F9D162", fg="#2D3436",
                      font=("Arial", 12, "bold"), relief="flat", width=180, height=40, padx=10, anchor="w")
order_btn.img = order_icon
order_btn.place(x=40, y=380)

notification_btn = tk.Button(sideBar, text="Notifications", image=notification_icon, compound="left", bg="#F9D162", fg="#2D3436",
                      font=("Arial", 12, "bold"), relief="flat", width=180, height=40, padx=10, anchor="w")
notification_btn.img = notification_icon
notification_btn.place(x=40, y=430)

appointment_btn = tk.Button(sideBar, text="Appointments", image=appointment_icon, compound="left", bg="#F9D162", fg="#2D3436",
                      font=("Arial", 12, "bold"), relief="flat", width=180, height=40, padx=10, anchor="w")
appointment_btn.img = appointment_icon
appointment_btn.place(x=40, y=480)


root.mainloop()
