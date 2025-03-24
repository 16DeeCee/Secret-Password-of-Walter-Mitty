import customtkinter as ctk
from libs.database import User
from libs.auth import Auth
from libs.database import DBQuery
from typing import Any


class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent: Any, db: DBQuery):
        super().__init__(parent)
        self.parent = parent
        self.db = db

        self.message_label = ctk.CTkLabel(self, text="Enter your credentials.", text_color="white")
        self.username_input = ctk.CTkEntry(self, placeholder_text="Username", height=35, width=200)
        self.password_input = ctk.CTkEntry(
            self, 
            placeholder_text="Password", 
            show="*", 
            height=35, 
            width=200
        )
        self.login_button = ctk.CTkButton(
            self, 
            text="Login", 
            height=35, 
            width=200, 
            command=self.handle_click_login
        )
        self.register_label = ctk.CTkLabel(
            self, 
            text="No account? Register here.", 
            cursor="hand2", 
            text_color="green"
        )

        self.message_label.pack(padx=10, pady=20)
        self.username_input.pack(padx=10, pady=10)
        self.password_input.pack(padx=10, pady=10)
        self.login_button.pack(padx=10, pady=10)
        self.register_label.pack(padx=0, pady=20)

        self.register_label.bind("<Button-1>", lambda _: self.parent.switch_frame())


    def handle_click_login(self) -> None:
        username, password = self.username_input.get(), self.password_input.get()

        user = self.db.get_user_data(username)

        if not user:
            self.message_label.configure(text="Incorrect username or password.")
            return
        
        if not Auth.verify_password(user.master_password, password):
            self.message_label.configure(text="Incorrect username or password.")
            return
        
        self.parent.logged_in(user)
        

class RegisterFrame(ctk.CTkFrame):
    def __init__(self, parent: Any, db: DBQuery):
        super().__init__(parent)
        self.parent = parent
        self.db = db

        self.message_label = ctk.CTkLabel(self, text="Enter your details.", text_color="white")
        self.username_input = ctk.CTkEntry(self, placeholder_text="Username", height=35, width=200)
        self.password_input = ctk.CTkEntry(
            self, 
            placeholder_text="Password", 
            show="*", 
            height=35, 
            width=200
        )
        self.confirm_password_input = ctk.CTkEntry(
            self, 
            placeholder_text="Confirm Password", 
            show="*", 
            height=35, 
            width=200
        )
        self.register_button = ctk.CTkButton(
            self, 
            text="Register", 
            height=35, 
            width=200, 
            command=self.handle_click_register
        )
        self.login_label = ctk.CTkLabel(
            self, 
            text="Already have an account? Login here.", 
            cursor="hand2", 
            text_color="green"
        )

        self.message_label.pack(padx=10, pady=20)
        self.username_input.pack(padx=10, pady=10)
        self.password_input.pack(padx=10, pady=10)
        self.confirm_password_input.pack(padx=10, pady=10)
        self.register_button.pack(padx=10, pady=10)
        self.login_label.pack(padx=0, pady=20)

        self.login_label.bind("<Button-1>", lambda _: self.parent.switch_frame())


    def handle_click_register(self) -> None:
        username, password = self.username_input.get(), self.password_input.get()

        try:
            self.validate_input(username, password)
        except ValueError as e:
            self.message_label.configure(text=f"{e}")
            return
        
        try:
            hashed_password = Auth.generate_hash_key(password)
            registered_user = self.db.add_user(user_name=username, password=hashed_password)
        except ValueError:
            self.message_label.configure(text=f"{registered_user} already exists.")
            return

        if registered_user:
            self.parent.switch_frame()
            self.message_label.configure(text=f"{registered_user}'s account has been created.")
        else:
            self.message_label.configure(text=f"Something went wrong.")

    
    def validate_input(self, username: str, password: str) -> None:
        if 5 > len(username) < 12:
            raise ValueError(f"Username must be at least 5-12 characters long: {len(username)}")
        
        if 8 > len(password) < 16:
            raise ValueError(f"Password must be at least 8-16 characters long: {len(password)}")

        if password != self.confirm_password_input.get():
            raise ValueError(f"Passwords do not match.")


class LoginWindow(ctk.CTkToplevel):
    def __init__(self, parent: Any):
        super().__init__(parent)
        self.parent = parent

        self.geometry("400x400")
        self.title("Login")
        self.wm_protocol("WM_DELETE_WINDOW", self.handle_close_login)

        self.login_frame = LoginFrame(self, self.parent.db)
        self.register_frame = RegisterFrame(self, self.parent.db)

        self.login_frame.pack(padx=20, pady=20, ipady=10)


    def handle_close_login(self) -> None:
        self.destroy()
        self.parent.quit()


    def logged_in(self, user: User) -> None:
        self.parent.deiconify()
        self.parent.user = user
        self.parent.display_user_data()
        self.destroy()


    def clear_text(self, entry: ctk.CTkEntry) -> None:
        if entry.get() != "":
            entry.delete(0, ctk.END)
            entry._activate_placeholder()
            self.focus()


    def switch_frame(self) -> None:
        if not self.login_frame.winfo_ismapped():
            self.login_frame.message_label.configure(text="Enter your credentials.")
            self.clear_text(self.login_frame.username_input)
            self.clear_text(self.login_frame.password_input)
            self.login_frame.pack(padx=20, pady=20, ipady=10)
            self.register_frame.pack_forget()
            self.title("Login")
            return
        
        self.register_frame.message_label.configure(text="Enter your details.")
        self.clear_text(self.register_frame.username_input)
        self.clear_text(self.register_frame.password_input)
        self.clear_text(self.register_frame.confirm_password_input)
        self.register_frame.pack(padx=20, pady=20, ipady=10)
        self.login_frame.pack_forget()
        self.title("Register")