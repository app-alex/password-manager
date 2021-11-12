from tkinter import *
from tkinter import messagebox
from ttkbootstrap import Style
from random import choice, randint, shuffle
import pyperclip
import json


table = []
table_widget = []
is_table = False
is_table_shown = False

try:
    with open("email.txt", "r") as data_file:
        default_email = data_file.read()
except FileNotFoundError:
    default_email = ""
    with open("email.txt", "w") as data_file:
        pass

def generate_password():
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']

    password_letters = [choice(letters) for _ in range(randint(8, 10))]
    password_symbols = [choice(symbols) for _ in range(randint(2, 3))]
    password_numbers = [choice(numbers) for _ in range(randint(2, 3))]

    password_list = password_letters + password_symbols + password_numbers
    shuffle(password_list)

    password = "".join(password_list)
    password_entry.delete(0, END)
    password_entry.insert(0, password)
    pyperclip.copy(password)


def save():

    website = website_entry.get()
    email = email_entry.get()
    password = password_entry.get()
    new_data = {
        "website": website,
        "email": email,
        "password": password
    }

    if len(website) == 0 or len(password) == 0:
        messagebox.showinfo(title="Oops", message="Please make sure you haven't left any fields empty.")
    else:
        try:
            with open("data.json", "r") as data_file:
                data = json.load(data_file)
        except FileNotFoundError:
            data = [new_data]

            with open("data.json", "w") as data_file:
                json.dump(data, data_file, indent=4)
        else:
            data.append(new_data)

            with open("data.json", "w") as data_file:
                json.dump(data, data_file, indent=4)
        finally:
            website_entry.delete(0, END)
            password_entry.delete(0, END)

            window.clipboard_clear()
            window.clipboard_append(password)

            with open("email.txt", "w") as data_file:
                data_file.write(email)
    update_table()


def find_password():
    website = website_entry.get()
    try:
        with open("data.json") as data_file:
            data = json.load(data_file)
    except FileNotFoundError:
        messagebox.showinfo(title="Error", message="No Data File Found.")
    else:
        table.clear()
        current_row = 5

        for account in data:
            if website.lower() in account["website"].lower():
                email = account["email"]
                password = account["password"]
                table_dict = {
                    "website": account["website"],
                    "email": email,
                    "password": password
                }

                table.append(table_dict)
                current_row +=1

        table_destroy()


def table_destroy():
    for _ in table_widget:
        for widget in _:
            widget.destroy()


def table_show():
    grid_offset = 0
    row_position = 0

    head = [Label(frame_table, text="For", width=10, borderwidth=3, relief="ridge", font="Helvetica 10 bold")]

    head[0].grid(sticky="wesn", row=row_position + grid_offset, column=0)
    head.append(Label(frame_table, text="Email/Username", width=15, borderwidth=3, relief="ridge", font="Helvetica 10 bold"))
    head[1].grid(sticky="wesn", row=row_position + grid_offset, column=1)
    head.append(Label(frame_table, text="Password", width=10, borderwidth=3, relief="ridge", font="Helvetica 10 bold"))
    head[2].grid(sticky="wesn", row=row_position + grid_offset, column=2)

    row_position += 1
    for account in table:

        temp_list = []

        temp_list.append(Label(frame_table, text=account["website"], borderwidth=1, relief="ridge"))
        temp_list[0].grid(sticky="wesn", row=row_position+grid_offset, column=0)

        temp_list.append(Button(frame_table, text=account["email"], borderwidth=1, relief="ridge", command=lambda x=account["email"]: copy_button(x)))
        temp_list[1].grid(sticky="we", row=row_position+grid_offset, column=1)

        temp_list.append(Button(frame_table, text="Copy", borderwidth=1, relief="ridge", command=lambda x=account["password"]: copy_button(x)))
        temp_list[2].grid(sticky="we", row=row_position+grid_offset, column=2)

        temp_list.append(Button(frame_table, text="Delete", borderwidth=1, relief="ridge", command=lambda x=account: delete_account(x)))
        temp_list[3].grid(sticky="we", row=row_position + grid_offset, column=3)

        table_widget.append(temp_list)

        row_position += 1


def copy_button(content):
    window.clipboard_clear()
    window.clipboard_append(content)


def update_table(e=None):
    find_password()
    table_show()


def delete_account(account):
    msg_box = messagebox.askquestion('Delete Account', 'Are you sure you want to delete the account?', icon='warning')
    if msg_box == 'yes':
        with open("data.json", "r") as data_file:
            data = json.load(data_file)
        with open('data.json', 'w'):
            pass
        data.remove(account)
        with open("data.json", "w") as data_file:
            json.dump(data, data_file, indent=4)
    update_table()


def resize_table(e):
    window.update_idletasks()
    table_canvas.config(width=frame_table.winfo_width())
    table_canvas.config(scrollregion=frame_table.bbox())


style = Style(theme='darkly')
window = style.master
window.option_add("*Font", "Helvetica 9")

window.title("Password Manager")
window.config(padx=50, pady=50)
window.resizable(width=False, height=False)

canvas = Canvas(height=200, width=200)
logo_img = PhotoImage(file="logo.png")
canvas.create_image(100, 100, image=logo_img)
canvas.grid(row=0, column=0)

main_frame = Frame(window)
main_frame.grid(row=1, column=0, )

spacing = Label()
spacing.grid(row=2, column=0)


# Labels
website_label = Label(main_frame, text="For:")
website_label.grid(sticky="e", row=1, column=0)

email_label = Label(main_frame, text="Email/Username:")
email_label.grid(sticky="e", row=2, column=0)

password_label = Label(main_frame, text="Password:")
password_label.grid(sticky="e", row=3, column=0)


# Entries
website_entry = Entry(main_frame, width=30)
website_entry.grid(sticky="wesn", row=1, column=1)
website_entry.focus()

email_entry = Entry(main_frame)
email_entry.grid(sticky="wesn", row=2, column=1, columnspan=2)
email_entry.insert(0, default_email)

password_entry = Entry(main_frame)
password_entry.grid(sticky="wesn", row=3, column=1)


# Buttons
search_button = Button(main_frame, text="Search", borderwidth=1, relief="ridge", command=update_table)
search_button.grid(sticky="we", row=1, column=2)

generate_password_button = Button(main_frame, text="Generate Password", borderwidth=1, relief="ridge", command=generate_password)
generate_password_button.grid(sticky="we", row=3, column=2)

add_button = Button(main_frame, text="Add", borderwidth=1, relief="ridge", command=save)
add_button.grid(sticky="we", row=4, column=1, columnspan=2)


frame_main = Frame(window)
frame_main.grid(row=3, column=0)
window.grid_columnconfigure(0, weight=1)

table_canvas = Canvas(frame_main)
table_canvas.grid(row=3, column=0, sticky='ew')

scrollbar = Scrollbar(frame_main, orient=VERTICAL, command=table_canvas.yview)
scrollbar.grid(row=3, column=1, sticky="ns")

table_canvas.configure(yscrollcommand=scrollbar.set)
table_canvas.bind('<Configure>', lambda e: table_canvas.configure(scrollregion=table_canvas.bbox("all")))

frame_table = Frame(table_canvas,)

update_table()

table_canvas.create_window((0, 0), window=frame_table, anchor="nw")
window.bind("<Configure>", resize_table)

window.bind("<Return>", update_table)

window.mainloop()
