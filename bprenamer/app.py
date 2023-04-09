# -*- coding: utf-8 -*-
# bprenamer/app.py

"""This module contains the BP Renamer application."""

import sys

from PyQt6.QtWidgets import QApplication

from .views import Window

def main():
	# Create the app
	app = QApplication(sys.argv)
	# Create and show the main window
	win = Window()
	win.show()
	#run the event loop
	sys.exit(app.exec())

	