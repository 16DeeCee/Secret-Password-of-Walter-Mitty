from .inputdialog import PasswordInputDialog
from libs.auth import Auth
from libs.database import Passwords
from libs.steganography  import Steganography
from tkinter import filedialog
from typing import Any
import customtkinter as ctk
import os


class PasswordDetailFrame(ctk.CTkFrame):
    def __init__(self, parent: Any, data: Passwords = None):
        super().__init__(parent)
        self.data = data
        self.site_url_text = ctk.StringVar(self, self.data.site_url) if data else ctk.StringVar(self, "")
        self.image_path = ""

        self.parent = parent
        self.grid_rowconfigure(list(range(7)), weight=1)
        self.grid_columnconfigure(list(range(2)), weight=1)

        self.error_message_label = ctk.CTkLabel(self, width=200, height=35,text="")
        self.site_url_label = ctk.CTkLabel(self, text="Site URL")
        self.site_url_input = ctk.CTkEntry(self, height=35, width=200, textvariable=self.site_url_text)
        self.password_label = ctk.CTkLabel(self, text="Password")
        self.password_input = ctk.CTkEntry(self, show="*", height=35, width=200)
        self.confirm_password_label = ctk.CTkLabel(self, text="Confirm Password")
        self.confirm_password_input = ctk.CTkEntry(self, show="*", height=35, width=200)
        self.image_path_label = ctk.CTkLabel(self, text="Image Path")
        self.image_path_text = ctk.CTkLabel(
            self, 
            width=200, 
            height=35, 
            text="No file chosen.", 
            wraplength=200
        )
        self.choose_file_button = ctk.CTkButton(
            self, 
            text="Choose a file", 
            height=35, 
            width=200, 
            command=self.choose_file
        )
        self.submit_button = ctk.CTkButton(
            self, 
            text="Submit", 
            height=35, 
            width=200, 
            command=self.submit_data
        )

        self.error_message_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        self.site_url_label.grid(row=1, column=0, padx=10, pady=10)
        self.site_url_input.grid(row=1, column=1, padx=10, pady=10)
        self.password_label.grid(row=2, column=0, padx=10, pady=10)
        self.password_input.grid(row=2, column=1, padx=10, pady=10)
        self.confirm_password_label.grid(row=3, column=0, padx=10, pady=10)
        self.confirm_password_input.grid(row=3, column=1, padx=10, pady=10)
        self.image_path_label.grid(row=4, column=0, padx=10, pady=10)
        self.image_path_text.grid(row=4, column=1, padx=10, pady=10)
        self.choose_file_button.grid(row=5, column=1, padx=10, pady=10)
        self.submit_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10)


    def add_password(self, site_url: str, password: str, confirm_password: str) -> None:
        try:
            self.validate_input(site_url, password, confirm_password)
        except ValueError as e:
            self.error_message_label.configure(text=e)
            return
        
        master_password = self.validate_master_password()
        if not master_password:
            return

        encrypted_password = Auth.encrypt_password(master_password, password)

        try:
            image_encoder = Steganography(self.image_path, encrypted_password)
            new_image_path = image_encoder.encode_bytes_in_image()
        except Exception as e:
            self.error_message_label.configure(text=e)
            return
        
        added_password = self.parent.db.add_passwords(site_url, new_image_path, self.parent.user.id)

        if added_password:
            self.parent.result = added_password
            self.parent.destroy()
    

    def update_password(self, site_url: str, password: str, confirm_password: str) -> None:
        if password or confirm_password:
            try:
                self.validate_input(site_url, password, confirm_password)
            except ValueError as e:
                self.error_message_label.configure(text=e)
        
        master_password = PasswordInputDialog.get_input(self.parent)
        if not master_password:
            return

        image_path = self.check_update_path_and_password(
            self.image_path, 
            password, 
            master_password
        )

        new_values = {}

        if image_path:
            new_values["image_path"] = image_path
        if site_url and site_url != self.data.site_url:
            new_values["site_url"] = site_url
        
        if not new_values:
            return
        
        updated_password = self.parent.db.update_password(self.parent.user.id, self.data.pid, new_values)

        if updated_password:
            self.parent.result = updated_password
            self.parent.destroy()
         

    def check_update_path_and_password(self, image_path, password, master_password):
        if not image_path and not password:
            return image_path
        
        temp_image_path = image_path if image_path else self.data.image_path
        
        if password:
            encrypted_password = Auth.encrypt_password(master_password, password)
        else:
            decoder = Steganography(temp_image_path)
            encrypted_password = decoder.decode_bytes_in_image()

        try:
            image_encoder = Steganography(temp_image_path, encrypted_password)
            new_image_path = image_encoder.encode_bytes_in_image()
        except Exception as e:
            self.error_message_label.configure(text=e)
            return image_path

        os.remove(self.data.image_path)
        
        return new_image_path

    
    def submit_data(self) -> None:
        site_url = self.site_url_input.get()
        password, confirm_password = self.password_input.get(), self.confirm_password_input.get()

        if not self.data:
            self.add_password(site_url, password, confirm_password)
        else:
            self.update_password(site_url, password, confirm_password)


    def choose_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg;*.png")], 
            title="Choose an image."
        )

        if file_path:
            filename = os.path.basename(file_path)

            self.image_path = file_path
            self.image_path_text.configure(text=f"Image Path: {self.truncate_text(filename)}")
    

    def validate_input(self, site_url, password, confirm_password):
        if 1 > len(site_url) < 50 and not self.data:
            raise ValueError(f"Site URL must be at least 2 characters long: {len(site_url)}")
        
        if 8 > len(password) < 32:
            raise ValueError(f"Password must be at least 8-32 characters long: {len(password)}")

        if password != confirm_password:
            raise ValueError(f"Passwords do not match.")
        
        if not self.image_path and not self.data:
            raise ValueError(f"Please choose an image.")


    def validate_master_password(self):
        master_password = PasswordInputDialog.get_input(self.parent)

        if not master_password:
            self.error_message_label.configure(text="Master Password is required.")
            return
        
        if not Auth.verify_password(self.parent.user.master_password, master_password):
            self.error_message_label.configure(text="Master password is incorrect.")
            return

        return master_password


    @staticmethod
    def truncate_text(text):
        max_length = 30
        return text[:max_length] + "..." if len(text) > max_length else text


class PasswordDetailsWindow(ctk.CTkToplevel):
    def __init__(self, parent, title="", data=None):
        super().__init__(parent)
        # access variables in App main window
        self.parent = parent
        self.db = self.parent.db
        self.user = self.parent.user
        self.result = None

        self.geometry("500x400")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.title(title)
        self.transient(self.parent)
        self.grab_set()

        self.password_details_frame = PasswordDetailFrame(self, data)
        self.password_details_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nwes")


    @staticmethod
    def show(parent, **kwargs):
        password_dialog = PasswordDetailsWindow(parent, **kwargs)
        parent.wait_window(password_dialog)

        return password_dialog.result