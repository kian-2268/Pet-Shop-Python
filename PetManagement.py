import tkinter
import tkinter as tk
from tkcalendar import DateEntry
from tkinter import messagebox
from tkinter import ttk
from datetime import date as dt
from tkinter import filedialog

import mysql.connector
from db import get_connection
from PIL import ImageTk, Image


def load_pet_management(parent, current_user):

    # stack the frames
    pet_management_frame = tk.Frame(parent, bg="#F9FAFB")
    pet_logs_frame = tk.Frame(parent, bg="#5AB9EA")
    add_pets_frame = tk.Frame(parent, bg="#F9D162")
    edit_pets_frame = tk.Frame(parent, bg="#F9D162")

    pet_management_frame.place(relwidth=1, relheight=1)
    pet_logs_frame.place(x=100, y=50, width=700, height=600)
    add_pets_frame.place(x=100, y=50, width=700, height=600)
    edit_pets_frame.place(x=100, y=50, width=700, height=600)

    #icons
    def load_icon(path, size=(24, 24)):
        img = Image.open(path)
        img = img.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)

    logs_icon = load_icon(r"C:\\Users\\user\\Pictures\\project\\files.png")
    add_icon = load_icon(r"C:\\Users\\user\\Pictures\\project\\plus.png")

    # Load data from MySQL
    def data():
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, breed, age, status FROM pets")
            rows = cursor.fetchall()
            conn.close()
            return rows
        except mysql.connector.Error as error:
            tkinter.messagebox.showerror("Database Error", f"Error: {error}")
            return []

    # UI
    title_label = tk.Label(
        pet_management_frame, text="Pet Management",
        bg="#F9FAFB", fg="#2D3436", font=("Arial", 20, "bold"))
    title_label.place(x=50, y=20)

    # Add Pet button
    add_btn = tk.Button(pet_management_frame, text="Add Pet", image=add_icon, bg="#5AB9EA",
                        fg="black", font=("Arial", 12, "bold"), relief="flat", width=110, height=35, padx=10,
                        anchor="w", compound="left")
    add_btn.config(command=lambda: [add_pets_frame.lift(), pet_logs_frame.lower()])
    add_btn.image = add_icon
    add_btn.place(x=700, y=80)

    # Pet Logs button → lift the logs frame
    petLogs_btn = tk.Button(pet_management_frame, text="Pet Logs", image=logs_icon, bg="#F9D162",
                            fg="black", font=("Arial", 10, "bold"), relief="flat", width=120,
                            height=35, padx=10, anchor="w", compound="left")
    petLogs_btn.config(command=lambda: [pet_logs_frame.lift(), add_pets_frame.lower(), load_all_logs()])
    petLogs_btn.image = logs_icon
    petLogs_btn.place(x=540, y=80)

    # search bar
    search = tk.Label(pet_management_frame, text="Search Pet",bg="#F9FAFB", fg="#2D3436", font=("Arial", 10, "bold"))
    search.place(x=50, y=150)

    search_entry = tk.Entry(pet_management_frame, bg="#F9FAFB", fg="#2D3436", font=("Arial", 10, "bold"))
    search_entry.place(x=50, y=170, width=400, height=30)

    #search pets
    def search_pets(keyword):
        """Search pets by id, name, breed, type, age, status"""
        keyword=f"%{keyword}%"

        try:
            conn = get_connection()
            cursor = conn.cursor()
            query = """SELECT id, name, breed, age, status FROM pets WHERE id LIKE %s OR name LIKE %s
                    OR breed LIKE %s OR age LIKE %s OR status LIKE %s OR type LIKE %s"""
            cursor.execute(query, (keyword, keyword, keyword, keyword, keyword, keyword))
            results = cursor.fetchall()
            conn.close()
            return results
        except mysql.connector.Error as error:
            tkinter.messagebox.showerror("Error", f"Error: {error}")
            return[]

    #enter-key event
    def on_search(event):
        keyword=search_entry.get().strip()
        pet_table.delete(*pet_table.get_children())
        if keyword:
            pets = search_pets(keyword)
            if not pets:
                tkinter.messagebox.showwarning("No Data", "No data found")
                return
        else:
            pets = data()

        for pet in pets:
            pet_table.insert("", "end", values=pet)

    search_entry.bind("<KeyRelease>", on_search)

    # Sort dropdown
    pet_sort = tk.Label( pet_management_frame, text="Sort Pets", bg="#F9FAFB", fg="#2D3436", font=("Arial", 10, "bold"))
    pet_sort.place(x=480, y=150)

    sort_options = ["All", "For Adoption", "Rescued"]
    dropdown = ttk.Combobox(
        pet_management_frame, values=sort_options,
        state="readonly", font=("Arial", 10, "bold"))
    dropdown.current(0)
    dropdown.place(x=480, y=170, width=150, height=30)

    #sort functionality
    def sort_table(status_filter):
        pet_table.delete(*pet_table.get_children())

        try:
            conn = get_connection()
            cursor = conn.cursor()

            if status_filter == "All":
                cursor.execute("SELECT id, name, breed, age, status FROM pets ORDER BY id DESC")
            else:
                cursor.execute("SELECT id, name, breed, age, status FROM pets WHERE status=%s ORDER BY id DESC",
                               (status_filter,))
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                tkinter.messagebox.showwarning("No Data", "No data found")

            for row in rows:
                pet_table.insert("", "end", values=row)

        except mysql.connector.Error as error:
            tkinter.messagebox.showerror("Database Error", f"Error: {error}")

    #bind comboBox
    def on_sort(event):
        status_selected = dropdown.get()
        sort_table(status_selected)

    dropdown.bind("<<ComboboxSelected>>", on_sort)

    # Table
    table = tk.Frame(pet_management_frame, bg="#F9FAFB")
    table.place(x=50, y=230, width=800, height=350)

    columns = ("ID", "Name", "Breed", "Age", "Status")
    pet_table = ttk.Treeview(table, columns=columns, show="headings", height=12)

    # headings
    for col in columns:
        pet_table.heading(col, text=col)
        pet_table.column(col, width=120, anchor="center")

    pet_table.pack(fill="both", expand=True)

    # Pagination Variables
    page_size = 20  # number of rows per page
    current_page = 1
    all_pets = data()  # full dataset
    total_pages = max(1, (len(all_pets) + page_size - 1) // page_size)

    # Function to display a page
    def display_page(page_num):
        nonlocal current_page, total_pages, all_pets

        current_page = page_num
        pet_table.delete(*pet_table.get_children())

        start_index = (page_num - 1) * page_size
        end_index = start_index + page_size
        page_data = all_pets[start_index:end_index]

        for pet in page_data:
            pet_table.insert("", "end", values=pet)

        # update page label
        page_label.config(text=f"Page {current_page} of {total_pages}")

    # Previous page
    def prev_page():
        if current_page > 1:
            display_page(current_page - 1)

    # Next page
    def next_page():
        if current_page < total_pages:
            display_page(current_page + 1)

    # Pagination Frame
    pagination_frame = tk.Frame(pet_management_frame, bg="#F9FAFB")
    pagination_frame.place(x=50, y=580, width=800, height=50)

    prev_btn = tk.Button(pagination_frame, text="<< Prev",
                         font=("Arial", 10, "bold"), relief="flat", width=10, command=prev_page)
    prev_btn.pack(side="left", padx=5)

    page_label = tk.Label(pagination_frame, text="Page 1 of X", font=("Arial", 10, "bold"), bg="#F9FAFB")
    page_label.pack(side="left", padx=10)

    next_btn = tk.Button(pagination_frame, text="Next >>",
                         font=("Arial", 10, "bold"), relief="flat", width=10, command=next_page)
    next_btn.pack(side="left", padx=5)

    # unselect on empty click
    def unselect(event):
        region = pet_table.identify("region", event.x, event.y)
        if region != "cell":
            pet_table.selection_remove(pet_table.selection())

    pet_table.bind("<Button-1>", unselect, add="+")

    selected_image_path = None
    pet_id = None
    db_image_bytes = None

    def load_pet_for_edit():
        nonlocal selected_image_path, pet_id, db_image_bytes

        selected_item = pet_table.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please choose a pet to edit.")
            return

        pet_values = pet_table.item(selected_item, "values")
        pet_id = pet_values[0]

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""SELECT name, type, status, breed, age, healthIssues, description, image FROM pets
                              WHERE id = %s""", (pet_id,))
            pet_data = cursor.fetchone()
            conn.close()

            if not pet_data:
                messagebox.showerror("Error", "Pet data not found.")
                return

        except mysql.connector.Error as error:
            messagebox.showerror("Database Error", f"Error: {error}")
            return

        # Unpack DB row
        db_name, db_type, db_status, db_breed, db_age, db_health, db_desc, db_image_bytes = pet_data

        # Convert None to empty string
        db_name = db_name or ""
        db_type = db_type or ""
        db_status = db_status or ""
        db_breed = db_breed or ""
        db_age = db_age or ""
        db_health = db_health or ""
        db_desc = db_desc or ""

        # Populate entry fields
        eName_entry.delete(0, "end")
        eName_entry.insert(0, db_name)

        etypes.set(db_type)  # combobox on edit frame
        estatus.set(db_status)

        ebreed_entry.delete(0, "end")
        ebreed_entry.insert(0, db_breed)

        eage_entry.delete(0, "end")
        eage_entry.insert(0, db_age)

        ehealth_entry.delete(0, "end")
        ehealth_entry.insert(0, db_health)

        edescription_text.delete("1.0", "end")
        edescription_text.insert("1.0", db_desc)

        # Load image
        if db_image_bytes:
            from io import BytesIO
            img = Image.open(BytesIO(db_image_bytes))
            img = img.resize((280, 190), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            eimage_label.configure(image=img_tk, text="")
            eimage_label.image = img_tk
            selected_image_path = None
        else:
            eimage_label.configure(image="", text="No Image Selected")
            eimage_label.image = None
            selected_image_path = None

        # Lift edit frame
        edit_pets_frame.lift()

    update_btn = tk.Button(edit_pets_frame, text="Update Pet", bg="#5AB9EA",
                           fg="white", font=("Arial", 12, "bold"), relief="flat", width=20)

    edit_btn = tk.Button(pagination_frame, text="Edit",
                         font=("Arial", 10, "bold"), relief="flat", width=10)
    edit_btn.config(command=load_pet_for_edit)
    edit_btn.pack(side="right", padx=5)

    #edit function
    tk.Label(edit_pets_frame, text="Edit A Pet", bg="#F9D162", fg="#2D3436",
             font=("Arial", 20, "bold")).place(x=30, y=80)

    #image
    eimage_label = tk.Label(edit_pets_frame, text="No Image Selected", bg="#F9D162",
                           fg="#2D3436", font=("Arial", 12), relief="solid")
    eimage_label.place(x=30, y=150, width=280, height=190)

    def echoose_image():
        nonlocal selected_image_path
        file_path = filedialog.askopenfilename(title="Select Image",
                                               filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
        if file_path:
            selected_image_path = file_path
            img = Image.open(file_path)
            img = img.resize((280, 190), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            eimage_label.configure(image=img_tk, text="")
            eimage_label.image = img_tk
    # Button to choose image
    echoose_image_btn = tk.Button(edit_pets_frame, text="Choose Image", bg="#5AB9EA",
                                 fg="white", font=("Arial", 12, "bold"), relief="flat", width=20)
    echoose_image_btn.config(command=echoose_image)
    echoose_image_btn.place(x=60, y=350)

    # name
    eName = tk.Label(edit_pets_frame, text="Enter pet's name: ", bg="#F9D162", fg="#2D3436",
                     font=("Arial", 10, "bold"))
    eName.place(x=330, y=150)
    eName_entry = tk.Entry(edit_pets_frame, bg="#F9FAFB", fg="#2D3436", font=("Arial", 10, "bold"))
    eName_entry.place(x=330, y=175, width=330, height=30)

    # type
    etype_Name = tk.Label(edit_pets_frame, text="Choose animal type: ", bg="#F9D162", fg="#2D3436",
                         font=("Arial", 10, "bold"))
    etype_Name.place(x=330, y=210)
    etype_options = ["Mammals", "Birds", "Reptiles", "Amphibians", "Invertebrates", "Fish"]
    etypes = ttk.Combobox(edit_pets_frame, values=etype_options, state="normal", font=("Arial", 10, "bold"))
    etypes.current(0)
    etypes.place(x=330, y=235, width=150, height=30)

    # status
    estatus_Name = tk.Label(edit_pets_frame, text="Status: ", bg="#F9D162", fg="#2D3436",
                           font=("Arial", 10, "bold"))
    estatus_Name.place(x=500, y=210)
    estatus_options = ["Rescued", "For Adoption"]
    estatus = ttk.Combobox(edit_pets_frame, values=estatus_options, state="normal", font=("Arial", 10, "bold"))
    estatus.current(0)
    estatus.place(x=500, y=235, width=160, height=30)

    # breed
    ebreed = tk.Label(edit_pets_frame, text="Enter breed: ", bg="#F9D162", fg="#2D3436",
                     font=("Arial", 10, "bold"))
    ebreed.place(x=330, y=270)
    ebreed_entry = tk.Entry(edit_pets_frame, bg="#F9FAFB", fg="#2D3436", font=("Arial", 10, "bold"))
    ebreed_entry.place(x=330, y=295, width=330, height=30)

    # age
    eage = tk.Label(edit_pets_frame, text="Enter age: ", bg="#F9D162", fg="#2D3436",
                   font=("Arial", 10, "bold"))
    eage.place(x=330, y=330)
    eage_entry = tk.Entry(edit_pets_frame, bg="#F9FAFB", fg="#2D3436", font=("Arial", 10, "bold"))
    eage_entry.place(x=330, y=355, width=150, height=30)

    # healthIssues
    ehealth = tk.Label(edit_pets_frame, text="Enter Health Issues: ", bg="#F9D162", fg="#2D3436",
                      font=("Arial", 10, "bold"))
    ehealth.place(x=330, y=390)
    ehealth_entry = tk.Entry(edit_pets_frame, bg="#F9FAFB", fg="#2D3436", font=("Arial", 10, "bold"))
    ehealth_entry.place(x=330, y=415, width=330, height=30)

    # description
    edescription = tk.Label(edit_pets_frame, text="Enter Description: ", bg="#F9D162", fg="#2D3436",
                           font=("Arial", 10, "bold"))
    edescription.place(x=330, y=450)
    edescription_text = tk.Text(edit_pets_frame, bg="#F9FAFB", fg="#2D3436", font=("Arial", 10, "bold"))
    edescription_text.place(x=330, y=475, width=330, height=100)

    # X Button
    eclose_btn = tk.Button(edit_pets_frame, text="X", bg="#F9D162", fg="#2D3436", font=("Arial", 12, "bold"),
                          width=3, relief="flat", command=lambda: pet_management_frame.lift())
    eclose_btn.place(x=655, y=5)

    # Update function
    def update_pet():
        nonlocal selected_image_path, pet_id, db_image_bytes

        new_name = eName_entry.get().strip()
        new_type = etypes.get()
        new_status = estatus.get()
        new_breed = ebreed_entry.get().strip()
        new_age = eage_entry.get().strip()
        new_health = ehealth_entry.get().strip()
        new_desc = edescription_text.get("1.0", "end").strip()

        # Image handling
        new_image_data = None
        if selected_image_path:
            with open(selected_image_path, 'rb') as f:
                new_image_data = f.read()
        else:
            new_image_data = db_image_bytes  # keep previous image

        if not all([new_name, new_type, new_status, new_breed, new_age, new_health, new_desc]):
            messagebox.showwarning("Incomplete Data", "Please fill all required fields")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            update_query = """UPDATE pets \
                              SET name=%s, \
                                  type=%s, \
                                  status=%s, \
                                  breed=%s, \
                                  age=%s, \
                                  healthIssues=%s, \
                                  description=%s, \
                                  image=%s \
                              WHERE id = %s """

            cursor.execute(update_query, (
                new_name, new_type, new_status, new_breed, new_age,
                new_health, new_desc, new_image_data, pet_id
            ))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Edit successful!")

            all_pets[:] = data()
            display_page(current_page)

            pet_management_frame.lift()

        except mysql.connector.Error as error:
            messagebox.showerror("Database Error", f"Error: {error}")

    update_btn.config(command=update_pet)
    update_btn.place(x=60, y=400)

    edit_btn.config(command=load_pet_for_edit)

    #delete
    delete_btn = tk.Button(pagination_frame, text="Delete",
                           font=("Arial", 10, "bold"), relief="flat", width=10)
    delete_btn.pack(side="right", padx=10)

    # Delete pet function
    def delete_pet():
        selected_item = pet_table.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a pet to delete.")
            return

        pet_values = pet_table.item(selected_item, "values")
        pet_id = pet_values[0]
        pet_name = pet_values[1]

        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete this pet '{pet_name}'?")
        if not confirm:
            messagebox.showinfo("Cancelled", "Pet deletion cancelled.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM pets WHERE id = %s", (pet_id,))
            conn.commit()
            conn.close()

            # Remove from table
            pet_table.delete(selected_item)
            messagebox.showinfo("Deleted", f"Pet '{pet_name}' has been deleted!")

            # Refresh pagination/all_pets
            all_pets[:] = data()
            total_pages = max(1, (len(all_pets) + page_size - 1) // page_size)
            display_page(current_page)

        except mysql.connector.Error as error:
            messagebox.showerror("Database Error", f"Error: {error}")

    # Bind delete button
    delete_btn.config(command=delete_pet)

    # Helper function to refresh table after search or sort
    def refresh_table(new_data):
        nonlocal all_pets, current_page, total_pages
        all_pets = new_data
        total_pages = max(1, (len(all_pets) + page_size - 1) // page_size)
        display_page(1)

    # Modify search function to use pagination
    def on_search(event):
        keyword = search_entry.get().strip()
        if keyword:
            pets = search_pets(keyword)
            if not pets:
                messagebox.showwarning("No Data", "No data found")
                pets = []
        else:
            pets = data()
        refresh_table(pets)

    search_entry.bind("<KeyRelease>", on_search)

    # Modify sort function to use pagination
    def sort_table(status_filter):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            if status_filter == "All":
                cursor.execute("SELECT id, name, breed, age, status FROM pets ORDER BY id DESC")
            else:
                cursor.execute(
                    "SELECT id, name, breed, age, status FROM pets WHERE status=%s ORDER BY id DESC",
                    (status_filter,))
            rows = cursor.fetchall()
            conn.close()
            refresh_table(rows)
        except mysql.connector.Error as error:
            messagebox.showerror("Database Error", f"Error: {error}")

    # Initially display first page
    display_page(1)

    #pet logs frame
    tk.Label(pet_logs_frame, text="Pet Logs", bg="#5AB9EA", fg="#F9FAFB",
             font=("Arial", 15, "bold")).place(x=30, y=30)

    # Buttons for logs
    rescue_btn = tk.Button(pet_logs_frame, text="Rescued/For Adoption", bg="#5AB9EA", fg="white",
                           font=("Arial", 12, "bold"), width=30, relief="flat")
    rescue_btn.place(x=50, y=80)

    adopted_btn = tk.Button(pet_logs_frame, text="Adopted", bg="#5AB9EA", fg="white",
                            font=("Arial", 12, "bold"), width=30, relief="flat")
    adopted_btn.place(x=350, y=80)

    # Label for status
    rescue_lbl = tk.Label(pet_logs_frame, text="Rescued/For Adoption Pets History", bg="#5AB9EA", fg="#F9FAFB",
                          font=("Arial", 13, "bold"))
    rescue_lbl.place(x=30, y=130)

    # X Button
    close_btn = tk.Button(pet_logs_frame, text="X", bg="#5AB9EA", fg="white",
                          font=("Arial", 12, "bold"), width=3, relief="flat",
                          command=lambda: pet_management_frame.lift())
    close_btn.place(x=655, y=5)

    # Table for logs
    logs_table_frame = tk.Frame(pet_logs_frame, bg="#F9FAFB")
    logs_table_frame.place(x=30, y=160, width=645, height=400)

    logs_columns = ("Date", "Name", "Breed", "Age", "Owner")
    logs_table = ttk.Treeview(
        logs_table_frame, columns=logs_columns,
        show="headings", height=20)

    for col in logs_columns:
        logs_table.heading(col, text=col)
        logs_table.column(col, width=100, anchor="center")

    logs_table.pack(fill="both", expand=True)

    def load_all_logs():
        # Update label
        rescue_lbl.config(text="All Pets History")

        # Clear table
        for row in logs_table.get_children():
            logs_table.delete(row)

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT date, name, breed, age, humanName FROM pets")
            rows = cursor.fetchall()
            conn.close()
        except mysql.connector.Error as error:
            tkinter.messagebox.showerror("Database Error", f"Error: {error}")
            return

        # Insert data into table
        for row in rows:
            logs_table.insert("", "end", values=row)

    #fecthing data from db
    def load_logs(status_list, label_text):
        # Update label
        rescue_lbl.config(text=label_text)

        # Clear previous table data
        for row in logs_table.get_children():
            logs_table.delete(row)

        # Fetch from database
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # If multiple statuses, use IN
            if isinstance(status_list, list):
                format_strings = ','.join(['%s'] * len(status_list))
                query = f"SELECT date, name, breed, age, humanName FROM pets WHERE status IN ({format_strings})"
                cursor.execute(query, tuple(status_list))
            else:
                cursor.execute(
                    "SELECT date, name, breed, age, humanName FROM pets WHERE status=%s", (status_list,))
            rows = cursor.fetchall()
            conn.close()
        except mysql.connector.Error as error:
            tkinter.messagebox.showerror("Database Error", f"Error: {error}")
            return

        # Insert data
        for row in rows:
            logs_table.insert("", "end", values=row)

    # Bind buttons
    rescue_btn.config(command=lambda: load_logs(["Rescued", "For Adoption"],
                                                "Rescued/For Adoption Pets History"))
    adopted_btn.config(command=lambda: load_logs("Adopted", "Adopted Pets History"))

    # add pets frame
    tk.Label(add_pets_frame, text="Add A Pet", bg="#F9D162", fg="#2D3436",
             font=("Arial", 20, "bold")).place(x=30, y=80)

    # section line whatever
    line2 = tk.Frame(add_pets_frame, bg="#F9FAFB", height=2, width=900)
    line2.place(x=0, y=60)
    line2 = tk.Frame(add_pets_frame, bg="#F9FAFB", height=2, width=900)
    line2.place(x=0, y=70)

    #add picture label
    # Image Section in Add Pet Frame
    image_label = tk.Label(add_pets_frame, text="No Image Selected", bg="#F9D162",
                           fg="#2D3436", font=("Arial", 12), relief="solid")
    image_label.place(x=30, y=150, width=280, height=190)

    selected_image_path = None

    def choose_image():
        nonlocal selected_image_path
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image Files", "*.jpg *.png *.jpeg")]
        )
        if file_path:
            selected_image_path = file_path
            img = Image.open(file_path)
            img = img.resize((280, 190), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            image_label.configure(image=img_tk, text="")
            image_label.image = img_tk

    # Button to choose image
    choose_image_btn = tk.Button(add_pets_frame, text="Choose Image", bg="#5AB9EA",
                                     fg="white", font=("Arial", 12, "bold"), relief="flat", width=20)
    choose_image_btn.config(command=choose_image)
    choose_image_btn.place(x=60, y=350)

    #name
    pName = tk.Label(add_pets_frame, text="Enter pet's name: ", bg="#F9D162", fg="#2D3436",
             font=("Arial", 10, "bold"))
    pName.place(x=330, y=150)
    pName_entry = tk.Entry(add_pets_frame, bg="#F9FAFB", fg="#2D3436", font=("Arial", 10, "bold"))
    pName_entry.place(x=330, y=175, width=330, height=30)

    #type
    type_Name = tk.Label(add_pets_frame, text="Choose animal type: ", bg="#F9D162", fg="#2D3436",
                     font=("Arial", 10, "bold"))
    type_Name.place(x=330, y=210)
    type_options = ["Mammals", "Birds", "Reptiles", "Amphibians", "Invertebrates", "Fish"]
    types = ttk.Combobox(add_pets_frame, values=type_options, state="readonly", font=("Arial", 10, "bold"))
    types.current(0)
    types.place(x=330, y=235, width=150, height=30)

    # status
    status_Name = tk.Label(add_pets_frame, text="Status: ", bg="#F9D162", fg="#2D3436",
                         font=("Arial", 10, "bold"))
    status_Name.place(x=500, y=210)
    status_options = ["Rescued", "For Adoption"]
    status = ttk.Combobox(add_pets_frame, values=status_options, state="readonly", font=("Arial", 10, "bold"))
    status.current(0)
    status.place(x=500, y=235, width=160, height=30)

    #breed
    breed = tk.Label(add_pets_frame, text="Enter breed: ", bg="#F9D162", fg="#2D3436",
                     font=("Arial", 10, "bold"))
    breed.place(x=330, y=270)
    breed_entry = tk.Entry(add_pets_frame, bg="#F9FAFB", fg="#2D3436", font=("Arial", 10, "bold"))
    breed_entry.place(x=330, y=295, width=330, height=30)

    #age
    age = tk.Label(add_pets_frame, text="Enter age: ", bg="#F9D162", fg="#2D3436",
                     font=("Arial", 10, "bold"))
    age.place(x=330, y=330)
    age_entry = tk.Entry(add_pets_frame, bg="#F9FAFB", fg="#2D3436", font=("Arial", 10, "bold"))
    age_entry.place(x=330, y=355, width=150, height=30)

    #healthIssues
    health = tk.Label(add_pets_frame, text="Enter Health Issues: ", bg="#F9D162", fg="#2D3436",
                   font=("Arial", 10, "bold"))
    health.place(x=330, y=390)
    health_entry = tk.Entry(add_pets_frame, bg="#F9FAFB", fg="#2D3436", font=("Arial", 10, "bold"))
    health_entry.place(x=330, y=415, width=330, height=30)

    #description
    description = tk.Label(add_pets_frame, text="Enter Description: ", bg="#F9D162", fg="#2D3436",
                      font=("Arial", 10, "bold"))
    description.place(x=330, y=450)
    description_text = tk.Text(add_pets_frame, bg="#F9FAFB", fg="#2D3436", font=("Arial", 10, "bold"))
    description_text.place(x=330, y=475, width=330, height=100)

    #date (realtime?)
    cal = tk.Label(add_pets_frame, text="Enter date: ", bg="#F9D162", fg="#2D3436", font=("Arial", 10, "bold"))
    cal.place(x=500, y=330)
    date = DateEntry(add_pets_frame, width=12, background="#F9D162", fg="#2D3436", borderwidth=2)
    date.place(x=500, y=355, width=150, height=30)

    # X Button
    close_btn = tk.Button(add_pets_frame, text="X", bg="#F9D162", fg="#2D3436", font=("Arial", 12, "bold"),
                          width=3, relief="flat", command=lambda: pet_management_frame.lift())
    close_btn.place(x=655, y=5)

    #save all data to db
    username = current_user

    def add_pet():
        nonlocal selected_image_path

        pet_name = pName_entry.get().strip()
        pet_type = types.get()
        pet_status = status.get()
        pet_breed = breed_entry.get().strip()
        pet_age = age_entry.get().strip()
        pet_health = health_entry.get().strip()
        pet_description = description_text.get("1.0", "end").strip()
        pet_date = date.get_date()

        pet_image = None
        if selected_image_path:
            with open(selected_image_path, 'rb') as f:
                pet_image = f.read()

        #check if all field is empty
        if not all([pet_name, pet_type, pet_status, pet_breed, pet_age, pet_health, pet_description, pet_date]):
            messagebox.showwarning("Incomplete Data", "Please fill all required fields")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            insert_query = """
                       INSERT INTO pets (name, type, status, breed, age, healthIssues, description, date, humanName, image)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                       """
            cursor.execute(insert_query, (pet_name, pet_type, pet_status, pet_breed, pet_age,
                                      pet_health, pet_description, pet_date, current_user, pet_image))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Pet '{pet_name}' has been added successfully!")

            # Clear all fields after adding
            pName_entry.delete(0, 'end')
            types.current(0)
            status.current(0)
            breed_entry.delete(0, 'end')
            age_entry.delete(0, 'end')
            health_entry.delete(0, 'end')
            description_text.delete("1.0", "end")
            date.set_date(dt.today())

            # Clear image preview and selected path
            image_label.config(image="", text="No Image Selected")
            image_label.image = None
            selected_image_path = None

            # Refresh main table
            pet_table.delete(*pet_table.get_children())
            for pet in data():
                pet_table.insert("", "end", values=pet)

            # Return to pet management frame
            pet_management_frame.lift()

        except mysql.connector.Error as error:
            messagebox.showerror("Database Error", f"Error: {error}")

    # add button
    addPet_btn = tk.Button(add_pets_frame, text="Add Pet", bg="#5AB9EA",
                            fg="white", font=("Arial", 12, "bold"), relief="flat", width=20)
    addPet_btn.config(command=add_pet)
    addPet_btn.place(x=60, y=400)

    #Pet Management
    pet_management_frame.lift()
