from tkinter import *
from tkinter import messagebox
from ttkbootstrap import Style
from random import choice, randint, shuffle
import pyperclip
import json
import os
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet, InvalidToken
from cryptography.exceptions import InvalidSignature


KEY = None


def encrypt(string):
    global KEY
    crypter = Fernet(KEY)
    encrypted_string = crypter.encrypt(string.encode())
    return encrypted_string


def decrypt(string):
    global KEY
    crypter = Fernet(KEY)
    decrypted_string = crypter.decrypt(string).decode()
    return decrypted_string


def get_key_from_password(password):
    salt = b'\xae`\x9b@T/\xf9\xa4\xab\x1e\xa6\r\xb07\xcc\xa3'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key


def app():
    table = []
    table_widget = []

    try:
        with open("email.txt", "rb") as data_file:
            default_email = decrypt(data_file.read())
    except FileNotFoundError:
        default_email = "default@mail"
        with open("email.txt", "wb") as data_file:
            data_file.write(encrypt(default_email))

    def generate_password():
        letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                   'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
                   'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
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

    def get_hidden_password(password):
        return ["*" for letter in password]

    def save():

        website = website_entry.get()
        email = email_entry.get()
        user = user_entry.get()
        password = password_entry.get()
        new_data = {
            "website": website,
            "email": email,
            "user": user,
            "password": password
        }

        if len(website) == 0 or len(password) == 0:
            messagebox.showinfo(title="Oops", message="Please make sure you haven't left any required fields empty.")
        else:
            try:
                with open("data.json", "rb") as data_file:
                    encrypted_data = data_file.read()
                    data = json.loads(decrypt(encrypted_data))
            except FileNotFoundError:
                data = [new_data]

                with open("data.json", "wb") as data_file:
                    encrypted_data = encrypt(json.dumps(data, sort_keys=True, indent=4))
                    data_file.write(encrypted_data)
            else:
                data.append(new_data)

                with open("data.json", "wb") as data_file:
                    encrypted_data = encrypt(json.dumps(data, sort_keys=True, indent=4))
                    data_file.write(encrypted_data)
            finally:
                website_entry.delete(0, END)
                password_entry.delete(0, END)

                window.clipboard_clear()
                window.clipboard_append(password)

                with open("email.txt", "wb") as data_file:
                    data_file.write(encrypt(email))

        update_table()

    def find_password():
        website = website_entry.get()
        try:
            with open("data.json", "rb") as data_file:
                encrypted_data = data_file.read()
                data = json.loads(decrypt(encrypted_data))

        except FileNotFoundError:
            messagebox.showinfo(title="Error", message="No Data File Found.")
        else:
            table.clear()
            current_row = 5

            for account in data:
                if website.lower() in account["website"].lower():
                    email = account["email"]
                    user = account["user"]
                    password = account["password"]
                    table_dict = {
                        "website": account["website"],
                        "email": email,
                        "user": user,
                        "password": password
                    }

                    table.append(table_dict)
                    current_row += 1

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

        head.append(Label(frame_table, text="Email", width=15, borderwidth=3, relief="ridge", font="Helvetica 10 bold"))
        head[1].grid(sticky="wesn", row=row_position + grid_offset, column=1)

        head.append(
            Label(frame_table, text="Username", width=15, borderwidth=3, relief="ridge", font="Helvetica 10 bold"))
        head[2].grid(sticky="wesn", row=row_position + grid_offset, column=2)

        head.append(
            Label(frame_table, text="Password", width=10, borderwidth=3, relief="ridge", font="Helvetica 10 bold"))
        head[3].grid(sticky="wesn", row=row_position + grid_offset, column=3)

        row_position += 1
        for account in table:
            temp_list = []

            temp_list.append(Label(frame_table, text=account["website"], borderwidth=1, relief="ridge"))
            temp_list[0].grid(sticky="wesn", row=row_position + grid_offset, column=0)

            temp_list.append(Button(frame_table, text=account["email"], borderwidth=1, relief="ridge",
                                    command=lambda x=account["email"]: copy_button(x)))
            temp_list[1].grid(sticky="we", row=row_position + grid_offset, column=1)

            temp_list.append(Button(frame_table, text=account["user"], borderwidth=1, relief="ridge",
                                    command=lambda x=account["user"]: copy_button(x)))
            temp_list[2].grid(sticky="we", row=row_position + grid_offset, column=2)

            temp_list.append(Button(frame_table, text=get_hidden_password(account["password"]), borderwidth=1, relief="ridge",
                                    command=lambda x=account["password"]: copy_button(x)))
            temp_list[3].grid(sticky="we", row=row_position + grid_offset, column=3)

            temp_list.append(Button(frame_table, text="Delete", borderwidth=1, relief="ridge",
                                    command=lambda x=account: delete_account(x)))
            temp_list[4].grid(sticky="we", row=row_position + grid_offset, column=4)

            table_widget.append(temp_list)

            row_position += 1

    def copy_button(content):
        window.clipboard_clear()
        window.clipboard_append(content)

    def update_table(e=None):
        find_password()
        table_show()

    def delete_account(account):
        msg_box = messagebox.askquestion('Delete Account', 'Are you sure you want to delete the account?',
                                         icon='warning')
        if msg_box == 'yes':
            with open("data.json", "rb") as data_file:
                encrypted_data = data_file.read()
                data = json.loads(decrypt(encrypted_data))
            with open('data.json', 'wb'):
                pass
            data.remove(account)
            with open("data.json", "wb") as data_file:
                encrypted_data = encrypt(json.dumps(data, sort_keys=True, indent=4))
                data_file.write(encrypted_data)
        update_table()

    def resize_table(e):
        window.update_idletasks()
        table_canvas.config(width=frame_table.winfo_width())
        table_canvas.config(scrollregion=frame_table.bbox())

    # Create main app window
    style = Style(theme='darkly')
    window = style.master
    window.option_add("*Font", "Helvetica 9")

    window.title("Password Manager")
    window.config(padx=50, pady=50)
    window.resizable(width=False, height=False)

    # Focus window
    window.after(1, lambda: window.focus_force())

    # Logo
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

    email_label = Label(main_frame, text="Email:")
    email_label.grid(sticky="e", row=2, column=0)

    user_label = Label(main_frame, text="Username:")
    user_label.grid(sticky="e", row=3, column=0)

    password_label = Label(main_frame, text="Password:")
    password_label.grid(sticky="e", row=4, column=0)

    # Entries
    website_entry = Entry(main_frame, width=30)
    website_entry.grid(sticky="wesn", row=1, column=1)
    website_entry.focus()

    email_entry = Entry(main_frame)
    email_entry.grid(sticky="wesn", row=2, column=1, columnspan=2)
    email_entry.insert(0, default_email)

    user_entry = Entry(main_frame)
    user_entry.grid(sticky="wesn", row=3, column=1, columnspan=2)

    password_entry = Entry(main_frame)
    password_entry.grid(sticky="wesn", row=4, column=1)

    # Buttons
    search_button = Button(main_frame, text="Search", borderwidth=1, relief="ridge", command=update_table)
    search_button.grid(sticky="we", row=1, column=2)

    generate_password_button = Button(main_frame, text="Generate Password", borderwidth=1, relief="ridge",
                                      command=generate_password)
    generate_password_button.grid(sticky="we", row=4, column=2)

    add_button = Button(main_frame, text="Add", borderwidth=1, relief="ridge", command=save)
    add_button.grid(sticky="we", row=5, column=1, columnspan=2)

    # Create data frame
    frame_main = Frame(window)
    frame_main.grid(row=3, column=0)
    window.grid_columnconfigure(0, weight=1)

    table_canvas = Canvas(frame_main)
    table_canvas.grid(row=3, column=0, sticky='ew')

    scrollbar = Scrollbar(frame_main, orient=VERTICAL, command=table_canvas.yview)
    scrollbar.grid(row=3, column=1, sticky="ns")

    table_canvas.configure(yscrollcommand=scrollbar.set)
    table_canvas.bind('<Configure>', lambda e: table_canvas.configure(scrollregion=table_canvas.bbox("all")))

    frame_table = Frame(table_canvas)

    update_table()

    table_canvas.create_window((0, 0), window=frame_table, anchor="nw")
    window.bind("<Configure>", resize_table)

    window.bind("<Return>", update_table)

    window.mainloop()


