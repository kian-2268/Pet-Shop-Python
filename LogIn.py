import tkinter
import tkinter as tk
import tkinter.font as tkFont
from tkinter import messagebox

import subprocess

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
toggle_button = tk.Button(root, text="Show", command=toggle_password)
toggle_button.place(x=380, y=335)

def open_MDB():
    email_val = email_field.get()
    password_val = password_field.get()

    #checks email and password field
    if email_val == "" or password_val == "":
        tkinter.messagebox.showerror("Log In Failed", "Email or password is required")
        return

    #temp
    if email_val == "admin" or password_val == "1234":
        root.withdraw() #hides window
        subprocess.Popen(["python", "Admin.py"]) #open admin (temp)
    else:
        tkinter.messagebox.showerror("Log In Failed", "Invalid email or password")

#logIn Btn
logIn = tk.Button(root, text="LOG IN", bg="#5AB9EA", fg="#F9FAFB", font=btn, relief="flat", command=open_MDB)
logIn.place(x=120, y=400, width=250, height=40)

root.mainloop()
