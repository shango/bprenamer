# -*- coding: utf-8 -*-
# bprenamer/views.py

"""This module is the BP Renamer main window."""

from collections import deque
from pathlib import Path
from PyQt6.QtWidgets import QFileDialog, QWidget
from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QFileDialog, QWidget

from .rename import Renamer
from .ui.window import Ui_Window

FILTERS = ";;".join(
	(
		"EXR Files (*.exr)",
		"PNG Files (*.png)",
		"JPG Files (*.jpg)",
		"GIF Files (*.gif)",
		"Text Files (*.txt)",
	)
)

class Window(QWidget, Ui_Window):
	def __init__(self):
		super().__init__()
		self._files = deque()
		self._filesCount = len(self._files)
		self._setupUI()
		self._connectSignalsSlots()


	def _setupUI(self):
		self.setupUi(self)
		self._updateStateWhenNoFiles()


	def _updateStateWhenNoFiles(self):
		self._filesCount = len(self._files)
		self.loadFilesButton.setEnabled(True)
		self.loadFilesButton.setFocus()
		self.renameFilesButton.setEnabled(False)
		self.prefixEdit.clear()
		self.prefixEdit.setEnabled(False)


	def _connectSignalsSlots(self):
		self.loadFilesButton.clicked.connect(self.loadFiles)
		self.renameFilesButton.clicked.connect(self.renameFiles)
		self.prefixEdit.textChanged.connect(self._updateStateWhenReady)


	def _updateStateWhenReady(self):
		if self.prefixEdit.text():
			self.renameFilesButton.setEnabled(True)
		else:
			self.renameFilesButton.setEnabled(False)


	def loadFiles(self):
		self.dstFileList.clear()
		if self.dirEdit.text():
			initDir = self.dirEdit.text()
		else:
			initDir = str(Path.home())
		files, filter = QFileDialog.getOpenFileNames(
			self, "Choose Files to Rename", initDir, filter=FILTERS
		)
		if len(files) > 0:
			fileExtension = filter[filter.index("*"): -1]
			self.extensionLabel.setText(fileExtension)
			srcDirName = str(Path(files[0]).parent)
			self.dirEdit.setText(srcDirName)
			self._updateStateWhenFilesLoaded()
		for file in files:
			self._files.append(Path(file))
			self.srcFileList.addItem(file)
		self._filesCount = len(self._files)

	
	def _updateStateWhenFilesLoaded(self):
		self.prefixedit.setEnabled(True)
		self.prefixEdit.setFocus(True)


	def renameFiles(self):
		self._runRenamerThread()
		self._updateStateWhileRenaming()


	def _updateStateWhileRenaming(self):
		self.loadFilesButton.setEnabled(False)
		self.renameFilesButton.setEnabled(False)


	def _runRenamerThread(self):
		prefix = self.prefixEdit.text()
		self._thread = QThread()
		self._renamer = Renamer(
			files=tuple(self._files),
			prefix=prefix,
		)
		self._renamer.moveToThread(self._thread)
		self._thread.started.connect(self._renamer.renameFiles)
		self._renamer.renamedFile.connect(self._updateStateWhenFileRenamed)
		self._renamer.progressed.connect(self._updateProgressBar)
		self._renamer.finished.connect(self._updateStateWhenNoFiles)
		self._renamer.finished.connect(self._thread.quit)
		self._thread.finished.connect(self._thread.deleteLater)
		self._thread.start()


	def _updateStateWhenFileRenamed(self, newFile):
		self._files.popleft()
		self.srcFileList.takeItem(0)
		self.dstFileList.addItem(str(newFile))


	def _updateProgressBar(self, fileNumber):
		progressPercent = int(fileNumber / self._filesCount * 100)
		self.progressBar.setValue(progressPercent)

