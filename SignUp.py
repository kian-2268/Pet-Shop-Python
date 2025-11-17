import tkinter
import tkinter as tk
import tkinter.font as tkFont
from tkinter import messagebox
from tkinter import ttk

import subprocess
import calendar
import mysql.connector
from db import get_connection

from PIL import ImageFont
from PIL.ImageTk import PhotoImage

root = tk.Tk()
root.title("Cuddle Corner")
root.geometry("500x500+500+150")
root.resizable(False, False)
root.configure(background="#E67E22")

#background
img_path = PhotoImage(file = r"C:\Users\user\Pictures\project\signUpBG.png")
bg_img = tkinter.Label(root, image=img_path)
bg_img.pack()

#font
font = r"C:\Users\user\OneDrive\Documents\fonts\beachday.ttf"

try:
    pillow_font = ImageFont.truetype(font, 18)
    name_font = pillow_font.getname()[0]
    custom = tkFont.Font(family=name_font, size=40, weight="bold")
    btn = tkFont.Font(family=name_font, size=20, weight="bold")
except Exception as e:
    print("Could not load custom font")
    custom = ("Arial", 18, "bold")

logo = tk.Label(root, text="Sign Up", bg="#F9FAFB", fg="#2D3436", font=custom)
logo.place(x=170, y=30)

#Email field
email = tk.Label(root, text="Enter email address: ", bg="#F9FAFB", fg="#2D3436", font=("Arial", 10, "bold"))
email.place(x=70, y=120)
email_field = tk.Entry(root, bg="#F9D162", fg="#2D3436", font=("Arial", 10, "bold"))
email_field.place(x=70, y=145, width=350, height=40)

#username
username = tk.Label(root, text="Enter username: ", bg="#F9FAFB", fg="#2D3436", font=("Arial", 10, "bold"))
username.place(x=70, y=190)
username_field = tk.Entry(root, bg="#F9D162", fg="#2D3436", font=("Arial", 10, "bold"))
username_field.place(x=70, y=215, width=350, height=40)

#birthday
birthday = tk.Label(root, text="Enter day of birth: ", bg="#F9FAFB", fg="#2D3436", font=("Arial", 10, "bold"))
birthday.place(x=70, y=260)

#password field
password = tk.Label(root, text="Password: ", bg="#F9FAFB", fg="#2D3436", font=("Arial", 10, "bold"))
password.place(x=70, y=320)
password_field = tk.Entry(root, bg="#F9D162", fg="#2D3436", font=("Arial", 10, "bold"), show="•")
password_field.place(x=70, y=345, width=350, height=40)

#birthday variables
month_var = tk.StringVar()
month_var.set("Month")
day_var = tk.StringVar()
day_var.set("Day")
year_var = tk.StringVar()
year_var.set("Year")

months = list(calendar.month_name)[1:] #jan to dec
years = list(range(1900, 2030))
days_list = []

#year menu
year_menu = ttk.Combobox(root, textvariable=year_var, values=years, state="readonly")
year_menu.place(x=70, y=285, width=110, height=30)

#month menu
month_menu = ttk.Combobox(root, textvariable=month_var, values=months, state="readonly")
month_menu.place(x=200, y=285, width=110, height=30)

#day menu
day_menu = ttk.Combobox(root, textvariable=day_var, values=days_list, state="readonly")
day_menu.place(x=340, y=285, width=80, height=30)

def update_Days(*args):
    if not month_var.get() or not year_var.get() or month_var.get() == "Month" or year_var.get() == "Year":
        return

    month_index = months.index(month_var.get())
    year_index = int(year_var.get())

    #number of days
    num_days = calendar.monthrange(year_index, month_index)[1]

    #comboBox for days
    day_menu["values"] = list(range(1, num_days+1))
    day_menu.set("Day")

month_menu.bind("<<ComboboxSelected>>", update_Days)
year_menu.bind("<<ComboboxSelected>>", update_Days)

def open_User():
    email_val = email_field.get()
    password_val = password_field.get()
    username_val = username_field.get()

    month_val = month_var.get()
    day_val = day_var.get()
    year_val = year_var.get()

    # checks
    if email_val == "" or password_val == "" or username_val == "":
        tkinter.messagebox.showerror("Sign Up Failed", "Please fill all required fields")
        return

    if month_val == "Month" or day_val == "Day" or year_val == "Year":
        tkinter.messagebox.showerror("Sign Up Failed", "Please select your birthday")
        return

    # convert birthday to YYYY-MM-DD format
    month_index = months.index(month_val) + 1
    birthday_f = f"{year_val}-{month_index:02d}-{int(day_val):02d}"

    try:
        # connect using db.py
        conn = get_connection()
        cursor = conn.cursor()

        query = ("INSERT INTO users (email, username, password, birthday, role) "
                 "VALUES (%s, %s, %s, %s, %s)")
        values = (email_val, username_val, password_val, birthday_f, "customer")

        cursor.execute(query, values)
        conn.commit()
        conn.close()

        tk.messagebox.showinfo("Sign Up Successful", "Account created successfully")

        root.withdraw()
        subprocess.Popen(["python", "LogIn.py"])

    except Exception as error:
        tkinter.messagebox.showerror("Database Error", f"Error: {error}")

#signUp Btn
signUp = tk.Button(root, text="Create Account", bg="#5AB9EA", fg="#2D3436", font=btn, relief="flat", command=open_User)
signUp.place(x=120, y=420, width=250, height=40)

root.mainloop()
