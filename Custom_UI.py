import sys
import os
import re
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,QMessageBox,QGridLayout,QToolButton,QComboBox,QDialog,QApplication, QScrollArea, QFrame, QSizePolicy
)
from PyQt5.QtGui import QPalette, QBrush, QPixmap,QRegExpValidator,QIcon,QIntValidator
from PyQt5.QtCore import Qt,QSize,QRegExp,QDateTime
from PyQt5.QtWidgets import QProgressDialog
from DatabaseManagement import DatabaseManager


SCRN_RATIO=0.7
DATE_TIME_FORMAT_QT = "dddd, MMMM d, yyyy hh:mm AP"
DISPLAY_DATE_TIME_FORMAT="dddd, MMMM d, yyyy hh:mm AP"
DATABASE_DATETIME_FORMAT="yyyy-MM-dd hh:mm"
PAGINATION_THRESHOLD = 100
ITEMS_PER_PAGE=100

STOCK_DB_COLUMNS = ['st_name', 'total_quantity', 'available_quantity']
STOCK_PRICE_DB_COLUMNS = ['stock_id', 'price', 'price_date']
CUSTOMER_DB_COLUMNS = ['name', 'contact_number', 'address', 'id_card_number', 'referrer_name', 'total_amount_due', 'amount_paid']
RENT_DB_COLUMNS = ['customer_id', 'stock_id', 'quantity', 'rent_date', 'payment_status', 'amount_due']
PAYMENTS_DB_COLUMNS = ['customer_id', 'payment_amount', 'discount', 'payment_date']
SELLING_STOCK_DB_COLUMNS = ['item_name', 'available_quantity', 'buying_price', 'selling_price', 'price_updated_date']
SOLD_ITEMS_DB_COLUMNS = ['stock_name', 'quantity', 'total_cost_amount', 'total_sale_amount', 'discount_amount','profit_amount', 'payment_date']
UNPAID_CUSTOMERS_DB_COLUMNS = ['customer_name', 'customer_mobile', 'id_card', 'amount_due', 'loan_date']



# Then in your customer_ui.py and other files that need the constants:
from themes import ThemeManager

tables={
    "customers": "Customer",
    "stock": "Stock",
    "rent":"Rent",
    "stock_price":"Stock_Price",
    "payments":"Payments",
    "selling_stock":"Selling_Stock",
    "sold_items":"Sold_Items",
    "unpaid_customers":"Unpaid_Customers",
}

def create_bold_label(text, font_size=10):
    label = QLabel(text)
    font = label.font()
    font.setPointSize(int(font_size*SCRN_RATIO))
    label.setFont(font)
    return label



def get_styled_input_labels(text):
    theme_manager = ThemeManager()
    label = QLabel("<b>"+text+"</b>")
    label.setStyleSheet(f"color: {theme_manager.INPUT_FIELDS_LABEL_COLOR}; font-size: {int(22*SCRN_RATIO)}px; border: none; background: transparent;")
    label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
    label.setContentsMargins(0, 0, int(20*SCRN_RATIO), 0)
    return label


def get_styled_label(text):
    theme_manager = ThemeManager()
    label = QLabel("<b>" + text + "</b>")
    label.setStyleSheet(f"color: {theme_manager.LABELS_TEXT_COLOR}; font-size: {int(35*SCRN_RATIO)}px;")
    label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
    label.setFixedHeight(int(50*SCRN_RATIO))
    return label

def get_styled_buttons(text, height, module_func, side_margin, bg_color="white", width=int(200*SCRN_RATIO), font_size=int(25*SCRN_RATIO)):
    theme_manager=ThemeManager()
    
    module_button = CustomButton(text)
    module_button.setStyleSheet(f"""
        QPushButton {{
            background-color: {theme_manager.BUTTONS_BG_COLOR}; 
            color: {theme_manager.BUTTONS_TEXT_COLOR}; 
            padding: {int(15*SCRN_RATIO)}px {int(30*SCRN_RATIO)}px; 
            font-size: {font_size}px;
            margin: 0px {side_margin}px;
            border-radius: {int(15*SCRN_RATIO)}px;
        }}
        
        QPushButton:hover {{
            background-color: {theme_manager.BUTTONS_HOVER_COLOR};
        }}
        """)
    module_button.setFixedHeight(int(height))
    module_button.setMinimumWidth(int(width))
    module_button.clicked.connect(module_func)
    module_button.setFocusPolicy(Qt.StrongFocus)  # Ensure buttons can receive focus
    return module_button



