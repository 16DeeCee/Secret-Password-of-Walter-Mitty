import customtkinter as ctk
from typing import Any, List

class MessageBox(ctk.CTkToplevel):
    def __init__(self, parent: Any, title: str = "", message: str = "", buttons: List[str] = ["OK"]):
        super().__init__(parent)
        self.parent = parent
        self.geometry("300x150")
        self.resizable(False, False)
        self.transient(self.parent)
        self.grab_set()
        self.title(title)

        self.result = None

        self.message_label = ctk.CTkLabel(self, text=message, wraplength=250)
        self.message_label.pack(padx=10, pady=10)

        for text in buttons:
            btn = self.message_button = ctk.CTkButton(
                self, 
                text=text, 
                command=lambda e = text: self.handle_button_click(e)
            )
            btn.pack(side="left", padx=5)
    
    def handle_button_click(self, text: str) -> None:
        self.result = text
        self.destroy()
        
    
    @staticmethod
    def show(parent: Any, **kwargs) -> str:
        message_box = MessageBox(parent, **kwargs)
        parent.wait_window(message_box)

        return message_box.result