def login_app():

    def login(e=None):
        global KEY
        KEY = get_key_from_password(main_password_entry.get())
        print(KEY)
        window_login.destroy()

        try:
            app()
        except (InvalidSignature, InvalidToken):
            messagebox.showinfo(title="Oops", message="Wrong Password.")
            quit()

    def register(e=None):
        if main_password_entry.get() == confirm_main_password_entry.get():
            global KEY
            KEY = get_key_from_password(main_password_entry.get())
            print(KEY)
            window_login.destroy()

            try:
                app()
            except (InvalidSignature, InvalidToken):
                messagebox.showinfo(title="Oops", message="Wrong Password!")
                quit()
        else:
            messagebox.showinfo(title="Oops", message="Passwords don't match!.")

    style = Style(theme='darkly')
    window_login = style.master
    window_login.option_add("*Font", "Helvetica 9")

    window_login.title("Password Manager")
    window_login.config(padx=50, pady=50)
    window_login.resizable(width=False, height=False)

    main_frame = Frame(window_login)
    main_frame.grid(row=0, column=0)

    main_password_label = Label(main_frame, text="Password:")
    main_password_label.grid(sticky="e", row=0, column=0)

    main_password_entry = Entry(main_frame, show="*", width=30)
    main_password_entry.grid(sticky="wesn", row=0, column=1)
    main_password_entry.focus()

    if os.path.isfile('./data.json') or os.path.isfile('./email.txt'):

        login_button = Button(main_frame, text="Login", borderwidth=1, relief="ridge", command=login)
        login_button.grid(sticky="we", row=0, column=2, )

        window_login.bind("<Return>", login)
    else:
        confirm_main_password_label = Label(main_frame, text="Confirm Password:")
        confirm_main_password_label.grid(sticky="e", row=1, column=0)

        confirm_main_password_entry = Entry(main_frame, show="*", width=30)
        confirm_main_password_entry.grid(sticky="wesn", row=1, column=1)
        confirm_main_password_entry.focus()

        register_button = Button(main_frame, text="Register", borderwidth=1, relief="ridge", command=register)
        register_button.grid(sticky="we", row=1, column=2, )

        window_login.bind("<Return>", register)

    window_login.mainloop()


if __name__ == '__main__':
    login_app()
