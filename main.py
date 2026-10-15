import sys
import os

import pandas as pd

from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QComboBox,
    QDoubleSpinBox,
    QDateEdit,
    QGroupBox,
    QTabWidget,
    QFrame,
    QMessageBox
)


class CryptoTradeProfitCalculator(QMainWindow):

    def __init__(self):
        super().__init__()

        # Main window settings
        self.setWindowTitle("Exit Price")
        self.setGeometry(100, 100, 1100, 750)

        # Store historical market data
        self.data = pd.DataFrame()

        # Build the graphical interface
        self.create_ui()

    def create_ui(self):

        # Main application widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main vertical layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Application title
        title = QLabel("Exit Price")

        title.setStyleSheet("""
            font-size: 30px;
            font-weight: bold;
            color: #1E3A8A;
            padding: 10px;
        """)

        # Application subtitle
        subtitle = QLabel(
            "Stock and Cryptocurrency Trade Profit Calculator"
        )

        subtitle.setStyleSheet("""
            font-size: 14px;
            color: #64748B;
            padding-bottom: 15px;
        """)

        # Add title and subtitle
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        # Create tabs
        self.tabs = QTabWidget()

        # Main calculator tab
        self.calculator_tab = QWidget()
        self.tabs.addTab(
            self.calculator_tab,
            "Trade Calculator"
        )

        # Comparison tab
        self.comparison_tab = QWidget()
        self.tabs.addTab(
            self.comparison_tab,
            "Compare Assets"
        )

        main_layout.addWidget(self.tabs)

        # Build the calculator interface
        self.create_calculator_tab()

        # Apply application styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F1F5F9;
            }

            QGroupBox {
                background-color: white;
                border: 1px solid #CBD5E1;
                border-radius: 10px;
                margin-top: 10px;
                padding: 15px;
                font-weight: bold;
            }

            QPushButton {
                background-color: #2563EB;
                color: white;
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #1D4ED8;
            }

            QComboBox, QDateEdit, QDoubleSpinBox {
                padding: 8px;
                border: 1px solid #CBD5E1;
                border-radius: 5px;
                background-color: white;
            }

            QTabWidget::pane {
                border: 1px solid #CBD5E1;
                background-color: #F8FAFC;
            }
        """)

    def create_calculator_tab(self):

        layout = QVBoxLayout()
        self.calculator_tab.setLayout(layout)

        # Create the trade input group
        trade_group = QGroupBox("Trade Details")
        grid = QGridLayout()
        trade_group.setLayout(grid)

        # Cryptocurrency selection
        grid.addWidget(
            QLabel("Select Cryptocurrency:"),
            0, 0
        )

        self.crypto_combo = QComboBox()

        self.crypto_combo.addItems([
            "BTC",
            "DOGE",
            "ETH",
            "ADA",
            "SOL"
        ])

        grid.addWidget(
            self.crypto_combo,
            0, 1
        )

        # Quantity input
        grid.addWidget(
            QLabel("Quantity Purchased:"),
            1, 0
        )

        self.quantity_input = QDoubleSpinBox()

        self.quantity_input.setRange(
            0.00000001,
            1000000000
        )

        self.quantity_input.setDecimals(8)
        self.quantity_input.setValue(1.0)

        grid.addWidget(
            self.quantity_input,
            1, 1
        )

        # Purchase date
        grid.addWidget(
            QLabel("Purchase Date:"),
            2, 0
        )

        self.buy_date = QDateEdit()

        self.buy_date.setCalendarPopup(True)
        self.buy_date.setDate(QDate.currentDate())

        grid.addWidget(
            self.buy_date,
            2, 1
        )

        # Selling date
        grid.addWidget(
            QLabel("Selling Date:"),
            3, 0
        )

        self.sell_date = QDateEdit()

        self.sell_date.setCalendarPopup(True)
        self.sell_date.setDate(QDate.currentDate())

        grid.addWidget(
            self.sell_date,
            3, 1
        )

        layout.addWidget(trade_group)

        # Calculate button
        self.calculate_button = QPushButton(
            "Calculate Profit / Loss"
        )

        layout.addWidget(self.calculate_button)

        # Result display
        self.result_label = QLabel(
            "Enter your trade details and calculate your result."
        )

        self.result_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.result_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #1E3A8A;
            padding: 25px;
            background-color: white;
            border-radius: 10px;
        """)

        layout.addWidget(self.result_label)

        layout.addStretch()


if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = CryptoTradeProfitCalculator()

    window.show()

    sys.exit(app.exec())