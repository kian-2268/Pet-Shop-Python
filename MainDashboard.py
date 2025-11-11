import tkinter as tk
from tkinter import messagebox
from tkinter import PhotoImage
from PIL import Image, ImageTk, ImageDraw

#main window
root = tk.Tk()
root.title("Cuddle Corner")
root.geometry("1200x700+140+60")
root.resizable(False, False)
root.configure(background="#F9FAFB")

#sidebar
sideBar = tk.Frame(root, bg="#F9D162", width=300, height=700)
sideBar.place(relx=0, rely=0)

#logo
logo_Label = tk.Label(sideBar, text="CUDDLE CORNER", bg="#F9D162", fg="#2D3436", font=("Comic Sans MS", 18, "bold"))
logo_Label.place(x=40, y=20)

#section line whatever
line = tk.Frame(sideBar, bg="#F9FAFB", height=2, width=300)
line.place(x=0, y=80)

#logIn_btn
logIn_btn = tk.Button(sideBar, text="Log In or \nSign Up", bg="#E67E22", fg="white",
                      font=("Arial", 12, "bold"), relief="flat", width=20, height=2)
logIn_btn.place(x=40, y=100)

#section line whatever
line2 = tk.Frame(sideBar, bg="#F9FAFB", height=2, width=300)
line2.place(x=0, y=170)

#buttons in the sidebar
overview_btn = tk.Button(sideBar, text="Overview", bg="#F9D162", fg="#2D3436",
                      font=("Arial", 12, "bold"), relief="flat", width=20, height=2)
overview_btn.place(x=40, y=180)

pets_btn = tk.Button(sideBar, text="Pets", bg="#F9D162", fg="#2D3436",
                      font=("Arial", 12, "bold"), relief="flat", width=20, height=2)
pets_btn.place(x=40, y=230)

products_btn = tk.Button(sideBar, text="Pets", bg="#F9D162", fg="#2D3436",
                      font=("Arial", 12, "bold"), relief="flat", width=20, height=2)
products_btn.place(x=40, y=280)

#header
header = tk.Frame(root, bg="#E67E22", height=150, width=950)
header.place(x=400, y=70)

lbl = tk.Label(header, text="Welcome to Cuddle Corner!", bg="#E67E22", fg="#F9FAFB", font=("Arial", 35, "bold"))
lbl.place(x=40, y=25)

sub_lbl = tk.Label(header, text="The Happiest Corner for Every Paw!", bg="#E67E22", fg="#F9FAFB",
                   font=("Arial", 15, "bold"))
sub_lbl.place(x=40, y=80)

#content overview
content = tk.Frame(root, bg="#5BB8E9", height=150, width=950)
content.place(x=300, y=300)

#grabe kaau ang error!! How to make a circular frame!!!

pet = tk.Label(content, text="Meet MingMing!", bg="#5BB8E9",
                    fg="#2D3436", font=("Comic Sans MS", 24, "bold"))
pet.place(x=400, y=10)

pet2 = tk.Label(content, text="Say hello to Mingming! This loving furball is"
                              "\nwaiting for a family to call her own. 🐾",
                    bg="#5BB8E9",fg="#2D3436", font=("Comic Sans MS", 10, "bold"))
pet2.place(x=400, y=60)

#buttons in overview
prod_btn = tk.Button(root, text="PET PRODUCTS AVAILABLE HERE! →", bg="#5BB8E9", fg="#2D3436",
                     font=("Arial", 12, "bold"), relief="flat", width=40, height=2)
prod_btn.place(x=800, y=500)

appoint_btn = tk.Button(root, text="NEED APPOINTMENTS? CLICK HERE! →", bg="#5BB8E9", fg="#2D3436",
                     font=("Arial", 12, "bold"), relief="flat", width=40, height=2)
appoint_btn.place(x=800, y=570)

root.mainloop()