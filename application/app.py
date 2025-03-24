from .data_window import PasswordDetailsWindow
from .inputdialog import PasswordInputDialog
from .login import LoginWindow
from .messagebox import MessageBox
from libs.auth import Auth
from libs.database import DBQuery, Passwords, User
from libs.password_checker import PasswordChecker
from libs.steganography import Steganography
from PIL import Image
from sqlalchemy.orm.collections import InstrumentedList
from typing import Any, Callable, List, Tuple

import customtkinter as ctk
import os

ctk.set_default_color_theme("green")
ctk.set_appearance_mode("dark")

# 360p max image resolution size
MAX_WIDTH = 640
MAX_HEIGHT = 360

class UserFrame(ctk.CTkFrame):
    def __init__(self, parent: Any):
        super().__init__(parent)
        # self.configure(height=100)
        self.name_label = ctk.CTkLabel(self, text="", font=("Helvetica", 20, "bold")) 
        self.name_label.pack(padx=20, pady=10, side="left")


class DataFrame(ctk.CTkScrollableFrame):
    def __init__(self, parent: Any):
        super().__init__(parent)
        self.password_list = []
        self.parent = parent

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.add_img = ctk.CTkImage(dark_image=Image.open("icons/add_icon.ico"))
        self.show_img = ctk.CTkImage(dark_image=Image.open("icons/show_icon.ico"))
        self.update_img = ctk.CTkImage(dark_image=Image.open("icons/edit_icon.ico"))
        self.delete_img = ctk.CTkImage(dark_image=Image.open("icons/delete_icon.ico"))
        self.check_img = ctk.CTkImage(dark_image=Image.open("icons/check_icon.ico"))
        

        self.data_label = ctk.CTkLabel(self, text="Passwords") 
        self.add_button = ctk.CTkButton(
            self, 
            width=40, 
            height=40, 
            image=self.add_img, 
            text="", command=self.add_password
        )

        self.data_label.grid(row=0, column=0)
        self.add_button.grid(row=0, column=1)


    def display_password_list(self, passwords: InstrumentedList) -> None:
        for row, data in enumerate(passwords):
            password_row = self.create_password_row(row + 1, data)

            self.password_list.append(password_row)


    def create_password_row(self, row: int, pw_data: Passwords) -> List[Any]:
        url_label = ctk.CTkLabel(self, text=pw_data.site_url)
        url_label.grid(row=row, column=0, padx=1, pady=1, sticky="we")

        show_button = self.create_button(row, 1, self.show_img, self.show_password_image, pw_data)
        check_button = self.create_button(row, 2, self.check_img, self.check_password, pw_data)
        edit_button = self.create_button(row, 3, self.update_img, self.update_data, pw_data)
        delete_button = self.create_button(row, 4, self.delete_img, self.delete_data, pw_data)

        return [url_label, show_button, check_button, edit_button, delete_button]
    

    def create_button(
        self, 
        row: int, 
        column: int, 
        image: Image.Image, 
        function: Callable, 
        data: Passwords
    ) -> ctk.CTkButton:
        button = ctk.CTkButton(
            master=self,
            width=40, 
            height=40, 
            image=image,
            text="",
            command=lambda e = (row, data) : function(e)
        )
        button.grid(row=row, column=column, padx=1, pady=1)

        return button
    

    def add_password(self) -> None:
        new_data = PasswordDetailsWindow.show(self.parent, title="Add New Password")

        if new_data:
            MessageBox.show(self.parent, title="Add Password", message="Password added successfully!")
            new_data = self.parent.get_latest_data()
            new_row = self.create_password_row(len(self.password_list) + 1, new_data.passwords[-1])

            self.password_list.append(new_row)

    
    def show_password_image(self, data: Tuple[int, Passwords]) -> None:
        _, password_data = data

        self.parent.handle_show_image(password_data)

    def check_password(self, data: Tuple[int, Passwords]) -> None:
        _, password_data = data
        plain_password = self.parent.decrypt_image(password_data.image_path)

        if not plain_password:
            return

        password_leak_num = PasswordChecker.check_password(plain_password)

        if password_leak_num > 0:
            MessageBox.show(
                self.parent, 
                title="Check Password Leak", 
                message=f"Your password has been leaked {password_leak_num} times. Change your password now.")
        else:
            MessageBox.show(self.parent, title="Check Password Leak", message="Your password is secured!")


    def update_data(self, data: Tuple[int, Passwords]) -> None:
        # print(f"updating the data. {data[1]}")
        row, password_data = data
        updated_data = PasswordDetailsWindow.show(self.parent, title="Update Password", data=password_data)

        if updated_data:
            MessageBox.show(self.parent, title="Update Password", message="Password updated successfully!")
            latest_data = self.parent.get_latest_data().passwords[row - 1]

            label, show_btn, check_btn, update_btn, delete_btn = self.password_list[row - 1]

            label.configure(text=latest_data.site_url)
            show_btn.configure(command=lambda e = (row, latest_data):self.show_password_image(e))
            check_btn.configure(command=lambda e = (row, latest_data):self.check_password(e))
            update_btn.configure(command=lambda e = (row, latest_data):self.update_data(e))
            delete_btn.configure(command=lambda e = (row, latest_data):self.delete_data(e))


    def delete_data(self, data: Tuple[int, Passwords]) -> None:
        row, pasword = data

        confirmation = MessageBox.show(
            self.parent, 
            title="Delete password", 
            message="Are you sure to delete this password?", 
            buttons=["Confirm", "Cancel"]
        )
        if confirmation != "Confirm":
            return
        
        deleted = self.parent.db.delete_password(pasword)
        if not deleted:
            MessageBox.show(self.parent, title="Error", message="Something went wrong.")
            return
        
        os.remove(pasword.image_path)

        latest_data = self.parent.get_latest_data().passwords
        
        for widget in self.password_list[row - 1]:
            widget.destroy()
        
        del self.password_list[row - 1]

        # modify grid row of data affected below the deleted data
        if row - 1 < len(self.password_list):
            for index in range(row - 1, len(self.password_list), 1):
                label, show_btn, check_btn, update_btn, delete_btn = self.password_list[index]
                func_data = (index + 1, latest_data[index])

                label.grid_configure(row=index + 1)
                self.modify_button(show_btn, func_data, self.show_password_image)
                self.modify_button(check_btn, func_data, self.check_password)
                self.modify_button(update_btn, func_data, self.update_data)
                self.modify_button(delete_btn, func_data, self.delete_data)

    
    @staticmethod
    def modify_button(button: ctk.CTkButton, data: tuple, function: Callable) -> None:
        button.grid_configure(row=data[0])
        button.configure(command = lambda e = data : function(e))


