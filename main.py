import tkinter as tk
from login import LoginPage
import sys


def main():
    root = tk.Tk()
    root.title("Login")
    root.geometry("700x500")

    login_page = LoginPage(root)
    # Handle the window close event by killing the application

    root.mainloop()


if __name__ == "__main__":
    main()
