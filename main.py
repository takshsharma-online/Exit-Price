import sys
from pathlib import Path

import pandas as pd

from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QDoubleSpinBox,
    QDateEdit,
    QTabWidget,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QFileDialog,
    QMessageBox,
    QHeaderView,
    QAbstractItemView,
)


APP_DIR = Path(__file__).resolve().parent


class ExitPrice(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("ExitPrice")
        self.setMinimumSize(900, 650)
        self.resize(1100, 760)

        self.data = pd.DataFrame()
        self.price_history = {}
        self.csv_path = None

        self.build_ui()
        self.apply_style()
        self.find_csv()

    # ==================================================
    # MAIN INTERFACE
    # ==================================================

    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(20)

        # Header
        header = QHBoxLayout()

        heading_layout = QVBoxLayout()
        heading_layout.setSpacing(5)

        title = QLabel("Exit Price")
        title.setObjectName("appTitle")

        subtitle = QLabel("Your cryptocurrency profit calculator")
        subtitle.setObjectName("subtitle")

        heading_layout.addWidget(title)
        heading_layout.addWidget(subtitle)

        header.addLayout(heading_layout)
        header.addStretch()

        self.csv_button = QPushButton("Choose CSV")
        self.csv_button.setObjectName("outlineButton")
        self.csv_button.clicked.connect(self.choose_csv)

        header.addWidget(self.csv_button)
        root.addLayout(header)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        self.build_calculator_tab()
        self.build_comparison_tab()

        root.addWidget(self.tabs)

        # Small file indicator, not a status bar.
        self.file_label = QLabel("No CSV loaded")
        self.file_label.setObjectName("fileLabel")
        root.addWidget(self.file_label)

    # ==================================================
    # CALCULATOR TAB
    # ==================================================

    def build_calculator_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 22, 10, 10)
        layout.setSpacing(18)

        heading = QLabel("Calculate your trade")
        heading.setObjectName("sectionTitle")
        layout.addWidget(heading)

        description = QLabel(
            "Choose an asset, enter your quantity, and select your dates."
        )
        description.setObjectName("description")
        layout.addWidget(description)

        # Input card
        input_card = self.make_card()
        grid = QGridLayout(input_card)
        grid.setContentsMargins(22, 22, 22, 22)
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(12)

        grid.addWidget(self.make_label("Cryptocurrency"), 0, 0)
        grid.addWidget(self.make_label("Quantity"), 0, 1)
        grid.addWidget(self.make_label("Buy date"), 2, 0)
        grid.addWidget(self.make_label("Sell date"), 2, 1)

        self.asset_combo = QComboBox()
        self.asset_combo.setMinimumHeight(42)
        self.asset_combo.setMaxVisibleItems(15)
        self.asset_combo.setEnabled(False)
        self.asset_combo.currentIndexChanged.connect(
            self.calculate_trade
        )

        self.quantity = QDoubleSpinBox()
        self.quantity.setRange(0.000001, 1_000_000_000)
        self.quantity.setDecimals(6)
        self.quantity.setValue(1.0)
        self.quantity.setMinimumHeight(42)
        self.quantity.valueChanged.connect(self.calculate_trade)

        self.buy_date = QDateEdit()
        self.buy_date.setCalendarPopup(True)
        self.buy_date.setDisplayFormat("dd MMM yyyy")
        self.buy_date.setMinimumHeight(42)
        self.buy_date.dateChanged.connect(self.buy_date_changed)

        self.sell_date = QDateEdit()
        self.sell_date.setCalendarPopup(True)
        self.sell_date.setDisplayFormat("dd MMM yyyy")
        self.sell_date.setMinimumHeight(42)
        self.sell_date.dateChanged.connect(self.sell_date_changed)

        grid.addWidget(self.asset_combo, 1, 0)
        grid.addWidget(self.quantity, 1, 1)
        grid.addWidget(self.buy_date, 3, 0)
        grid.addWidget(self.sell_date, 3, 1)

        layout.addWidget(input_card)

        self.calculate_button = QPushButton("Calculate Profit / Loss")
        self.calculate_button.setMinimumHeight(44)
        self.calculate_button.clicked.connect(self.calculate_trade)
        layout.addWidget(self.calculate_button)

        # Results
        results_heading = QLabel("Your results")
        results_heading.setObjectName("sectionTitle")
        layout.addWidget(results_heading)

        results_grid = QGridLayout()
        results_grid.setSpacing(14)

        self.purchase_card, self.purchase_result = self.result_card(
            "Purchase cost"
        )
        self.sale_card, self.sale_result = self.result_card(
            "Sale value"
        )
        self.profit_card, self.profit_result = self.result_card(
            "Profit / loss"
        )
        self.roi_card, self.roi_result = self.result_card(
            "Return on investment"
        )

        results_grid.addWidget(self.purchase_card, 0, 0)
        results_grid.addWidget(self.sale_card, 0, 1)
        results_grid.addWidget(self.profit_card, 1, 0)
        results_grid.addWidget(self.roi_card, 1, 1)

        layout.addLayout(results_grid)

        # Price details
        details_card = self.make_card()
        details_layout = QVBoxLayout(details_card)
        details_layout.setContentsMargins(20, 16, 20, 16)
        details_layout.setSpacing(10)

        self.buy_price_label = QLabel("Buy price: —")
        self.sell_price_label = QLabel("Sell price: —")
        self.actual_dates_label = QLabel("Actual price dates: —")

        for label in (
            self.buy_price_label,
            self.sell_price_label,
            self.actual_dates_label,
        ):
            label.setObjectName("detailLabel")
            label.setWordWrap(True)
            details_layout.addWidget(label)

        layout.addWidget(details_card)
        layout.addStretch()

        self.tabs.addTab(tab, "Trade Calculator")

    # ==================================================
    # COMPARISON TAB
    # ==================================================

    def build_comparison_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 22, 10, 10)
        layout.setSpacing(18)

        heading = QLabel("Compare cryptocurrencies")
        heading.setObjectName("sectionTitle")
        layout.addWidget(heading)

        description = QLabel(
            "Compare estimated returns across all available assets."
        )
        description.setObjectName("description")
        layout.addWidget(description)

        controls = self.make_card()
        grid = QGridLayout(controls)
        grid.setContentsMargins(20, 20, 20, 20)
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(12)

        grid.addWidget(self.make_label("Quantity"), 0, 0)
        grid.addWidget(self.make_label("Buy date"), 0, 1)
        grid.addWidget(self.make_label("Sell date"), 0, 2)

        self.compare_quantity = QDoubleSpinBox()
        self.compare_quantity.setRange(0.000001, 1_000_000_000)
        self.compare_quantity.setDecimals(6)
        self.compare_quantity.setValue(1.0)
        self.compare_quantity.setMinimumHeight(40)

        self.compare_buy_date = QDateEdit()
        self.compare_buy_date.setCalendarPopup(True)
        self.compare_buy_date.setDisplayFormat("dd MMM yyyy")
        self.compare_buy_date.setMinimumHeight(40)

        self.compare_sell_date = QDateEdit()
        self.compare_sell_date.setCalendarPopup(True)
        self.compare_sell_date.setDisplayFormat("dd MMM yyyy")
        self.compare_sell_date.setMinimumHeight(40)

        grid.addWidget(self.compare_quantity, 1, 0)
        grid.addWidget(self.compare_buy_date, 1, 1)
        grid.addWidget(self.compare_sell_date, 1, 2)

        self.compare_button = QPushButton("Compare assets")
        self.compare_button.setMinimumHeight(42)
        self.compare_button.clicked.connect(self.compare_assets)

        grid.addWidget(self.compare_button, 2, 0, 1, 3)

        layout.addWidget(controls)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Asset",
            "Buy price",
            "Sell price",
            "Purchase cost",
            "Profit / loss",
            "ROI",
        ])

        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        layout.addWidget(self.table)

        self.tabs.addTab(tab, "Compare Assets")

    # ==================================================
    # UI HELPERS
    # ==================================================

    @staticmethod
    def make_card():
        card = QFrame()
        card.setObjectName("card")
        return card

    @staticmethod
    def make_label(text):
        label = QLabel(text)
        label.setObjectName("fieldLabel")
        return label

    def result_card(self, title):
        card = self.make_card()

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 17, 20, 17)
        layout.setSpacing(9)

        heading = QLabel(title)
        heading.setObjectName("resultHeading")

        value = QLabel("—")
        value.setObjectName("resultValue")
        value.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        layout.addWidget(heading)
        layout.addWidget(value)

        return card, value

    # ==================================================
    # FIND AND LOAD CSV
    # ==================================================

    def find_csv(self):
        """
        Try the expected filename, then look for CSV files
        in the project directory. If none are found, let
        the user select the file manually.
        """

        preferred = [
            APP_DIR / "combined(1).csv",
            APP_DIR / "combined.csv",
        ]

        for path in preferred:
            if path.is_file():
                self.load_csv(path)
                return

        candidates = sorted(
            path for path in APP_DIR.glob("*.csv")
            if path.is_file()
        )

        if len(candidates) == 1:
            self.load_csv(candidates[0])
            return

        if candidates:
            combined_candidates = [
                path for path in candidates
                if "combined" in path.name.lower()
            ]

            if len(combined_candidates) == 1:
                self.load_csv(combined_candidates[0])
                return

        # Do not crash or show an unnecessary error.
        # Ask the user to locate the CSV.
        self.choose_csv()

    def choose_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select your cryptocurrency CSV",
            str(Path.home()),
            "CSV Files (*.csv);;All Files (*)",
        )

        if file_path:
            self.load_csv(Path(file_path))

    def load_csv(self, path):
        try:
            df = pd.read_csv(path)

            # Match column names without case sensitivity.
            columns = {
                str(column).strip().lower(): column
                for column in df.columns
            }

            required = ["date", "close", "name"]
            missing = [
                column for column in required
                if column not in columns
            ]

            if missing:
                QMessageBox.warning(
                    self,
                    "CSV format not recognised",
                    "The file needs these columns:\n"
                    "date, close, name\n\n"
                    f"Missing: {', '.join(missing)}\n\n"
                    f"Found: {', '.join(map(str, df.columns))}",
                )
                return

            df = df.rename(columns={
                columns["date"]: "date",
                columns["close"]: "close",
                columns["name"]: "asset",
            })

            df["date"] = pd.to_datetime(
                df["date"], errors="coerce", utc=True
            ).dt.tz_convert(None)

            df["close"] = pd.to_numeric(
                df["close"], errors="coerce"
            )

            df["asset"] = df["asset"].astype(str).str.strip()

            df = df.dropna(subset=["date", "close", "asset"])
            df = df[df["close"] > 0]
            df = df[df["asset"] != ""]

            if df.empty:
                QMessageBox.warning(
                    self,
                    "No usable data",
                    "This CSV does not contain valid price records.",
                )
                return

            history = {}

            for asset, group in df.groupby("asset"):
                series = (
                    group.groupby("date")["close"]
                    .last()
                    .sort_index()
                )

                if not series.empty:
                    history[str(asset)] = series

            if not history:
                QMessageBox.warning(
                    self,
                    "No assets found",
                    "No cryptocurrency price records were found.",
                )
                return

            # Save the loaded data.
            self.data = df
            self.price_history = history
            self.csv_path = path

            first = df["date"].min().date()
            last = df["date"].max().date()

            first_qdate = QDate(
                first.year, first.month, first.day
            )
            last_qdate = QDate(
                last.year, last.month, last.day
            )

            default_buy = last_qdate.addDays(-30)

            if default_buy < first_qdate:
                default_buy = first_qdate

            # Configure date limits before setting dates.
            for widget in (
                self.buy_date,
                self.sell_date,
                self.compare_buy_date,
                self.compare_sell_date,
            ):
                widget.blockSignals(True)
                widget.setMinimumDate(first_qdate)
                widget.setMaximumDate(last_qdate)

            self.buy_date.setDate(default_buy)
            self.sell_date.setDate(last_qdate)
            self.compare_buy_date.setDate(default_buy)
            self.compare_sell_date.setDate(last_qdate)

            for widget in (
                self.buy_date,
                self.sell_date,
                self.compare_buy_date,
                self.compare_sell_date,
            ):
                widget.blockSignals(False)

            # Populate the dropdown after the data is ready.
            self.asset_combo.blockSignals(True)
            self.asset_combo.clear()
            self.asset_combo.addItems(sorted(history.keys()))
            self.asset_combo.setEnabled(True)
            self.asset_combo.blockSignals(False)

            self.file_label.setText(
                f"Loaded: {path.name}  ·  "
                f"{len(history)} assets  ·  "
                f"{len(df):,} records"
            )

            self.calculate_trade()
            self.compare_assets()

        except (OSError, pd.errors.ParserError, ValueError) as error:
            QMessageBox.critical(
                self,
                "Could not load CSV",
                f"Unable to read this file:\n{path}\n\n{error}",
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Unexpected error",
                f"Something went wrong while loading the CSV:\n\n{error}",
            )

    # ==================================================
    # DATE HANDLING
    # ==================================================

    def buy_date_changed(self, date):
        if date > self.sell_date.date():
            self.sell_date.setDate(date)

        self.calculate_trade()

    def sell_date_changed(self, date):
        if date < self.buy_date.date():
            self.buy_date.setDate(date)

        self.calculate_trade()

    # ==================================================
    # PRICE LOOKUP
    # ==================================================

    def find_price(self, asset, selected_date):
        """
        Find the latest closing price on or before the
        selected date.
        """

        if asset not in self.price_history:
            return None, None

        series = self.price_history[asset]
        target = pd.Timestamp(selected_date.toPyDate())

        available = series.loc[series.index <= target]

        if available.empty:
            return None, None

        actual_date = available.index[-1]
        price = float(available.iloc[-1])

        return price, actual_date

    @staticmethod
    def money(value):
        return f"${value:,.2f}"

    @staticmethod
    def colour_result(label, value):
        if value > 0:
            label.setStyleSheet("color: #16845b;")
        elif value < 0:
            label.setStyleSheet("color: #d64545;")
        else:
            label.setStyleSheet("color: #263b32;")

    # ==================================================
    # CALCULATE PROFIT / LOSS
    # ==================================================

    def calculate_trade(self, *_):
        if not self.price_history:
            return

        asset = self.asset_combo.currentText()

        if not asset:
            return

        quantity = self.quantity.value()

        buy_price, buy_actual_date = self.find_price(
            asset, self.buy_date.date()
        )

        sell_price, sell_actual_date = self.find_price(
            asset, self.sell_date.date()
        )

        if buy_price is None or sell_price is None:
            self.purchase_result.setText("Unavailable")
            self.sale_result.setText("Unavailable")
            self.profit_result.setText("Unavailable")
            self.roi_result.setText("Unavailable")

            self.buy_price_label.setText("Buy price: unavailable")
            self.sell_price_label.setText("Sell price: unavailable")
            self.actual_dates_label.setText(
                "No price records found for the selected dates."
            )
            return

        purchase_cost = buy_price * quantity
        sale_value = sell_price * quantity
        profit_loss = sale_value - purchase_cost

        roi = (
            profit_loss / purchase_cost * 100
            if purchase_cost else 0.0
        )

        self.purchase_result.setText(
            self.money(purchase_cost)
        )
        self.sale_result.setText(
            self.money(sale_value)
        )
        self.profit_result.setText(
            self.money(profit_loss)
        )
        self.roi_result.setText(
            f"{roi:+.2f}%"
        )

        self.colour_result(self.profit_result, profit_loss)
        self.colour_result(self.roi_result, roi)

        self.buy_price_label.setText(
            f"Buy price: {self.money(buy_price)} per unit"
        )
        self.sell_price_label.setText(
            f"Sell price: {self.money(sell_price)} per unit"
        )

        self.actual_dates_label.setText(
            f"Price dates used: {buy_actual_date:%d %b %Y}"
            f" – {sell_actual_date:%d %b %Y}"
        )

    # ==================================================
    # COMPARE ASSETS
    # ==================================================

    def compare_assets(self, *_):
        if not self.price_history:
            return

        buy_date = self.compare_buy_date.date()
        sell_date = self.compare_sell_date.date()

        if buy_date > sell_date:
            QMessageBox.warning(
                self,
                "Invalid dates",
                "The buy date must be on or before the sell date.",
            )
            return

        quantity = self.compare_quantity.value()
        results = []

        for asset in sorted(self.price_history):
            buy_price, _ = self.find_price(asset, buy_date)
            sell_price, _ = self.find_price(asset, sell_date)

            if buy_price is None or sell_price is None:
                continue

            cost = buy_price * quantity
            value = sell_price * quantity
            profit = value - cost
            roi = profit / cost * 100 if cost else 0.0

            results.append({
                "asset": asset,
                "buy": buy_price,
                "sell": sell_price,
                "cost": cost,
                "profit": profit,
                "roi": roi,
            })

        # Best profit first.
        results.sort(
            key=lambda item: item["profit"],
            reverse=True,
        )

        self.table.setRowCount(len(results))

        for row, result in enumerate(results):
            values = [
                result["asset"],
                self.money(result["buy"]),
                self.money(result["sell"]),
                self.money(result["cost"]),
                self.money(result["profit"]),
                f'{result["roi"]:+.2f}%',
            ]

            for column, text in enumerate(values):
                item = QTableWidgetItem(text)

                if column > 0:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignRight
                        | Qt.AlignmentFlag.AlignVCenter
                    )

                if column in (4, 5):
                    number = (
                        result["profit"]
                        if column == 4
                        else result["roi"]
                    )

                    if number > 0:
                        item.setForeground(QColor("#16845b"))
                    elif number < 0:
                        item.setForeground(QColor("#d64545"))

                self.table.setItem(row, column, item)

    # ==================================================
    # SIMPLE GREEN THEME
    # ==================================================

    def apply_style(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f8f5;
            }

            QWidget {
                font-family: "Arial";
                font-size: 13px;
                color: #263b32;
            }

            QLabel#appTitle {
                color: #176b4d;
                font-size: 30px;
                font-weight: bold;
            }

            QLabel#subtitle {
                color: #74847b;
                font-size: 13px;
            }

            QLabel#sectionTitle {
                color: #244b39;
                font-size: 20px;
                font-weight: bold;
            }

            QLabel#description {
                color: #74847b;
                font-size: 13px;
            }

            QLabel#fieldLabel {
                color: #42594c;
                font-weight: bold;
            }

            QLabel#resultHeading {
                color: #74847b;
                font-size: 13px;
            }

            QLabel#resultValue {
                color: #263b32;
                font-size: 23px;
                font-weight: bold;
            }

            QLabel#detailLabel {
                color: #52685b;
                font-size: 13px;
            }

            QLabel#fileLabel {
                color: #74847b;
                font-size: 11px;
            }

            QFrame#card {
                background-color: #ffffff;
                border: 1px solid #e1eae2;
                border-radius: 12px;
            }

            QComboBox,
            QDoubleSpinBox,
            QDateEdit {
                background-color: #ffffff;
                border: 1px solid #d7e3d9;
                border-radius: 7px;
                padding: 8px;
                selection-background-color: #d8eee0;
                min-height: 22px;
            }

            QComboBox:hover,
            QDoubleSpinBox:hover,
            QDateEdit:hover {
                border: 1px solid #75aa8c;
            }

            QComboBox:focus,
            QDoubleSpinBox:focus,
            QDateEdit:focus {
                border: 1px solid #26835d;
            }

            QComboBox QAbstractItemView {
                background-color: white;
                color: #263b32;
                selection-background-color: #d8eee0;
                selection-color: #176b4d;
                border: 1px solid #d7e3d9;
                outline: none;
                padding: 4px;
            }

            QPushButton {
                background-color: #21835b;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 11px 18px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #176b4a;
            }

            QPushButton:pressed {
                background-color: #12573c;
            }

            QPushButton:disabled {
                background-color: #cbd8ce;
                color: #718076;
            }

            QPushButton#outlineButton {
                background-color: white;
                color: #21835b;
                border: 1px solid #b9d7c2;
            }

            QPushButton#outlineButton:hover {
                background-color: #edf6ef;
            }

            QTabWidget::pane {
                background-color: transparent;
                border: none;
                top: -1px;
            }

            QTabBar::tab {
                background-color: #eaf0eb;
                color: #63746a;
                padding: 12px 22px;
                margin-right: 5px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }

            QTabBar::tab:selected {
                background-color: #21835b;
                color: white;
            }

            QTabBar::tab:hover:!selected {
                background-color: #dce9df;
            }

            QTableWidget {
                background-color: white;
                alternate-background-color: #f6faf6;
                border: 1px solid #e1eae2;
                border-radius: 10px;
                gridline-color: #edf2ed;
                selection-background-color: #dcefe2;
                selection-color: #244b39;
            }

            QHeaderView::section {
                background-color: #edf4ee;
                color: #42594c;
                padding: 12px 8px;
                border: none;
                border-bottom: 1px solid #dfe9e0;
                font-weight: bold;
            }

            QTableCornerButton::section {
                background-color: #edf4ee;
                border: none;
            }

            QScrollBar:vertical {
                background: #f5f8f5;
                width: 10px;
                margin: 0;
            }

            QScrollBar::handle:vertical {
                background: #c5d9ca;
                border-radius: 5px;
                min-height: 25px;
            }

            QScrollBar::handle:vertical:hover {
                background: #91b69d;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)


# ======================================================
# START APPLICATION
# ======================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = ExitPrice()
    window.show()

    sys.exit(app.exec())