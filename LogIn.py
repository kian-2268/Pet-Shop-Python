import tkinter
import tkinter as tk
import tkinter.font as tkFont
from tkinter import messagebox

import subprocess
import mysql.connector

from PIL import ImageFont
from PIL.ImageTk import PhotoImage

root = tk.Tk()
root.title("Cuddle Corner")
root.geometry("500x500+500+150")
root.resizable(False, False)
root.configure(background="#E67E22")

#background
img_path = PhotoImage(file = r"C:\Users\user\Pictures\project\logInBG.png")
bg_img = tkinter.Label(root, image=img_path)
bg_img.pack()

#font
font = r"C:\Users\user\OneDrive\Documents\fonts\beachday.ttf"

try:
    pillow_font = ImageFont.truetype(font, 18)
    name_font = pillow_font.getname()[0]
    custom = tkFont.Font(family=name_font, size=30, weight="bold")
    btn = tkFont.Font(family=name_font, size=20, weight="bold")
except Exception as e:
    print("Could not load custom font")
    custom = ("Arial", 18, "bold")
    btn = ("Arial", 18, "bold")

"""logo = tk.Label(root, text="CUDDLE CORNER", bg="#E67E22", fg="#2D3436", font=custom)
logo.place(x=100, y=50)

sub = tk.Label(root, text="The Happiest Corner for Every Paw!", bg="#E67E22", fg="#2D3436",
               font=("Arial", 12, "bold"))
sub.place(x=95, y=90)"""

#see password
def toggle_password():
    if password_field.cget('show') == '':
        #hide password
        password_field.config(show='•')
        toggle_button.config(text='Show')
    else:
        #show password
        password_field.config(show='')
        toggle_button.config(text='Hide')

#Email field
email = tk.Label(root, text="Email Address: ", bg="#E67E22", fg="#2D3436", font=("Arial", 12, "bold"))
email.place(x=70, y=170)
email_field = tk.Entry(root, bg="#F9D162", fg="#2D3436", font=("Arial", 12, "bold"))
email_field.place(x=70, y=200, width=350, height=40)

#password field
password = tk.Label(root, text="Password: ", bg="#E67E22", fg="#2D3436", font=("Arial", 12, "bold"))
password.place(x=70, y=260)
password_field = tk.Entry(root, bg="#F9D162", fg="#2D3436", font=("Arial", 12, "bold"), show="•")
password_field.place(x=70, y=290, width=350, height=40)

#see password button
toggle_button = tk.Button(root, text="Show", bg="#E67E22", fg="#2D3436", bd=0, command=toggle_password)
toggle_button.place(x=380, y=335)

signUp = tk.Label(root, text="Didn't have an account?", bg="#E67E22", fg="#2D3436",
                      font=("Arial", 10, "bold"))
signUp.place(x=135, y=445)

def open_MDB():
    email_val = email_field.get()
    password_val = password_field.get()

    #checks email and password field
    if email_val == "" or password_val == "":
        tkinter.messagebox.showerror("Log In Failed", "Email or password is required")
        return

    try:
        # connecting to database
        conn = mysql.connector.connect(host="localhost", user="root", password="",
                                       database="cuddle_corner")
        cursor = conn.cursor()

        #verify roles
        query = ("SELECT role FROM users WHERE email = %s and password = %s")
        cursor.execute(query, (email_val, password_val))
        result = cursor.fetchone()

        conn.close()

        if result:
            role = result[0] #admin, staff, customer
            root.withdraw()

            #redirect panels based on roles
            if role == "admin":
                subprocess.Popen(["python", "Admin.py"])
            elif role == "staff":
                subprocess.Popen(["python", "Staff.py"])
            else:
                subprocess.Popen(["python", "Customer.py"])
        else:
            tkinter.messagebox.showerror("Log In Failed", "Email or password is required")

    except mysql.connector.Error as error:
        tkinter.messagebox.showerror("Database Error", f"Error: {error}")

def open_SignUp():
    root.withdraw()
    subprocess.Popen(["python", "SignUp.py"])

#logIn Btn
logIn = tk.Button(root, text="LOG IN", bg="#5AB9EA", fg="#F9FAFB", font=btn, relief="flat", command=open_MDB)
logIn.place(x=120, y=400, width=250, height=40)

signUp_btn = tk.Button(root, text="S̲i̲gn̲ ̲U̲p̲", bg="#E67E22", fg="#2D3436",
                       font=("Arial", 10, "bold"), bd=0, relief="flat", command=open_SignUp)
signUp_btn.place(x=298, y=441, width=50, height=30)


root.mainloop()
