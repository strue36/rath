from rath.links.aiohttp import AIOHttpLink
from rath.links.validate import ValidatingLink, ValidationError
from rath.operation import Operation, opify
import pytest
from rath.links import compose
from rath.links.testing.mock import AsyncMockLink, AsyncMockResolver
from rath import Rath
from PyQt5 import QtWidgets, QtCore
from koil.qt import QtKoil, QtTask, QtFuture
from tests.apis.countries import acountries


class QtRathWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.koil = QtKoil()

        public_link = AIOHttpLink(url="https://countries.trevorblades.com/")
        validating_link = ValidatingLink()

        self.rath = Rath(link=compose(validating_link, public_link))
        self.rath.connect()

        self.countries_query = QtTask(acountries)

        self.button_greet = QtWidgets.QPushButton("Greet")
        self.greet_label = QtWidgets.QLabel("")

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.button_greet)
        layout.addWidget(self.greet_label)

        self.setLayout(layout)

        self.button_greet.clicked.connect(self.greet)

    def greet(self):
        self.countries_query.run()


class QtFuncWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.koil = QtKoil()

        self.button_greet = QtWidgets.QPushButton("Greet")
        self.greet_label = QtWidgets.QLabel("")

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.button_greet)
        layout.addWidget(self.greet_label)

        self.setLayout(layout)

        self.button_greet.clicked.connect(self.greet)

    def greet(self):
        self.greet_label.setText("Hello!")


def test_no_interference(qtbot):
    """Tests if just adding koil interferes with normal
    qtpy widgets.

    Args:
        qtbot (_type_): _description_
    """
    widget = QtFuncWidget()
    qtbot.addWidget(widget)

    # click in the Greet button and make sure it updates the appropriate label
    qtbot.mouseClick(widget.button_greet, QtCore.Qt.LeftButton)

    assert widget.greet_label.text() == "Hello!"


def test_call_query(qtbot):
    """Tests if we can call a task from a koil widget."""
    widget = QtRathWidget()
    qtbot.addWidget(widget)

    # click in the Greet button and make sure it updates the appropriate label
    with qtbot.waitSignal(widget.countries_query.returned, timeout=1000) as p:
        qtbot.mouseClick(widget.button_greet, QtCore.Qt.LeftButton)

    countries = p.args[0]
    assert isinstance(countries, list), "Not a list"
