# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI_EXAFSfit_wTable.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1273, 783)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setGeometry(QtCore.QRect(30, 90, 271, 451))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 269, 449))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(25, 10, 100, 42))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(1080, 670, 141, 41))
        self.pushButton_3.setObjectName("pushButton_3")
        self.checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox.setGeometry(QtCore.QRect(1050, 40, 171, 20))
        self.checkBox.setObjectName("checkBox")
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(560, 76, 71, 31))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(480, 82, 71, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.checkBox_3 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_3.setGeometry(QtCore.QRect(30, 60, 101, 20))
        self.checkBox_3.setObjectName("checkBox_3")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(530, 115, 501, 31))
        self.lineEdit.setObjectName("lineEdit")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(330, 120, 181, 25))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(495, 25, 551, 41))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.label_5 = QtWidgets.QLabel(self.frame)
        self.label_5.setGeometry(QtCore.QRect(260, 15, 16, 19))
        self.label_5.setObjectName("label_5")
        self.label_3 = QtWidgets.QLabel(self.frame)
        self.label_3.setGeometry(QtCore.QRect(10, 15, 51, 16))
        self.label_3.setObjectName("label_3")
        self.dSB_khigh = QtWidgets.QDoubleSpinBox(self.frame)
        self.dSB_khigh.setGeometry(QtCore.QRect(180, 10, 71, 25))
        self.dSB_khigh.setSingleStep(0.1)
        self.dSB_khigh.setProperty("value", 12.0)
        self.dSB_khigh.setObjectName("dSB_khigh")
        self.label_6 = QtWidgets.QLabel(self.frame)
        self.label_6.setGeometry(QtCore.QRect(154, 13, 20, 21))
        self.label_6.setObjectName("label_6")
        self.dSB_klow = QtWidgets.QDoubleSpinBox(self.frame)
        self.dSB_klow.setGeometry(QtCore.QRect(70, 10, 62, 25))
        self.dSB_klow.setSingleStep(0.1)
        self.dSB_klow.setProperty("value", 3.0)
        self.dSB_klow.setObjectName("dSB_klow")
        self.label_4 = QtWidgets.QLabel(self.frame)
        self.label_4.setGeometry(QtCore.QRect(140, 15, 16, 19))
        self.label_4.setObjectName("label_4")
        self.label_8 = QtWidgets.QLabel(self.frame)
        self.label_8.setGeometry(QtCore.QRect(530, 14, 16, 19))
        self.label_8.setObjectName("label_8")
        self.dSB_rlow = QtWidgets.QDoubleSpinBox(self.frame)
        self.dSB_rlow.setGeometry(QtCore.QRect(350, 10, 62, 25))
        self.dSB_rlow.setSingleStep(0.1)
        self.dSB_rlow.setProperty("value", 1.0)
        self.dSB_rlow.setObjectName("dSB_rlow")
        self.label_7 = QtWidgets.QLabel(self.frame)
        self.label_7.setGeometry(QtCore.QRect(290, 14, 51, 16))
        self.label_7.setObjectName("label_7")
        self.dSB_rhigh = QtWidgets.QDoubleSpinBox(self.frame)
        self.dSB_rhigh.setGeometry(QtCore.QRect(460, 9, 62, 25))
        self.dSB_rhigh.setSingleStep(0.1)
        self.dSB_rhigh.setProperty("value", 4.0)
        self.dSB_rhigh.setObjectName("dSB_rhigh")
        self.label_10 = QtWidgets.QLabel(self.frame)
        self.label_10.setGeometry(QtCore.QRect(420, 14, 16, 19))
        self.label_10.setObjectName("label_10")
        self.label_9 = QtWidgets.QLabel(self.frame)
        self.label_9.setGeometry(QtCore.QRect(440, 11, 20, 21))
        self.label_9.setObjectName("label_9")
        self.line = QtWidgets.QFrame(self.frame)
        self.line.setGeometry(QtCore.QRect(270, 0, 20, 41))
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setLineWidth(2)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setObjectName("line")
        self.checkBox_5 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_5.setGeometry(QtCore.QRect(40, 650, 261, 20))
        self.checkBox_5.setCheckable(True)
        self.checkBox_5.setObjectName("checkBox_5")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(40, 550, 261, 31))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progressBar.sizePolicy().hasHeightForWidth())
        self.progressBar.setSizePolicy(sizePolicy)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.dB_window_k = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.dB_window_k.setGeometry(QtCore.QRect(860, 80, 62, 25))
        self.dB_window_k.setMaximum(2.0)
        self.dB_window_k.setProperty("value", 1.0)
        self.dB_window_k.setObjectName("dB_window_k")
        self.label_11 = QtWidgets.QLabel(self.centralwidget)
        self.label_11.setGeometry(QtCore.QRect(830, 83, 21, 21))
        self.label_11.setObjectName("label_11")
        self.label_12 = QtWidgets.QLabel(self.centralwidget)
        self.label_12.setGeometry(QtCore.QRect(930, 82, 21, 21))
        self.label_12.setObjectName("label_12")
        self.dB_window_r = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.dB_window_r.setGeometry(QtCore.QRect(960, 80, 62, 25))
        self.dB_window_r.setMaximum(2.0)
        self.dB_window_r.setProperty("value", 1.0)
        self.dB_window_r.setObjectName("dB_window_r")
        self.comboBox_2 = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_2.setGeometry(QtCore.QRect(710, 76, 104, 31))
        self.comboBox_2.setObjectName("comboBox_2")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.label_13 = QtWidgets.QLabel(self.centralwidget)
        self.label_13.setGeometry(QtCore.QRect(640, 82, 61, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_13.setFont(font)
        self.label_13.setObjectName("label_13")
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(485, 675, 581, 31))
        self.textBrowser.setObjectName("textBrowser")
        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_4.setGeometry(QtCore.QRect(350, 670, 110, 41))
        self.pushButton_4.setObjectName("pushButton_4")
        self.comboBox_3 = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_3.setGeometry(QtCore.QRect(410, 76, 61, 31))
        self.comboBox_3.setObjectName("comboBox_3")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.label_14 = QtWidgets.QLabel(self.centralwidget)
        self.label_14.setGeometry(QtCore.QRect(330, 81, 71, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_14.setFont(font)
        self.label_14.setObjectName("label_14")
        self.scrollArea_2 = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea_2.setGeometry(QtCore.QRect(1050, 65, 181, 77))
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollArea_2.setObjectName("scrollArea_2")
        self.scrollAreaWidgetContents_2 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 179, 75))
        self.scrollAreaWidgetContents_2.setObjectName("scrollAreaWidgetContents_2")
        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)
        self.cB_multifit = QtWidgets.QCheckBox(self.centralwidget)
        self.cB_multifit.setGeometry(QtCore.QRect(1050, 10, 211, 21))
        self.cB_multifit.setObjectName("cB_multifit")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(330, 10, 161, 51))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.splitter = QtWidgets.QSplitter(self.groupBox)
        self.splitter.setGeometry(QtCore.QRect(10, 26, 151, 18))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.radioButton = QtWidgets.QRadioButton(self.splitter)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.radioButton.setFont(font)
        self.radioButton.setObjectName("radioButton")
        self.radioButton_2 = QtWidgets.QRadioButton(self.splitter)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.radioButton_2.setFont(font)
        self.radioButton_2.setObjectName("radioButton_2")
        self.radioButton_3 = QtWidgets.QRadioButton(self.splitter)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.radioButton_3.setFont(font)
        self.radioButton_3.setObjectName("radioButton_3")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(340, 170, 881, 481))
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.North)
        self.tabWidget.setObjectName("tabWidget")
        self.tabWidgetPage1 = QtWidgets.QWidget()
        self.tabWidgetPage1.setObjectName("tabWidgetPage1")
        self.widget = QtWidgets.QWidget(self.tabWidgetPage1)
        self.widget.setGeometry(QtCore.QRect(10, 40, 841, 401))
        self.widget.setObjectName("widget")
        self.pB_refresh = QtWidgets.QPushButton(self.tabWidgetPage1)
        self.pB_refresh.setGeometry(QtCore.QRect(20, 10, 110, 32))
        self.pB_refresh.setObjectName("pB_refresh")
        self.cB_plotModel = QtWidgets.QCheckBox(self.tabWidgetPage1)
        self.cB_plotModel.setGeometry(QtCore.QRect(640, 6, 91, 20))
        self.cB_plotModel.setObjectName("cB_plotModel")
        self.checkBox_4 = QtWidgets.QCheckBox(self.tabWidgetPage1)
        self.checkBox_4.setGeometry(QtCore.QRect(750, 0, 91, 31))
        self.checkBox_4.setObjectName("checkBox_4")
        self.tabWidget.addTab(self.tabWidgetPage1, "")
        self.tabWidgetPage2 = QtWidgets.QWidget()
        self.tabWidgetPage2.setObjectName("tabWidgetPage2")
        self.pB_setXaxis = QtWidgets.QPushButton(self.tabWidgetPage2)
        self.pB_setXaxis.setGeometry(QtCore.QRect(40, 400, 110, 35))
        self.pB_setXaxis.setObjectName("pB_setXaxis")
        self.pB_openResult = QtWidgets.QPushButton(self.tabWidgetPage2)
        self.pB_openResult.setGeometry(QtCore.QRect(20, 2, 110, 38))
        self.pB_openResult.setObjectName("pB_openResult")
        self.tB_xaxis = QtWidgets.QTextBrowser(self.tabWidgetPage2)
        self.tB_xaxis.setGeometry(QtCore.QRect(160, 400, 641, 31))
        self.tB_xaxis.setObjectName("tB_xaxis")
        self.tB_result = QtWidgets.QTextBrowser(self.tabWidgetPage2)
        self.tB_result.setGeometry(QtCore.QRect(140, 5, 531, 31))
        self.tB_result.setObjectName("tB_result")
        self.combo_fitParam = QtWidgets.QComboBox(self.tabWidgetPage2)
        self.combo_fitParam.setGeometry(QtCore.QRect(680, 10, 104, 31))
        self.combo_fitParam.setObjectName("combo_fitParam")
        self.w_fitResult = QtWidgets.QWidget(self.tabWidgetPage2)
        self.w_fitResult.setGeometry(QtCore.QRect(30, 60, 811, 331))
        self.w_fitResult.setObjectName("w_fitResult")
        self.tabWidget.addTab(self.tabWidgetPage2, "")
        self.lcdNumber = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcdNumber.setGeometry(QtCore.QRect(230, 600, 81, 31))
        self.lcdNumber.setStyleSheet("font: 75 14pt \"Arial\";\n"
"color: rgb(255, 0, 0);")
        self.lcdNumber.setObjectName("lcdNumber")
        self.label_15 = QtWidgets.QLabel(self.centralwidget)
        self.label_15.setGeometry(QtCore.QRect(40, 605, 181, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_15.setFont(font)
        self.label_15.setObjectName("label_15")
        self.checkBox_2 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_2.setGeometry(QtCore.QRect(1120, 150, 101, 21))
        self.checkBox_2.setObjectName("checkBox_2")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1273, 22))
        self.menubar.setObjectName("menubar")
        self.menuOptions = QtWidgets.QMenu(self.menubar)
        self.menuOptions.setObjectName("menuOptions")
        MainWindow.setMenuBar(self.menubar)
        self.actionEnable_multifit = QtWidgets.QAction(MainWindow)
        self.actionEnable_multifit.setCheckable(True)
        self.actionEnable_multifit.setObjectName("actionEnable_multifit")
        self.actionBoost_3 = QtWidgets.QAction(MainWindow)
        self.actionBoost_3.setCheckable(True)
        self.actionBoost_3.setObjectName("actionBoost_3")
        self.menuOptions.addAction(self.actionEnable_multifit)
        self.menuOptions.addAction(self.actionBoost_3)
        self.menubar.addAction(self.menuOptions.menuAction())

        self.retranslateUi(MainWindow)
        self.comboBox_3.setCurrentIndex(1)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "Open"))
        self.pushButton_3.setText(_translate("MainWindow", "Fit"))
        self.checkBox.setText(_translate("MainWindow", "Show fit parameters"))
        self.comboBox.setItemText(0, _translate("MainWindow", "3"))
        self.comboBox.setItemText(1, _translate("MainWindow", "2"))
        self.comboBox.setItemText(2, _translate("MainWindow", "1"))
        self.comboBox.setItemText(3, _translate("MainWindow", "0"))
        self.label.setText(_translate("MainWindow", "k weight"))
        self.checkBox_3.setText(_translate("MainWindow", "Each data"))
        self.lineEdit.setText(_translate("MainWindow", "ALL"))
        self.label_2.setText(_translate("MainWindow", "fit data (ex. 1,3,5-10 or \'ALL\')"))
        self.label_5.setText(_translate("MainWindow", "Å"))
        self.label_3.setText(_translate("MainWindow", "k range:"))
        self.label_6.setText(_translate("MainWindow", "to"))
        self.label_4.setText(_translate("MainWindow", "Å"))
        self.label_8.setText(_translate("MainWindow", "Å"))
        self.label_7.setText(_translate("MainWindow", "r range:"))
        self.label_10.setText(_translate("MainWindow", "Å"))
        self.label_9.setText(_translate("MainWindow", "to"))
        self.checkBox_5.setText(_translate("MainWindow", "use the previous result as an input"))
        self.label_11.setText(_translate("MainWindow", "dk: "))
        self.label_12.setText(_translate("MainWindow", "dr: "))
        self.comboBox_2.setItemText(0, _translate("MainWindow", "kaiser"))
        self.comboBox_2.setItemText(1, _translate("MainWindow", "hanning"))
        self.comboBox_2.setItemText(2, _translate("MainWindow", "welch"))
        self.label_13.setText(_translate("MainWindow", "window"))
        self.pushButton_4.setText(_translate("MainWindow", "Set Output"))
        self.comboBox_3.setItemText(0, _translate("MainWindow", "k"))
        self.comboBox_3.setItemText(1, _translate("MainWindow", "r"))
        self.comboBox_3.setItemText(2, _translate("MainWindow", "q"))
        self.label_14.setText(_translate("MainWindow", "fit space"))
        self.cB_multifit.setText(_translate("MainWindow", "Fit with multiple conditions"))
        self.groupBox.setTitle(_translate("MainWindow", "plot space"))
        self.radioButton.setText(_translate("MainWindow", "k"))
        self.radioButton_2.setText(_translate("MainWindow", "r"))
        self.radioButton_3.setText(_translate("MainWindow", "q"))
        self.pB_refresh.setText(_translate("MainWindow", "Refresh"))
        self.cB_plotModel.setText(_translate("MainWindow", "plot model"))
        self.checkBox_4.setText(_translate("MainWindow", "plot fitting"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabWidgetPage1), _translate("MainWindow", "EXAFS"))
        self.pB_setXaxis.setText(_translate("MainWindow", "Set X axis"))
        self.pB_openResult.setText(_translate("MainWindow", "Open result"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabWidgetPage2), _translate("MainWindow", "fitResults"))
        self.label_15.setText(_translate("MainWindow", "Maximu free parameters:"))
        self.checkBox_2.setText(_translate("MainWindow", "Show a tabel"))
        self.menuOptions.setTitle(_translate("MainWindow", "Options"))
        self.actionEnable_multifit.setText(_translate("MainWindow", "Enable multifit"))
        self.actionBoost_3.setText(_translate("MainWindow", "Boost"))

