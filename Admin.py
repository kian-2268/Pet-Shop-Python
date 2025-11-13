import tkinter
import tkinter as tk
import tkinter.font as tkFont

from PIL import ImageFont

#Admin Window
root = tk.Tk()
root.title("Cuddle Corner")
root.geometry("1200x700+140+60")
root.resizable(False, False)
root.configure(background="#F9FAFB")

#sidebar
sideBar = tk.Frame(root, bg="#F9D162", width=300, height=700)
sideBar.place(relx=0, rely=0)

#font
font_pth = r"C:\Users\user\OneDrive\Documents\fonts\beachday.ttf"
try:
    pil_font = ImageFont.truetype(font_pth, 18)
    font_name = pil_font.getname()[0]  # Extract the font family name
    custom_font = tkFont.Font(family=font_name, size=23, weight="bold")
    pet_font = tkFont.Font(family=font_name, size=30, weight="bold")
except Exception as e:
    print("⚠️ Could not load custom font:", e)
    custom_font = ("Comic Sans MS", 18, "bold")

#logo
logo_Label = tk.Label(sideBar, text="CUDDLE CORNER", bg="#F9D162", fg="#2D3436", font=custom_font)
logo_Label.place(x=40, y=20)

#section line whatever
line = tk.Frame(sideBar, bg="#F9FAFB", height=2, width=300)
line.place(x=0, y=80)

#logIn_btn
logIn_btn = tk.Button(sideBar, text="Admin", bg="#E67E22", fg="white",
                      font=("Arial", 12, "bold"), relief="flat", width=20, height=2)
logIn_btn.place(x=40, y=100)

#section line whatever
line2 = tk.Frame(sideBar, bg="#F9FAFB", height=2, width=300)
line2.place(x=0, y=170)

#sidebar buttons
pet_btn = tk.Button(sideBar, text="Pet Management", bg="#F9D162", fg="#2D3436",
                      font=("Arial", 12, "bold"), relief="flat", width=20, height=2)
pet_btn.place(x=40, y=180)

inventory_btn = tk.Button(sideBar, text="Inventory Management", bg="#F9D162", fg="#2D3436",
                          font=("Arial", 12, "bold"), relief="flat", width=20, height=2)
inventory_btn.place(x=40, y=230)

sales_btn = tk.Button(sideBar, text="Sales Management", bg="#F9D162", fg="#2D3436",
                      font=("Arial", 12, "bold"), relief="flat", width=20, height=2)
sales_btn.place(x=40, y=280)

adoption_btn = tk.Button(sideBar, text="Adoption Management", bg="#F9D162", fg="#2D3436",
                      font=("Arial", 12, "bold"), relief="flat", width=20, height=2)
adoption_btn.place(x=40, y=330)

staff_btn = tk.Button(sideBar, text="Staff Management", bg="#F9D162", fg="#2D3436",
                      font=("Arial", 12, "bold"), relief="flat", width=20, height=2)
staff_btn.place(x=40, y=380)

customer_btn = tk.Button(sideBar, text="Customer Management", bg="#F9D162", fg="#2D3436",
                      font=("Arial", 12, "bold"), relief="flat", width=20, height=2)
customer_btn.place(x=40, y=430)

appointment_btn = tk.Button(sideBar, text="Appointment Scheduling", bg="#F9D162", fg="#2D3436",
                      font=("Arial", 12, "bold"), relief="flat", width=20, height=2)
appointment_btn.place(x=40, y=480)

report_btn = tk.Button(sideBar, text="Reports And Analytics", bg="#F9D162", fg="#2D3436",
                      font=("Arial", 12, "bold"), relief="flat", width=20, height=2)
report_btn.place(x=40, y=530)

root.mainloop()
