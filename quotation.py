import tkinter as tk
from tkinter import filedialog
from PIL import Image
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


class Invoice:
    def __init__(self):
        self.company_name = ""
        self.company_address = ""
        self.company_logo_path = ""
        self.customer_name = ""
        self.date = ""
        self.items = []

    def set_company(self, name, address, logo_path):
        self.company_name = name
        self.company_address = address
        self.company_logo_path = logo_path

    def set_customer(self, name, date):
        self.customer_name = name
        self.date = date

    def add_item(self, description, quantity, price):
        self.items.append((description, quantity, price))

    def generate_pdf(self):
        # Create the PDF canvas
        c = canvas.Canvas("quotation.pdf", pagesize=A4, )

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

        # Set the company name and address
        c.setFont("Helvetica", 10)
        c.drawString(logo_width + logo_left + 2 * cm, logo_bottom + logo_height + 10, self.company_name)

        c.setFont("Helvetica", 10)
        company_lines = self.company_address.split("\n")
        for i, line in enumerate(company_lines):
            c.drawString(logo_width + logo_left + 2 * cm, logo_bottom + logo_height - 10 - i * 20, line)

        # Draw the quotation/Invoice line

        type = "QUOTATION"
        canvas_width = A4[0]
        c.setStrokeColor(colors.ReportLabLightBlue)
        c.line(logo_left, logo_bottom - 60, logo_left + logo_width - 10, logo_bottom - 60)
        c.setFont("Helvetica", 10)
        c.drawString(logo_left + logo_width + 2.5, logo_bottom - 63, type)
        c.line(logo_left + logo_width + 3 * cm, logo_bottom - 60, canvas_width - 1 * cm, logo_bottom - 60)

        # Set the customer details
        c.setFont("Helvetica", 10)
        c.drawString(logo_left, logo_bottom - 90, "Bill To:")
        c.setFont("Helvetica-Bold", 10)
        c.drawString(logo_left, logo_bottom - 110, self.customer_name)
        c.setFont("Helvetica", 10)
        c.drawString(logo_width + logo_left + 5 * cm, logo_bottom - 90, "Date:")
        c.drawString(logo_width + logo_left + 6 * cm, logo_bottom - 90, self.date)

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
        t.drawOn(c, 2 * cm, logo_bottom - logo_height / 4 - 150 - table_height)

        # draw rectangle that will contain the total
        total_rect_x = logo_width + logo_left + 1.5 * cm
        total_rect_y = logo_bottom - logo_height / 4 - 178 - table_height
        total_rect_width = 8.8 * cm
        total_rect_height = 15

        # Define color in Hex
        light_orange = colors.HexColor("#f6c3a6")
        c.setFillColor(light_orange)
        c.rect(total_rect_x, total_rect_y, total_rect_width, total_rect_height, fill=True, stroke=False)

        # create subtotal and total after table
        c.setFont("Helvetica", 11)
        c.setFillColor(colors.black)
        c.drawString(logo_width + logo_left + 2.5 * cm, logo_bottom - logo_height / 4 - 175 - table_height, "TOTAL")
        c.drawString(logo_width + logo_left + 8.3 * cm, logo_bottom - logo_height / 4 - 175 - table_height,
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
        c.setFont("Helvetica", 10)
        title = "Payment Details:"

        title_width = c.stringWidth(title, "Helvetica", 10)
        c.drawString(logo_left, top_of_page, title)
        c.line(logo_left, top_of_page - 2, logo_left + title_width, top_of_page - 2)

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
                y = top_of_page - 47 - word_num * 20  # Adjust the line spacing (20 in this example)
                c.drawString(xx, y, maneno)

            return y

        # payment()

        # Creating Terms & Conditions area

        c.setFont("Helvetica", 11)
        conditions = "Terms & Conditions:"
        value_y = payment()
        conditions_width = c.stringWidth(conditions, "Helvetica", 11)
        c.drawString(logo_left, value_y - 50, conditions)
        c.line(logo_left, value_y - 52, logo_left + conditions_width, value_y - 52)

        def terms():

            words = "Quotation is valid for seven days from date of issue\n" \
                    "The price quoted is not inclusive of VAT\n"

            words_list = words.split("\n")

            for word_num, maneno in enumerate(words_list):
                xx = logo_left
                y = value_y - 52 - 40 - word_num * 20  # Adjust the line spacing (20 in this example)
                c.drawString(xx, y, maneno)

            return y

        terms()

        """line_width = 50
        # Example usage
        text = "Amount in Words: " + set_amount(amount) + " Shillings Only"
        lines = textwrap.wrap(text, width=line_width)
        print(lines)

        for line_num, line in enumerate(lines):
            x = logo_left + 0.2 * cm
            y = top_of_page - 47 - line_num * 12  # Adjust the line spacing (12 in this example)
            c.drawString(x, y, line)"""

        payment_details = ""

        # Save the PDF
        c.save()


class QuotationGeneratorGUI:
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
        menu_bar.add_cascade(label="Invoice", menu=invoice_menu, command= self.invoicegenerator)

        # Creating quotation menubar
        quotes_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Quotation", menu=quotes_menu, )

    def invoicegenerator(self):
        pass

    def create_widgets(self):
        self.create_menu()
        quantities_list = ["Cabro 60mm", "Pavers 60mm", "Trihex 60mm", "Venus 60mm", "Splendor 60mm", "Libra 60mm",
                           "Hexagon 60mm", "Zig-zag 60mm",
                           "Uni 60mm", "Quad 60mm", "Road kerbs", "Road channels", "Slabs", "Cement", "Dust",
                           "Rock chips",
                           "Labor", "Kajiado sand", "Ground roller", "Cabro cutter", "Sand"]
        self.company_name_label = tk.Label(self.root, text="Company Name:")
        self.company_name_entry = tk.Entry(self.root)
        self.company_address_label = tk.Label(self.root, text="Company Address:")
        self.company_address_text = tk.Text(self.root, height=4)
        self.company_logo_button = tk.Button(self.root, text="Select Company Logo", command=self.select_logo)
        self.customer_name_label = tk.Label(self.root, text="Customer Name:")
        self.customer_name_entry = tk.Entry(self.root)
        self.date_label = tk.Label(self.root, text="Date:")
        self.date_text = tk.Entry(self.root)
        self.item_description_label = tk.Label(self.root, text="Item Description:")
        self.item_description_entry = AutocompleteCombobox(self.root, completevalues=quantities_list)
        self.item_quantity_label = tk.Label(self.root, text="Quantity:")
        self.item_quantity_entry = tk.Spinbox(self.root, from_=0, to=1000)
        self.item_price_label = tk.Label(self.root, text="Price:")
        self.item_price_entry = tk.Entry(self.root)
        self.add_item_button = tk.Button(self.root, text="Add Item", command=self.add_item)
        self.generate_button = tk.Button(self.root, text="Generate Invoice", command=self.generate_invoice)
        self.current_total_label = tk.Label(self.root, text="Sub Total:")
        self.current_total_textbox = tk.Label(self.root, text="0", font=("Helvetica", 11, "bold"))

        # Layout using grid
        self.company_name_label.grid(row=0, column=0, sticky="w")
        self.company_name_entry.grid(row=0, column=1, padx=5, pady=5)
        self.company_address_label.grid(row=1, column=0, sticky="w")
        self.company_address_text.grid(row=1, column=1, padx=5, pady=5)
        self.company_logo_button.grid(row=2, column=0, columnspan=2, pady=5)
        self.date_label.grid(row=3, column=0, sticky="w")
        self.date_text.grid(row=3, column=1, padx=5, pady=5)
        self.customer_name_label.grid(row=4, column=0, sticky="w")
        self.customer_name_entry.grid(row=4, column=1, padx=5, pady=5)
        self.item_description_label.grid(row=5, column=0, sticky="w")
        self.item_description_entry.grid(row=5, column=1, padx=5, pady=5)
        self.item_quantity_label.grid(row=6, column=0, sticky="w")
        self.item_quantity_entry.grid(row=6, column=1, padx=5, pady=5)
        self.item_price_label.grid(row=7, column=0, sticky="w")
        self.item_price_entry.grid(row=7, column=1, padx=5, pady=5)
        self.add_item_button.grid(row=8, column=0, columnspan=2, pady=5)
        self.generate_button.grid(row=9, column=0, columnspan=2, pady=5)
        self.current_total_label.grid(row=11, column=0, sticky="w")
        self.current_total_textbox.grid(row=11, column=1, sticky="w")
        # Create treeview to view selections

        self.treeview = ttk.Treeview(self.root, columns=["Description", "Quantity", "Price", "Total"])
        self.treeview.heading("#0", text="SI No")
        self.treeview.heading("Description", text="Description")
        self.treeview.heading("Quantity", text="Quantity")
        self.treeview.heading("Price", text="Price (ksh)")
        self.treeview.heading("Total", text="Total Amt.")

        # Create a vertical scrollbar

        self.scroll_bar = ttk.Scrollbar(self.root, orient="vertical")
        self.treeview.config(yscrollcommand=self.scroll_bar.set)
        self.scroll_bar.config(command=self.treeview.yview)

        """self.treeview.column("#0", width=50, anchor="center")
        self.treeview.column("Description", width=300, anchor="w")
        self.treeview.column("Quantity", width=100, anchor="center")
        self.treeview.column("Price", width=100, anchor="e")
        self.treeview.column("Total",  anchor="e")"""

        self.treeview.grid(row=10, column=0, columnspan=2, pady=5, padx=(15, 0))
        self.scroll_bar.grid(row=10, column=3, sticky="ns")

        # Adding buttons to add or delete items from treeview
        self.delete_item_button = tk.Button(self.root, text="Delete Item", command=self.delete_item)
        self.delete_item_button.grid(row=8, column=1, columnspan=2, pady=5)

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
                              "Email: sales@kentonkenya.com\n" \
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
        description = self.item_description_entry.get()
        quantity = int(self.item_quantity_entry.get())
        price = float(self.item_price_entry.get())
        self.invoice.add_item(description, quantity, price)

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

    def delete_item(self):
        selected_item = self.treeview.selection()

        if selected_item:
            item_num = int(self.treeview.item(selected_item, "text"))
            # Delete the item from the invoice and the Treeview
            popped = self.invoice.items.pop(item_num - 1)
            popped
            self.treeview.delete(selected_item)

            # Re-index the items in the Treeview
            for idx, item in enumerate(self.treeview.get_children()):
                self.treeview.item(item, text=str(idx + 1))

            self.calculate_total()

    def calculate_total(self):
        cum_total = sum(int(self.treeview.item(item, "values")[-1]) for item in self.treeview.get_children())

        # update label to reflect the total

        self.current_total_textbox.config(text=f"{cum_total}")

    def generate_invoice(self):

        entered_date = self.date_text.get().strip()

        if not entered_date:
            todays_date = datetime.now().strftime("%d %B %Y")
            self.date_text.insert(tk.END, todays_date)
            entered_date = todays_date

        self.invoice.set_customer(self.customer_name_entry.get().strip(), entered_date)
        self.invoice.generate_pdf()

