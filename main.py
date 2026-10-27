# ============================================================
# Fixed Price - Cryptocurrency Profit Calculator
# ============================================================
# This application helps users calculate the profit or loss
# they could make from a cryptocurrency investment.
#
# Users can:
# 1. Load cryptocurrency prices from a CSV file.
# 2. Select a cryptocurrency and investment dates.
# 3. Calculate profit, loss, and return on investment (ROI).
# 4. Compare the prices of different cryptocurrencies.
#
# The interface uses a simple green-and-white colour theme
# to keep the application clean and easy to understand.
# ============================================================


import sys
from pathlib import Path

import pandas as pd

# PyQt6 provides all the tools needed to create the desktop UI.
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QComboBox,
    QDoubleSpinBox,
    QDateEdit,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QFileDialog,
    QMessageBox,
    QFrame,
)


class FixedPrice(QMainWindow):
    """
    This is the main class for the Fixed Price application.

    It manages the window, loads the cryptocurrency dataset,
    calculates investment results, and compares assets.
    """

    def __init__(self):
        # Set up the main window before adding our own widgets.
        super().__init__()

        self.setWindowTitle("Fixed Price")
        self.setMinimumSize(900, 650)
        self.resize(1050, 750)

        # These colours keep the application looking consistent.
        self.green = "#23845B"
        self.dark_green = "#176443"
        self.light_green = "#EAF6EF"
        self.white = "#FFFFFF"
        self.background = "#F5F8F6"
        self.text_colour = "#26352D"
        self.muted_colour = "#6B7A70"
        self.border_colour = "#DCE7DF"

        # The dataset will be stored here once a CSV file loads.
        self.data = pd.DataFrame()
        self.csv_path = None

        # Build the interface first so the application is ready
        # for the user, even if the CSV file is not found.
        self.build_interface()
        self.apply_styles()

        # Try to find the CSV file automatically.
        # If it is not in the project folder, the user can
        # choose the file manually.
        csv_file = self.find_csv()

        if csv_file:
            self.load_csv(csv_file)
        else:
            self.choose_csv(show_message=False)

    # --------------------------------------------------------
    # FIND THE CSV FILE
    # --------------------------------------------------------

    def find_csv(self):
        """
        Look for the cryptocurrency CSV file in sensible places.

        Keeping the CSV next to main.py is the easiest option.
        If it is not there, the user can select it manually.
        """

        # Find the folder containing this Python file.
        app_folder = Path(__file__).resolve().parent

        # Check the most likely filenames first.
        possible_files = [
            app_folder / "combined(1).csv",
            app_folder / "combined.csv",
        ]

        for file_path in possible_files:
            if file_path.is_file():
                return file_path

        # If the expected filenames are missing, look for any
        # CSV file in the same folder.
        other_csv_files = sorted(app_folder.glob("*.csv"))

        if len(other_csv_files) == 1:
            return other_csv_files[0]

        # If several CSV files exist, it is safer to let the
        # user choose the correct one rather than guess.
        return None

    # --------------------------------------------------------
    # BUILD THE MAIN INTERFACE
    # --------------------------------------------------------

    def build_interface(self):
        """Create the main window layout and its two tabs."""

        # The central widget holds everything inside the window.
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # A vertical layout places the heading, tabs, and footer
        # neatly on top of one another.
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(28, 24, 28, 18)
        main_layout.setSpacing(18)

        # ---------------- HEADER ----------------

        header_layout = QHBoxLayout()

        heading_layout = QVBoxLayout()
        heading_layout.setSpacing(5)

        title = QLabel("Fixed Price")
        title.setObjectName("mainTitle")

        subtitle = QLabel(
            "A simple way to calculate and compare "
            "cryptocurrency investments."
        )
        subtitle.setObjectName("subtitle")
        subtitle.setWordWrap(True)

        heading_layout.addWidget(title)
        heading_layout.addWidget(subtitle)

        header_layout.addLayout(heading_layout)
        header_layout.addStretch()

        # This button allows the user to load or change the CSV
        # file without restarting the application.
        self.load_button = QPushButton("Load CSV")
        self.load_button.setObjectName("secondaryButton")
        self.load_button.clicked.connect(self.choose_csv)

        header_layout.addWidget(self.load_button)

        main_layout.addLayout(header_layout)

        # ---------------- TABS ----------------

        # Separate tabs keep the calculator and comparison tools
        # organised instead of squeezing everything into one page.
        self.tabs = QTabWidget()

        self.calculator_tab = QWidget()
        self.compare_tab = QWidget()

        self.tabs.addTab(self.calculator_tab, "Profit Calculator")
        self.tabs.addTab(self.compare_tab, "Compare Assets")

        main_layout.addWidget(self.tabs)

        # Build the contents of each tab.
        self.build_calculator_tab()
        self.build_compare_tab()

        # ---------------- FOOTER ----------------

        # This small label shows which dataset is currently loaded.
        # It also helps the user check that the correct file is used.
        self.file_status = QLabel("No CSV file loaded")
        self.file_status.setObjectName("footerLabel")

        main_layout.addWidget(self.file_status)

    # --------------------------------------------------------
    # PROFIT CALCULATOR TAB
    # --------------------------------------------------------

    def build_calculator_tab(self):
        """Create the controls used to calculate an investment."""

        layout = QVBoxLayout(self.calculator_tab)
        layout.setContentsMargins(8, 18, 8, 8)
        layout.setSpacing(18)

        # The form card keeps all investment inputs together.
        input_card = QFrame()
        input_card.setObjectName("card")

        form_layout = QGridLayout(input_card)
        form_layout.setContentsMargins(24, 24, 24, 24)
        form_layout.setHorizontalSpacing(20)
        form_layout.setVerticalSpacing(16)

        # Users select the cryptocurrency they want to analyse.
        asset_label = QLabel("Cryptocurrency")
        self.asset_combo = QComboBox()
        self.asset_combo.setMinimumHeight(40)

        # Investment amount is entered as a monetary value.
        amount_label = QLabel("Investment amount")
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.01, 1_000_000_000)
        self.amount_input.setDecimals(2)
        self.amount_input.setValue(1000.00)
        self.amount_input.setPrefix("$ ")
        self.amount_input.setMinimumHeight(40)

        # The user chooses when they would have bought the asset.
        buy_date_label = QLabel("Purchase date")
        self.buy_date = QDateEdit()
        self.buy_date.setCalendarPopup(True)
        self.buy_date.setDisplayFormat("dd MMM yyyy")
        self.buy_date.setMinimumHeight(40)

        # The second date is used to estimate the value at sale.
        sell_date_label = QLabel("Sale date")
        self.sell_date = QDateEdit()
        self.sell_date.setCalendarPopup(True)
        self.sell_date.setDisplayFormat("dd MMM yyyy")
        self.sell_date.setMinimumHeight(40)

        # Add each label and input to the form.
        form_layout.addWidget(asset_label, 0, 0)
        form_layout.addWidget(self.asset_combo, 1, 0)

        form_layout.addWidget(amount_label, 0, 1)
        form_layout.addWidget(self.amount_input, 1, 1)

        form_layout.addWidget(buy_date_label, 2, 0)
        form_layout.addWidget(self.buy_date, 3, 0)

        form_layout.addWidget(sell_date_label, 2, 1)
        form_layout.addWidget(self.sell_date, 3, 1)

        layout.addWidget(input_card)

        # ---------------- CALCULATE BUTTON ----------------

        self.calculate_button = QPushButton("Calculate Profit / Loss")
        self.calculate_button.setObjectName("primaryButton")
        self.calculate_button.setMinimumHeight(46)

        # Clicking the button runs our calculation method.
        self.calculate_button.clicked.connect(self.calculate_profit)

        layout.addWidget(self.calculate_button)

        # ---------------- RESULTS ----------------

        # These labels are updated after a calculation.
        # Starting with dashes makes it clear that no result
        # has been calculated yet.
        results_card = QFrame()
        results_card.setObjectName("card")

        results_layout = QGridLayout(results_card)
        results_layout.setContentsMargins(24, 24, 24, 24)
        results_layout.setHorizontalSpacing(20)
        results_layout.setVerticalSpacing(18)

        self.purchase_price_result = self.create_result_label("--")
        self.sale_price_result = self.create_result_label("--")
        self.units_result = self.create_result_label("--")
        self.final_value_result = self.create_result_label("--")
        self.profit_result = self.create_result_label("--")
        self.roi_result = self.create_result_label("--")

        results_layout.addWidget(
            self.create_result_group("Price at purchase", self.purchase_price_result),
            0, 0
        )
        results_layout.addWidget(
            self.create_result_group("Price at sale", self.sale_price_result),
            0, 1
        )
        results_layout.addWidget(
            self.create_result_group("Units purchased", self.units_result),
            1, 0
        )
        results_layout.addWidget(
            self.create_result_group("Value at sale", self.final_value_result),
            1, 1
        )
        results_layout.addWidget(
            self.create_result_group("Profit / Loss", self.profit_result),
            2, 0
        )
        results_layout.addWidget(
            self.create_result_group("Return on investment", self.roi_result),
            2, 1
        )

        layout.addWidget(results_card)
        layout.addStretch()

    def create_result_label(self, text):
        """
        Make a result label with larger text.

        Using one helper method keeps all the result values
        looking the same.
        """

        label = QLabel(text)
        label.setObjectName("resultValue")
        label.setWordWrap(True)
        return label

    def create_result_group(self, heading, value_label):
        """
        Put a heading and its result together in a small section.
        """

        group = QWidget()
        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(0, 0, 0, 0)
        group_layout.setSpacing(6)

        heading_label = QLabel(heading)
        heading_label.setObjectName("resultHeading")

        group_layout.addWidget(heading_label)
        group_layout.addWidget(value_label)

        return group

    # --------------------------------------------------------
    # COMPARE ASSETS TAB
    # --------------------------------------------------------

    def build_compare_tab(self):
        """Create a table for comparing cryptocurrency prices."""

        layout = QVBoxLayout(self.compare_tab)
        layout.setContentsMargins(8, 18, 8, 8)
        layout.setSpacing(16)

        description = QLabel(
            "Compare the recorded prices of different "
            "cryptocurrencies on a selected date."
        )
        description.setObjectName("sectionDescription")
        description.setWordWrap(True)

        layout.addWidget(description)

        # The user chooses a date to compare asset prices.
        date_layout = QHBoxLayout()

        compare_date_label = QLabel("Comparison date")

        self.compare_date = QDateEdit()
        self.compare_date.setCalendarPopup(True)
        self.compare_date.setDisplayFormat("dd MMM yyyy")
        self.compare_date.setMinimumHeight(40)

        self.compare_button = QPushButton("Compare Prices")
        self.compare_button.setObjectName("primaryButton")
        self.compare_button.setMinimumHeight(40)

        # Clicking this button fills the table with price data.
        self.compare_button.clicked.connect(self.compare_assets)

        date_layout.addWidget(compare_date_label)
        date_layout.addWidget(self.compare_date)
        date_layout.addStretch()
        date_layout.addWidget(self.compare_button)

        layout.addLayout(date_layout)

        # Each row in the table represents one cryptocurrency.
        self.comparison_table = QTableWidget()
        self.comparison_table.setColumnCount(3)
        self.comparison_table.setHorizontalHeaderLabels(
            ["Cryptocurrency", "Recorded Date", "Closing Price"]
        )

        self.comparison_table.setAlternatingRowColors(True)
        self.comparison_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.comparison_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.comparison_table.horizontalHeader().setStretchLastSection(True)
        self.comparison_table.setMinimumHeight(300)

        layout.addWidget(self.comparison_table)

        # This message is used when the selected date has no data.
        self.compare_status = QLabel("")
        self.compare_status.setObjectName("sectionDescription")
        self.compare_status.setWordWrap(True)

        layout.addWidget(self.compare_status)
        layout.addStretch()

    # --------------------------------------------------------
    # APPLY THE GREEN-AND-WHITE THEME
    # --------------------------------------------------------

    def apply_styles(self):
        """
        Apply a consistent style to the whole application.

        Keeping the colours and widget styles here makes it
        easier to update the appearance in the future.
        """

        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.background};
            }}

            QWidget {{
                color: {self.text_colour};
                font-family: Arial;
                font-size: 14px;
            }}

            QLabel#mainTitle {{
                color: {self.dark_green};
                font-size: 30px;
                font-weight: bold;
            }}

            QLabel#subtitle {{
                color: {self.muted_colour};
                font-size: 14px;
            }}

            QLabel#footerLabel {{
                color: {self.muted_colour};
                font-size: 11px;
            }}

            QLabel#resultHeading {{
                color: {self.muted_colour};
                font-size: 13px;
            }}

            QLabel#resultValue {{
                color: {self.dark_green};
                font-size: 21px;
                font-weight: bold;
            }}

            QLabel#sectionDescription {{
                color: {self.muted_colour};
                font-size: 13px;
            }}

            QFrame#card {{
                background-color: {self.white};
                border: 1px solid {self.border_colour};
                border-radius: 12px;
            }}

            QLineEdit, QComboBox, QDoubleSpinBox, QDateEdit {{
                background-color: {self.white};
                border: 1px solid {self.border_colour};
                border-radius: 7px;
                padding: 8px;
                color: {self.text_colour};
            }}

            QComboBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {{
                border: 1px solid {self.green};
            }}

            QPushButton {{
                border-radius: 8px;
                padding: 10px 16px;
                font-weight: bold;
            }}

            QPushButton#primaryButton {{
                background-color: {self.green};
                color: {self.white};
                border: none;
            }}

            QPushButton#primaryButton:hover {{
                background-color: {self.dark_green};
            }}

            QPushButton#secondaryButton {{
                background-color: {self.light_green};
                color: {self.dark_green};
                border: 1px solid {self.border_colour};
            }}

            QPushButton#secondaryButton:hover {{
                background-color: #D9EEE0;
            }}

            QTabWidget::pane {{
                background-color: transparent;
                border: none;
            }}

            QTabBar::tab {{
                background-color: transparent;
                color: {self.muted_colour};
                padding: 12px 20px;
                margin-right: 6px;
                border-bottom: 3px solid transparent;
                font-weight: bold;
            }}

            QTabBar::tab:selected {{
                color: {self.dark_green};
                border-bottom: 3px solid {self.green};
            }}

            QTableWidget {{
                background-color: {self.white};
                alternate-background-color: {self.light_green};
                border: 1px solid {self.border_colour};
                border-radius: 8px;
                gridline-color: {self.border_colour};
                selection-background-color: #D6EEDF;
                selection-color: {self.text_colour};
            }}

            QHeaderView::section {{
                background-color: {self.light_green};
                color: {self.dark_green};
                padding: 10px;
                border: none;
                border-bottom: 1px solid {self.border_colour};
                font-weight: bold;
            }}
        """)

    # --------------------------------------------------------
    # LOAD THE CSV DATASET
    # --------------------------------------------------------

    def choose_csv(self, show_message=True):
        """
        Open a file picker so the user can choose a CSV file.

        This is useful if the dataset is stored somewhere other
        than the application folder.
        """

        # Start browsing from the project folder when possible.
        start_folder = str(Path(__file__).resolve().parent)

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select cryptocurrency CSV file",
            start_folder,
            "CSV Files (*.csv);;All Files (*)"
        )

        # The user may close the file picker without choosing.
        # In that case, there is nothing more to do.
        if not file_path:
            if show_message and self.data.empty:
                QMessageBox.information(
                    self,
                    "No file selected",
                    "Please select a CSV file to use the calculator."
                )
            return

        self.load_csv(file_path)

    def load_csv(self, file_path):
        """
        Read the selected CSV and prepare its columns for use.

        The dataset should contain a date, a closing price,
        and a cryptocurrency name.
        """

        try:
            # Pandas makes it easier to read and organise CSV data.
            loaded_data = pd.read_csv(file_path)

            # Some datasets use capital letters in column names,
            # while others use lowercase. Normalising the names
            # lets the application work with either format.
            loaded_data.columns = [
                str(column).strip().lower()
                for column in loaded_data.columns
            ]

            # These columns are essential for our calculations.
            required_columns = ["date", "close", "name"]

            missing_columns = [
                column
                for column in required_columns
                if column not in loaded_data.columns
            ]

            if missing_columns:
                QMessageBox.warning(
                    self,
                    "CSV format problem",
                    "The selected file is missing these required "
                    "columns:\n\n"
                    + ", ".join(missing_columns)
                    + "\n\nPlease use a file containing date, "
                      "close, and Name columns."
                )
                return

            # Convert dates into a format Python can compare.
            # Invalid dates become empty values instead of causing
            # the entire application to stop.
            loaded_data["date"] = pd.to_datetime(
                loaded_data["date"],
                errors="coerce"
            )

            # Closing prices must be numeric before calculations.
            loaded_data["close"] = pd.to_numeric(
                loaded_data["close"],
                errors="coerce"
            )

            # Remove rows where a date, price, or asset name
            # is missing or unusable.
            loaded_data = loaded_data.dropna(
                subset=["date", "close", "name"]
            )

            # Negative and zero prices cannot be used for a
            # meaningful investment calculation.
            loaded_data = loaded_data[
                loaded_data["close"] > 0
            ]

            # Remove spaces from asset names for cleaner dropdowns.
            loaded_data["name"] = (
                loaded_data["name"].astype(str).str.strip()
            )

            loaded_data = loaded_data[
                loaded_data["name"] != ""
            ]

            # Sort the records so date-based lookups are predictable.
            loaded_data = loaded_data.sort_values("date")

            # If nothing useful remains, there is no point
            # continuing with an empty dataset.
            if loaded_data.empty:
                QMessageBox.warning(
                    self,
                    "No usable data",
                    "The selected CSV does not contain valid "
                    "dates and closing prices."
                )
                return

            # Save the cleaned data for the rest of the application.
            self.data = loaded_data.reset_index(drop=True)
            self.csv_path = Path(file_path)

            # Update the dropdowns and date controls to match
            # the dates and assets found in the selected dataset.
            self.update_controls()

            # Show the filename and a quick summary of the data.
            asset_count = self.data["name"].nunique()
            record_count = len(self.data)

            self.file_status.setText(
                f"Loaded: {self.csv_path.name}  ·  "
                f"{asset_count} assets  ·  {record_count:,} records"
            )

            if show_message := False:
                pass

        except Exception as error:
            # A helpful error message is better than a silent failure.
            QMessageBox.critical(
                self,
                "Could not load CSV",
                f"Something went wrong while reading the file:\n\n{error}"
            )

    # --------------------------------------------------------
    # UPDATE ASSET LISTS AND DATE PICKERS
    # --------------------------------------------------------

    def update_controls(self):
        """Fill the dropdowns and date pickers using the loaded data."""

        if self.data.empty:
            return

        # Get a sorted list of available cryptocurrency names.
        assets = sorted(self.data["name"].unique().tolist())

        # Block signals while refreshing the dropdown so that
        # intermediate changes do not trigger unwanted actions.
        self.asset_combo.blockSignals(True)
        self.asset_combo.clear()
        self.asset_combo.addItems(assets)
        self.asset_combo.blockSignals(False)

        # Find the first and last dates available in the dataset.
        first_date = self.data["date"].min().date()
        last_date = self.data["date"].max().date()

        # Convert Python dates into the format Qt's date picker uses.
        minimum_qdate = QDate(
            first_date.year,
            first_date.month,
            first_date.day
        )

        maximum_qdate = QDate(
            last_date.year,
            last_date.month,
            last_date.day
        )

        # Prevent the user from selecting dates outside the dataset.
        for date_picker in [
            self.buy_date,
            self.sell_date,
            self.compare_date
        ]:
            date_picker.setMinimumDate(minimum_qdate)
            date_picker.setMaximumDate(maximum_qdate)

        # Set sensible starting dates so the user can try the
        # calculator straight away.
        self.buy_date.setDate(minimum_qdate)
        self.sell_date.setDate(maximum_qdate)
        self.compare_date.setDate(maximum_qdate)

    # --------------------------------------------------------
    # FIND A PRICE FOR A SELECTED DATE
    # --------------------------------------------------------

    def get_price_for_date(self, asset_name, selected_date):
        """
        Find the closing price closest to the requested date.

        Cryptocurrency datasets do not always contain a record
        for every calendar day. If the exact date is missing,
        this method uses the most recent available record on or
        before the selected date.

        It never uses a future record for a past-date lookup.
        """

        # Keep only records belonging to the chosen asset.
        asset_data = self.data[
            self.data["name"] == asset_name
        ].sort_values("date")

        if asset_data.empty:
            return None

        # Convert the selected date into a timestamp so it can
        # be compared directly with the dates in the dataset.
        requested_timestamp = pd.Timestamp(selected_date)

        # Only use data dated on or before the requested date.
        available_data = asset_data[
            asset_data["date"] <= requested_timestamp
        ]

        if available_data.empty:
            return None

        # The final row is the closest available record before
        # or on the selected date.
        price_row = available_data.iloc[-1]

        return {
            "price": float(price_row["close"]),
            "date": price_row["date"],
        }

    # --------------------------------------------------------
    # CALCULATE PROFIT OR LOSS
    # --------------------------------------------------------

    def calculate_profit(self):
        """Calculate the estimated result of an investment."""

        # We cannot calculate anything until a dataset is loaded.
        if self.data.empty:
            QMessageBox.warning(
                self,
                "No dataset loaded",
                "Please load a cryptocurrency CSV file first."
            )
            return

        asset_name = self.asset_combo.currentText()

        # Read the investment amount and selected dates.
        investment = self.amount_input.value()
        purchase_date = self.buy_date.date().toPyDate()
        sale_date = self.sell_date.date().toPyDate()

        # Buying after the selected sale date would make the
        # calculation invalid, so ask the user to correct it.
        if purchase_date > sale_date:
            QMessageBox.warning(
                self,
                "Check your dates",
                "The purchase date must be before or the same "
                "as the sale date."
            )
            return

        # Look up the two closing prices in the dataset.
        purchase_record = self.get_price_for_date(
            asset_name,
            purchase_date
        )

        sale_record = self.get_price_for_date(
            asset_name,
            sale_date
        )

        # If there is no suitable historical price for either
        # date, show a message rather than guessing a price.
        if purchase_record is None or sale_record is None:
            QMessageBox.warning(
                self,
                "Price unavailable",
                "A suitable price could not be found for the "
                "selected dates. Please try different dates."
            )
            return

        purchase_price = purchase_record["price"]
        sale_price = sale_record["price"]

        # Calculate how many units the original investment buys.
        units_bought = investment / purchase_price

        # Estimate what those units would be worth at the sale price.
        final_value = units_bought * sale_price

        # A positive result means profit; a negative result means loss.
        profit_loss = final_value - investment

        # ROI shows the profit or loss as a percentage of
        # the original investment.
        roi = (profit_loss / investment) * 100

        # Update each result on the screen.
        self.purchase_price_result.setText(
            f"${purchase_price:,.6f}"
        )

        self.sale_price_result.setText(
            f"${sale_price:,.6f}"
        )

        self.units_result.setText(
            f"{units_bought:,.6f}"
        )

        self.final_value_result.setText(
            f"${final_value:,.2f}"
        )

        self.profit_result.setText(
            f"${profit_loss:,.2f}"
        )

        self.roi_result.setText(
            f"{roi:+.2f}%"
        )

        # Green represents profit, while red makes a loss easier
        # to spot at a glance.
        result_colour = (
            self.green if profit_loss >= 0 else "#C0392B"
        )

        self.profit_result.setStyleSheet(
            f"color: {result_colour}; font-size: 21px; font-weight: bold;"
        )

        self.roi_result.setStyleSheet(
            f"color: {result_colour}; font-size: 21px; font-weight: bold;"
        )

        # The selected date might not exist exactly in the CSV.
        # Show the dates actually used so the result is transparent.
        self.file_status.setText(
            f"Using prices recorded on "
            f"{purchase_record['date'].strftime('%d %b %Y')} "
            f"and {sale_record['date'].strftime('%d %b %Y')}."
        )

    # --------------------------------------------------------
    # COMPARE CRYPTOCURRENCY PRICES
    # --------------------------------------------------------

    def compare_assets(self):
        """
        Fill the comparison table with each asset's latest
        available closing price on or before the chosen date.
        """

        if self.data.empty:
            QMessageBox.warning(
                self,
                "No dataset loaded",
                "Please load a cryptocurrency CSV file first."
            )
            return

        # Clear old results before adding the new comparison.
        self.comparison_table.setRowCount(0)
        self.compare_status.setText("")

        chosen_date = self.compare_date.date().toPyDate()

        # Each asset gets its own row in the comparison table.
        assets = sorted(self.data["name"].unique().tolist())

        for asset_name in assets:
            record = self.get_price_for_date(
                asset_name,
                chosen_date
            )

            # Some assets might not have data on or before
            # the chosen date, so skip them safely.
            if record is None:
                continue

            row_index = self.comparison_table.rowCount()
            self.comparison_table.insertRow(row_index)

            # Add the name, actual recorded date, and price.
            values = [
                asset_name,
                record["date"].strftime("%d %b %Y"),
                f"${record['price']:,.6f}",
            ]

            for column_index, value in enumerate(values):
                item = QTableWidgetItem(value)

                # Left-align the cryptocurrency name and
                # right-align the date and price for readability.
                if column_index == 0:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignVCenter
                        | Qt.AlignmentFlag.AlignLeft
                    )
                else:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignVCenter
                        | Qt.AlignmentFlag.AlignRight
                    )

                self.comparison_table.setItem(
                    row_index,
                    column_index,
                    item
                )

        # Tell the user how many assets were found.
        total_rows = self.comparison_table.rowCount()

        if total_rows == 0:
            self.compare_status.setText(
                "No suitable prices were found for this date."
            )
        else:
            self.compare_status.setText(
                f"Showing {total_rows} cryptocurrencies with "
                f"available prices on or before "
                f"{chosen_date.strftime('%d %b %Y')}."
            )

    # --------------------------------------------------------
    # START THE APPLICATION
    # --------------------------------------------------------


def main():
    """
    Start the desktop application.

    Keeping the startup code in a function makes the program
    easier to organise and understand.
    """

    # QApplication manages the main event loop and desktop UI.
    app = QApplication(sys.argv)

    # Use a clean font throughout the application.
    app.setFont(QFont("Arial", 10))

    # Create and display the main Fixed Price window.
    window = FixedPrice()
    window.show()

    # Keep the application running until the user closes it.
    sys.exit(app.exec())


# This check makes sure the application starts when main.py
# is run directly, without starting it automatically if the
# file is imported by another Python file.
if __name__ == "__main__":
    main()