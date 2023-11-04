from tkinter import messagebox
import tkinter as tk
import os
from PIL import Image, ImageTk
from quotation import QuotationGeneratorGUI




class LoginPage:
    def __init__(self, root):
        self.root = root
        self.app_frame = None
        self.login_frame = tk.Frame(self.root)
        self.login_frame.configure(bg="black")
        self.login_frame.pack()

        # Create frames for left and right columns

        self.left_frame = tk.Frame(self.login_frame, bg="black")
        self.left_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.right_frame = tk.Frame(self.login_frame, bg="black")
        self.right_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.create_widgets()

    def create_widgets(self):

        self.welcome_label = tk.Label(self.left_frame, text="WELCOME", font=("Helvetica", 24, "bold"), fg="white",
                                      bg="black")
        self.welcome_label.pack()

        # Load the image

        images_folder = os.path.join(os.getcwd(), "images")
        image_path = os.path.join(images_folder, "mario.png")
        self.image = Image.open(image_path)
        self.image = self.image.resize((250, 250), Image.LANCZOS)
        self.photo = ImageTk.PhotoImage(self.image)
        self.image_label = tk.Label(
            self.left_frame, image=self.photo, bg="black")
        self.image_label.pack(pady=100)

        # Right Column: Sign In, Username, Password, and Buttons
        signin_icon_path = os.path.join(images_folder, "builder.ico")
        self.signin_icon = Image.open(signin_icon_path)
        self.signin_icon = self.signin_icon.resize((85, 85), Image.LANCZOS)
        self.icon = ImageTk.PhotoImage(self.signin_icon)
        self.signin_icon_label = tk.Label(
            self.right_frame, image=self.icon, bg="black")
        self.signin_icon_label.grid(row=0, column=0, padx=150, pady=(40, 5))

        self.signin_label = tk.Label(self.right_frame, text="SIGN IN", font=(
            "Helvetica", 14), fg="white", bg="black")
        self.signin_label.grid(row=1, column=0, pady=(0, 20))

        self.username_text_label = tk.Label(self.right_frame, text="Username", font=("Helvetica", 10), fg="white",
                                            bg="black")
        self.username_text_label.grid(
            row=2, column=0, sticky="w", padx=(80, 0), pady=(0, 5))

        self.username_entry = tk.Entry(self.right_frame, font=("Helvetica", 10), bg="white", fg="black",
                                       highlightthickness=1, relief="flat", width=35)
        self.username_entry.grid(
            row=3, column=0, sticky="w", padx=(80, 0), pady=(0, 30))

        self.password_text_label = tk.Label(self.right_frame, text="Password", font=("Helvetica", 10), fg="white",
                                            bg="black")
        self.password_text_label.grid(
            row=4, column=0, sticky="w", padx=(80, 0), pady=(0, 5))

        self.password_entry = tk.Entry(self.right_frame, font=("Helvetica", 10), bg="white", fg="black",
                                       highlightthickness=1, relief="flat", width=35)
        self.password_entry.grid(row=5, column=0, sticky="w", padx=(80, 0), )

        self.login_btn = tk.Button(self.right_frame, text="LOGIN", width=18, bd=0, fg="white", bg="#4287f5",
                                   activebackground="#4287f5", cursor="hand2", font=("Helvetica", 12),
                                   highlightthickness=0, command=self.login)
        self.login_btn.grid(row=6, column=0, pady=(30, 0), padx=(20, 0))

    def login(self):

        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if username == "kenton" and password == "1212":
            self.login_frame.destroy()

            # Create the Tkinter GUI window
            self.app_frame = tk.Frame(self.root)

            # Create an instance of the InvoiceGeneratorGUI
            gui = QuotationGeneratorGUI(self.app_frame)
            self.app_frame.pack()

            # Start the Tkinter event loop

        else:
            error = messagebox.showerror(
                "Password", "Username or password does not exist")

            if error:
                self.username_entry.delete(0, tk.END)
                self.password_entry.delete(0, tk.END)
