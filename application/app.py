from .login import LoginWindow
import customtkinter

customtkinter.set_default_color_theme("green")
customtkinter.set_appearance_mode("dark")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("600x500")
        self.title("Password Manager")

        self.login_window = LoginWindow(self)
        self.withdraw()

        self.button = customtkinter.CTkButton(self, command=self.buttonclick)
        self.button.grid(row=0, column=0, padx=20, pady=10)


    def buttonclick(self):
        print("Welcome to Tkinter!")

# app = App()
# app.mainloop()