import customtkinter as ctk

class PasswordDetailFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.site_url_input = ctk.CTkEntry(self, placeholder_text="Site URL", height=35, width=200)
        self.site_url_input.pack(padx=10, pady=10)
        self.password_input = ctk.CTkEntry(self, placeholder_text="Password", show="*", height=35, width=200)
        self.password_input.pack(padx=10, pady=10)
        self.confirm_password_input = ctk.CTkEntry(self, placeholder_text="Confirm Password", show="*", height=35, width=200)
        self.confirm_password_input.pack(padx=10, pady=10)
        self.image_path_input = ctk.CTkEntry(self, placeholder_text="Image Path", height=35, width=200)
        self.image_path_input.pack(padx=10, pady=10)

        self.submit_button = ctk.CTkButton(self, text="Submit", height=35, width=200, command=self.submit_data)
        self.submit_button.pack(padx=10, pady=10)
    
    def submit_data(self):
        site_url, image_path = self.site_url_input.get(), self.image_path_input.get()
        added_password = self.parent.db.add_passwords(site_url, image_path, self.parent.user.id)

        if added_password:
            self.parent.destroy()


class PasswordDetailsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.geometry("600x400")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.title("Add New Password")

        # access variables in App main window
        self.parent = parent
        self.db = self.parent.db
        self.user = self.parent.user

        self.password_details_frame = PasswordDetailFrame(self)
        self.password_details_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nwes")