from application.app import App
import os

app = App()

def CREATE_FOLDER(path: str):
    if not os.path.exists(path):
        os.mkdir(path)

CREATE_FOLDER("images")

if __name__ == "__main__":
    # app.mainloop()
    pass