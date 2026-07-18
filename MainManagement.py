import os
from time import sleep
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QStackedWidget
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from Custom_UI import *
from Stock_Management_ui import StockManagement
from DatabaseManagement import DatabaseManager
from CustomerManagement_ui import CustomerManagement
from datetime import datetime
from RentManagement_ui import RentManagement
# Ratio Multiplier for Different screen to adjust the program
from Reports_ui import ReportManagement
from Sale_Management_ui import SaleManagement
from themes import ThemeManager

# Load icons using resource_path


class MainManagement(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.db_manager = DatabaseManager()
        self.db_manager.create_tables()

    def initUI(self):
        # Set window properties
        window_icon = QIcon(resource_path('Assets/rental icon-01.png'))
        self.setWindowTitle("Stock Management and Rental System")
        self.setWindowIcon(window_icon)
        screen = QApplication.primaryScreen().size()
        default_width = int(screen.width() * 0.8)   # 80% of screen width
        default_height = int(screen.height() * 0.8)  # 80% of screen height
        self.resize(default_width, default_height)
        # self.showMaximized()
        self.show()

        # Create central widget and main stacked widget
        self.central_widget = QWidget()
        self.main_stacked_widget = QStackedWidget()
        self.progress_label = QLabel("")

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.main_stacked_widget)
        self.central_widget.setLayout(main_layout)
        self.setCentralWidget(self.central_widget)
        # Create main screens
        self.main_menu_screen = None

        self.stock_management = StockManagement(
            self.main_stacked_widget, self.main_menu_screen)
        self.customer_management = CustomerManagement(
            self.main_stacked_widget, self.main_menu_screen)
        self.rent_management = RentManagement(
            self.main_stacked_widget, self.main_menu_screen)
        self.report_management = ReportManagement(
            self.main_stacked_widget, self.main_menu_screen)
        self.sale_management = SaleManagement(
            self.main_stacked_widget, self.main_menu_screen)
        self.create_main_screens()
        self.stock_management.main_menu_screen = self.main_menu_screen
        self.customer_management.main_menu_screen = self.main_menu_screen
        self.rent_management.main_menu_screen = self.main_menu_screen
        self.report_management.main_menu_screen = self.main_menu_screen
        self.sale_management.main_menu_screen = self.main_menu_screen
        # Show initial screen
        self.main_stacked_widget.setCurrentWidget(self.main_menu_screen)
        self.show()

    # Then modify your MainManagement.py to use ThemeManager:

    def change_theme(self, theme_name):
        self.close()
        theme_manager = ThemeManager()
        theme_manager.update_theme(theme_name)
        new_management = MainManagement()
        new_management.show()

    def create_main_screens(self):
        modules = [
            ("Stock Management", self.stock_management.setup_stock_management_Screen),
            ("Customer Management",
             self.customer_management.setup_customer_management_screen),
            ("Rent Management", self.rent_management.setup_rent_management_screen),
            ("Sales Management", self.sale_management.setup_sale_management_screen),
            ("Reports", self.report_management.setup_report_management_screen),
            ("Upload Database", self.upload_to_google_drive)
        ]
        management_layout, self.main_menu_screen = setup_options_management_screen(
            self.main_stacked_widget, "Stock Management & Rental System", modules, provide_theme_buttons=True, main_object=self)
        # Add progress label
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet(
            f"font-size: {int(20*SCRN_RATIO)}px; color: blue;")

        # self.progress_label.setAlignment(Qt.AlignBottom)
        self.progress_label.setFixedHeight(
            int(20*SCRN_RATIO))  # Adjust height as needed

        management_layout.addWidget(self.progress_label)
        self.create_navigation_ribbon()

    def create_navigation_ribbon(self):
        ribbon_layout = QHBoxLayout()
        ribbon_buttons = [
            ("Stock Management", self.stock_management.setup_stock_management_Screen),
            ("Customer Management",
             self.customer_management.setup_customer_management_screen),
            ("Rent Management", self.rent_management.setup_rent_management_screen),
            ("Reports", self.report_management.setup_report_management_screen)
        ]

        for button_text, button_callback in ribbon_buttons:
            button = get_styled_buttons(
                button_text,
                height=int(40 * SCRN_RATIO),
                module_func=button_callback,
                side_margin=int(10 * SCRN_RATIO),
                width=int(150 * SCRN_RATIO),
                font_size=int(20 * SCRN_RATIO)
            )
            ribbon_layout.addWidget(button)
        ribbon_widget = QWidget()
        ribbon_widget.setLayout(ribbon_layout)
        # Add the ribbon layout to the main layout
        self.main_stacked_widget.insertWidget(0, ribbon_widget)

    def authenticate_google_drive(self):
        gauth = GoogleAuth()

        # Specify the path to save credentials
        credentials_path = "credentials.json"

        # Load saved credentials if available
        if os.path.exists(credentials_path):
            gauth.LoadCredentialsFile(credentials_path)
            if gauth.access_token_expired:  # Refresh token if expired
                gauth.Refresh()
            else:  # Authenticate if credentials are invalid
                gauth.Authorize()
        else:
            # Perform the first-time authentication
            gauth.LocalWebserverAuth()
            # Save the credentials for future use
            gauth.SaveCredentialsFile(credentials_path)

        return gauth

    def upload_to_google_drive(self):
        try:
            self.progress_label.setText("Authenticating with Google Drive...")
            QApplication.processEvents()  # Ensure UI updates immediately

            gauth = self.authenticate_google_drive()
            drive = GoogleDrive(gauth)
            self.progress_label.setText("Preparing to upload the database...")
            QApplication.processEvents()

            # Define the path to your SQLite3 database file
            db_file_path = 'stock_rental_system.db'
            db_file_name = 'stock_rental_system.db'

            # Check if the file already exists on Google Drive
            file_list = drive.ListFile(
                {'q': f"title='{db_file_name}'"}).GetList()
            old_file_name = None  # Initialize variable to handle the deletion step

            if file_list:
                self.progress_label.setText(
                    "Renaming the existing file on Google Drive...")
                QApplication.processEvents()

                # Rename the existing file with a timestamp before uploading the new one
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                old_file = file_list[0]
                old_file_name = f"{db_file_name}_{timestamp}.db"

                old_file['title'] = old_file_name
                old_file.Upload()  # Update the title to rename the file
                self.progress_label.setText(
                    f"Renamed existing file to '{old_file_name}'.")
                QApplication.processEvents()
            else:
                self.progress_label.setText(
                    "No existing file found. Proceeding with the upload...")
                QApplication.processEvents()

            self.progress_label.setText("Uploading the new database file...")
            QApplication.processEvents()

            # Upload the new file
            new_file = drive.CreateFile({'title': db_file_name})
            new_file.SetContentFile(db_file_path)
            new_file.Upload()

            self.progress_label.setText(
                f"File '{db_file_name}' uploaded successfully.")
            QApplication.processEvents()

            # Optionally, delete the renamed file if it exists
            if old_file_name:
                self.progress_label.setText(
                    f"Deleting the old database file '{old_file_name}'...")
                QApplication.processEvents()
                old_file.Delete()
                self.progress_label.setText(
                    f"Deleted the previous version '{old_file_name}'.")
                QApplication.processEvents()
                self.progress_label.setText(
                    "Database upload completed successfully.")
                QApplication.processEvents()
                sleep(2)
                self.progress_label.setText("")
                QApplication.processEvents()

        except Exception as e:
            self.progress_label.setText(f"An error occurred: {e}")
            QApplication.processEvents()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainManagement()
    window.show()
    app.exec_()