class TableScreen(QWidget):
    def __init__(self, stacked_widget, title, headers, **kwargs):
        super().__init__()

        # Store passed parameters as class variables
        self.stacked_widget = stacked_widget
        self.title = title
        self.headers = headers
        self.db_manager=DatabaseManager()
        # Store optional parameters with defaults
        self.table_data = kwargs.get('table_data', None)
        self.search_columns = kwargs.get('search_columns', None)
        self.button_actions = kwargs.get('button_actions', None)
        self.back_action = kwargs.get('back_action', None)
        self.editable_columns = kwargs.get('editable_columns', None)
        self.sortable_columns = kwargs.get('sortable_columns', None)
        self.full_data_columns = kwargs.get('full_data_columns', None)
        self.last_col_function = kwargs.get('last_col_function', None)
        self.hidden_columns = kwargs.get('hidden_columns', None)
        self.show_pagination = kwargs.get('show_pagination', True)
        self.table_name = kwargs.get('table_name', None)
        self.db_columns = kwargs.get('db_columns', None)
        self.search_function=kwargs.get('search_function',None)
        self.filter_options=kwargs.get('filter_options',None)
        self.add_ending_zero=kwargs.get('ending_zero',None)
        # Constants
        self.PAGINATION_THRESHOLD = PAGINATION_THRESHOLD
        self.ITEMS_PER_PAGE = ITEMS_PER_PAGE
        # Initialize UI components
        self.theme_manager = ThemeManager()
        self.table_widget = None
        self.search_inputs = {}
        self.filter_inputs = {}
        self.pagination_widget = None
        self.initial_data=self.table_data
        # Setup UI
        self.init_ui()
        
    def init_ui(self):
        self.layout = QVBoxLayout()
        content_margin = int(10 * SCRN_RATIO)
        self.setLayout(self.layout)
        
        # Setup base screen
        self.setup_base_screen()
        
        self.setup_filter_options()
        # Setup table and related components
        self.setup_table()
        self.setup_search()
        self.setup_pagination()
        self.setup_buttons()
        # self.setStyleSheet(f"background-color: {self.theme_manager.INPUT_SCREEN_BG_COLOR};")
        self.setStyleSheet("background-color: white;")
        # Add to stacked widget
        self.stacked_widget.addWidget(self)
        self.stacked_widget.setCurrentWidget(self)
    
    def setup_base_screen(self):
        self.setStyleSheet("background-color: white;")

        content_margin = int(10 * SCRN_RATIO)
        self.layout.setContentsMargins(content_margin, content_margin, content_margin, content_margin)
        title_label = get_styled_label(self.title)
        self.layout.addWidget(title_label)
        
    def setup_table(self):
        self.table_widget = QTableWidget()
        self.setStyleSheet("background-color: white;")
        self.table_widget.setColumnCount(len(self.headers))
        self.table_widget.setHorizontalHeaderLabels(self.headers)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.table_widget.setStyleSheet("background-color: white;")
        
        if self.hidden_columns:
            for col in self.hidden_columns:
                self.table_widget.setColumnHidden(col, True)
        
        if self.sortable_columns:
            self.table_widget.setSortingEnabled(True)
            for col in range(self.table_widget.columnCount()):
                if col in self.sortable_columns:
                    self.table_widget.horizontalHeader().setSortIndicatorShown(True)
        
        if self.full_data_columns:
            self.table_widget.cellDoubleClicked.connect(self.handle_double_click)
            
        self.layout.addWidget(self.table_widget)
        
        # Populate initial data if no pagination
        if not (self.table_data and self.show_pagination):
            self.populate_table_data(self.table_data)
            
    def handle_double_click(self, row, col):
        if col in self.full_data_columns:
            item = self.table_widget.item(row, col)
            if item:
                QMessageBox.information(
                    self.table_widget,
                    "Cell Content",
                    item.text(),
                    QMessageBox.Ok
                )
                
    def setup_search(self):
        if not self.search_columns:
            return
            
        search_layout = QHBoxLayout()
        i = 0
        for placeholder, column_index in self.search_columns.items():
            search_input = QLineEdit()
            search_input.setStyleSheet("background-color: white;")
            search_input.setMinimumHeight(int(40 * SCRN_RATIO))
            search_input.setPlaceholderText(placeholder)
            
            if self.db_columns:
                self.search_inputs[self.db_columns[i]] = search_input
                i += 1
            self.filter_inputs[column_index] = search_input
            
            search_input.textChanged.connect(self.filter_table_view)
            search_layout.addWidget(search_input)
            
        if ((self.db_manager and self.table_name and self.db_columns)  or (self.search_function)) and self.show_pagination:
            search_button = QPushButton("Search")
            search_button.setStyleSheet(f"background-color: {self.theme_manager.BUTTONS_BG_COLOR}; color: white;")
            search_button.setMinimumHeight(int(40 * SCRN_RATIO))
            search_button.setFixedWidth(int(100 * SCRN_RATIO))
            search_button.clicked.connect(self.perform_database_search)
            search_layout.addWidget(search_button)
            
        self.layout.addLayout(search_layout)
        
    def filter_table_view(self):
        if getattr(self.table_widget, '_database_search_active', False):
            return
        
        for row in range(self.table_widget.rowCount()):
            should_hide = False
            for column, input_widget in self.filter_inputs.items():
                search_text = input_widget.text().lower().strip()
                if search_text:
                    item = self.table_widget.item(row, column)
                    if item:
                        cell_text = item.text().lower()
                        if not cell_text.startswith(search_text):
                            should_hide = True
                            break
            
            self.table_widget.setRowHidden(row, should_hide)



    def setup_filter_options(self):
        if self.filter_options is None:
            return
        filter_layout = QHBoxLayout()
        for filter_text, filter_func in self.filter_options:
            filter_button = get_styled_buttons(
                filter_text,
                height=int(60 * SCRN_RATIO),
                module_func=filter_func,
                width=int(200 * SCRN_RATIO),
                side_margin=int(10 * SCRN_RATIO),
                font_size=int(20 * SCRN_RATIO)
            )
            filter_layout.addWidget(filter_button)
        self.layout.addLayout(filter_layout)


    def check_data_length_and_populate_table(self, results):
        if not results or len(results) == 0:
            self.table_widget.setRowCount(0)
            if self.pagination_widget:
                self.pagination_widget.hide()
            return

        if self.show_pagination:
            self.table_data = results
            if not self.pagination_widget:
                self.setup_pagination()
            else:
                # Just update the existing pagination widget
                self.current_page = 1
                total_pages = (len(self.table_data) + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE
                self.page_label.setText(f"Page 1 of {total_pages}")
                self.pagination_widget.show()
                self.update_table_view()
            return

        self.populate_table_data(results)

    def setup_pagination(self):
        if not (self.table_data and self.show_pagination):
            if self.pagination_widget:
                self.pagination_widget.hide()
            return
            
        if self.pagination_widget:
            self.pagination_widget.show()
            self.current_page = 1
            total_pages = (len(self.table_data) + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE
            self.page_label.setText(f"Page 1 of {total_pages}")
            self.update_table_view()
            return
                
        self.current_page = 1
        self.pagination_widget = QWidget()
        pagination_layout = QHBoxLayout()
        self.pagination_widget.setLayout(pagination_layout)
        
        total_pages = (len(self.table_data) + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE
        self.page_label = QLabel(f"Page 1 of {total_pages}")
        
        prev_button = QPushButton("Previous")
        next_button = QPushButton("Next")
        
        page_input = QLineEdit()
        page_input.setFixedWidth(int(50 * SCRN_RATIO))
        page_input.setValidator(QIntValidator(1, total_pages))
        
        items_per_page_combo = QComboBox()
        items_per_page_combo.addItems(['50', '100', '200', '500'])
        items_per_page_combo.setCurrentText(str(self.ITEMS_PER_PAGE))
        
        # Connect signals
        prev_button.clicked.connect(lambda: self.go_to_page(self.current_page - 1))
        next_button.clicked.connect(lambda: self.go_to_page(self.current_page + 1))
        page_input.returnPressed.connect(
            lambda: self.go_to_page(int(page_input.text()) if page_input.text() else 1)
        )
        items_per_page_combo.currentTextChanged.connect(self.change_items_per_page)
        
        # Style widgets
        for widget in [prev_button, next_button]:
            widget.setFixedHeight(int(30 * SCRN_RATIO))
            widget.setFixedWidth(int(100 * SCRN_RATIO))
            widget.setStyleSheet(f"background-color: {self.theme_manager.BUTTONS_BG_COLOR}; color: white;")
            
        page_input.setStyleSheet("background-color: white;")
        items_per_page_combo.setStyleSheet("background-color: white;")
        
        # Add widgets to layout
        pagination_layout.addWidget(prev_button)
        pagination_layout.addWidget(page_input)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(next_button)
        pagination_layout.addWidget(QLabel("Items per page:"))
        pagination_layout.addWidget(items_per_page_combo)
        pagination_layout.addStretch()
        
        self.layout.addWidget(self.pagination_widget)
        self.update_table_view()       

    def perform_database_search(self,calling_from_outside=False):
        search_criteria = {}
        for col_name, search_input in self.search_inputs.items():
            if search_input.text().strip():
                search_criteria[col_name] = search_input.text().strip()
        self.table_widget._database_search_active = True
        if search_criteria or calling_from_outside:
            if self.search_function:
                results=self.search_function(search_criteria)
            else:
                results = self.db_manager.search_items(self.table_name, search_criteria)

            if self.add_ending_zero:
                results=get_all_items_with_adding_leading_zero(results)
            self.check_data_length_and_populate_table(results)
        else:
            self.check_data_length_and_populate_table(self.initial_data)
            
        self.table_widget._database_search_active = False
        
                    
        
    def go_to_page(self, page_num):
        total_pages = (len(self.table_data) + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE
        if 1 <= page_num <= total_pages:
            self.current_page = page_num
            self.update_table_view()
            
    def change_items_per_page(self, new_value):
        self.ITEMS_PER_PAGE = int(new_value)
        self.current_page = 1
        self.update_table_view()
        
    def populate_table_data(self, table_data, check_pagination=True):
        if not table_data or not isinstance(table_data, list):
            self.table_widget.setRowCount(0)
            return
            
        # Only check pagination threshold on initial population
        if check_pagination and len(table_data) > self.PAGINATION_THRESHOLD and self.show_pagination:
            self.table_data = table_data
            self.update_table_view()
            return
        
        for row in range(self.table_widget.rowCount()):
            self.table_widget.setRowHidden(row, False)
            
        num_function_cols = len(self.last_col_function) if self.last_col_function else 0
        self.table_widget.setRowCount(len(table_data))
        self.table_widget.setColumnCount(len(table_data[0]) + num_function_cols)
        
        if self.last_col_function:
            base_columns = len(table_data[0])
            for idx, button_name in enumerate(self.last_col_function.keys()):
                header_item = QTableWidgetItem(button_name)
                self.table_widget.setHorizontalHeaderItem(base_columns + idx, header_item)
                
        for row_idx, row_data in enumerate(table_data):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem()
                item.setBackground(Qt.white)
                if "date" in self.headers[col_idx].lower():
                    value = QDateTime.fromString(value, DATABASE_DATETIME_FORMAT).toString(DISPLAY_DATE_TIME_FORMAT)
                if isinstance(value, (int, float)):
                    # item.setData(Qt.DisplayRole, float(value))
                    item.setData(Qt.DisplayRole, round(value))
                else:
                    item.setText(str(value))
                    
                self.table_widget.setItem(row_idx, col_idx, item)
                
                if self.editable_columns and col_idx in self.editable_columns:
                    item.setFlags(item.flags() | Qt.ItemIsEditable)
                else:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    
            if self.last_col_function:
                for col_idx, (button_name, function) in enumerate(self.last_col_function.items()):
                    action_button = QPushButton(button_name)
                    action_button.clicked.connect(
                        lambda checked, r=row_idx, f=function: f(r)
                    )
                    action_button.setStyleSheet(f"background-color: {self.theme_manager.BACKGROUND_COLOR};")
                    self.table_widget.setCellWidget(row_idx, len(row_data) + col_idx, action_button)

    def update_table_view(self):
        start_idx = (self.current_page - 1) * self.ITEMS_PER_PAGE
        end_idx = min(start_idx + self.ITEMS_PER_PAGE, len(self.table_data))
        visible_data = self.table_data[start_idx:end_idx]
        
        # Pass check_pagination=False to avoid recursion
        self.populate_table_data(visible_data, check_pagination=False)
        
        total_pages = (len(self.table_data) + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE
        self.page_label.setText(f"Page {self.current_page} of {total_pages}")
        
    def setup_buttons(self):
        if self.button_actions:
            button_layout = QHBoxLayout() if len(self.button_actions) > 2 else QVBoxLayout()
            
            for button_text, button_callback in self.button_actions:
                button = get_styled_buttons(
                    button_text,
                    height=int(60 * SCRN_RATIO),
                    module_func=button_callback,
                    width=int(200 * SCRN_RATIO),
                    side_margin=int(10 * SCRN_RATIO)
                )
                button_layout.addWidget(button, alignment=Qt.AlignCenter)
            
            self.layout.addLayout(button_layout)
            
        if self.back_action:
            back_button = get_styled_buttons(
                'Back',
                height=int(60 * SCRN_RATIO),
                module_func=self.back_action,
                width=int(200 * SCRN_RATIO),
                side_margin=int(10 * SCRN_RATIO)
            )
            self.layout.addWidget(back_button, alignment=Qt.AlignCenter)
            
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            current_item = self.table_widget.currentItem()
            current_row = self.table_widget.currentRow()
            current_col = self.table_widget.currentColumn()
            
            # Check if the current cell has a button widget
            button_widget = self.table_widget.cellWidget(current_row, current_col)
            if isinstance(button_widget, QPushButton):
                button_widget.click()  # Simulate button click
            elif current_item:  # Handle normal cells
                if self.editable_columns and current_col in self.editable_columns:
                    self.table_widget.editItem(current_item)
                elif self.full_data_columns and current_col in self.full_data_columns:
                    self.handle_double_click(current_row, current_col)
        elif event.key() == Qt.Key_Backspace and self.back_action:
            self.back_action()

        super().keyPressEvent(event)



def check_warning(self,response):
    if response[1]==False:
        QMessageBox.warning(self, "Error", response[0])
        return True
    else:
        return False


def get_date_columns(table_widget):
    date_columns=[]
    for col in range(table_widget.columnCount()):
        if "date" in table_widget.horizontalHeaderItem(col).text().lower():
            date_columns.append(col)
    return date_columns


def get_table_data(table_widget):
    date_columns=get_date_columns(table_widget)
    rows = []
    row_count = table_widget.rowCount()
    col_count = table_widget.columnCount()

    if row_count == 0:
        return ('No data found in the table.', False)

    for row_idx in range(row_count):
        # Skip hidden rows
        if table_widget.isRowHidden(row_idx):
            continue

        row_data = []
        for col_idx in range(col_count):
            # Get the item from the cell
            item = table_widget.item(row_idx, col_idx)
            # If item exists, get its text; otherwise, append an empty string
            if not item:
                continue
            if item.text() != "" or item.text() is not None:
                item=item.text()
                if col_idx in date_columns:
                    item=QDateTime.fromString(item, DISPLAY_DATE_TIME_FORMAT).toString(DATABASE_DATETIME_FORMAT)
                row_data.append(item)
            else:
                return (f"Row {row_idx + 1} has missing data. Please fill in all fields.", False)
        rows.append(row_data)

    return rows


# Method 2: Get entire row as a list of values
def get_single_row_data(table_widget, row_number):
    row_data = []
    date_columns=get_date_columns(table_widget)
    for col in range(table_widget.columnCount()):
        item = table_widget.item(row_number, col)
        if item and item.text().strip()!='' and item.text() is not None:
            item=item.text()
            if col in date_columns:
                item=QDateTime.fromString(item, DISPLAY_DATE_TIME_FORMAT).toString(DATABASE_DATETIME_FORMAT)
            row_data.append(item)
        else:
            row_data.append(None)
    return row_data



def confirm_deletion(self,title,message):
        reply = QMessageBox.question(
            self,
            title,
            message,
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            return True
        return False


def has_alphabet_or_special_char(s):

    # Regular expression to match any alphabet or special character
    ## Will return true if there is any alphabet or special character
    return bool(re.search(r'[a-zA-Z!@#$%^&*()_+\-=\[\]{};:\'\"\\|,<>\/?]', s))




class CustomButton(QPushButton):
    def keyPressEvent(self, event):
        if event.key() in [Qt.Key_Enter, Qt.Key_Return]:
            self.clicked.emit()
        else:
            super().keyPressEvent(event)


def setup_options_management_screen(stacked_widget, title, options, provide_theme_buttons=False, 
main_object=None):
    theme_manager = ThemeManager()
    management_screen = QWidget()
    management_layout = QVBoxLayout()
    management_screen.setLayout(management_layout)
    
    bg_img_path = resource_path(theme_manager.BACKGROUND_IMG).replace('\\','/')

    def resize_background():
        palette = QPalette()
        pixmap = QPixmap(bg_img_path)
        scaled_pixmap = pixmap.scaled(management_screen.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        palette.setBrush(QPalette.Window, QBrush(scaled_pixmap))
        management_screen.setPalette(palette)
    
    def handle_resize(event):
        resize_background()
        QWidget.resizeEvent(management_screen, event)
    
    management_screen.resizeEvent = handle_resize
    management_screen.setAutoFillBackground(True)
    management_screen.setObjectName("management_screen")
    management_screen.setFocusPolicy(Qt.StrongFocus)
    
    # Title first - centered and static
    management_label = get_styled_label(title)
    management_layout.addWidget(management_label, alignment=Qt.AlignHCenter)
    # Add this line to reduce space between label and first button # Reduces space between all widgets
    # Or for more control, add a spacer with custom height
    if provide_theme_buttons:
        # Create absolute positioned container for theme buttons
        theme_container = QWidget(management_screen)
        theme_container.setFixedSize(int(250*SCRN_RATIO), int(50*SCRN_RATIO))  # Adjust size as needed
        theme_layout = QHBoxLayout(theme_container)
        theme_layout.setSpacing(int(50*SCRN_RATIO))  # Minimal spacing between buttons
        theme_layout.setContentsMargins(0, 0, 0, 0)  # No margins
        
        def create_theme_button(icon_path, theme_name):
            button = QToolButton()
            button.setIcon(QIcon(resource_path(icon_path)))
            button.setIconSize(QSize(int(60*SCRN_RATIO), int(60*SCRN_RATIO)))  # Slightly smaller icons
            button.setFixedSize(int(50*SCRN_RATIO), int(50*SCRN_RATIO))  # Compact button size
            button.setToolTip(f"{theme_name} Theme")
            
            button.setStyleSheet(f"""
                QToolButton {{
                    border: none;
                    border-radius: {4*SCRN_RATIO}px;
                    padding: {2*SCRN_RATIO}px;
                    background-color: transparent;
                    margin: 0px {1*SCRN_RATIO}px;
                }}
                QToolButton:hover {{
                    background-color: rgba(0, 0, 0, 0.1);
                }}
            """)
            
            return button
        
        # Create theme buttons with icons
        blue_button = create_theme_button("Assets/blue_theme.png", "Blue")
        orange_button = create_theme_button("Assets/orange_theme.png", "Orange")
        black_button = create_theme_button("Assets/black_theme.png", "Black")
        
        # Add buttons to theme layout
        theme_layout.addWidget(blue_button)
        theme_layout.addWidget(orange_button)
        theme_layout.addWidget(black_button)
        
        # Connect theme buttons
        blue_button.clicked.connect(lambda: main_object.change_theme("blue"))
        orange_button.clicked.connect(lambda: main_object.change_theme("orange"))
        black_button.clicked.connect(lambda: main_object.change_theme("black"))
        
        # Position theme container absolutely in top-left corner
        theme_container.move(int(1500*SCRN_RATIO), int(30*SCRN_RATIO))  # Adjust position as needed

    # Content margin and spacing
    content_margin = int(10* SCRN_RATIO)
    management_layout.setContentsMargins(content_margin, content_margin, content_margin, content_margin)
    management_layout.setSpacing(content_margin)

    # Add option buttons
    buttons = []
    for button_name, button_func in options:
        customer_button = get_styled_buttons(button_name, height=int(100 * SCRN_RATIO), 
                                          module_func=button_func, 
                                          side_margin=int(800 * SCRN_RATIO))
        management_layout.addWidget(customer_button)
        buttons.append(customer_button)

    current_index = 0
    if buttons:
        buttons[current_index].setFocus()

    def handle_key_press(event):
        nonlocal current_index
        if event.key() == Qt.Key_Up:
            if current_index > 0:
                current_index -= 1
                buttons[current_index].setFocus()
        elif event.key() == Qt.Key_Down:
            if current_index < len(buttons) - 1:
                current_index += 1
                buttons[current_index].setFocus()
        elif event.key() == Qt.Key_Backspace:
            if not options[-1][0] == "Upload Database":
                options[-1][1]()
                return
        else:
            event.ignore()

    management_screen.keyPressEvent = handle_key_press
    resize_background()

    stacked_widget.addWidget(management_screen)
    stacked_widget.setCurrentWidget(management_screen)
    return (management_layout, management_screen)




def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)



def setup_input_screen(main_stacked_widget, back_action, calling_object, form_fields, save_stock_method, title):
    # Add Stock Screen
    theme_manager = ThemeManager()
    add_stock_screen = QWidget()
    add_stock_layout = QVBoxLayout()
    add_stock_screen.setLayout(add_stock_layout)
    content_margin = int(10 * SCRN_RATIO)
    add_stock_layout.setContentsMargins(content_margin, content_margin, content_margin, content_margin)
    add_stock_screen.setStyleSheet("background-color: white;")
    # Set focus policy
    add_stock_screen.setFocusPolicy(Qt.StrongFocus)
    # Install event filter
    add_stock_screen.installEventFilter(calling_object)
    
    # Title
    add_stock_title = get_styled_label(title)
    add_stock_layout.addWidget(add_stock_title)
    
    # Form Layout
    form_layout = QGridLayout()
    form_layout.setSpacing(int(30 * SCRN_RATIO))
    # Only allow digits
    rx = QRegExp("[0-9]*")
    validator = QRegExpValidator(rx)
    for i, (label_text, attr_name) in enumerate(form_fields):
        label = get_styled_input_labels(label_text)
        input_field = QLineEdit()
        if attr_name == "id_card_input":
            input_field.setMaxLength(13)
        if attr_name == "contact_input" or attr_name == "mobile_no_input":
            input_field.setMaxLength(11)

        if "price" in attr_name or "quantity" in attr_name or "id" in attr_name or "contact" in attr_name or "mobile" in attr_name:
            input_field.setValidator(validator)
        input_field.setMinimumHeight(int(45 * SCRN_RATIO))
        input_field.setStyleSheet(f"""
            QLineEdit {{
                font-size: {int(22 * SCRN_RATIO)}px; 
                background-color: #F8F9FA;
                border: 2px solid #E9ECEF;
                border-radius: {int(8 * SCRN_RATIO)}px;
                padding: {int(10 * SCRN_RATIO)}px;
                color: #333333;
            }}
            QLineEdit:focus {{
                border: 2px solid {theme_manager.BUTTONS_BG_COLOR};
                background-color: #FFFFFF;
            }}
        """)
        setattr(calling_object, attr_name, input_field)
        
        form_layout.addWidget(label, i, 0)
        form_layout.addWidget(input_field, i, 1)
    
    add_stock_layout.addLayout(form_layout)
    
    # Button Layout
    button_layout = QHBoxLayout()
    button_layout.addStretch()
    
    back_button = get_styled_buttons(
        'Back',
        height=int(50 * SCRN_RATIO),
        module_func=back_action,
        side_margin=int(10 * SCRN_RATIO),
        width=int(180 * SCRN_RATIO)
    )
    button_layout.addWidget(back_button)
    
    # Save Button
    save_stock_button = get_styled_buttons(
        'Save',
        height=int(50 * SCRN_RATIO),
        module_func=save_stock_method,
        side_margin=int(10 * SCRN_RATIO),
        bg_color="#02C39A",
        width=int(180 * SCRN_RATIO)
    )
    button_layout.addWidget(save_stock_button)
    button_layout.addStretch()
    
    add_stock_layout.addLayout(button_layout)
    
    # Add screens to main stacked widget
    main_stacked_widget.addWidget(add_stock_screen)
    main_stacked_widget.setCurrentWidget(add_stock_screen)
    return add_stock_screen, save_stock_button



def get_all_items_with_adding_leading_zero(data):
    if len(data)==0:
        return data
    for i,item in enumerate(data):
        data[i]=item+(0,)
    return data

def create_progress_dialog(self,data_length,title):
        # Create progress dialog
    progress = QProgressDialog(f"{title}...", "Cancel", 0, data_length, self)
    progress.setWindowModality(Qt.WindowModal)
    progress.setWindowTitle("Processing")
    progress.setMinimumDuration(0)  # Show immediately for any number of items
    return progress



class SelectedItemsDialog(QDialog):
    def __init__(self, headers, parent=None):
        super().__init__(parent)
        self.headers = headers
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Selected Items")
        self.setModal(True)
        layout = QVBoxLayout()
        
        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.headers) + 1)  # +1 for Remove button
        headers_with_action = self.headers + ["Remove"]
        self.table.setHorizontalHeaderLabels(headers_with_action)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
        
        self.setLayout(layout)
        self.resize(int(600*SCRN_RATIO), int(400*SCRN_RATIO))
        
    def update_items(self, items, remove_callback,selling_quantity_index):
        items=[[item[0],item[1],item[selling_quantity_index]] for item in items]
        self.table.setRowCount(len(items))
        for row, item in enumerate(items):
            for col, value in enumerate(item):
                table_item = QTableWidgetItem(str(value))
                table_item.setFlags(table_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, col, table_item)
            
            # Add Remove button
            remove_button = QPushButton("Remove")
            remove_button.clicked.connect(lambda checked, r=row: remove_callback(r))
            self.table.setCellWidget(row, len(self.headers), remove_button)

class StockSelector:
    def __init__(self,available_quantity_index,table_widget=None,item_key_index=0,rent_sell_quantity_index=6):
        """
        headers_to_show: List of headers to display in the popup
        item_key_index: Index of the unique identifier column in the data
        """
        self.table_widget=table_widget
        self.selected_items = {}  # Dictionary to store selected items
        self.headers = ['Stock ID','Stock Name','Quantity']
        self.selling_quantity_index=rent_sell_quantity_index
        self.available_quantity_index=available_quantity_index
        self.item_key_index = item_key_index
        self.dialog = None
        
    
    def add_item(self, row_data):
        """Add an item to the selected items list"""
        item_data=get_single_row_data(self.table_widget,row_data)

        if has_alphabet_or_special_char(item_data[self.selling_quantity_index]):
            QMessageBox.warning(None, "Validation Error", f"Enter a valid quantity.\nProblem in id: {item_data[0]}\nName: {item_data[1]}")
            return
        
        quantity_to_sell = int(item_data[self.selling_quantity_index])
        available_quantity = int(item_data[self.available_quantity_index])

        if quantity_to_sell == 0:
            QMessageBox.warning(None, "Input Error", f"No Quantity Sellected\nProblem in id: {item_data[0]}\nName: {item_data[1]}")
            return

        if quantity_to_sell > available_quantity:
            QMessageBox.warning(None, "Insufficient Stock", f"The quantity exceeds available stock.\nProblem in id: {item_data[0]}\nName: {item_data[1]}")
            return
    
        self.selected_items[item_data[0]] = item_data
        self.update_dialog()
        return
            
    def remove_item(self, row_index):
        """Remove an item from the selected items list"""
        item_data=get_single_row_data(table_widget=self.table_widget,row_number=row_index)
        self.selected_items.pop(item_data[0],None)
        self.update_dialog()
            
    def show_selected_items(self):
        """Show the dialog with selected items"""
        if not self.selected_items:
            QMessageBox.warning(None, "No Items Selected", "No items have been selected.")
            return
        if not self.dialog:
            self.dialog = SelectedItemsDialog(self.headers)
        self.update_dialog()
        self.dialog.show()
        
    def update_dialog(self):
        """Update the dialog with current items"""
        if self.dialog:
            self.dialog.update_items(
                list(self.selected_items.values()),
                self.remove_item,
                selling_quantity_index=self.selling_quantity_index
            )
    
    def get_selected_items(self):
        """Return list of selected items"""
        if len(self.selected_items)==0:
            return []
        item_values=list(self.selected_items.values())
        return item_values
    

def get_screen_size():
        # Get screen dimensions
    screen = QApplication.primaryScreen().geometry()
    screen_width = screen.width()
    screen_height = screen.height()
    return screen_width,screen_height


class CardScreen(QWidget):
    def __init__(self, stacked_widget, title, card_generator_func, **kwargs):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.title = title
        self.card_generator_func = card_generator_func  # Function that takes (row_data, parent) and returns a QWidget (the card)
        self.db_manager = DatabaseManager()
        
        self.table_data = kwargs.get('table_data', [])
        self.search_columns = kwargs.get('search_columns', None)
        self.button_actions = kwargs.get('button_actions', None)
        self.back_action = kwargs.get('back_action', None)
        self.db_columns = kwargs.get('db_columns', None)
        self.table_name = kwargs.get('table_name', None)
        self.search_function = kwargs.get('search_function', None)
        self.filter_options = kwargs.get('filter_options', None)
        self.show_pagination = kwargs.get('show_pagination', True)
        self.PAGINATION_THRESHOLD = 0 # Always paginate cards to ensure fast loading
        self.ITEMS_PER_PAGE = 20 # Lowered for performance with Card UI
        self.current_page = 1
        self.pagination_widget = None
        self.add_ending_zero = kwargs.get('ending_zero', None)

        # We can implement pagination later, for now we will just use a scroll area
        self.initial_data = self.table_data
        
        self.theme_manager = ThemeManager()
        self.search_inputs = {}
        self.filter_inputs = {}
        
        self.init_ui()
        
    def init_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setStyleSheet("background-color: white;")
    
        content_margin = int(10 * SCRN_RATIO)
        self.layout.setContentsMargins(content_margin, content_margin, content_margin, content_margin)
        
        # Title
        title_label = get_styled_label(self.title)
        self.layout.addWidget(title_label)
        
        # Filter Options
        if self.filter_options:
            filter_layout = QHBoxLayout()
            for filter_text, filter_func in self.filter_options:
                filter_button = get_styled_buttons(
                    filter_text, height=int(60 * SCRN_RATIO), module_func=filter_func, width=int(200 * SCRN_RATIO), side_margin=int(10 * SCRN_RATIO), font_size=int(20 * SCRN_RATIO)
                )
                filter_layout.addWidget(filter_button)
            self.layout.addLayout(filter_layout)
            
        # Search
        self.setup_search()
        
        # Scroll Area for Cards
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.cards_container = QWidget()
        self.cards_container.setStyleSheet("background-color: transparent;")
        
        # Use a GridLayout for cards (e.g. 2 or 3 columns based on preference, let's use a dynamic grid but for simplicity we wrap it in grid)
        self.cards_layout = QGridLayout()
        self.cards_layout.setSpacing(int(20 * SCRN_RATIO))
        self.cards_layout.setAlignment(Qt.AlignTop)
        
        self.cards_container.setLayout(self.cards_layout)
        self.scroll_area.setWidget(self.cards_container)
        
        self.layout.addWidget(self.scroll_area)
        
        # Pagination Setup
        self.setup_pagination()
        
        # Buttons Setup
        self.setup_buttons()
        
        self.check_data_length_and_populate_cards(self.table_data)
        
        self.stacked_widget.addWidget(self)
        self.stacked_widget.setCurrentWidget(self)

    def setup_search(self):
        if not self.search_columns:
            return
            
        search_layout = QHBoxLayout()
        i = 0
        for placeholder, column_index in self.search_columns.items():
            search_input = QLineEdit()
            search_input.setStyleSheet("background-color: white; padding: 5px; border-radius: 5px;")
            search_input.setMinimumHeight(int(40 * SCRN_RATIO))
            search_input.setPlaceholderText(placeholder)
            
            if self.db_columns:
                self.search_inputs[self.db_columns[i]] = search_input
                i += 1
            self.filter_inputs[column_index] = search_input
            
            search_input.textChanged.connect(self.filter_cards_view)
            search_layout.addWidget(search_input)
            
        if (self.db_manager and self.table_name and self.db_columns) or self.search_function:
            search_button = QPushButton("Search DB")
            search_button.setStyleSheet(f"background-color: {self.theme_manager.BUTTONS_BG_COLOR}; color: white; border-radius: 5px;")
            search_button.setMinimumHeight(int(40 * SCRN_RATIO))
            search_button.setFixedWidth(int(100 * SCRN_RATIO))
            search_button.clicked.connect(self.perform_database_search)
            search_layout.addWidget(search_button)
            
        self.layout.addLayout(search_layout)

    def filter_cards_view(self):
        # Filtering happens simply by hiding/showing cards
        for i in range(self.cards_layout.count()):
            widget = self.cards_layout.itemAt(i).widget()
            if widget:
                row_data = widget.property("row_data")
                if not row_data:
                    continue
                should_hide = False
                for column, input_widget in self.filter_inputs.items():
                    search_text = input_widget.text().lower().strip()
                    if search_text:
                        # Assuming row_data has the same structure
                        if column < len(row_data):
                            cell_text = str(row_data[column]).lower()
                            if not cell_text.startswith(search_text):
                                should_hide = True
                                break
                widget.setVisible(not should_hide)

    def perform_database_search(self, calling_from_outside=False):
        search_criteria = {}
        for col_name, search_input in self.search_inputs.items():
            if search_input.text().strip():
                search_criteria[col_name] = search_input.text().strip()
                
        if search_criteria or calling_from_outside:
            if self.search_function:
                results = self.search_function(search_criteria)
            else:
                results = self.db_manager.search_items(self.table_name, search_criteria)
            
            if self.add_ending_zero:
                results = get_all_items_with_adding_leading_zero(results)
            self.check_data_length_and_populate_cards(results)
        else:
            self.check_data_length_and_populate_cards(self.initial_data)

    def check_data_length_and_populate_cards(self, results):
        if not results or len(results) == 0:
            self.populate_cards([])
            if self.pagination_widget:
                self.pagination_widget.hide()
            return

        if self.show_pagination:
            self.table_data = results
            if not self.pagination_widget:
                self.setup_pagination()
            else:
                self.current_page = 1
                total_pages = (len(self.table_data) + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE
                self.page_label.setText(f"Page 1 of {total_pages}")
                self.pagination_widget.show()
                self.update_cards_view()
            return

        self.populate_cards(results)

    def setup_pagination(self):
        if not (self.table_data and self.show_pagination):
            if self.pagination_widget:
                self.pagination_widget.hide()
            return
            
        if self.pagination_widget:
            self.pagination_widget.show()
            self.current_page = 1
            total_pages = (len(self.table_data) + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE
            self.page_label.setText(f"Page 1 of {total_pages}")
            self.update_cards_view()
            return
                
        self.current_page = 1
        self.pagination_widget = QWidget()
        pagination_layout = QHBoxLayout()
        self.pagination_widget.setLayout(pagination_layout)
        
        total_pages = (len(self.table_data) + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE
        self.page_label = QLabel(f"Page 1 of {total_pages}")
        
        from PyQt5.QtWidgets import QPushButton, QLineEdit, QComboBox
        from PyQt5.QtGui import QIntValidator
        prev_button = QPushButton("Previous")
        next_button = QPushButton("Next")
        
        page_input = QLineEdit()
        page_input.setFixedWidth(int(50 * SCRN_RATIO))
        page_input.setValidator(QIntValidator(1, total_pages))
        
        items_per_page_combo = QComboBox()
        items_per_page_combo.addItems(['20', '50', '100', '200'])
        items_per_page_combo.setCurrentText(str(self.ITEMS_PER_PAGE))
        
        prev_button.clicked.connect(lambda: self.go_to_page(self.current_page - 1))
        next_button.clicked.connect(lambda: self.go_to_page(self.current_page + 1))
        page_input.returnPressed.connect(
            lambda: self.go_to_page(int(page_input.text()) if page_input.text() else 1)
        )
        items_per_page_combo.currentTextChanged.connect(self.change_items_per_page)
        
        for widget in [prev_button, next_button]:
            widget.setFixedHeight(int(30 * SCRN_RATIO))
            widget.setFixedWidth(int(100 * SCRN_RATIO))
            widget.setStyleSheet(f"background-color: {self.theme_manager.BUTTONS_BG_COLOR}; color: white;")
            
        page_input.setStyleSheet("background-color: white;")
        items_per_page_combo.setStyleSheet("background-color: white;")
        
        pagination_layout.addWidget(prev_button)
        pagination_layout.addWidget(page_input)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(next_button)
        pagination_layout.addWidget(QLabel("Items per page:"))
        pagination_layout.addWidget(items_per_page_combo)
        pagination_layout.addStretch()
        
        self.layout.addWidget(self.pagination_widget)
        self.update_cards_view()

    def go_to_page(self, page_num):
        total_pages = (len(self.table_data) + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE
        if 1 <= page_num <= total_pages:
            self.current_page = page_num
            self.update_cards_view()
            
    def change_items_per_page(self, new_value):
        self.ITEMS_PER_PAGE = int(new_value)
        self.current_page = 1
        self.update_cards_view()

    def update_cards_view(self):
        start_idx = (self.current_page - 1) * self.ITEMS_PER_PAGE
        end_idx = min(start_idx + self.ITEMS_PER_PAGE, len(self.table_data))
        visible_data = self.table_data[start_idx:end_idx]
        
        self.populate_cards(visible_data, check_pagination=False)
        
        total_pages = (len(self.table_data) + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE
        self.page_label.setText(f"Page {self.current_page} of {total_pages}")

    def setup_buttons(self):
        button_layout = QHBoxLayout()
        if self.button_actions:
            for button_text, button_callback in self.button_actions:
                button = get_styled_buttons(
                    button_text, height=int(60 * SCRN_RATIO), module_func=button_callback, width=int(200 * SCRN_RATIO), side_margin=int(10 * SCRN_RATIO)
                )
                button_layout.addWidget(button, alignment=Qt.AlignCenter)
                
        if self.back_action:
            back_button = get_styled_buttons(
                'Back', height=int(60 * SCRN_RATIO), module_func=self.back_action, width=int(200 * SCRN_RATIO), side_margin=int(10 * SCRN_RATIO)
            )
            button_layout.addWidget(back_button, alignment=Qt.AlignCenter)
            
        self.layout.addLayout(button_layout)

    def populate_cards(self, table_data, check_pagination=True):
        if check_pagination and len(table_data) > self.PAGINATION_THRESHOLD and self.show_pagination:
            self.table_data = table_data
            if not self.pagination_widget:
                self.setup_pagination()
            else:
                self.pagination_widget.show()
                self.update_cards_view()
            return

        if check_pagination:
            self.table_data = table_data
        
        # Clear existing cards
        while self.cards_layout.count():
            child = self.cards_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        if not table_data:
            empty_label = QLabel("No records found.")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: gray; font-size: 20px;")
            self.cards_layout.addWidget(empty_label, 0, 0)
            return
            
        columns = 1 # Force single column layout

        
        for idx, row_data in enumerate(table_data):
            card = self.card_generator_func(row_data, self)
            card.setProperty("row_data", row_data)
            row = idx // columns
            col = idx % columns
            self.cards_layout.addWidget(card, row, col)