import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageEnhance
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.units import cm
from num2words import num2words
from datetime import datetime
from tkinter import ttk
from ttkthemes import ThemedStyle
from ttkwidgets.autocomplete import AutocompleteEntry
from ttkwidgets.autocomplete import AutocompleteCombobox
import os
import textwrap
import random
import sqlite3


class Invoice:
    def __init__(self):
        self.number = ""
        self.company_name = ""
        self.company_address = ""
        self.company_logo_path = ""
        self.customer_name = ""
        self.date = ""
        self.items = []
        self.payments = []
        self.balance = ""
        self.database()

    def set_company(self, name, address, logo_path):
        self.company_name = name
        self.company_address = address
        self.company_logo_path = logo_path

    def set_customer(self, name, date):
        self.customer_name = name
        self.date = date

    def add_item(self, description, quantity, price):
        self.items.append((description, quantity, price))

    def add_payments(self, pay_date, pay_details, pays):
        self.payments.append((pay_date, pay_details, pays))

    def get_invoice_number(self, number):

        self.number = number

    def show_balance(self, balance):

        self.balance = balance

    # connect to database
    def database(self):

        self.conn = sqlite3.connect("C:/Users/user/PycharmProjects/invoice/invoice.db")
        self.cursor = self.conn.cursor()

    def create_tables(self):
        self.database()
        self.cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY,
            invoice_number INTEGER,
            customer_name TEXT,
            date TEXT,
            total_amount REAL,
            balance REAL
            )
            '''
        )
        self.cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS items (
            item_id INTEGER PRIMARY KEY,
            invoice_number INTEGER,
            item_name TEXT,
            quantity INTEGER,
            price REAL,
            FOREIGN KEY (invoice_number) REFERENCES invoices (invoice_number)
            )
            '''
        )
        self.cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS payments (
            payment_id INTEGER PRIMARY KEY,
            invoice_number INTEGER,
            date TEXT, 
            description TEXT,
            amount REAL,
            FOREIGN KEY (invoice_number) REFERENCES invoices (invoice_number)
            )
            '''
        )

        # self.conn.commit()
        self.conn.close()

    def generate_pdf(self):

        # Create the PDF canvas
        c = canvas.Canvas("invoice.pdf", pagesize=A4, )

        # function to create frame

        def frame():

            # Creating frame for the document
            frame_x = 15
            frame_y = 15
            frame_width = A4[0] - 30
            frame_height = A4[1] - 40

            return c.rect(frame_x, frame_y, frame_width, frame_height)

        frame()

        # Load the company logo
        logo = Image.open(self.company_logo_path)
        logo_width = 7.72 * cm
        logo_height = 2.9 * cm

        # Set the logo position and size
        logo_left = 2 * cm
        logo_bottom = 650
        c.drawImage(self.company_logo_path, logo_left, logo_bottom, width=logo_width, height=logo_height)

        # Set the INVOICE tag
        c.setFont("Helvetica-Bold", 30)
        c.drawString(logo_width + logo_left + 4.5 * cm, logo_bottom + logo_height + 10, "INVOICE")

        # Set the Invoice Number tag

        c.setFont("Helvetica", 12)
        c.drawString(logo_width + logo_left + 5.95 * cm, logo_bottom + logo_height - 10, f"INV- {self.number}- 2023")

        # Set the company name and address
        c.setFont("Helvetica", 10)
        c.drawString(logo_left, logo_bottom - 30, self.company_name)

        c.setFont("Helvetica", 10)
        company_lines = self.company_address.split("\n")
        for i, line in enumerate(company_lines):
            c.drawString(logo_left, logo_bottom - 50 - i * 20, line)

        # Draw the quotation/Invoice line

        type = "INVOICE"
        canvas_width = A4[0]
        c.setStrokeColor(colors.ReportLabLightBlue)
        c.line(logo_left, logo_bottom - 150, logo_left + logo_width - 10, logo_bottom - 150)
        c.setFont("Helvetica", 10)
        c.drawString(logo_left + logo_width + 15, logo_bottom - 153, type)
        c.line(logo_left + logo_width + 3 * cm, logo_bottom - 150, canvas_width - 1 * cm, logo_bottom - 150)

        # Set the customer details
        c.setFont("Helvetica", 10)
        c.drawString(logo_left, logo_bottom - 180, "Bill To:")
        c.setFont("Helvetica-Bold", 10)
        c.drawString(logo_left, logo_bottom - 200, self.customer_name)
        c.setFont("Helvetica", 10)
        c.drawString(logo_width + logo_left + 4 * cm, logo_bottom - 180, "Order Date:")
        c.drawString(logo_width + logo_left + 6 * cm, logo_bottom - 180, self.date)

        # Create the table for items
        table_style = TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.cornflowerblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("ALIGN", (0, 1), (0, -1), "CENTER"),
            ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("TOPPADDING", (0, 0), (-1, 0), 12),
            ("TOPPADDING", (0, 1), (-1, -1), 12),
            ("LINEBELOW", (0, 1), (-1, -1), 0.2, colors.ReportLabLightBlue),
        ])

        table_style_second_page = TableStyle([

            ("ALIGN", (0, 0), (0, -1), "CENTER"),
            ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
            # ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("TOPPADDING", (0, 0), (-1, 0), 12),
            ("TOPPADDING", (0, 1), (-1, -1), 12),
            ("LINEBELOW", (0, 0), (-1, -1), 0.2, colors.ReportLabLightBlue),
        ])

        table_data = [["SI No", "Description", "Quantity", "Price(ksh)", "Total Amt."]]
        count = 0
        cum_total = 0
        for item in self.items:
            count += 1
            description, quantity, price = item
            total = quantity * price
            cum_total += total
            table_data.append([str(count), description, str(quantity), str(int(price)), str(int(total))])

        # Define column widths
        col_widths = [1.5 * cm, 8.5 * cm, 2 * cm, 3 * cm, 3 * cm]

        # Create the table and set the column widths

        t = Table(table_data, colWidths=col_widths)
        t.setStyle(table_style)

        # Draw the table
        table_width = sum(col_widths)
        table_height = len(table_data) * 0.8 * cm
        t.wrapOn(c, table_width, table_height)
        total_rect_y = 0

        def get_y_pos(count):

            if 1 <= count < 3:
                y_pos = 350

            elif 3 <= count < 5:
                y_pos = 300

            elif 5 <= count < 7:
                y_pos = 250

            elif 7 <= count < 9:
                y_pos = 200

            elif 9 <= count <= 11:
                y_pos = 130

            return y_pos, y_pos - 20

        if 0 <= count <= 11:
            result1, total_rect_y = get_y_pos(count)
            t.drawOn(c, logo_left, result1)

        def new_table():
            global total_rect_y, total_rect_y_new

            first_table_rows = 15

            if count <= 14:
                first_table_rows = count

            # Slicing the table data to include only the first 5 rows
            sliced_table_data = table_data[:first_table_rows]
            t = Table(sliced_table_data, colWidths=col_widths)
            t.setStyle(table_style)

            # Draw the table
            table_width = sum(col_widths)
            table_height = len(sliced_table_data) * 0.8 * cm
            t.wrapOn(c, table_width, table_height)

            t.drawOn(c, logo_left, 30)
            c.showPage()
            frame()

            # start new rest of the table
            rest_of_table_rows = table_data[first_table_rows:count + 1]
            t = Table(rest_of_table_rows, colWidths=col_widths)
            t.setStyle(table_style_second_page)
            length = count + 1 - first_table_rows

            def get_y_pos(length):

                y_pos_mapping = {
                    (1, 3): 750,
                    (3, 5): 700,
                    (5, 7): 650,
                    (7, 9): 600,
                    (9, 11): 550,
                    (11, 12): 500,
                    (12, 13): 450,
                    (13, 15): 400,
                    (15, 17): 350,
                    (17, 19): 300,
                    (19, 21): 250,
                    (21, 23): 200,
                    (23, 25): 250,

                }
                for (start, end), y_position in y_pos_mapping.items():
                    if start <= length < end:
                        return y_position, y_position - 20

            y_position, total_rect_y_new = get_y_pos(length)
            total_rect_y = total_rect_y_new
            # Draw the table
            table_width = sum(col_widths)
            table_height = len(rest_of_table_rows) * 0.8 * cm
            t.wrapOn(c, table_width, table_height)

            t.drawOn(c, logo_left, y_position)

        if count > 11:
            new_table()
            total_rect_y = total_rect_y_new

        # draw rectangle that will contain the total

        total_rect_x = logo_width + logo_left + 1.5 * cm

        total_rect_width = 8.8 * cm
        total_rect_height = 15

        # Define color in Hex
        light_orange = colors.HexColor("#f6c3a6")
        c.setFillColor(light_orange)
        c.rect(total_rect_x, total_rect_y, total_rect_width, total_rect_height, fill=True, stroke=False)

        # create subtotal and total after table
        c.setFont("Helvetica", 11)
        c.setFillColor(colors.black)
        c.drawString(logo_width + logo_left + 2.5 * cm, total_rect_y + 3, "TOTAL")
        c.drawString(logo_width + logo_left + 8.2 * cm, total_rect_y + 3,
                     str(cum_total))

        amount = num2words(cum_total)

        def set_amount(x):
            word = amount.replace("-", " ")
            final_word = word.replace(",", "")

            final_word = final_word.title()

            words = final_word.split()

            y = []

            for x in words:
                if x == "And":
                    x = x.lower()

                y.append(x)

            sentence = " ".join(y)

            return sentence

        # place total amount in words on screen
        # draw rectangle that will contain the total

        # Define color in Hex
        green = colors.HexColor("#c4d79b")
        c.setFillColor(green)
        c.rect(logo_left, total_rect_y - 50, table_width, total_rect_height, fill=True, stroke=False)

        # create subtotal and total after table
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.black)
        c.drawString(logo_left + 0.2 * cm, total_rect_y - 47,
                     "Amount in Words : " + set_amount(amount) + " Shillings Only")

        c.showPage()

        frame()

        # Creating second page title and contents

        top_of_page = 750

        # Create the table for payments
        pay_table_style = TableStyle([
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("ALIGN", (0, 1), (0, -1), "CENTER"),
            ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("SPAN", (0, 0), (-1, 0)),
            ("FONTSIZE", (0, 0), (-1, 0), 12),
            ("TOPPADDING", (0, 0), (-1, 0), 5),
            ("TOPPADDING", (0, 1), (-1, -1), 5),
            ("GRID", (0, 1), (-1, -1), 1, colors.black),
            ("LINEBELOW", (0, 1), (-1, -1), 0.2, colors.ReportLabLightBlue),
        ])

        payment_table_data = [
            ["PAYMENT HISTORY"],  # Title row
        ]
        for pays in self.payments:
            count += 1
            date, description, paid = pays

            payment_table_data.append([date, description, str(int(paid))])

        # Define column widths
        pay_col_widths = [3 * cm, 8.5 * cm, 3 * cm]

        # Create the table and set the column widths

        t = Table(payment_table_data, colWidths=pay_col_widths)
        t.setStyle(pay_table_style)

        # Draw the table
        pay_table_width = sum(pay_col_widths)
        pay_table_height = len(payment_table_data) * 0.8 * cm
        t.wrapOn(c, pay_table_width, pay_table_height)
        t.drawOn(c, logo_left + 1.5 * cm, top_of_page - logo_height / 4 + 70 - pay_table_height)

        # Create the table for balance
        bal_table_style = TableStyle([
            ("ALIGN", (0, 1), (0, -1), "CENTER"),
            ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
            ("TOPPADDING", (0, 1), (-1, -1), 12),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ])

        balance_table_data = []

        balance = self.balance

        balance_table_data.append(["", "Balance", balance])

        # Define column widths
        bal_col_widths = [3 * cm, 8.5 * cm, 3 * cm]

        # Create the table and set the column widths

        t = Table(balance_table_data, colWidths=bal_col_widths)
        t.setStyle(bal_table_style)

        # Draw the table
        bal_table_width = sum(bal_col_widths)
        bal_table_height = len(balance_table_data) * 0.8 * cm
        t.wrapOn(c, bal_table_width, bal_table_height)
        t.drawOn(c, logo_left + 1.5 * cm, top_of_page - logo_height / 4 + 52 - pay_table_height)

        # draw rectangle that will contain the balance
        balance_rect_x = logo_width + logo_left + 1.5 * cm
        balance_rect_y = top_of_page - logo_height / 4 + 35 - pay_table_height
        balance_rect_width = 8.8 * cm
        balance_rect_height = 15

        bal = num2words(balance)

        def set_balance(x):
            word = bal.replace("-", " ")
            final_word = word.replace(",", "")

            final_word = final_word.title()

            words = final_word.split()

            y = []

            for x in words:
                if x == "And":
                    x = x.lower()

                y.append(x)

            sentence = " ".join(y)

            return sentence

        # draw rectangle that will contain the balance
        total_rect_height = 15

        # Define color in Hex
        green = colors.HexColor("#c4d79b")
        c.setFillColor(green)
        c.rect(logo_left, balance_rect_y - 20, table_width, total_rect_height, fill=True, stroke=False)

        # create balnce in words
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.black)
        c.drawString(logo_left + 0.2 * cm, balance_rect_y - 17,
                     "Balance : " + set_balance(bal) + " Shillings Only")

        c.setFont("Helvetica", 10)
        title = "Payment Details:"

        title_width = c.stringWidth(title, "Helvetica", 10)
        c.drawString(logo_left, balance_rect_y - 55, title)
        c.line(logo_left, balance_rect_y - 57, logo_left + title_width, balance_rect_y - 57)

        # Payment details
        history = []
        count = 0

        for x in range(5):
            count += 1
            history.append(count)

        def payment():

            words = f"{history[0]})   Lipa na mpesa\nPaybill\nBusiness Number 247247\nAccount Number 0766 357 558\n\n\n" \
                    f"{history[1]})   Bank Transfer\nEquity Bank\nAccount Number: 1330 2609 4444 7\nKenton Ventures\n\n\n" \
                    f"{history[2]})   Lipa na Mpesa\nPaybill\nBusiness Number: 542542\nAccount Number 357558\n\n\n"

            words_list = words.split("\n")

            def has_digit(sentence):
                for char in sentence:
                    if char.isdigit():
                        return True
                    else:
                        return False

            for word_num, maneno in enumerate(words_list):
                result = has_digit(maneno)
                xx = logo_left + 1 * cm + (0 if result else 0.7) * cm
                y = balance_rect_y - 102 - word_num * 20  # Adjust the line spacing (20 in this example)
                c.drawString(xx, y, maneno)

            return y

        payment()

        def insert_invoice():
            self.database()
            query = '''
                INSERT INTO invoices (invoice_number, customer_name, date, total_amount, balance)
                VALUES (?, ?, ?, ?, ?)
            '''

            values = (self.number, self.customer_name, self.date, cum_total, self.balance)
            self.cursor.execute(query, values)
            self.conn.commit()
            self.conn.close()

        insert_invoice()
        self.database()
        query = '''
            SELECT * FROM invoices
        '''
        query2 = '''
            SELECT * FROM items
        '''

        self.cursor.execute(query)
        rows_inv = self.cursor.fetchall()
        self.cursor.execute(query2)
        rows_items = self.cursor.fetchall()

        # Save the PDF
        c.save()


class InvoiceGeneratorGUI:

    def __init__(self, root):
        self.root = root
        self.invoice = Invoice()
        self.create_widgets()

    # Create menu bar
    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        # Creating file menubar

        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open")
        file_menu.add_separator()
        file_menu.add_separator()
        file_menu.add_command(label="Save")
        file_menu.add_command(label="Save As")
        file_menu.add_separator()
        file_menu.add_separator()
        file_menu.add_command(label="Exit")

        # Creating invoice menubar
        invoice_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Invoice", menu=invoice_menu, command=self.invoicegenerator)

        # Creating quotation menubar
        quotes_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Quotation", menu=quotes_menu, )

    def invoicegenerator(self):
        pass

    def create_widgets(self):
        self.create_menu()
        self.invoice.database()
        self.invoice.create_tables()

        def fetch_invoice_numbers(table_name):
            self.invoice.database()
            query_check_invoice_number = f'''
                                    SELECT invoice_number FROM {table_name}
                                    '''

            self.invoice.cursor.execute(query_check_invoice_number)
            query_check_invoice_results = set(row[0] for row in self.invoice.cursor.fetchall())

            return query_check_invoice_results

        def delete_records_if_not_in_invoice_table():

            invoice_numbers = fetch_invoice_numbers("invoices")
            items_numbers = fetch_invoice_numbers("items")
            payments_numbers = fetch_invoice_numbers("payments")

            # Identify invoice numbers that are in items and payments but not in invoices
            missing_invoice_numbers = items_numbers.union(payments_numbers) - invoice_numbers
            # Delete records associated with missing invoice numbers from items table

            for inv_number in missing_invoice_numbers:
                delete_record_from_items(inv_number)

            for inv_number in missing_invoice_numbers:
                delete_records_from_payments(inv_number)

        def delete_record_from_items(invoice_num):
            self.invoice.cursor.execute('''DELETE FROM items WHERE invoice_number = ? ''', (invoice_num,))
            self.invoice.conn.commit()

        def delete_records_from_payments(invoice_num):
            self.invoice.cursor.execute('''DELETE FROM payments WHERE invoice_number = ? ''', (invoice_num,))
            self.invoice.conn.commit()

        delete_records_if_not_in_invoice_table()

        quantities_list = ["Cabro 60mm", "Pavers 60mm", "Trihex 60mm", "Venus 60mm", "Splendor 60mm", "Libra 60mm",
                           "Hexagon 60mm", "Zig-zag 60mm",
                           "Uni 60mm", "Quad 60mm", "Road kerbs", "Road channels", "Slabs", "Cement", "Dust",
                           "Rock chips",
                           "Labor", "Kajiado sand", "Ground roller", "Cabro cutter", "Sand"]
        status_list = ["Paid", "Incomplete"]
        # Create a canvas to hold your content.
        self.master_canvas = tk.Canvas(self.root, relief=tk.FLAT, bd=0, bg="#a6abaa", borderwidth=0,
                                       highlightthickness=1)
        self.main_frame = tk.Frame(self.master_canvas, bg="#a6abaa")
        # Create company details
        self.company_main_frame = tk.Frame(self.main_frame, relief=tk.GROOVE, bd=3, bg="#a6abaa")
        self.company_main_frame.pack(fill="x", pady=(20, 20), padx=(15, 0))

        self.company_details_frame = tk.Frame(self.company_main_frame, relief=tk.GROOVE, bd=3, bg="#a6abaa")
        self.company_details_frame.grid(row=0, column=0, padx=(0, 10))

        self.company_name_label = tk.Label(self.company_details_frame, text="Company Name:", bg="#a6abaa",
                                           font=("bold", 10))
        self.company_name_label.grid(row=0, column=0, padx=(5, 45), pady=5, sticky="w")

        self.company_name_entry = tk.Entry(self.company_details_frame, width=40)
        self.company_name_entry.grid(row=0, column=1, padx=(0, 200), pady=5, sticky="w")

        self.company_address_label = tk.Label(self.company_details_frame, text="Company Address:", bg="#a6abaa",
                                              font=("bold", 10))

        self.company_address_label.grid(row=1, column=0, padx=(5, 45), pady=5, sticky="w")

        self.company_address_text = tk.Text(self.company_details_frame, height=4, width=30)
        self.company_address_text.grid(row=1, column=1, padx=(0, 5), pady=20, sticky="w")

        self.company_logo_button = tk.Button(self.company_details_frame, text="Select Company Logo"
                                             , command=self.select_logo)
        self.company_logo_button.grid(row=2, column=0, columnspan=2, padx=(100, 35), pady=5, sticky="w")

        self.invoice_frame = tk.Frame(self.company_main_frame, relief=tk.FLAT, bg="#a6abaa", )
        self.invoice_frame.grid(row=0, column=1, padx=(0, 0), sticky="w")

        self.invoice_search_entry = tk.Entry(self.invoice_frame, width=20)
        self.invoice_search_entry.grid(row=0, column=1, padx=(0, 5), pady=(0, 80), sticky="w")

        def update_search_results(event):

            search_text = self.invoice_search_entry.get()
            self.invoice.database()
            query = '''
                        SELECT * FROM invoices 
                        WHERE customer_name = ? OR invoice_number = ?
                    '''
            self.invoice.cursor.execute(query, (self.invoice_search_entry.get(), self.invoice_search_entry.get()))

            search_results = self.invoice.cursor.fetchall()
            self.invoice.conn.close()
            filtered_result = []
            for x in search_results:
                for result in x:
                    if search_text in str(result):
                        position = len(filtered_result)
                        filtered_result.append(search_results)

            show_search_results(filtered_result)

        # bind with key release listener
        self.invoice_search_entry.bind("<KeyRelease>", update_search_results)

        def show_search_results(results):
            global number
            self.search_results_list.delete(0, tk.END)
            count = []
            if results:
                for result in results:
                    number = result[len(count)][1]
                    output = result[len(count)][2]
                    count.append(result)
                    self.search_results_list.insert(tk.END, output)

                self.search_results_list.grid(row=0, column=3, padx=(0, 5), pady=(0, 0), sticky="w")

            else:
                self.search_results_list.grid_forget()

        def show_selected_result(event):
            selected_index = self.search_results_list.curselection()

            if selected_index:
                selected_result = self.search_results_list.get(selected_index)
                self.invoice_search_entry.delete(0, tk.END)
                self.invoice_search_entry.insert(0, selected_result)
                self.invoice_number_label.config(text=f"INV-{number}- 2023")
                self.invoice.get_invoice_number(number)
                self.search_results_list.grid_forget()

                # populate the invoice data fetched from database
                self.invoice.database()
                query = '''
                        SELECT customer_name, date, total_amount, balance FROM invoices WHERE invoice_number = ?
                        
                '''

                self.invoice.cursor.execute(query, (number,))
                names_results = self.invoice.cursor.fetchall()
                for rows in names_results:
                    name = rows[0]
                    date = rows[1]
                    total = rows[2]
                    balance = rows[3]

                # clear all other entry boxes
                self.item_description_entry.delete(0, tk.END)
                self.item_quantity_entry.delete(0, tk.END)
                self.item_price_entry.delete(0, tk.END)

                self.payment_details_entry.delete(0, tk.END)
                self.payment_date_entry.delete(0, tk.END)
                self.payment_label_entry.delete(0, tk.END)

                self.customer_name_entry.delete(0, tk.END)
                self.date_text.delete(0, tk.END)

                self.treeview.delete(*self.treeview.get_children())
                self.payment_treeview.delete(*self.payment_treeview.get_children())

                def update_invoice():

                    # First clear anything from the current lists
                    self.invoice.items.clear()
                    self.invoice.payments.clear()
                    self.customer_name_entry.insert(0, name)
                    self.date_text.insert(0, date)

                    query_2 = '''
                              SELECT item_name, quantity, price FROM items WHERE invoice_number = ?

                                    '''
                    self.invoice.cursor.execute(query_2, (number,))
                    items_result = self.invoice.cursor.fetchall()
                    item_count = 0

                    query_3 = '''
                            SELECT date, description, amount FROM payments WHERE invoice_number = ?

                                                        '''
                    self.invoice.cursor.execute(query_2, (number,))
                    items_result = self.invoice.cursor.fetchall()
                    item_count = 0
                    for item in items_result:
                        self.invoice.items.append(item)
                        item_count += 1
                        item_name, quantity, price = item
                        product = quantity * price
                        self.treeview.insert("", "end", text=str(item_count),
                                             values=(item_name, quantity, price, str(int(product))))
                    self.calculate_total()

                    self.invoice.cursor.execute(query_3, (number,))
                    payment_result = self.invoice.cursor.fetchall()
                    pay_count = 0
                    for pay in payment_result:
                        self.invoice.payments.append(pay)
                        pay_count += 1
                        pay_date, pay_description, paid_amount = pay
                        self.payment_treeview.insert("", "end", text=str(pay_count),
                                                     values=(pay_date, pay_description, paid_amount))

                    self.calculate_total()
                    self.get_balance()

                update_invoice()

            # Write function to update database after load invoice function is run

        self.search_results_list = tk.Listbox(self.invoice_frame, height=5, width=30)
        self.search_results_list.grid(row=0, column=3, padx=(0, 0), pady=(0, 0), sticky="w", )
        self.search_results_list.bind("<ButtonRelease-1>", show_selected_result)
        self.search_results_list.grid_forget()

        self.invoice_search_label = tk.Label(self.invoice_frame, text="Search Invoice:", bg="#a6abaa")
        self.invoice_search_label.grid(row=0, column=0, padx=(5, 45),
                                       pady=(0, 80), sticky="w")

        self.image = "images/search-icon.jpg"
        self.image = Image.open(self.image)
        self.image = self.image.resize((15, 15), Image.LANCZOS)
        self.image = ImageTk.PhotoImage(self.image, )


        self.invoice_search_btn = tk.Button(self.invoice_frame, image=self.image, bg="#a6abaa",
                                            command=self.load_invoice)
        self.invoice_search_btn.grid(row=0, column=1, padx=(85, 0), pady=(0, 80))

        self.invoice_number_label_text = tk.Label(self.invoice_frame, text="Invoice Number:", bg="#a6abaa")
        self.invoice_number_label_text.grid(row=1, column=0, padx=(5, 45), pady=5, sticky="w")

        self.invoice_number_label = tk.Label(self.invoice_frame, text=f"INV-{self.invoice.number}- 2023", width=25)
        self.invoice_number_label.grid(row=1, column=1, padx=(0, 5), pady=(0, 5), sticky="w")

        self.invoice_status = tk.Label(self.invoice_frame, text="Invoice Status:", bg="#a6abaa")
        self.invoice_status.grid(row=2, column=0, padx=(5, 45), pady=5, sticky="w")

        self.invoice_status_selection = AutocompleteCombobox(self.invoice_frame, completevalues=status_list, )
        self.invoice_status_selection.grid(row=2, column=1, padx=(0, 5), pady=5, sticky="w")

        self.details_frame = tk.Frame(self.main_frame, relief=tk.GROOVE, bd=3, bg="#a6abaa")
        self.details_frame.pack(fill="x", pady=(20, 20), padx=(15, 0))

        self.customer_details_frame = tk.Frame(self.details_frame, relief=tk.GROOVE, bd=3, bg="#a6abaa", )
        self.customer_details_frame.grid(row=0, column=0, padx=(0, 15))

        self.customer_name_label = tk.Label(self.customer_details_frame, text="Customer Name:", bg="#a6abaa")
        self.customer_name_label.grid(row=0, column=0, padx=(5, 45), pady=(15, 15), sticky="w")

        self.customer_name_entry = tk.Entry(self.customer_details_frame, width=33)
        self.customer_name_entry.grid(row=0, column=1, padx=(20, 243), pady=(15, 15), sticky="w")

        self.date_label = tk.Label(self.customer_details_frame, text="Date:", bg="#a6abaa")
        self.date_label.grid(row=1, column=0, padx=(5, 45), pady=15, sticky="w")

        self.date_text = tk.Entry(self.customer_details_frame, width=33)
        self.date_text.grid(row=1, column=1, padx=(20, 0), pady=5, sticky="w")

        self.item_details_frame = tk.Frame(self.details_frame, relief=tk.FLAT, bg="#a6abaa", )
        self.item_details_frame.grid(row=0, column=1, padx=(0, 0), sticky="w")

        self.item_description_label = tk.Label(self.item_details_frame, text="Item Description:", bg="#a6abaa")
        self.item_description_label.grid(row=0, column=0, padx=(5, 45), pady=5, sticky="w")

        self.item_description_entry = AutocompleteCombobox(self.item_details_frame, completevalues=quantities_list,
                                                           width=30)
        self.item_description_entry.grid(row=0, column=1, padx=(0, 5), pady=5, sticky="w")

        self.item_quantity_label = tk.Label(self.item_details_frame, text="Quantity:", bg="#a6abaa")
        self.item_quantity_label.grid(row=1, column=0, padx=(5, 45), pady=5, sticky="w")

        self.item_quantity_entry = tk.Spinbox(self.item_details_frame, from_=0, to=1000)
        self.item_quantity_entry.grid(row=1, column=1, padx=(0, 5), pady=5, sticky="w")

        self.item_price_label = tk.Label(self.item_details_frame, text="Price:", bg="#a6abaa")
        self.item_price_label.grid(row=2, column=0, padx=(5, 45), pady=5, sticky="w")

        self.item_price_entry = tk.Entry(self.item_details_frame, width=20)
        self.item_price_entry.grid(row=2, column=1, padx=(0, 5), pady=5, sticky="w")

        def on_enter_keypress(event):
            if event.keysym == "Return" and self.item_price_entry.get():
                self.add_item()

        self.item_price_entry.bind("<KeyPress>", on_enter_keypress)

        self.history_label = tk.Label(self.main_frame, text="Payment History", font=('Helvetica', 12, 'bold'), bd=7,
                                      relief=tk.GROOVE)
        self.invoice_history_text = tk.Text(self.main_frame, height=18, width=30)

        self.add_item_button = tk.Button(self.item_details_frame, text="Add Item", command=self.add_item, width=12)
        self.add_item_button.grid(row=0, column=2, padx=(50, 5), pady=5, sticky="w")

        # Create treeview to view selections
        self.purchase_list_frame = tk.Frame(self.main_frame, relief=tk.GROOVE, bd=3, bg="#a6abaa")
        self.purchase_list_frame.pack(pady=(10, 10))
        self.current_total_label = tk.Label(self.purchase_list_frame, text="SUB TOTAL:", font=("Helvetica", 11,)
                                            , bg="#a6abaa")
        self.current_total_textbox = tk.Label(self.purchase_list_frame, text="0", font=("Helvetica", 11, "bold"),
                                              bg="#a6abaa")

        def on_item_delete_keypress(event):
            selected_item = self.treeview.selection()

            if selected_item and event.keysym == "Delete":
                self.delete_item()

        self.treeview_label = tk.Label(self.purchase_list_frame, text=" I T E M S       L I S T ",
                                       font=("Helevetica", 14, "bold"),
                                       width=30, bg="#a6abaa")
        self.treeview_label.grid(row=0, column=0, columnspan=2, pady=(5, 0))

        self.treeview = ttk.Treeview(self.purchase_list_frame, columns=["Description", "Quantity", "Price", "Total"])
        self.treeview.heading("#0", text="SI No")
        self.treeview.heading("Description", text="Description")
        self.treeview.heading("Quantity", text="Quantity")
        self.treeview.heading("Price", text="Price (ksh)")
        self.treeview.heading("Total", text="Total Amt.")

        # Create a vertical scrollbar

        self.scroll_bar = ttk.Scrollbar(self.purchase_list_frame, orient="vertical")
        self.treeview.config(yscrollcommand=self.scroll_bar.set)
        self.scroll_bar.config(command=self.treeview.yview)

        self.treeview.column("#0", width=50, anchor="center")
        self.treeview.column("Description", width=300, anchor="w")
        self.treeview.column("Quantity", width=100, anchor="center")
        self.treeview.column("Price", width=100, anchor="e")
        self.treeview.column("Total", anchor="e")

        self.treeview.grid(row=1, column=0, columnspan=2, pady=5, padx=(15, 0))
        self.treeview.bind("<KeyPress>", on_item_delete_keypress)

        self.current_total_label.grid(row=2, column=0, pady=5, padx=(100, 0), sticky="e")

        self.current_total_textbox.grid(row=2, column=1, pady=5, padx=(100, 0), sticky="w")
        self.scroll_bar.grid(row=1, column=2, pady=5, sticky="ns")

        # Payment History section
        # Create treeview to view selections
        self.payment_frame = tk.Frame(self.main_frame, relief=tk.GROOVE, bd=3, bg="#a6abaa", )
        self.payment_frame.pack(pady=(10, 10))

        self.payment_treeview_label = tk.Label(self.payment_frame, text="PAYMENT HISTORY",
                                               font=("Helevetica", 12, "bold"),
                                               width=30, bg="#a6abaa")
        self.payment_treeview_label.grid(row=0, column=0, columnspan=4, pady=(5, 0))

        self.payment_date_label = tk.Label(self.payment_frame, text="Date:", bg="#a6abaa")
        self.payment_date_label.grid(row=1, column=0, padx=(5, 35), pady=(15, 15), sticky="w")

        self.payment_date_entry = tk.Entry(self.payment_frame, width=25)
        self.payment_date_entry.grid(row=1, column=1, padx=(20, 50), pady=(15, 15), sticky="w")

        self.payment_label_text = tk.Label(self.payment_frame, text="Pay:", bg="#a6abaa")
        self.payment_label_text.grid(row=2, column=0, padx=(5, 35), pady=15, sticky="w")

        self.payment_label_entry = tk.Entry(self.payment_frame, width=25)
        self.payment_label_entry.grid(row=2, column=1, padx=(20, 0), pady=5, sticky="w")

        self.payment_details_label = tk.Label(self.payment_frame, text="Details:", bg="#a6abaa")
        self.payment_details_label.grid(row=1, column=2, padx=(25, 35), pady=15, sticky="w")

        self.payment_details_entry = tk.Entry(self.payment_frame, width=25)
        self.payment_details_entry.grid(row=1, column=3, padx=(0, 20), pady=5, sticky="w")

        self.pay_btn = tk.Button(self.payment_frame, text="Pay", width=15, command=self.add_pay)
        self.pay_btn.grid(row=2, column=3, pady=5, columnspan=2, padx=(10, 20), sticky="w")

        self.pay_edit_btn = tk.Button(self.payment_frame, text="Delete", width=15, command=self.delete_payment)
        self.pay_edit_btn.grid(row=2, column=2, padx=(30, 0), pady=5, sticky="w")

        self.payment_treeview = ttk.Treeview(self.payment_frame, columns=["Date", "Description", "Payment"],
                                             show="headings")
        self.payment_treeview.heading("#0", text="SI No")
        self.payment_treeview.heading("Date", text="Date")
        self.payment_treeview.heading("Description", text="Description")
        self.payment_treeview.heading("Payment", text="Payment (ksh)")
        # Create a vertical scrollbar

        self.scroll_bar = ttk.Scrollbar(self.payment_frame, orient="vertical")
        self.payment_treeview.config(yscrollcommand=self.scroll_bar.set)
        self.scroll_bar.config(command=self.payment_treeview.yview)

        self.payment_treeview.column("#0", width=50, anchor="center")
        self.payment_treeview.column("Date", width=100, anchor="w")
        self.payment_treeview.column("Description", width=250, anchor="w")
        self.payment_treeview.column("Payment", width=150, anchor="center")

        # self.payment_treeview.column("Total", anchor="e")

        def on_payment_delete_keypress(event):
            selected_item = self.payment_treeview.selection()

            if selected_item and event.keysym == "Delete":
                self.delete_payment()

        self.payment_treeview.grid(row=3, column=0, columnspan=4, pady=5, padx=(15, 0))
        self.payment_treeview.bind("<KeyPress>", on_payment_delete_keypress)

        self.scroll_bar.grid(row=3, column=3, padx=(105, 0), pady=5, sticky="ns")

        self.current_balance_label = tk.Label(self.payment_frame, text="BALANCE:", font=("Helvetica", 11,)
                                              , bg="#a6abaa")
        self.current_balance_textbox = tk.Label(self.payment_frame, text="0", font=("Helvetica", 11, "bold"),
                                                bg="#a6abaa")

        self.current_balance_label.grid(row=4, column=1, pady=5, padx=(100, 0), sticky="e")

        self.current_balance_textbox.grid(row=4, column=2, pady=5, padx=(100, 0), sticky="w")

        self.generate_button = tk.Button(self.payment_frame, text="Generate Invoice", width=20,
                                         command=self.generate_invoice)

        self.generate_button.grid(row=5, column=1, padx=(150, 5), pady=(15, 5), sticky="w", columnspan=2, )

        # Adding buttons to add or delete items from treeview
        self.delete_item_button = tk.Button(self.item_details_frame, text="Delete Item", command=self.delete_item,
                                            width=12)
        self.delete_item_button.grid(row=2, column=2, padx=(50, 5), pady=5, sticky="w")

        self.main_scroll_bar = ttk.Scrollbar(self.master_canvas, orient="vertical")
        self.master_canvas.config(yscrollcommand=self.main_scroll_bar.set)
        self.main_scroll_bar.config(command=self.master_canvas.yview)

        # Add the scrollbar and main frame to the canvas.
        self.main_scroll_bar.pack(side="right", fill="y")
        self.master_canvas.pack(side="left", fill="both", expand=True)
        self.master_canvas.create_window((0, 0), window=self.main_frame, anchor="nw")

        # Bind the event for updating the scrolling region when the window size changes.

        def configure_canvas(event):
            # Update the scrolling region when the main frame size changes.
            self.master_canvas.configure(scrollregion=self.master_canvas.bbox("all"))

        self.main_frame.bind("<Configure>", configure_canvas)

        def on_mousewheel(event):
            # Check the direction of the scrolling (up or down).
            if event.delta > 0:
                self.master_canvas.yview_scroll(-1, "units")

            if event.delta < 0:
                self.master_canvas.yview_scroll(1, "units")

        self.master_canvas.bind("<MouseWheel>", on_mousewheel)

        def get_invoice_number():
            while True:
                number = random.randint(1, 1000)

                # Check if the generated invoice number already exists in the database
                self.invoice.database()
                query = '''
                        SELECT invoice_number from invoices WHERE invoice_number = ?
                '''

                self.invoice.cursor.execute(query, (number,))
                existing_invoice = self.invoice.cursor.fetchall()

                if not existing_invoice:
                    self.invoice.get_invoice_number(number)
                    self.invoice_number_label.config(text=f"INV-{self.invoice.number}- 2023")

                    return number

        get_invoice_number()

    def load_invoice(self):
        # fetch data from
        self.invoice.database()
        query = '''
            SELECT * FROM invoices 
            WHERE customer_name = ? OR invoice_number = ?
        '''
        self.invoice.cursor.execute(query, (self.invoice_search_entry.get(), self.invoice_search_entry.get()))

        search_results = self.invoice.cursor.fetchall()
        self.invoice.conn.close()

        if search_results:
            messagebox.showinfo("Success", "Entries found")

            # clear all other entry boxes
            self.item_description_entry.delete(0, tk.END)
            self.item_quantity_entry.delete(0, tk.END)
            self.item_price_entry.delete(0, tk.END)

            self.payment_details_entry.delete(0, tk.END)
            self.payment_date_entry.delete(0, tk.END)
            self.payment_label_entry.delete(0, tk.END)

            self.customer_name_entry.delete(0, tk.END)
            self.date_text.delete(0, tk.END)

            self.treeview.delete(*self.treeview.get_children())
            self.payment_treeview.delete(*self.payment_treeview.get_children())

            self.update_invoice()

    # Write function to update database after load invoice function is run

    def update_invoice(self):
        self.customer_name_entry.insert(0, tk.END)
        self.date_text.delete(0, tk.END)

    def select_logo(self):

        entered_company_name = self.company_name_entry.get().strip()
        entered_company_address = self.company_address_text.get("1.0", tk.END).strip()

        if not entered_company_name:
            default_name = "KENTON PAVERS"
            self.company_name_entry.insert(tk.END, default_name)
            entered_company_name = default_name

        if not entered_company_address:
            default_address = "RONGAI\n" \
                              "PO BOX 8019 – 00300\n" \
                              "Tel: +254 705 357 558\n" \
                              "Email:sales@kentonkenya.com\n" \
                              "www.kentonkenya.com" \

            self.company_address_text.insert(tk.END, default_address)
            entered_company_address = default_address

        # Get the path to the "images" folder
        images_folder = os.path.join(os.getcwd(), "images")

        # Example of accessing an image in your code
        image_path = os.path.join(images_folder, "ktn.png")
        refined_path = image_path.replace("\\", "/")

        logo_path = filedialog.askopenfilename(filetypes=(("Image files", "*.png *.jpg *.jpeg"), ("All files", "*.*")))

        if logo_path:
            self.invoice.set_company(entered_company_name, entered_company_address, logo_path)

        else:

            self.invoice.set_company(entered_company_name, entered_company_address, refined_path)

    def add_item(self):

        try:
            description = self.item_description_entry.get()
            quantity = int(self.item_quantity_entry.get())
            price = float(self.item_price_entry.get())
            self.invoice.add_item(description, quantity, price)

            self.invoice.database()
            query = '''
                    INSERT INTO items (invoice_number, item_name, quantity, price)
                    VALUES (?, ?, ?, ?)
                '''

            values = (self.invoice.number, description, quantity, price)
            self.invoice.cursor.execute(query, values)
            self.invoice.conn.commit()
            self.invoice.conn.close()

            # Clear the entry fields
            self.item_description_entry.delete(0, tk.END)
            self.item_quantity_entry.delete(0, tk.END)
            self.item_price_entry.delete(0, tk.END)

            # Update the Treeview with the entered items
            item_num = len(self.invoice.items)
            total = quantity * price
            self.treeview.insert("", "end", text=str(item_num),
                                 values=(description, str(quantity), str(int(price)), str(int(total))))
            self.calculate_total()
            self.get_balance()

        except ValueError:
            # Handle the case where quantity or price is not a valid integer or float
            messagebox.showerror("Error", "Quantity and price must be valid numbers.")

        except Exception as e:
            # Handle other exceptions
            messagebox.showerror("Error", "An error occurred while adding the item.")

    def delete_item(self):
        selected_item = self.treeview.selection()

        if selected_item:
            item_num = int(self.treeview.item(selected_item, "text"))
            # Delete the item from the invoice and the Treeview
            popped = self.invoice.items.pop(item_num - 1)
            popped
            self.treeview.delete(selected_item)

            # Delete from the database the item in question
            self.invoice.database()
            query = '''
                            DELETE FROM items WHERE item_name = ? AND invoice_number = ?
                            
                        '''

            values = (popped[0], self.invoice.number)
            self.invoice.cursor.execute(query, values)
            self.invoice.conn.commit()
            self.invoice.conn.close()

            # Re-index the items in the Treeview
            for idx, item in enumerate(self.treeview.get_children()):
                self.treeview.item(item, text=str(idx + 1))

            self.calculate_total()
            self.get_balance()

    def calculate_total(self):

        cum_total = sum(int(self.treeview.item(item, "values")[-1]) for item in self.treeview.get_children())

        # update label to reflect the total

        self.current_total_textbox.config(text=f"{cum_total}")

        return cum_total

    def add_pay(self):

        try:
            pay_description = self.payment_details_entry.get()
            pay_date = self.payment_date_entry.get()
            payment = int(self.payment_label_entry.get())
            self.invoice.add_payments(pay_date, pay_description, payment)

            self.invoice.database()
            query = '''
                            INSERT INTO payments (invoice_number, date, description, amount)
                            VALUES (?, ?, ?, ?)
                        '''

            values = (self.invoice.number, pay_date, pay_description, payment)
            self.invoice.cursor.execute(query, values)
            self.invoice.conn.commit()
            self.invoice.conn.close()

            # Clear the entry fields
            self.payment_details_entry.delete(0, tk.END)
            self.payment_date_entry.delete(0, tk.END)
            self.payment_label_entry.delete(0, tk.END)

            item_num = len(self.invoice.payments)

            self.payment_treeview.insert("", "end", text=str(item_num),
                                         values=(str(pay_date), pay_description, str(int(payment))))

            self.get_balance()

        except ValueError as ve:
            messagebox.showerror("Error", "Payment must be an integer")

    def delete_payment(self):
        selected_item = self.payment_treeview.selection()

        if selected_item:
            item_num = int(self.payment_treeview.item(selected_item, "text"))
            # Delete the item from the invoice and the Treeview
            popped = self.invoice.payments.pop(item_num - 1)
            popped
            self.payment_treeview.delete(selected_item)

            # Delete from the database the payment in question
            self.invoice.database()
            query = '''
                    DELETE FROM payments WHERE date = ? AND invoice_number = ?

                    '''

            values = (popped[0], self.invoice.number)
            self.invoice.cursor.execute(query, values)
            self.invoice.conn.commit()
            self.invoice.conn.close()

            # Re-index the items in the Treeview
            for idx, item in enumerate(self.payment_treeview.get_children()):
                self.payment_treeview.item(item, text=str(idx + 1))

        self.get_balance()

    def get_balance(self):

        summation = sum(
            float(self.payment_treeview.item(item, "values")[-1]) for item in self.payment_treeview.get_children())
        balance = self.calculate_total() - summation
        # update label to reflect the total
        self.invoice.show_balance(balance)
        self.current_balance_textbox.config(text=f"{balance}")

        return balance

    def generate_invoice(self):

        try:

            entered_date = self.date_text.get().strip()
            entered_company_name = self.company_name_entry.get().strip()
            entered_company_address = self.company_address_text.get("1.0", tk.END).strip()

            if not entered_date:
                todays_date = datetime.now().strftime("%d %B %Y")
                self.date_text.insert(tk.END, todays_date)
                entered_date = todays_date

            if not entered_company_name and entered_company_address:
                # Handle the case where the company name is not entered
                raise ValueError("Please enter company details")

            self.invoice.set_customer(self.customer_name_entry.get().strip(), entered_date)
            self.invoice.generate_pdf()

        except ValueError as ve:
            # Handle the case where the company name is not entered
            messagebox.showerror("Error", str(ve))


# Create the Tkinter GUI window
root = tk.Tk()
root.title("Invoice Generator")
root.configure(bg="#a6abaa")


images_folder = os.path.abspath('images')
icon_path = os.path.join(images_folder, '33755_computer game_mario_super mario_icon.png')
root.iconphoto(True, tk.PhotoImage(file=icon_path))
root.geometry("1200x600")

# Create an instance of the InvoiceGeneratorGUI
gui = InvoiceGeneratorGUI(root)

# Start the Tkinter event loop
root.mainloop()
