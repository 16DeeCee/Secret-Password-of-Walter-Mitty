# Secret Password of Walter Mitty
This project is a password checker and manager with the following capabilities:
- Create a user account to store passwords
- Encrypt and retrieve passwords using AES encryption, hidden in the images through steganography
- Check if a password has been compromised

## Features
- **Password Breach Checker**: Checks if the password has been leaked using HaveIBeenPwned ([HIBP](https://haveibeenpwned.com/API/v3#PwnedPasswords)) API
- **AES Encryption**: Securely encrypts password before hiding it in an image
- **Steganography**: Hides encrypted password bytes in image files
- **Master Password Protection**: Master password is used to authenticate user and to derive AES encryption key for each stored passwords.

## Technologies/Tools Used
- **Python**: Core programming language
- **Cryptography**: For AES and encryption and authentication
- **CustomTkinter**: Used for Graphical User Interface (GUI)
- **SQLAlchemy**: ORM (overkill, I know. Only used for the sake of learning.)
- **SQLite**: Database

## Installation
1. Clone the repository:
```bash
git clone https://github.com/16DeeCee/Secret-Password-of-Walter-Mitty.git
cd Secret-Password-of-Walter-Mitty
```
2. Install required packages:
```bash
pip install -r requirements.txt
```
3. Run the application:
```bash
python main.py
```

