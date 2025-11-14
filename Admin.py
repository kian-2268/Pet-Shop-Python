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

def load_icon(path, size=(30,30)):
    img = Image.open(path)
    img = img.resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(img)

#load all icons
admin_icon = load_icon(r"C:\Users\user\Pictures\project\user.png")
pet_icon = load_icon(r"C:\Users\user\Pictures\project\pawprint.png")
inventory_icon = load_icon(r"C:\Users\user\Pictures\project\file-cabinet.png")
sales_icon = load_icon(r"C:\Users\user\Pictures\project\sales.png")
adoption_icon = load_icon(r"C:\Users\user\Pictures\project\share.png")
staff_icon = load_icon(r"C:\Users\user\Pictures\project\group.png")
customer_icon = load_icon(r"C:\Users\user\Pictures\project\customer-review.png")
appointment_icon = load_icon(r"C:\Users\user\Pictures\project\appointment.png")
report_icon = load_icon(r"C:\Users\user\Pictures\project\report.png")

#logo
"""
logo_Label = tk.Label(sideBar, text="CUDDLE CORNER", bg="#F9D162", fg="#2D3436", font=custom_font)
logo_Label.place(x=40, y=20)
"""

#section line whatever
line = tk.Frame(sideBar, bg="#F9FAFB", height=2, width=300)
line.place(x=0, y=80)

#admin_btn
admin_btn = tk.Button(sideBar, text="Admin", image=admin_icon, compound="left", bg="#F1A842", fg="white",
                      font=("Arial", 12, "bold"), relief="flat", width=150, height=40, padx=10, anchor="w")
admin_btn.img = admin_icon
admin_btn.place(x=40, y=100)

#section line whatever
line2 = tk.Frame(sideBar, bg="#F9FAFB", height=2, width=300)
line2.place(x=0, y=170)

#sidebar buttons
pet_btn = tk.Button(sideBar, text="Pet Management", image=pet_icon, compound="left", bg="#F9D162", fg="#2D3436",
                      font=("Arial", 12, "bold"), relief="flat", width=180, height=40, padx=10, anchor="w")
pet_btn.img = pet_icon
pet_btn.place(x=40, y=180)

inventory_btn = tk.Button(sideBar, text="Inventory", image=inventory_icon, compound="left", bg="#F9D162", fg="#2D3436",
                          font=("Arial", 12, "bold"), relief="flat", width=180, height=40, padx=10, anchor="w")
inventory_btn.img = inventory_icon
inventory_btn.place(x=40, y=230)

sales_btn = tk.Button(sideBar, text="Sales Management", image=sales_icon, compound="left", bg="#F9D162", fg="#2D3436",
                      font=("Arial", 12, "bold"), relief="flat", width=180, height=40, padx=10, anchor="w")
sales_btn.img = sales_icon
sales_btn.place(x=40, y=280)

adoption_btn = tk.Button(sideBar, text="Adoption", image=adoption_icon, compound="left", bg="#F9D162", fg="#2D3436",
                      font=("Arial", 12, "bold"), relief="flat", width=180, height=40, padx=10, anchor="w")
adoption_btn.img = adoption_icon
adoption_btn.place(x=40, y=330)

staff_btn = tk.Button(sideBar, text="Staff Management", image=staff_icon, compound="left", bg="#F9D162", fg="#2D3436",
                      font=("Arial", 12, "bold"), relief="flat", width=180, height=40, padx=10, anchor="w")
staff_btn.img = staff_icon
staff_btn.place(x=40, y=380)

customer_btn = tk.Button(sideBar, text="Customers", image=customer_icon, compound="left", bg="#F9D162", fg="#2D3436",
                      font=("Arial", 12, "bold"), relief="flat", width=180, height=40, padx=10, anchor="w")
customer_btn.img = customer_icon
customer_btn.place(x=40, y=430)

appointment_btn = tk.Button(sideBar, text="Appointments", image=appointment_icon, compound="left", bg="#F9D162", fg="#2D3436",
                      font=("Arial", 12, "bold"), relief="flat", width=180, height=40, padx=10, anchor="w")
appointment_btn.img = appointment_icon
appointment_btn.place(x=40, y=480)

report_btn = tk.Button(sideBar, text="Reports Analysis", image=report_icon, compound="left", bg="#F9D162", fg="#2D3436",
                      font=("Arial", 12, "bold"), relief="flat", width=180, height=40, padx=10, anchor="w")
report_btn.img = report_icon
report_btn.place(x=40, y=530)

root.mainloop()
