from customtkinter import *
from libs.database import DBQuery
from libs.auth import Auth

db = DBQuery()

class LoginFrame(CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent

        self.username_input = CTkEntry(self, placeholder_text="Username", height=35, width=200)
        self.username_input.pack(padx=10, pady=10)
        self.password_input = CTkEntry(self, placeholder_text="Password", show="*", height=35, width=200)
        self.password_input.pack(padx=10, pady=10)
        self.login_button = CTkButton(self, text="Login", height=35, width=200, command=self.handle_click_login)
        self.login_button.pack(padx=10, pady=10)

        self.register_label = CTkLabel(self, text="No account? Register here.", cursor="hand2", text_color="green")
        self.register_label.pack(padx=0, pady=20)
        self.register_label.bind("<Button-1>", lambda e: self.parent.handle_switch_frame())

    def handle_click_login(self):
        username, password = self.username_input.get(), self.password_input.get()

        user = db.get_user_data(username)

        if not user:
            self.parent.message_label.configure(text=f"Incorrect username or password.")
            return
        
        if not Auth.verify_password(user.master_password, password):
            self.parent.message_label.configure(text=f"Incorrect username or password.")
            return
        
        
        self.parent.logged_in()
        
        


class RegisterFrame(CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent

        self.username_input = CTkEntry(self, placeholder_text="Username", height=35, width=200)
        self.username_input.pack(padx=10, pady=10)
        self.password_input = CTkEntry(self, placeholder_text="Password", show="*", height=35, width=200)
        self.password_input.pack(padx=10, pady=10)
        self.confirm_password_input = CTkEntry(self, placeholder_text="Confirm Password", show="*", height=35, width=200)
        self.confirm_password_input.pack(padx=10, pady=10)
        self.register_button = CTkButton(self, text="Register", height=35, width=200, command=self.handle_click_register)
        self.register_button.pack(padx=10, pady=10)

        self.register_label = CTkLabel(self, text="Already have an account? Login here.", cursor="hand2", text_color="green")
        self.register_label.pack(padx=0, pady=20)
        self.register_label.bind("<Button-1>", lambda e: self.parent.handle_switch_frame())

    def handle_click_register(self):
        username, password = self.username_input.get(), self.password_input.get()

        try:
            self.validate_input(username, password)
        except ValueError as e:
            self.parent.message_label.configure(text=f"{e}")
            return
        
        try:
            hashed_password = Auth.generate_hash_key(password)
            registered_user = db.add_user(user_name=username, password=hashed_password)
        except ValueError:
            self.parent.message_label.configure(text=f"{registered_user} already exists.")
            return

        if registered_user:
            self.parent.message_label.configure(text=f"{registered_user}'s account has been created.")
            self.parent.switch_frame()
        else:
            self.parent.message_label.configure(text=f"Something went wrong.")

    
    def validate_input(self, username, password):
        if 5 > len(username) < 12:
            raise ValueError(f"Username must be at least 5-12 characters long: {len(username)}")
        
        if 8 > len(password) < 16:
            raise ValueError(f"Password must be at least 8-16 characters long: {len(password)}")

        if password != self.confirm_password_input.get():
            raise ValueError(f"Passwords do not match.")
        
    


class LoginWindow(CTkToplevel):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.geometry("600x400")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.title("Login")
        self.wm_protocol("WM_DELETE_WINDOW", self.handle_close_login)

        self.message_label = CTkLabel(self, text="", text_color="white")
        self.message_label.grid(row=0, column=0)

        self.login_frame = LoginFrame(self)
        self.login_frame.grid(row=1, column=0, padx=10, pady=5, ipady=10)
        self.register_frame = RegisterFrame(self)

        self.parent = parent

    def handle_close_login(self):
        self.destroy()
        self.parent.quit()

    def logged_in(self):
        self.parent.deiconify()

        self.destroy()


    def handle_switch_frame(self):
        self.message_label.configure(text="")
        self.switch_frame()
    
    def clear_text(self, entry):
        if entry.get() != "":
            entry.delete(0, END)
            entry._activate_placeholder()
            self.focus()


    def switch_frame(self):
        if not self.login_frame.grid_info():
            self.clear_text(self.login_frame.username_input)
            self.clear_text(self.login_frame.password_input)
            self.login_frame.grid(row=1, column=0, padx=20, pady=20, ipady=10, sticky="nsew")
            self.register_frame.grid_forget()

            return
        
        self.clear_text(self.register_frame.username_input)
        self.clear_text(self.register_frame.password_input)
        self.clear_text(self.register_frame.confirm_password_input)
        self.register_frame.grid(row=1, column=0, padx=20, pady=20, ipady=10, sticky="nsew")
        self.login_frame.grid_forget()