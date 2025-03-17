from .login import LoginWindow
from .data_window import PasswordDetailsWindow
import customtkinter as ctk
# import tkinter as tk
from PIL import Image
from typing import Callable, List
from libs.database import DBQuery

# 360p max image resolution size
MAX_WIDTH = 640
MAX_HEIGHT = 360

ctk.set_default_color_theme("green")
ctk.set_appearance_mode("dark")

class UserFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.name_label = ctk.CTkLabel(self, text="Tarnished") 
        self.name_label.pack(padx=10, pady=10)

class DataFrame(ctk.CTkScrollableFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.password_list = []
        self.parent = parent
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.show_img = ctk.CTkImage(dark_image=Image.open("icons/show_icon.ico"))
        self.update_img = ctk.CTkImage(dark_image=Image.open("icons/edit_icon.ico"))
        self.delete_img = ctk.CTkImage(dark_image=Image.open("icons/delete_icon.ico"))
        self.add_img = ctk.CTkImage(dark_image=Image.open("icons/add_icon.ico"))

        self.data_label = ctk.CTkLabel(self, text="Passwords") 
        self.data_label.grid(row=0, column=0)
        # self.data_label.rowconfigure(weight=1)
        self.add_button = ctk.CTkButton(self, width=40, height=40, image=self.add_img, text="", command=self.add_password)
        self.add_button.grid(row=0, column=1)

    def display_password_list(self, password_list: List) -> None:
        for row, data in enumerate(password_list):
            url_label = ctk.CTkLabel(self, text=data.site_url)
            url_label.grid(row=row + 1, column=0, padx=1, pady=1, sticky="we")

            add_button = self.display_button(row, 1, self.show_img, self.show_password_image, data)
            edit_button = self.display_button(row, 2, self.update_img, self.update_data, data)
            delete_button = self.display_button(row, 3, self.delete_img, self.delete_data, data)

            self.password_list.append([url_label, add_button, edit_button, delete_button])

    def display_button(self, row: int, column: int, image: Image.Image, function: Callable, data: List) -> ctk.CTkButton:
        button = ctk.CTkButton(
            master=self,
            width=40, 
            height=40, 
            image=image,
            text="",
            command=lambda e = (row, data) : function(e)
        )

        button.grid(row=row + 1, column=column, padx=1, pady=1)

        return button
    
    def add_password(self):
        self.show_password_inputs = PasswordDetailsWindow(self.parent)
        self.show_password_inputs.focus()
    
    def show_password_image(self, data):
        self.parent.handle_show_image(data[1])

    def update_data(self, data):
        print(f"updating the data. {data[1]}")

    def delete_data(self, data):
        row, details = data
        deleted = self.parent.db.delete_password(details)
        if deleted:
            for widget in self.password_list[row]:
                widget.destroy()
    
        self.parent.get_latest_data()


class ImageFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.image_label = ctk.CTkLabel(self, text="No selected image.")
        self.image_label.grid(row=0, column=0)


    def display_image(self, image_path: str) -> None:
        image = Image.open(image_path)

        img_width, img_height = image.size
        aspect_ratio = img_width / img_height

        if aspect_ratio > (16/9):
            new_width = min(img_width, MAX_WIDTH)
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = min(img_height, MAX_HEIGHT)
            new_width = int(new_height / aspect_ratio)
        
        password_image = ctk.CTkImage(dark_image=image, size=(new_height, new_width))
        self.image_label.configure(text="", image=password_image)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.db = DBQuery()
        self.user = None

        self.geometry("800x500")
        self.title("Password Manager")
        self.grid_columnconfigure([0, 1], weight=1, pad=1)
        self.grid_rowconfigure([0, 1], weight=1, pad=2)

        self.login_window = LoginWindow(self)
        self.withdraw()

        self.user_frame = UserFrame(self)
        self.user_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, ipadx=10, ipady=5, sticky="nsew")

        self.data_frame = DataFrame(self)
        self.data_frame.grid(row=1, column=0, padx=5, pady=5, ipadx=10, ipady=5, sticky="nsew")

        self.image_frame = ImageFrame(self)
        self.image_frame.grid(row=1, column=1, padx=5, pady=5, ipadx=10, ipady=5, sticky="nsew")


    def get_latest_data(self):
        new_data = self.db.get_user_data(self.user.username)
        self.user = new_data
    
    def display_password_list(self):
        self.data_frame.display_password_list(self.user.passwords)

    def handle_show_image(self, password_data):
        self.image_frame.display_image(password_data.image_path)