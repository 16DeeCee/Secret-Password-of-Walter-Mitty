import os

def CREATE_FOLDER(path: str):
    if not os.path.exists(path):
        os.mkdir(path)

CREATE_FOLDER("images")

if __name__ == "__main__":
    pass # run tkinter