class ImageFrame(ctk.CTkFrame):
    def __init__(self, parent: Any):
        super().__init__(parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.parent = parent
        self.chosen_password = None

        self.image_label = ctk.CTkLabel(self, text="No selected image.")
        self.decrypt_button = ctk.CTkButton(self, text="Decrypt Image Password", command=self.show_password)

        self.image_label.grid(row=1, column=0)


    def display_image(self, password: Passwords) -> None:
        if not self.chosen_password:
            self.decrypt_button.grid(row=0, column=0, padx=5, pady=5)

        self.chosen_password = password

        image = Image.open(password.image_path)
        img_width, img_height = image.size
        aspect_ratio = img_width / img_height

        if aspect_ratio > (16/9):
            new_width = min(img_width, MAX_WIDTH)
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = min(img_height, MAX_HEIGHT)
            new_width = int(new_height / aspect_ratio)
        
        password_image = ctk.CTkImage(dark_image=image, size=(new_height, new_width))

        self.image_label.configure(text=password.site_url, image=password_image)


    def show_password(self) -> None:
        plain_password = self.parent.decrypt_image(self.chosen_password.image_path)

        if plain_password:
            MessageBox.show(self.parent, title="Password", message=plain_password)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.db = DBQuery()
        self.user = None

        self.geometry("800x500")
        self.title("Password Manager")
        self.grid_columnconfigure(0, weight=1, pad=1)
        self.grid_columnconfigure(1, weight=2, pad=1)
        self.grid_rowconfigure(0, weight=0, pad=1)
        self.grid_rowconfigure(1, weight=1, pad=1)

        self.login_window = LoginWindow(self)
        self.withdraw()

        self.user_frame = UserFrame(self)
        self.data_frame = DataFrame(self)
        self.image_frame = ImageFrame(self)

        self.user_frame.grid(
            row=0, 
            column=0, 
            columnspan=2, 
            padx=5, 
            pady=5, 
            ipadx=5, 
            ipady=5, 
            sticky="nsew"
        )
        self.data_frame.grid(row=1, column=0, padx=5, pady=5, ipadx=10, ipady=5, sticky="nsew")
        self.image_frame.grid(row=1, column=1, padx=5, pady=5, ipadx=10, ipady=5, sticky="nsew")


    def get_latest_data(self) -> User:
        new_data = self.db.get_user_data(self.user.username)
        self.user = new_data

        return new_data
    

    def display_user_data(self) -> None:
        self.user_frame.name_label.configure(text=f"{self.user.username}")
        self.data_frame.display_password_list(self.user.passwords)


    def handle_show_image(self, password_data: Passwords) -> None:
        self.image_frame.display_image(password_data)

    def decrypt_image(self, image_path: str) -> str | None:
        decoder = Steganography(image_path)

        master_password = PasswordInputDialog.get_input(self)
        
        if not master_password:
            MessageBox.show(self, title="Error", message="Master password is required.")
            return

        hidden_bytes = decoder.decode_bytes_in_image()

        try:
            plain_password = Auth.decrypt_password(master_password, hidden_bytes)
        except ValueError as e:
            MessageBox.show(self, title="Incorrect", message=e)
            return

        return plain_password