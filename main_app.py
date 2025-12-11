"""
Car Rental System - PyQt6 Desktop Application
Main application file
"""

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                              QTableWidget, QTableWidgetItem, QMessageBox, 
                              QDialog, QFormLayout, QComboBox, QDateEdit,
                              QTextEdit, QStackedWidget, QTabWidget, QSpinBox,
                              QDoubleSpinBox, QFileDialog, QHeaderView, QFrame)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QPixmap, QIcon
from datetime import datetime, date
from decimal import Decimal
import os

# Import database functions
from car_rental_system import (
    login_user, get_db_connection, add_car, list_available_cars, 
    list_users, register_user, update_booking_status, create_booking, 
    get_booking_details, create_maintenance_record, list_maintenance_records
)


class LoginWindow(QDialog):
    """Login dialog window"""
    
    def __init__(self):
        super().__init__()
        self.user = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Car Rental System - Login')
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel('Car Rental System')
        title.setStyleSheet('font-size: 24px; font-weight: bold; margin: 20px;')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Form layout
        form_layout = QFormLayout()
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText('Enter your email')
        form_layout.addRow('Email:', self.email_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText('Enter your password')
        self.password_input.returnPressed.connect(self.login)
        form_layout.addRow('Password:', self.password_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.login_btn = QPushButton('Login')
        self.login_btn.clicked.connect(self.login)
        self.login_btn.setStyleSheet('padding: 10px; font-size: 14px;')
        btn_layout.addWidget(self.login_btn)
        
        self.signup_btn = QPushButton('Sign Up')
        self.signup_btn.clicked.connect(self.show_signup)
        self.signup_btn.setStyleSheet('padding: 10px; font-size: 14px;')
        btn_layout.addWidget(self.signup_btn)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        
    def login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        
        if not email or not password:
            QMessageBox.warning(self, 'Error', 'Please enter both email and password')
            return
        
        user = login_user(email, password)
        if user:
            self.user = user
            self.accept()
        else:
            QMessageBox.warning(self, 'Error', 'Invalid email or password')
            
    def show_signup(self):
        signup_dialog = SignupDialog(self)
        if signup_dialog.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(self, 'Success', 'Registration successful! Please login.')


class SignupDialog(QDialog):
    """Signup dialog for new customers"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Sign Up - New Customer')
        self.setFixedSize(450, 500)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel('Create New Account')
        title.setStyleSheet('font-size: 20px; font-weight: bold; margin: 10px;')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Form layout
        form_layout = QFormLayout()
        
        self.fullname_input = QLineEdit()
        form_layout.addRow('Full Name:', self.fullname_input)
        
        self.email_input = QLineEdit()
        form_layout.addRow('Email:', self.email_input)
        
        self.phone_input = QLineEdit()
        form_layout.addRow('Phone:', self.phone_input)
        
        self.address_input = QLineEdit()
        form_layout.addRow('Address:', self.address_input)
        
        self.license_input = QLineEdit()
        form_layout.addRow('License No:', self.license_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow('Password:', self.password_input)
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow('Confirm Password:', self.confirm_password_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.signup_btn = QPushButton('Sign Up')
        self.signup_btn.clicked.connect(self.signup)
        self.signup_btn.setStyleSheet('padding: 10px; font-size: 14px;')
        btn_layout.addWidget(self.signup_btn)
        
        self.cancel_btn = QPushButton('Cancel')
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet('padding: 10px; font-size: 14px;')
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
    def signup(self):
        # Validate inputs
        if not all([
            self.fullname_input.text().strip(),
            self.email_input.text().strip(),
            self.phone_input.text().strip(),
            self.password_input.text().strip()
        ]):
            QMessageBox.warning(self, 'Error', 'Please fill in all required fields')
            return
        
        if self.password_input.text() != self.confirm_password_input.text():
            QMessageBox.warning(self, 'Error', 'Passwords do not match')
            return
        
        # Register user
        user_id = register_user(
            full_name=self.fullname_input.text().strip(),
            email=self.email_input.text().strip(),
            password=self.password_input.text().strip(),
            role='customer',
            phone=self.phone_input.text().strip(),
            address=self.address_input.text().strip(),
            license_no=self.license_input.text().strip()
        )
        
        if user_id:
            self.accept()
        else:
            QMessageBox.warning(self, 'Error', 'Registration failed. Email may already exist.')


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle(f'Car Rental System - {self.user["role"].title()} Dashboard')
        self.setGeometry(100, 100, 1200, 700)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Header
        header = QLabel(f'Welcome, {self.user["full_name"]} ({self.user["role"].title()})')
        header.setStyleSheet('font-size: 18px; font-weight: bold; padding: 10px; background-color: #3498db; color: white;')
        main_layout.addWidget(header)
        
        # Logout button
        logout_btn = QPushButton('Logout')
        logout_btn.clicked.connect(self.logout)
        logout_btn.setMaximumWidth(100)
        main_layout.addWidget(logout_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        # Load dashboard based on role
        if self.user['role'] == 'admin':
            self.load_admin_dashboard(main_layout)
        elif self.user['role'] == 'staff':
            self.load_staff_dashboard(main_layout)
        else:
            self.load_customer_dashboard(main_layout)
            
    def logout(self):
        self.close()
        login_window = LoginWindow()
        if login_window.exec() == QDialog.DialogCode.Accepted:
            main_window = MainWindow(login_window.user)
            main_window.show()
            
    def load_admin_dashboard(self, layout):
        """Load admin dashboard"""
        tabs = QTabWidget()
        
        # Dashboard tab
        dashboard_tab = QWidget()
        dashboard_layout = QVBoxLayout()
        
        # Statistics
        stats_frame = QFrame()
        stats_frame.setFrameStyle(QFrame.Shape.Box)
        stats_layout = QHBoxLayout()
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM cars")
            total_cars = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM bookings WHERE status = 'approved'")
            active_bookings = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            
            conn.close()
            
            stats_layout.addWidget(self.create_stat_widget('Total Cars', total_cars))
            stats_layout.addWidget(self.create_stat_widget('Active Bookings', active_bookings))
            stats_layout.addWidget(self.create_stat_widget('Total Users', total_users))
        
        stats_frame.setLayout(stats_layout)
        dashboard_layout.addWidget(stats_frame)
        dashboard_layout.addStretch()
        dashboard_tab.setLayout(dashboard_layout)
        
        # Cars tab
        cars_tab = self.create_cars_tab()
        
        # Users tab
        users_tab = self.create_users_tab()
        
        # Bookings tab
        bookings_tab = self.create_bookings_tab()
        
        tabs.addTab(dashboard_tab, 'Dashboard')
        tabs.addTab(cars_tab, 'Cars')
        tabs.addTab(users_tab, 'Users')
        tabs.addTab(bookings_tab, 'Bookings')
        
        layout.addWidget(tabs)
        
    def create_stat_widget(self, title, value):
        """Create a statistics widget"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Shape.Box)
        widget.setStyleSheet('background-color: #ecf0f1; padding: 20px; border-radius: 5px;')
        
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet('font-size: 14px; color: #7f8c8d;')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        value_label = QLabel(str(value))
        value_label.setStyleSheet('font-size: 32px; font-weight: bold; color: #2c3e50;')
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        widget.setLayout(layout)
        return widget
        
    def create_cars_tab(self):
        """Create cars management tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Add car button
        add_car_btn = QPushButton('Add New Car')
        add_car_btn.clicked.connect(self.add_car_dialog)
        add_car_btn.setMaximumWidth(150)
        layout.addWidget(add_car_btn)
        
        # Cars table
        self.cars_table = QTableWidget()
        self.cars_table.setColumnCount(9)
        self.cars_table.setHorizontalHeaderLabels([
            'ID', 'Plate No', 'Brand', 'Model', 'Year', 'Color', 
            'Rate/Day', 'Status', 'Actions'
        ])
        self.cars_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.cars_table)
        
        # Refresh button
        refresh_btn = QPushButton('Refresh')
        refresh_btn.clicked.connect(self.load_cars_data)
        refresh_btn.setMaximumWidth(100)
        layout.addWidget(refresh_btn)
        
        widget.setLayout(layout)
        
        # Load initial data
        self.load_cars_data()
        
        return widget
        
    def load_cars_data(self):
        """Load cars data into table"""
        conn = get_db_connection()
        if not conn:
            return
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cars ORDER BY created_at DESC")
        cars = cursor.fetchall()
        conn.close()
        
        self.cars_table.setRowCount(len(cars))
        
        for row, car in enumerate(cars):
            self.cars_table.setItem(row, 0, QTableWidgetItem(str(car['car_id'])))
            self.cars_table.setItem(row, 1, QTableWidgetItem(car['plate_no']))
            self.cars_table.setItem(row, 2, QTableWidgetItem(car['brand']))
            self.cars_table.setItem(row, 3, QTableWidgetItem(car['model']))
            self.cars_table.setItem(row, 4, QTableWidgetItem(str(car['year'])))
            self.cars_table.setItem(row, 5, QTableWidgetItem(car['color']))
            self.cars_table.setItem(row, 6, QTableWidgetItem(f"${car['rate_per_day']:.2f}"))
            self.cars_table.setItem(row, 7, QTableWidgetItem(car['status']))
            
            # Action button
            action_btn = QPushButton('Update Status')
            action_btn.clicked.connect(lambda checked, c=car: self.update_car_status_dialog(c))
            self.cars_table.setCellWidget(row, 8, action_btn)
            
    def add_car_dialog(self):
        """Show add car dialog"""
        dialog = AddCarDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_cars_data()
            
    def update_car_status_dialog(self, car):
        """Show update car status dialog"""
        dialog = UpdateCarStatusDialog(car, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_cars_data()
            
    def create_users_tab(self):
        """Create users management tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Add user button
        add_user_btn = QPushButton('Add New User')
        add_user_btn.clicked.connect(self.add_user_dialog)
        add_user_btn.setMaximumWidth(150)
        layout.addWidget(add_user_btn)
        
        # Users table
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(7)
        self.users_table.setHorizontalHeaderLabels([
            'ID', 'Full Name', 'Email', 'Role', 'Phone', 'License No', 'Address'
        ])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.users_table)
        
        # Refresh button
        refresh_btn = QPushButton('Refresh')
        refresh_btn.clicked.connect(self.load_users_data)
        refresh_btn.setMaximumWidth(100)
        layout.addWidget(refresh_btn)
        
        widget.setLayout(layout)
        
        # Load initial data
        self.load_users_data()
        
        return widget
        
    def load_users_data(self):
        """Load users data into table"""
        users = list_users()
        if not users:
            return
            
        self.users_table.setRowCount(len(users))
        
        for row, user in enumerate(users):
            self.users_table.setItem(row, 0, QTableWidgetItem(str(user['user_id'])))
            self.users_table.setItem(row, 1, QTableWidgetItem(user['full_name']))
            self.users_table.setItem(row, 2, QTableWidgetItem(user['email']))
            self.users_table.setItem(row, 3, QTableWidgetItem(user['role']))
            self.users_table.setItem(row, 4, QTableWidgetItem(user.get('phone', '')))
            self.users_table.setItem(row, 5, QTableWidgetItem(user.get('license_no', '')))
            self.users_table.setItem(row, 6, QTableWidgetItem(user.get('address', '')))
            
    def add_user_dialog(self):
        """Show add user dialog"""
        dialog = AddUserDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_users_data()
            
    def create_bookings_tab(self):
        """Create bookings management tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Bookings table
        self.bookings_table = QTableWidget()
        self.bookings_table.setColumnCount(10)
        self.bookings_table.setHorizontalHeaderLabels([
            'ID', 'Customer', 'Car', 'Start Date', 'End Date', 
            'Total Amount', 'Status', 'Payment', 'Actions', 'Receipt'
        ])
        self.bookings_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.bookings_table)
        
        # Refresh button
        refresh_btn = QPushButton('Refresh')
        refresh_btn.clicked.connect(self.load_bookings_data)
        refresh_btn.setMaximumWidth(100)
        layout.addWidget(refresh_btn)
        
        widget.setLayout(layout)
        
        # Load initial data
        self.load_bookings_data()
        
        return widget
        
    def load_bookings_data(self):
        """Load bookings data into table"""
        conn = get_db_connection()
        if not conn:
            return
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT b.*, 
                   u.full_name as customer_name,
                   c.brand as car_brand,
                   c.model as car_model
            FROM bookings b
            JOIN users u ON b.customer_id = u.user_id
            JOIN cars c ON b.car_id = c.car_id
            ORDER BY b.date_created DESC
        """)
        bookings = cursor.fetchall()
        conn.close()
        
        self.bookings_table.setRowCount(len(bookings))
        
        for row, booking in enumerate(bookings):
            self.bookings_table.setItem(row, 0, QTableWidgetItem(str(booking['booking_id'])))
            self.bookings_table.setItem(row, 1, QTableWidgetItem(booking['customer_name']))
            self.bookings_table.setItem(row, 2, QTableWidgetItem(f"{booking['car_brand']} {booking['car_model']}"))
            self.bookings_table.setItem(row, 3, QTableWidgetItem(str(booking['start_date'])))
            self.bookings_table.setItem(row, 4, QTableWidgetItem(str(booking['end_date'])))
            self.bookings_table.setItem(row, 5, QTableWidgetItem(f"${booking['total_amount']:.2f}"))
            self.bookings_table.setItem(row, 6, QTableWidgetItem(booking['status']))
            self.bookings_table.setItem(row, 7, QTableWidgetItem(booking.get('payment_status', 'pending')))
            
            # Action button
            if booking['status'] == 'pending':
                action_btn = QPushButton('Manage')
                action_btn.clicked.connect(lambda checked, b=booking: self.manage_booking_dialog(b))
                self.bookings_table.setCellWidget(row, 8, action_btn)
            
            # Receipt button
            receipt_btn = QPushButton('View Receipt')
            receipt_btn.clicked.connect(lambda checked, b=booking: self.view_receipt(b['booking_id']))
            self.bookings_table.setCellWidget(row, 9, receipt_btn)
            
    def manage_booking_dialog(self, booking):
        """Show manage booking dialog"""
        dialog = ManageBookingDialog(booking, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_bookings_data()
            
    def view_receipt(self, booking_id):
        """View booking receipt"""
        dialog = ReceiptDialog(booking_id, self)
        dialog.exec()
        
    def load_staff_dashboard(self, layout):
        """Load staff dashboard"""
        tabs = QTabWidget()
        
        # Bookings tab
        bookings_tab = self.create_bookings_tab()
        
        # Cars tab
        cars_tab = self.create_cars_tab()
        
        tabs.addTab(bookings_tab, 'Bookings')
        tabs.addTab(cars_tab, 'Cars')
        
        layout.addWidget(tabs)
        
    def load_customer_dashboard(self, layout):
        """Load customer dashboard"""
        tabs = QTabWidget()
        
        # Available Cars tab
        available_cars_tab = self.create_available_cars_tab()
        
        # My Bookings tab
        my_bookings_tab = self.create_my_bookings_tab()
        
        tabs.addTab(available_cars_tab, 'Available Cars')
        tabs.addTab(my_bookings_tab, 'My Bookings')
        
        layout.addWidget(tabs)
        
    def create_available_cars_tab(self):
        """Create available cars tab for customers"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Available cars table
        self.available_cars_table = QTableWidget()
        self.available_cars_table.setColumnCount(8)
        self.available_cars_table.setHorizontalHeaderLabels([
            'Brand', 'Model', 'Year', 'Color', 'Seats', 'Rate/Day', 'Status', 'Book'
        ])
        self.available_cars_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.available_cars_table)
        
        # Refresh button
        refresh_btn = QPushButton('Refresh')
        refresh_btn.clicked.connect(self.load_available_cars)
        refresh_btn.setMaximumWidth(100)
        layout.addWidget(refresh_btn)
        
        widget.setLayout(layout)
        
        # Load initial data
        self.load_available_cars()
        
        return widget
        
    def load_available_cars(self):
        """Load available cars for booking"""
        conn = get_db_connection()
        if not conn:
            return
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cars WHERE status != 'maintenance' ORDER BY brand, model")
        cars = cursor.fetchall()
        conn.close()
        
        self.available_cars_table.setRowCount(len(cars))
        
        for row, car in enumerate(cars):
            self.available_cars_table.setItem(row, 0, QTableWidgetItem(car['brand']))
            self.available_cars_table.setItem(row, 1, QTableWidgetItem(car['model']))
            self.available_cars_table.setItem(row, 2, QTableWidgetItem(str(car['year'])))
            self.available_cars_table.setItem(row, 3, QTableWidgetItem(car['color']))
            self.available_cars_table.setItem(row, 4, QTableWidgetItem(str(car['seats'])))
            self.available_cars_table.setItem(row, 5, QTableWidgetItem(f"${car['rate_per_day']:.2f}"))
            self.available_cars_table.setItem(row, 6, QTableWidgetItem(car['status']))
            
            # Book button
            if car['status'] == 'available':
                book_btn = QPushButton('Book Now')
                book_btn.clicked.connect(lambda checked, c=car: self.book_car_dialog(c))
                self.available_cars_table.setCellWidget(row, 7, book_btn)
            
    def book_car_dialog(self, car):
        """Show book car dialog"""
        dialog = BookCarDialog(car, self.user, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_available_cars()
            
    def create_my_bookings_tab(self):
        """Create my bookings tab for customers"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # My bookings table
        self.my_bookings_table = QTableWidget()
        self.my_bookings_table.setColumnCount(8)
        self.my_bookings_table.setHorizontalHeaderLabels([
            'ID', 'Car', 'Start Date', 'End Date', 'Total', 'Status', 'Payment', 'Receipt'
        ])
        self.my_bookings_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.my_bookings_table)
        
        # Refresh button
        refresh_btn = QPushButton('Refresh')
        refresh_btn.clicked.connect(self.load_my_bookings)
        refresh_btn.setMaximumWidth(100)
        layout.addWidget(refresh_btn)
        
        widget.setLayout(layout)
        
        # Load initial data
        self.load_my_bookings()
        
        return widget
        
    def load_my_bookings(self):
        """Load customer's bookings"""
        conn = get_db_connection()
        if not conn:
            return
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT b.*, c.brand, c.model
            FROM bookings b
            JOIN cars c ON b.car_id = c.car_id
            WHERE b.customer_id = %s
            ORDER BY b.date_created DESC
        """, (self.user['user_id'],))
        bookings = cursor.fetchall()
        conn.close()
        
        self.my_bookings_table.setRowCount(len(bookings))
        
        for row, booking in enumerate(bookings):
            self.my_bookings_table.setItem(row, 0, QTableWidgetItem(str(booking['booking_id'])))
            self.my_bookings_table.setItem(row, 1, QTableWidgetItem(f"{booking['brand']} {booking['model']}"))
            self.my_bookings_table.setItem(row, 2, QTableWidgetItem(str(booking['start_date'])))
            self.my_bookings_table.setItem(row, 3, QTableWidgetItem(str(booking['end_date'])))
            self.my_bookings_table.setItem(row, 4, QTableWidgetItem(f"${booking['total_amount']:.2f}"))
            self.my_bookings_table.setItem(row, 5, QTableWidgetItem(booking['status']))
            self.my_bookings_table.setItem(row, 6, QTableWidgetItem(booking.get('payment_status', 'pending')))
            
            # Receipt button
            receipt_btn = QPushButton('View Receipt')
            receipt_btn.clicked.connect(lambda checked, b=booking: self.view_receipt(b['booking_id']))
            self.my_bookings_table.setCellWidget(row, 7, receipt_btn)


class AddCarDialog(QDialog):
    """Dialog for adding a new car"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Add New Car')
        self.setFixedSize(450, 500)
        
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        self.plate_no_input = QLineEdit()
        form_layout.addRow('Plate Number:', self.plate_no_input)
        
        self.brand_input = QLineEdit()
        form_layout.addRow('Brand:', self.brand_input)
        
        self.model_input = QLineEdit()
        form_layout.addRow('Model:', self.model_input)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(['sedan', 'suv', 'van', 'truck', 'coupe'])
        form_layout.addRow('Type:', self.type_combo)
        
        self.year_input = QSpinBox()
        self.year_input.setRange(1990, 2030)
        self.year_input.setValue(2024)
        form_layout.addRow('Year:', self.year_input)
        
        self.color_input = QLineEdit()
        form_layout.addRow('Color:', self.color_input)
        
        self.rate_input = QDoubleSpinBox()
        self.rate_input.setRange(0, 10000)
        self.rate_input.setValue(50.0)
        self.rate_input.setPrefix('$')
        form_layout.addRow('Rate per Day:', self.rate_input)
        
        self.seats_input = QSpinBox()
        self.seats_input.setRange(2, 12)
        self.seats_input.setValue(4)
        form_layout.addRow('Seats:', self.seats_input)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(['available', 'maintenance'])
        form_layout.addRow('Status:', self.status_combo)
        
        layout.addLayout(form_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton('Save')
        save_btn.clicked.connect(self.save_car)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
    def save_car(self):
        if not all([
            self.plate_no_input.text().strip(),
            self.brand_input.text().strip(),
            self.model_input.text().strip(),
            self.color_input.text().strip()
        ]):
            QMessageBox.warning(self, 'Error', 'Please fill in all required fields')
            return
        
        car_id = add_car(
            plate_no=self.plate_no_input.text().strip(),
            brand=self.brand_input.text().strip(),
            model=self.model_input.text().strip(),
            type=self.type_combo.currentText(),
            year=self.year_input.value(),
            color=self.color_input.text().strip(),
            rate_per_day=self.rate_input.value(),
            seats=self.seats_input.value(),
            status=self.status_combo.currentText()
        )
        
        if car_id:
            QMessageBox.information(self, 'Success', 'Car added successfully!')
            self.accept()
        else:
            QMessageBox.warning(self, 'Error', 'Failed to add car')


class UpdateCarStatusDialog(QDialog):
    """Dialog for updating car status"""
    
    def __init__(self, car, parent=None):
        super().__init__(parent)
        self.car = car
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Update Car Status')
        self.setFixedSize(350, 200)
        
        layout = QVBoxLayout()
        
        label = QLabel(f"Update status for {self.car['brand']} {self.car['model']}")
        label.setStyleSheet('font-weight: bold; margin: 10px;')
        layout.addWidget(label)
        
        form_layout = QFormLayout()
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(['available', 'maintenance', 'rented'])
        self.status_combo.setCurrentText(self.car['status'])
        form_layout.addRow('Status:', self.status_combo)
        
        layout.addLayout(form_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton('Update')
        save_btn.clicked.connect(self.update_status)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
    def update_status(self):
        new_status = self.status_combo.currentText()
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("UPDATE cars SET status = %s WHERE car_id = %s", 
                             (new_status, self.car['car_id']))
                conn.commit()
                conn.close()
                QMessageBox.information(self, 'Success', 'Car status updated successfully!')
                self.accept()
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Failed to update: {str(e)}')


class AddUserDialog(QDialog):
    """Dialog for adding a new user"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Add New User')
        self.setFixedSize(450, 450)
        
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        self.fullname_input = QLineEdit()
        form_layout.addRow('Full Name:', self.fullname_input)
        
        self.email_input = QLineEdit()
        form_layout.addRow('Email:', self.email_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow('Password:', self.password_input)
        
        self.role_combo = QComboBox()
        self.role_combo.addItems(['customer', 'staff', 'admin'])
        form_layout.addRow('Role:', self.role_combo)
        
        self.phone_input = QLineEdit()
        form_layout.addRow('Phone:', self.phone_input)
        
        self.address_input = QLineEdit()
        form_layout.addRow('Address:', self.address_input)
        
        self.license_input = QLineEdit()
        form_layout.addRow('License No:', self.license_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton('Save')
        save_btn.clicked.connect(self.save_user)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
    def save_user(self):
        if not all([
            self.fullname_input.text().strip(),
            self.email_input.text().strip(),
            self.password_input.text().strip()
        ]):
            QMessageBox.warning(self, 'Error', 'Please fill in all required fields')
            return
        
        user_id = register_user(
            full_name=self.fullname_input.text().strip(),
            email=self.email_input.text().strip(),
            password=self.password_input.text().strip(),
            role=self.role_combo.currentText(),
            phone=self.phone_input.text().strip(),
            address=self.address_input.text().strip(),
            license_no=self.license_input.text().strip()
        )
        
        if user_id:
            QMessageBox.information(self, 'Success', 'User added successfully!')
            self.accept()
        else:
            QMessageBox.warning(self, 'Error', 'Failed to add user. Email may already exist.')


class ManageBookingDialog(QDialog):
    """Dialog for managing bookings"""
    
    def __init__(self, booking, parent=None):
        super().__init__(parent)
        self.booking = booking
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Manage Booking')
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        # Booking details
        details = f"""
        Booking ID: {self.booking['booking_id']}
        Customer: {self.booking['customer_name']}
        Car: {self.booking['car_brand']} {self.booking['car_model']}
        Start Date: {self.booking['start_date']}
        End Date: {self.booking['end_date']}
        Total Amount: ${self.booking['total_amount']:.2f}
        Current Status: {self.booking['status']}
        """
        
        details_label = QLabel(details)
        details_label.setStyleSheet('background-color: #ecf0f1; padding: 10px; border-radius: 5px;')
        layout.addWidget(details_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        approve_btn = QPushButton('Approve')
        approve_btn.clicked.connect(lambda: self.update_booking('approved'))
        approve_btn.setStyleSheet('background-color: #27ae60; color: white; padding: 10px;')
        btn_layout.addWidget(approve_btn)
        
        reject_btn = QPushButton('Reject')
        reject_btn.clicked.connect(lambda: self.update_booking('rejected'))
        reject_btn.setStyleSheet('background-color: #e74c3c; color: white; padding: 10px;')
        btn_layout.addWidget(reject_btn)
        
        layout.addLayout(btn_layout)
        
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)
        
        self.setLayout(layout)
        
    def update_booking(self, status):
        success = update_booking_status(self.booking['booking_id'], status)
        if success:
            QMessageBox.information(self, 'Success', f'Booking {status} successfully!')
            self.accept()
        else:
            QMessageBox.warning(self, 'Error', 'Failed to update booking status')


class BookCarDialog(QDialog):
    """Dialog for booking a car"""
    
    def __init__(self, car, user, parent=None):
        super().__init__(parent)
        self.car = car
        self.user = user
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Book Car')
        self.setFixedSize(450, 450)
        
        layout = QVBoxLayout()
        
        # Car details
        car_info = QLabel(f"{self.car['brand']} {self.car['model']} ({self.car['year']})\n"
                         f"Rate: ${self.car['rate_per_day']:.2f} per day")
        car_info.setStyleSheet('font-weight: bold; font-size: 14px; margin: 10px;')
        layout.addWidget(car_info)
        
        form_layout = QFormLayout()
        
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        self.start_date.setMinimumDate(QDate.currentDate())
        self.start_date.dateChanged.connect(self.calculate_total)
        form_layout.addRow('Start Date:', self.start_date)
        
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate().addDays(1))
        self.end_date.setCalendarPopup(True)
        self.end_date.setMinimumDate(QDate.currentDate().addDays(1))
        self.end_date.dateChanged.connect(self.calculate_total)
        form_layout.addRow('End Date:', self.end_date)
        
        self.pickup_input = QLineEdit()
        form_layout.addRow('Pickup Location:', self.pickup_input)
        
        self.dropoff_input = QLineEdit()
        form_layout.addRow('Dropoff Location:', self.dropoff_input)
        
        self.payment_combo = QComboBox()
        self.payment_combo.addItems(['credit_card', 'debit_card', 'cash', 'bank_transfer'])
        form_layout.addRow('Payment Method:', self.payment_combo)
        
        self.total_label = QLabel('$0.00')
        self.total_label.setStyleSheet('font-size: 16px; font-weight: bold; color: #2c3e50;')
        form_layout.addRow('Total Amount:', self.total_label)
        
        layout.addLayout(form_layout)
        
        # Calculate initial total
        self.calculate_total()
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        book_btn = QPushButton('Book Now')
        book_btn.clicked.connect(self.book_car)
        book_btn.setStyleSheet('background-color: #3498db; color: white; padding: 10px;')
        btn_layout.addWidget(book_btn)
        
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
    def calculate_total(self):
        start = self.start_date.date().toPyDate()
        end = self.end_date.date().toPyDate()
        
        if end > start:
            days = (end - start).days + 1
            total = Decimal(self.car['rate_per_day']) * days
            self.total_label.setText(f"${total:.2f}")
        else:
            self.total_label.setText('Invalid dates')
            
    def book_car(self):
        if not all([
            self.pickup_input.text().strip(),
            self.dropoff_input.text().strip()
        ]):
            QMessageBox.warning(self, 'Error', 'Please fill in all fields')
            return
        
        start_date = self.start_date.date().toPyDate()
        end_date = self.end_date.date().toPyDate()
        
        if end_date <= start_date:
            QMessageBox.warning(self, 'Error', 'End date must be after start date')
            return
        
        # Check if car is available for selected dates
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM bookings
                WHERE car_id = %s
                AND status IN ('approved', 'pending')
                AND ((start_date <= %s AND end_date >= %s) 
                OR (start_date <= %s AND end_date >= %s)
                OR (start_date >= %s AND end_date <= %s))
            """, (self.car['car_id'], end_date, start_date, 
                  start_date, end_date, start_date, end_date))
            
            result = cursor.fetchone()
            if result['count'] > 0:
                QMessageBox.warning(self, 'Error', 'Car is not available for selected dates')
                conn.close()
                return
            
            # Calculate total
            days = (end_date - start_date).days + 1
            total_amount = Decimal(self.car['rate_per_day']) * days
            
            # Create booking
            try:
                booking_id = create_booking(
                    customer_id=self.user['user_id'],
                    car_id=self.car['car_id'],
                    start_date=start_date.strftime('%Y-%m-%d'),
                    end_date=end_date.strftime('%Y-%m-%d'),
                    pickup_location=self.pickup_input.text().strip(),
                    dropoff_location=self.dropoff_input.text().strip(),
                    total_amount=total_amount,
                    payment_method=self.payment_combo.currentText()
                )
                
                if booking_id:
                    QMessageBox.information(self, 'Success', 
                        'Booking created successfully! Waiting for approval.')
                    self.accept()
                else:
                    QMessageBox.warning(self, 'Error', 'Failed to create booking')
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Failed to create booking: {str(e)}')
            finally:
                conn.close()


class ReceiptDialog(QDialog):
    """Dialog for viewing booking receipt"""
    
    def __init__(self, booking_id, parent=None):
        super().__init__(parent)
        self.booking_id = booking_id
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Booking Receipt')
        self.setFixedSize(600, 700)
        
        layout = QVBoxLayout()
        
        # Get booking details
        booking_details = get_booking_details(self.booking_id)
        
        if not booking_details:
            QMessageBox.warning(self, 'Error', 'Booking not found')
            self.reject()
            return
        
        # Calculate rental duration
        start_date = datetime.strptime(str(booking_details['start_date']), '%Y-%m-%d')
        end_date = datetime.strptime(str(booking_details['end_date']), '%Y-%m-%d')
        days = (end_date - start_date).days + 1
        
        # Receipt content
        receipt_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; }}
                .header {{ text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; }}
                .header h1 {{ color: #3498db; margin: 10px 0; }}
                .section {{ margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 5px; }}
                .section-title {{ font-weight: bold; color: #2c3e50; font-size: 16px; margin-bottom: 10px; }}
                .detail-row {{ display: flex; justify-content: space-between; margin: 5px 0; }}
                .detail-label {{ font-weight: bold; }}
                .total {{ font-size: 20px; color: #27ae60; font-weight: bold; }}
                .footer {{ margin-top: 30px; text-align: center; color: #7f8c8d; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>CAR RENTAL SYSTEM</h1>
                <p>Booking Receipt</p>
                <p>Receipt Date: {datetime.now().strftime('%Y-%m-%d')}</p>
            </div>
            
            <div class="section">
                <div class="section-title">Booking Information</div>
                <div class="detail-row">
                    <span class="detail-label">Booking ID:</span>
                    <span>#{booking_details['booking_id']}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Booking Date:</span>
                    <span>{booking_details.get('date_created', 'N/A')}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Status:</span>
                    <span>{booking_details['status']}</span>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">Customer Information</div>
                <div class="detail-row">
                    <span class="detail-label">Name:</span>
                    <span>{booking_details['full_name']}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Email:</span>
                    <span>{booking_details['email']}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Phone:</span>
                    <span>{booking_details.get('phone', 'N/A')}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">License No:</span>
                    <span>{booking_details.get('license_no', 'N/A')}</span>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">Car Information</div>
                <div class="detail-row">
                    <span class="detail-label">Car:</span>
                    <span>{booking_details['brand']} {booking_details['model']}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Plate Number:</span>
                    <span>{booking_details['plate_no']}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Color:</span>
                    <span>{booking_details['color']}</span>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">Rental Details</div>
                <div class="detail-row">
                    <span class="detail-label">Start Date:</span>
                    <span>{booking_details['start_date']}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">End Date:</span>
                    <span>{booking_details['end_date']}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Rental Duration:</span>
                    <span>{days} day(s)</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Rate per Day:</span>
                    <span>${booking_details['rate_per_day']:.2f}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Pickup Location:</span>
                    <span>{booking_details.get('pickup_location', 'N/A')}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Dropoff Location:</span>
                    <span>{booking_details.get('dropoff_location', 'N/A')}</span>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">Payment Information</div>
                <div class="detail-row">
                    <span class="detail-label">Payment Method:</span>
                    <span>{booking_details.get('payment_method', 'N/A')}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Payment Status:</span>
                    <span>{booking_details.get('payment_status', 'pending')}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label total">Total Amount:</span>
                    <span class="total">${float(booking_details['total_amount']):.2f}</span>
                </div>
            </div>
            
            <div class="footer">
                <p>Thank you for choosing our Car Rental System!</p>
                <p>For any inquiries, please contact our support team.</p>
            </div>
        </body>
        </html>
        """
        
        from PyQt6.QtWidgets import QTextBrowser
        
        text_browser = QTextBrowser()
        text_browser.setHtml(receipt_html)
        layout.addWidget(text_browser)
        
        # Close button
        close_btn = QPushButton('Close')
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)


def main():
    app = QApplication(sys.argv)
    
    # Show login window
    login_window = LoginWindow()
    if login_window.exec() == QDialog.DialogCode.Accepted:
        # Show main window with user data
        main_window = MainWindow(login_window.user)
        main_window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
