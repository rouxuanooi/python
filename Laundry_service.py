import sqlite3
import hashlib
import time
from datetime import datetime, timedelta
import qrcode
from io import BytesIO
import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
from PIL import Image, ImageTk
import webbrowser

class LaundryManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Laundry Management System")
        self.root.geometry("800x600")

        # Initialize database
        self.initialize_database()

        # Current user info
        self.current_user = None
        self.is_admin = False

        # Colors
        self.bg_color = "#ffffff"
        self.button_color = "#4169e1"
        self.text_color = "#000000"

        # QR code image reference
        self.qr_photo = None

        self.show_login_screen()

    def initialize_database(self):
        self.conn = sqlite3.connect('laundry.db')
        self.cursor = self.conn.cursor()

        # Create tables if they don't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                is_admin INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS laundry_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                service_id INTEGER NOT NULL,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                pickup_date TIMESTAMP,
                status TEXT DEFAULT 'Pending',
                weight REAL NOT NULL,
                total_price REAL NOT NULL,
                payment_method TEXT DEFAULT NULL,
                payment_status TEXT DEFAULT 'Pending',
                qr_code BLOB,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (service_id) REFERENCES services (id)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price_per_kg REAL NOT NULL,
                description TEXT,
                estimated_time_hours INTEGER NOT NULL
            )
        ''')

        # Insert default services if none exist
        self.cursor.execute("SELECT COUNT(*) FROM services")
        if self.cursor.fetchone()[0] == 0:
            default_services = [
                ('Regular Wash', 5.0, 'Basic washing and drying', 24),
                ('Express Wash', 8.0, 'Fast washing and drying (priority)', 12),
                ('Dry Cleaning', 10.0, 'Professional dry cleaning', 48),
                ('Ironing Only', 3.0, 'Ironing service without washing', 6)
            ]
            self.cursor.executemany('''
                INSERT INTO services (name, price_per_kg, description, estimated_time_hours)
                VALUES (?, ?, ?, ?)
            ''', default_services)

        # Create admin if not exists
        self.cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1")
        if self.cursor.fetchone()[0] == 0:
            admin_password = hashlib.sha256("admin123".encode()).hexdigest()
            self.cursor.execute('''
                INSERT INTO users (username, password, email, is_admin)
                VALUES (?, ?, ?, 1)
            ''', ("admin", admin_password, "admin@laundry.com"))

        self.conn.commit()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        self.clear_window()
        self.current_user = None
        self.is_admin = False

        # Main frame
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = tk.Label(main_frame, text="Laundry Management System", font=("Arial", 20, "bold"),
                             bg=self.bg_color, fg=self.text_color)
        title_label.pack(pady=20)

        # Login frame
        login_frame = tk.Frame(main_frame, bg=self.bg_color)
        login_frame.pack(pady=20)

        # Username
        tk.Label(login_frame, text="Username:", bg=self.bg_color, fg=self.text_color).grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = tk.Entry(login_frame, width=30)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        # Password
        tk.Label(login_frame, text="Password:", bg=self.bg_color, fg=self.text_color).grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(login_frame, width=30, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        # Login button
        login_button = tk.Button(main_frame, text="Login", command=self.login, bg=self.button_color, fg="white")
        login_button.pack(pady=10)

        # Register button
        register_button = tk.Button(main_frame, text="Register New Account", command=self.show_register_screen,
                                   bg=self.button_color, fg="white")
        register_button.pack(pady=10)

    def show_register_screen(self):
        self.clear_window()

        # Main frame
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = tk.Label(main_frame, text="Register New Account", font=("Arial", 20, "bold"),
                             bg=self.bg_color, fg=self.text_color)
        title_label.pack(pady=20)

        # Register frame
        register_frame = tk.Frame(main_frame, bg=self.bg_color)
        register_frame.pack(pady=20)

        # Username
        tk.Label(register_frame, text="Username:", bg=self.bg_color, fg=self.text_color).grid(row=0, column=0, padx=5, pady=5)
        self.reg_username_entry = tk.Entry(register_frame, width=30)
        self.reg_username_entry.grid(row=0, column=1, padx=5, pady=5)

        # Password
        tk.Label(register_frame, text="Password:", bg=self.bg_color, fg=self.text_color).grid(row=1, column=0, padx=5, pady=5)
        self.reg_password_entry = tk.Entry(register_frame, width=30, show="*")
        self.reg_password_entry.grid(row=1, column=1, padx=5, pady=5)

        # Confirm Password
        tk.Label(register_frame, text="Confirm Password:", bg=self.bg_color, fg=self.text_color).grid(row=2, column=0, padx=5, pady=5)
        self.reg_confirm_password_entry = tk.Entry(register_frame, width=30, show="*")
        self.reg_confirm_password_entry.grid(row=2, column=1, padx=5, pady=5)

        # Email
        tk.Label(register_frame, text="Email:", bg=self.bg_color, fg=self.text_color).grid(row=3, column=0, padx=5, pady=5)
        self.reg_email_entry = tk.Entry(register_frame, width=30)
        self.reg_email_entry.grid(row=3, column=1, padx=5, pady=5)

        # Phone
        tk.Label(register_frame, text="Phone:", bg=self.bg_color, fg=self.text_color).grid(row=4, column=0, padx=5, pady=5)
        self.reg_phone_entry = tk.Entry(register_frame, width=30)
        self.reg_phone_entry.grid(row=4, column=1, padx=5, pady=5)

        # Register button
        register_button = tk.Button(main_frame, text="Register", command=self.register, bg=self.button_color, fg="white")
        register_button.pack(pady=10)

        # Back to login button
        back_button = tk.Button(main_frame, text="Back to Login", command=self.show_login_screen,
                               bg=self.button_color, fg="white")
        back_button.pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        self.cursor.execute('''
            SELECT id, username, is_admin FROM users
            WHERE username = ? AND password = ?
        ''', (username, hashed_password))

        user = self.cursor.fetchone()

        if user:
            self.current_user = {
                'id': user[0],
                'username': user[1],
                'is_admin': bool(user[2])
            }
            self.is_admin = bool(user[2])

            if self.is_admin:
                self.show_admin_dashboard()
            else:
                self.show_customer_dashboard()
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def register(self):
        username = self.reg_username_entry.get()
        password = self.reg_password_entry.get()
        confirm_password = self.reg_confirm_password_entry.get()
        email = self.reg_email_entry.get()
        phone = self.reg_phone_entry.get()

        if not username or not password or not confirm_password or not email:
            messagebox.showerror("Error", "Please fill in all required fields")
            return

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            self.cursor.execute('''
                INSERT INTO users (username, password, email, phone)
                VALUES (?, ?, ?, ?)
            ''', (username, hashed_password, email, phone))
            self.conn.commit()
            messagebox.showinfo("Success", "Registration successful! Please login.")
            self.show_login_screen()
        except sqlite3.IntegrityError as e:
            if "username" in str(e):
                messagebox.showerror("Error", "Username already exists")
            elif "email" in str(e):
                messagebox.showerror("Error", "Email already exists")
            else:
                messagebox.showerror("Error", "Registration failed")

    def show_admin_dashboard(self):
        self.clear_window()

        # Main frame
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = tk.Label(main_frame, text=f"Admin Dashboard - Welcome {self.current_user['username']}",
                             font=("Arial", 20, "bold"), bg=self.bg_color, fg=self.text_color)
        title_label.pack(pady=20)

        # Notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Orders tab
        orders_frame = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(orders_frame, text="Manage Orders")

        # Treeview for orders
        columns = ("ID", "Customer", "Order Date", "Pickup Date", "Status", "Weight", "Price", "Payment Method", "Payment Status")
        self.orders_tree = ttk.Treeview(orders_frame, columns=columns, show="headings")

        for col in columns:
            self.orders_tree.heading(col, text=col)
            self.orders_tree.column(col, width=100, anchor=tk.CENTER)

        self.orders_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Buttons frame
        buttons_frame = tk.Frame(orders_frame, bg=self.bg_color)
        buttons_frame.pack(pady=10)

        # Update status button
        update_button = tk.Button(buttons_frame, text="Update Status", command=self.update_order_status,
                                bg=self.button_color, fg="white")
        update_button.pack(side=tk.LEFT, padx=5)

        # View receipt button
        receipt_button = tk.Button(buttons_frame, text="View Receipt", command=self.view_receipt_as_admin,
                                  bg=self.button_color, fg="white")
        receipt_button.pack(side=tk.LEFT, padx=5)

        # Refresh button
        refresh_button = tk.Button(buttons_frame, text="Refresh", command=self.refresh_orders,
                                  bg=self.button_color, fg="white")
        refresh_button.pack(side=tk.LEFT, padx=5)

        # Services tab
        services_frame = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(services_frame, text="Manage Services")

        # Treeview for services
        service_columns = ("ID", "Name", "Price/kg", "Description", "Est. Time (hrs)")
        self.services_tree = ttk.Treeview(services_frame, columns=service_columns, show="headings")

        for col in service_columns:
            self.services_tree.heading(col, text=col)
            self.services_tree.column(col, width=100, anchor=tk.CENTER)

        self.services_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Service buttons frame
        service_buttons_frame = tk.Frame(services_frame, bg=self.bg_color)
        service_buttons_frame.pack(pady=10)

        # Add service button
        add_service_button = tk.Button(service_buttons_frame, text="Add Service", command=self.show_add_service_dialog,
                                     bg=self.button_color, fg="white")
        add_service_button.pack(side=tk.LEFT, padx=5)

        # Edit service button
        edit_service_button = tk.Button(service_buttons_frame, text="Edit Service", command=self.show_edit_service_dialog,
                                       bg=self.button_color, fg="white")
        edit_service_button.pack(side=tk.LEFT, padx=5)

        # Delete service button
        delete_service_button = tk.Button(service_buttons_frame, text="Delete Service", command=self.delete_service,
                                        bg="red", fg="white")
        delete_service_button.pack(side=tk.LEFT, padx=5)

        # Users tab
        users_frame = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(users_frame, text="Manage Users")

        # Treeview for users
        user_columns = ("ID", "Username", "Email", "Phone", "Admin", "Joined")
        self.users_tree = ttk.Treeview(users_frame, columns=user_columns, show="headings")

        for col in user_columns:
            self.users_tree.heading(col, text=col)
            self.users_tree.column(col, width=100, anchor=tk.CENTER)

        self.users_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Logout button
        logout_button = tk.Button(main_frame, text="Logout", command=self.show_login_screen,
                                bg="red", fg="white")
        logout_button.pack(pady=10)

        # Load initial data
        self.refresh_orders()
        self.refresh_services()
        self.refresh_users()

    def show_customer_dashboard(self):
        self.clear_window()

        # Main frame
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = tk.Label(main_frame, text=f"Customer Dashboard - Welcome {self.current_user['username']}",
                             font=("Arial", 20, "bold"), bg=self.bg_color, fg=self.text_color)
        title_label.pack(pady=20)

        # Notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # New Order tab
        new_order_frame = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(new_order_frame, text="New Order")

        # Service selection
        tk.Label(new_order_frame, text="Select Service:", bg=self.bg_color, fg=self.text_color).pack(pady=5)

        self.service_var = tk.StringVar()
        self.service_dropdown = ttk.Combobox(new_order_frame, textvariable=self.service_var, state="readonly")
        self.service_dropdown.pack(pady=5)

        # Load services
        self.cursor.execute("SELECT id, name, price_per_kg, estimated_time_hours FROM services")
        services = self.cursor.fetchall()
        self.services = {f"{s[1]} (RM{s[2]}/kg, {s[3]} hrs)": s[0] for s in services}
        self.service_dropdown['values'] = list(self.services.keys())

        # Weight input
        tk.Label(new_order_frame, text="Weight (kg):", bg=self.bg_color, fg=self.text_color).pack(pady=5)
        self.weight_entry = tk.Entry(new_order_frame)
        self.weight_entry.pack(pady=5)

        # Calculate button
        calculate_button = tk.Button(new_order_frame, text="Calculate Price", command=self.calculate_price,
                                   bg=self.button_color, fg="white")
        calculate_button.pack(pady=10)

        # Price display
        self.price_label = tk.Label(new_order_frame, text="Total Price: RM0.00", bg=self.bg_color, fg=self.text_color)
        self.price_label.pack(pady=5)

        # Submit order button
        submit_button = tk.Button(new_order_frame, text="Submit Order", command=self.submit_order,
                                 bg=self.button_color, fg="white")
        submit_button.pack(pady=10)

        # My Orders tab
        my_orders_frame = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(my_orders_frame, text="My Orders")

        # Treeview for orders
        columns = ("ID", "Order Date", "Pickup Date", "Status", "Weight", "Price", "Payment Method", "Payment Status", "Remaining Time")
        self.my_orders_tree = ttk.Treeview(my_orders_frame, columns=columns, show="headings")

        for col in columns:
            self.my_orders_tree.heading(col, text=col)
            self.my_orders_tree.column(col, width=100, anchor=tk.CENTER)

        self.my_orders_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Buttons frame
        buttons_frame = tk.Frame(my_orders_frame, bg=self.bg_color)
        buttons_frame.pack(pady=10)

        # Payment button
        payment_button = tk.Button(buttons_frame, text="Proceed to Payment", command=self.initiate_payment_process,
                                  bg=self.button_color, fg="white")
        payment_button.pack(side=tk.LEFT, padx=5)

        # View receipt button
        receipt_button = tk.Button(buttons_frame, text="View Receipt", command=self.view_receipt_as_customer,
                                  bg=self.button_color, fg="white")
        receipt_button.pack(side=tk.LEFT, padx=5)

        # Refresh button
        refresh_button = tk.Button(buttons_frame, text="Refresh", command=self.refresh_my_orders,
                                  bg=self.button_color, fg="white")
        refresh_button.pack(side=tk.LEFT, padx=5)

        # Logout button
        logout_button = tk.Button(main_frame, text="Logout", command=self.show_login_screen,
                                bg="red", fg="white")
        logout_button.pack(pady=10)

        # Load initial data
        self.refresh_my_orders()

    def refresh_orders(self):
        # Clear existing data
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)

        # Fetch and display orders
        self.cursor.execute('''
            SELECT o.id, u.username, o.order_date, o.pickup_date, o.status, o.weight,
                   o.total_price, o.payment_method, o.payment_status
            FROM laundry_orders o
            JOIN users u ON o.user_id = u.id
            ORDER BY o.order_date DESC
        ''')

        for order in self.cursor.fetchall():
            pickup_date = order[3] if order[3] else "Not set"
            payment_method = order[7] if order[7] else "Not selected"
            payment_status = order[8] if order[8] else "Pending"

            self.orders_tree.insert("", tk.END, values=(
                order[0], order[1], order[2], pickup_date, order[4],
                order[5], f"RM{order[6]:.2f}", payment_method, payment_status
            ))

    def refresh_services(self):
        # Clear existing data
        for item in self.services_tree.get_children():
            self.services_tree.delete(item)

        # Fetch and display services
        self.cursor.execute("SELECT id, name, price_per_kg, description, estimated_time_hours FROM services")

        for service in self.cursor.fetchall():
            self.services_tree.insert("", tk.END, values=service)

    def refresh_users(self):
        # Clear existing data
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)

        # Fetch and display users
        self.cursor.execute("SELECT id, username, email, phone, is_admin, created_at FROM users")

        for user in self.cursor.fetchall():
            admin_status = "Yes" if user[4] else "No"
            self.users_tree.insert("", tk.END, values=user[:4] + (admin_status,) + (user[5],))

    def refresh_my_orders(self):
        # Clear existing data
        for item in self.my_orders_tree.get_children():
            self.my_orders_tree.delete(item)

        # Update columns to include payment method
        columns = ("ID", "Order Date", "Pickup Date", "Status", "Weight", "Price", "Payment Method", "Payment Status", "Remaining Time")
        self.my_orders_tree['columns'] = columns
        for col in columns:
            self.my_orders_tree.heading(col, text=col)

        # Fetch and display orders for current user
        self.cursor.execute('''
            SELECT id, order_date, pickup_date, status, weight, total_price,
                   payment_method, payment_status
            FROM laundry_orders
            WHERE user_id = ?
            ORDER BY order_date DESC
        ''', (self.current_user['id'],))

        for order in self.cursor.fetchall():
            # Calculate remaining time
            remaining_time = "N/A"
            if order[2] and order[3] not in ('Completed', 'Cancelled'):
                pickup_date = datetime.strptime(order[2], "%Y-%m-%d %H:%M:%S")
                remaining_time = pickup_date - datetime.now()
                if remaining_time.total_seconds() > 0:
                    remaining_time = str(remaining_time).split(".")[0]
                else:
                    remaining_time = "Ready for pickup"

            pickup_date = order[2] if order[2] else "Not set"
            payment_method = order[6] if order[6] else "Not selected"
            payment_status = order[7] if order[7] else "Pending"

            self.my_orders_tree.insert("", tk.END, values=(
                order[0],
                order[1],
                pickup_date,
                order[3],
                order[4],
                f"RM{order[5]:.2f}",
                payment_method,
                payment_status,
                remaining_time
            ))

    def update_order_status(self):
        selected_item = self.orders_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an order to update")
            return

        order_id = self.orders_tree.item(selected_item)['values'][0]

        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Update Order Status")
        dialog.geometry("300x200")

        # Current status
        current_status = self.orders_tree.item(selected_item)['values'][4]
        tk.Label(dialog, text=f"Current Status: {current_status}").pack(pady=10)

        # New status
        tk.Label(dialog, text="New Status:").pack()
        status_var = tk.StringVar(value=current_status)
        status_options = ["Pending", "Processing", "Ready for Pickup", "Completed", "Cancelled"]
        status_dropdown = ttk.Combobox(dialog, textvariable=status_var, values=status_options, state="readonly")
        status_dropdown.pack(pady=10)

        # Pickup date (if status is Ready for Pickup)
        pickup_frame = tk.Frame(dialog)
        pickup_frame.pack(pady=5)

        tk.Label(pickup_frame, text="Pickup Date:").pack(side=tk.LEFT)
        pickup_date_entry = tk.Entry(pickup_frame)
        pickup_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        pickup_date_entry.pack(side=tk.LEFT)

        def update_status():
            new_status = status_var.get()
            pickup_date = pickup_date_entry.get() if new_status == "Ready for Pickup" else None

            try:
                self.cursor.execute('''
                    UPDATE laundry_orders
                    SET status = ?, pickup_date = ?
                    WHERE id = ?
                ''', (new_status, pickup_date, order_id))
                self.conn.commit()
                messagebox.showinfo("Success", "Order status updated successfully")
                self.refresh_orders()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update order status: {str(e)}")

        # Update button
        update_button = tk.Button(dialog, text="Update", command=update_status, bg=self.button_color, fg="white")
        update_button.pack(pady=10)

    def show_add_service_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Service")
        dialog.geometry("400x300")

        # Name
        tk.Label(dialog, text="Service Name:").pack(pady=5)
        name_entry = tk.Entry(dialog, width=30)
        name_entry.pack(pady=5)

        # Price
        tk.Label(dialog, text="Price per kg (RM):").pack(pady=5)
        price_entry = tk.Entry(dialog, width=30)
        price_entry.pack(pady=5)

        # Description
        tk.Label(dialog, text="Description:").pack(pady=5)
        desc_entry = tk.Entry(dialog, width=30)
        desc_entry.pack(pady=5)

        # Estimated time
        tk.Label(dialog, text="Estimated Time (hours):").pack(pady=5)
        time_entry = tk.Entry(dialog, width=30)
        time_entry.pack(pady=5)

        def add_service():
            try:
                self.cursor.execute('''
                    INSERT INTO services (name, price_per_kg, description, estimated_time_hours)
                    VALUES (?, ?, ?, ?)
                ''', (
                    name_entry.get(),
                    float(price_entry.get()),
                    desc_entry.get(),
                    int(time_entry.get())
                ))
                self.conn.commit()
                messagebox.showinfo("Success", "Service added successfully")
                self.refresh_services()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for price and time")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add service: {str(e)}")

        # Add button
        add_button = tk.Button(dialog, text="Add Service", command=add_service, bg=self.button_color, fg="white")
        add_button.pack(pady=10)

    def show_edit_service_dialog(self):
        selected_item = self.services_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a service to edit")
            return

        service_id = self.services_tree.item(selected_item)['values'][0]

        # Fetch service details
        self.cursor.execute('''
            SELECT name, price_per_kg, description, estimated_time_hours
            FROM services
            WHERE id = ?
        ''', (service_id,))
        service = self.cursor.fetchone()

        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Service")
        dialog.geometry("400x300")

        # Name
        tk.Label(dialog, text="Service Name:").pack(pady=5)
        name_entry = tk.Entry(dialog, width=30)
        name_entry.insert(0, service[0])
        name_entry.pack(pady=5)

        # Price
        tk.Label(dialog, text="Price per kg (RM):").pack(pady=5)
        price_entry = tk.Entry(dialog, width=30)
        price_entry.insert(0, service[1])
        price_entry.pack(pady=5)

        # Description
        tk.Label(dialog, text="Description:").pack(pady=5)
        desc_entry = tk.Entry(dialog, width=30)
        desc_entry.insert(0, service[2])
        desc_entry.pack(pady=5)

        # Estimated time
        tk.Label(dialog, text="Estimated Time (hours):").pack(pady=5)
        time_entry = tk.Entry(dialog, width=30)
        time_entry.insert(0, service[3])
        time_entry.pack(pady=5)

        def update_service():
            try:
                self.cursor.execute('''
                    UPDATE services
                    SET name = ?, price_per_kg = ?, description = ?, estimated_time_hours = ?
                    WHERE id = ?
                ''', (
                    name_entry.get(),
                    float(price_entry.get()),
                    desc_entry.get(),
                    int(time_entry.get()),
                    service_id
                ))
                self.conn.commit()
                messagebox.showinfo("Success", "Service updated successfully")
                self.refresh_services()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for price and time")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update service: {str(e)}")

        # Update button
        update_button = tk.Button(dialog, text="Update Service", command=update_service, bg=self.button_color, fg="white")
        update_button.pack(pady=10)

    def delete_service(self):
        selected_item = self.services_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a service to delete")
            return

        service_id = self.services_tree.item(selected_item)['values'][0]
        service_name = self.services_tree.item(selected_item)['values'][1]

        if messagebox.askyesno("Confirm", f"Are you sure you want to delete '{service_name}'?"):
            try:
                self.cursor.execute("DELETE FROM services WHERE id = ?", (service_id,))
                self.conn.commit()
                messagebox.showinfo("Success", "Service deleted successfully")
                self.refresh_services()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete service: {str(e)}")

    def calculate_price(self):
        selected_service = self.service_var.get()
        weight_text = self.weight_entry.get()

        if not selected_service or not weight_text:
            messagebox.showerror("Error", "Please select a service and enter weight")
            return

        try:
            weight = float(weight_text)
            if weight <= 0:
                raise ValueError("Weight must be positive")

            service_id = self.services[selected_service]
            self.cursor.execute("SELECT price_per_kg FROM services WHERE id = ?", (service_id,))
            price_per_kg = self.cursor.fetchone()[0]

            total_price = weight * price_per_kg
            self.price_label.config(text=f"Total Price: RM{total_price:.2f}")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid weight (positive number)")

    def submit_order(self):
        selected_service = self.service_var.get()
        weight_text = self.weight_entry.get()
        price_text = self.price_label.cget("text").replace("Total Price: RM", "")

        if not selected_service or not weight_text or price_text == "0.00":
            messagebox.showerror("Error", "Please calculate the price first")
            return

        try:
            weight = float(weight_text)
            total_price = float(price_text)
            service_id = self.services[selected_service]

            # Get estimated time for the service
            self.cursor.execute("SELECT estimated_time_hours FROM services WHERE id = ?", (service_id,))
            estimated_hours = self.cursor.fetchone()[0]
            pickup_date = datetime.now() + timedelta(hours=estimated_hours)

            # Generate QR code with detailed receipt information
            receipt_info = (
                f"Laundry Service Receipt\n"
                f"Order ID: {self.cursor.lastrowid + 1}\n"  # Estimate next ID
                f"Customer: {self.current_user['username']}\n"
                f"Service: {selected_service.split(' (')[0]}\n"
                f"Weight: {weight} kg\n"
                f"Amount: RM{total_price:.2f}\n"
                f"Pickup Date: {pickup_date.strftime('%Y-%m-%d %H:%M')}\n"
                f"Status: Pending"
            )

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(receipt_info)
            qr.make(fit=True)

            qr_img = qr.make_image(fill_color="black", back_color="white")
            img_byte_arr = BytesIO()
            qr_img.save(img_byte_arr, format='PNG')
            qr_bytes = img_byte_arr.getvalue()

            # Insert order with NULL payment_method (to be selected in payment dialog)
            self.cursor.execute('''
                INSERT INTO laundry_orders
                (user_id, service_id, pickup_date, weight, total_price, payment_method, payment_status, qr_code)
                VALUES (?, ?, ?, ?, ?, NULL, 'Pending', ?)
            ''', (
                self.current_user['id'],
                service_id,
                pickup_date.strftime("%Y-%m-%d %H:%M:%S"),
                weight,
                total_price,
                qr_bytes
            ))
            self.conn.commit()

            messagebox.showinfo("Success", "Order submitted successfully! Please proceed to payment.")
            self.refresh_my_orders()

            # Reset form
            self.service_var.set("")
            self.weight_entry.delete(0, tk.END)
            self.price_label.config(text="Total Price: RM0.00")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to submit order: {str(e)}")

    def initiate_payment_process(self):
        selected_item = self.my_orders_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an order to pay")
            return

        order_id = self.my_orders_tree.item(selected_item)['values'][0]
        payment_status = self.my_orders_tree.item(selected_item)['values'][7]  # Payment status
        total_price = float(self.my_orders_tree.item(selected_item)['values'][5].replace('RM', ''))

        if payment_status == "Paid":
            messagebox.showinfo("Info", "This order has already been paid")
            return

        self.show_payment_selection(order_id, total_price)

    def show_payment_selection(self, order_id, total_price):
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Payment Method")
        dialog.geometry("400x300")
        dialog.grab_set()  # Make the dialog modal

        # Title
        tk.Label(dialog, text="Select Payment Method", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(dialog, text=f"Order ID: {order_id}").pack()
        tk.Label(dialog, text=f"Amount: RM{total_price:.2f}", font=("Arial", 12, "bold")).pack(pady=5)

        # Payment method buttons
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=20)

        # Cash payment button
        cash_btn = tk.Button(btn_frame, text="Cash Payment\n(Pay when picking up)",
                           command=lambda: self.process_cash_payment(dialog, order_id),
                           bg="#4CAF50", fg="white", width=20, height=3)
        cash_btn.pack(pady=10)

        # Online payment button
        online_btn = tk.Button(btn_frame, text="Online Transfer\n(Pay now)",
                             command=lambda: self.process_online_payment(dialog, order_id, total_price),
                             bg="#2196F3", fg="white", width=20, height=3)
        online_btn.pack(pady=10)

    def process_cash_payment(self, dialog, order_id):
        # Confirm selection
        if not messagebox.askyesno("Confirm", "You selected Cash Payment. You will pay when picking up.\n\nContinue?"):
            return

        try:
            # Update payment method and status
            self.cursor.execute('''
                UPDATE laundry_orders
                SET payment_method = 'Cash',
                    payment_status = 'Pending'
                WHERE id = ?
            ''', (order_id,))
            self.conn.commit()

            messagebox.showinfo("Success", "Cash payment selected. Please pay when picking up your laundry.")
            dialog.destroy()
            self.refresh_my_orders()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process payment: {str(e)}")

    def process_online_payment(self, dialog, order_id, total_price):
        # Confirm selection
        if not messagebox.askyesno("Confirm", f"You selected Online Transfer for RM{total_price:.2f}.\n\nContinue to payment?"):
            return

        # Show payment details
        payment_dialog = tk.Toplevel(self.root)
        payment_dialog.title("Online Payment")
        payment_dialog.geometry("450x550")
        payment_dialog.grab_set()

        # Payment instructions
        tk.Label(payment_dialog, text="Online Payment Instructions", font=("Arial", 14, "bold")).pack(pady=10)

        # Bank details
        tk.Label(payment_dialog, text="Please transfer to:", font=("Arial", 11)).pack()
        tk.Label(payment_dialog, text="Bank: Laundry Services Bank").pack()
        tk.Label(payment_dialog, text="Account: 1234 5678 9012").pack()
        tk.Label(payment_dialog, text="Amount: RM" + str(total_price)).pack()
        tk.Label(payment_dialog, text="Reference: ORDER" + str(order_id)).pack(pady=10)

        # QR code display
        qr_frame = tk.Frame(payment_dialog)
        qr_frame.pack(pady=10)

        # Generate QR code with payment info
        payment_info = f"Bank Transfer\nOrder: {order_id}\nAmount: RM{total_price:.2f}\nRef: ORDER{order_id}"
        qr = qrcode.QRCode(version=1, box_size=8, border=4)
        qr.add_data(payment_info)
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img = qr_img.resize((200, 200), Image.Resampling.LANCZOS)

        self.qr_photo = ImageTk.PhotoImage(qr_img)
        qr_label = tk.Label(qr_frame, image=self.qr_photo)
        qr_label.pack()

        # Confirm payment button
        def confirm_payment():
            try:
                self.cursor.execute('''
                    UPDATE laundry_orders
                    SET payment_method = 'Online Transfer',
                        payment_status = 'Paid'
                    WHERE id = ?
                ''', (order_id,))
                self.conn.commit()

                # Show receipt after payment
                messagebox.showinfo("Success", "Payment confirmed! Please bring your receipt when picking up.")
                payment_dialog.destroy()
                dialog.destroy()
                self.refresh_my_orders()
                self.show_receipt(order_id)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to confirm payment: {str(e)}")

        tk.Button(payment_dialog, text="I Have Made the Payment",
                 command=confirm_payment, bg="green", fg="white").pack(pady=20)

    def view_receipt_as_admin(self):
        selected_item = self.orders_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an order to view receipt")
            return

        order_id = self.orders_tree.item(selected_item)['values'][0]
        self.show_receipt(order_id)

    def view_receipt_as_customer(self):
        selected_item = self.my_orders_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an order to view receipt")
            return

        order_id = self.my_orders_tree.item(selected_item)['values'][0]
        self.show_receipt(order_id)

    def show_receipt(self, order_id):
        # Fetch order details with service information
        self.cursor.execute('''
            SELECT o.id, u.username, s.name, o.weight, o.total_price,
                   o.order_date, o.pickup_date, o.status, o.payment_status, o.payment_method,
                   o.qr_code
            FROM laundry_orders o
            JOIN users u ON o.user_id = u.id
            JOIN services s ON o.service_id = s.id
            WHERE o.id = ?
        ''', (order_id,))

        order = self.cursor.fetchone()

        if not order:
            messagebox.showerror("Error", "Order not found")
            return

        # Create receipt dialog
        receipt_dialog = tk.Toplevel(self.root)
        receipt_dialog.title(f"Receipt for Order #{order[0]}")
        receipt_dialog.geometry("500x700")

        # Main receipt frame
        main_frame = tk.Frame(receipt_dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = tk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(header_frame, text="LAUNDRY SERVICE", font=("Arial", 16, "bold")).pack()
        tk.Label(header_frame, text="123 Clean Street, Laundry City", font=("Arial", 10)).pack()
        tk.Label(header_frame, text="Tel: 012-345 6789 | Email: info@laundry.com", font=("Arial", 10)).pack()

        # Separator
        tk.Frame(main_frame, height=2, bg="black").pack(fill=tk.X, pady=10)

        # Order info
        info_frame = tk.Frame(main_frame)
        info_frame.pack(fill=tk.X)

        # Left column
        left_frame = tk.Frame(info_frame)
        left_frame.pack(side=tk.LEFT, anchor="w")

        tk.Label(left_frame, text=f"Order ID: #{order[0]}", anchor="w", font=("Arial", 10)).pack(fill=tk.X)
        tk.Label(left_frame, text=f"Customer: {order[1]}", anchor="w", font=("Arial", 10)).pack(fill=tk.X)
        tk.Label(left_frame, text=f"Order Date: {order[5]}", anchor="w", font=("Arial", 10)).pack(fill=tk.X)

        # Right column
        right_frame = tk.Frame(info_frame)
        right_frame.pack(side=tk.RIGHT, anchor="e")

        tk.Label(right_frame, text=f"Status: {order[7]}", anchor="e", font=("Arial", 10)).pack(fill=tk.X)
        tk.Label(right_frame, text=f"Payment: {order[9]}", anchor="e", font=("Arial", 10)).pack(fill=tk.X)
        tk.Label(right_frame, text=f"Payment Status: {order[8]}", anchor="e", font=("Arial", 10)).pack(fill=tk.X)

        # Separator
        tk.Frame(main_frame, height=2, bg="black").pack(fill=tk.X, pady=10)

        # Service details
        details_frame = tk.Frame(main_frame)
        details_frame.pack(fill=tk.X, pady=5)

        # Table header
        tk.Label(details_frame, text="Service", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w")
        tk.Label(details_frame, text="Weight", font=("Arial", 10, "bold")).grid(row=0, column=1)
        tk.Label(details_frame, text="Price", font=("Arial", 10, "bold")).grid(row=0, column=2, sticky="e")

        # Service row
        tk.Label(details_frame, text=order[2], font=("Arial", 10)).grid(row=1, column=0, sticky="w")
        tk.Label(details_frame, text=f"{order[3]} kg", font=("Arial", 10)).grid(row=1, column=1)
        tk.Label(details_frame, text=f"RM{order[4]:.2f}", font=("Arial", 10)).grid(row=1, column=2, sticky="e")

        # Separator
        tk.Frame(main_frame, height=2, bg="black").pack(fill=tk.X, pady=10)

        # Total
        total_frame = tk.Frame(main_frame)
        total_frame.pack(fill=tk.X)

        tk.Label(total_frame, text="Total:", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        tk.Label(total_frame, text=f"RM{order[4]:.2f}", font=("Arial", 12, "bold")).pack(side=tk.RIGHT)

        # Pickup info
        pickup_frame = tk.Frame(main_frame)
        pickup_frame.pack(fill=tk.X, pady=10)

        tk.Label(pickup_frame, text="Pickup Information:", font=("Arial", 10, "bold")).pack(anchor="w")
        tk.Label(pickup_frame, text=f"Pickup Date: {order[6]}", font=("Arial", 10)).pack(anchor="w")

        # QR code display
        if order[10]:  # If QR code exists
            try:
                img = Image.open(BytesIO(order[10]))
                img = img.resize((150, 150), Image.Resampling.LANCZOS)
                qr_img = ImageTk.PhotoImage(img)

                qr_frame = tk.Frame(main_frame)
                qr_frame.pack(pady=10)

                qr_label = tk.Label(qr_frame, image=qr_img)
                qr_label.image = qr_img
                qr_label.pack()

                tk.Label(qr_frame, text="Scan for order details", font=("Arial", 8)).pack()
            except Exception as e:
                print(f"Error displaying QR code: {str(e)}")

        # Footer
        footer_frame = tk.Frame(main_frame)
        footer_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Label(footer_frame, text="Thank you for your business!", font=("Arial", 10, "italic")).pack()
        tk.Label(footer_frame, text="Please bring this receipt when picking up", font=("Arial", 9)).pack()

        # Print button (simulated)
        print_button = tk.Button(main_frame, text="Print Receipt",
                               command=lambda: messagebox.showinfo("Print", "Receipt sent to printer"),
                               bg=self.button_color, fg="white")
        print_button.pack(pady=10)

        # Close button
        close_button = tk.Button(main_frame, text="Close",
                               command=receipt_dialog.destroy,
                               bg="red", fg="white")
        close_button.pack(pady=5)

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = LaundryManagementSystem(root)
    root.mainloop()