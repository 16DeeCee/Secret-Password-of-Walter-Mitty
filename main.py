from application.app import App
from libs.database import DBQuery
import os

app = App()
db = DBQuery()

db.create_tables()

# folder for storing images
if not os.path.exists("images"):
    os.mkdir("images")

if __name__ == "__main__":
    app.mainloop()