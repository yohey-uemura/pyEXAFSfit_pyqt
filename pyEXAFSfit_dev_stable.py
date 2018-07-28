import sys
import os
import string
import csv
import fileinput
import glob
import re
import yaml
import math
import time
import collections
import h5py
import matplotlib

#matplotlib.rcParams['backend.qt5'] = 'PySide2'
matplotlib.use('Qt5Agg')
matplotlib.rcParams['backend.qt5'] = 'PySide2'

#import matplotlib.pyplot
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


import numpy as np
import pandas as pd
import natsort
from collections import OrderedDict
import Test_re as readFEFF

from PySide2 import QtCore, QtWidgets, QtGui

if sys.platform =='win32':
    from UI_EXAFSfit_wTable_win import Ui_MainWindow
    from dialog_Fit_win import Ui_Dialog
else:
    from UI_EXAFSfit_wTable import Ui_MainWindow
    from dialog_Fit import Ui_Dialog

from dialog_FEFF import Ui_Dialog as Ui_FEFF
from dialog_multiFit import Ui_Dialog as Ui_multifit
from UI_tableview import Ui_Form as ui_tableview
from dialog_Text import Ui_Dialog as ui_Text

import use_larch as LarchF
import larch
from larch_plugins.xafs import autobk, xftf, xftr, feffit, _ff2chi, feffrunner
from larch_plugins.xafs.feffit import feffit_transform, feffit_dataset, feffit_report
from larch_plugins.xafs.feffdat import feffpath
from larch_plugins.io import read_ascii
import larch.builtins as larch_builtins
import larch.fitting as larchfit

home_dir = QtCore.QDir()
text = home_dir.homePath()
cwd = os.getcwd()

class Error(object):

  def __init__(self, log_fname, mode='a'):
    self.log = open(log_fname, mode)

def get_var_name(**kwargs):
    return list(kwargs.keys())[0]

class params:
    dir = ""
    current_dfile = ""
    outdir = ""
    dfiles = []
    grid = QtWidgets.QGridLayout()
    grid2 = QtWidgets.QGridLayout()
    grid_dialog = QtWidgets.QGridLayout()
    cbs = []
    ex3 = []
    E_intp = []
    path_to_ex3 = ""
    colors = ["Red", "Blue", "Green", "DeepPink", "Black", "Orange", "Brown","OrangeRed",
               "DarkRed","Crimson", "DarkBlue", "DarkGreen", "Hotpink","Coral",
              "DarkMagenta",  "FireBrick", "GoldenRod", "Grey",
              "Indigo", "MediumBlue", "MediumVioletRed"]
    if sys.platform == 'win32':
        homedir = os.environ['HOMEPATH']
    else:
        homedir = os.environ['HOME']
    exafs = []
    path_to_exafs = ""
    #exafs_cB = QtGui.QButtonGroup()
    d_chis = {}
    pathCB = []
    Hlayouts = []
    FitConditions = {'FEFF file':[],'amp':[],'dE':[],'dR':[],'ss':[],'cB':[],'pB':[]}
    feffdir =''
    index_ = 0
    results_rb = QtWidgets.QButtonGroup()

    #for key in FitConditions.keys():
    #    FitConditions[key]=[]

class ItemTableModel(QtCore.QAbstractTableModel):
    def __init__(self, items, headers, *args, **kwargs):
        super(ItemTableModel, self).__init__()
        self.items = items[:]
        self.header = headers[:]

    def rowCount(self, parent):
        return len(self.items)

    def columnCount(self, parent):
        return len(self.header)

class MainWindow(QtWidgets.QMainWindow):
    wSignal = QtCore.Signal()
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.u = Ui_MainWindow()
        self.u.setupUi(self)

        self.dialog = QtWidgets.QDialog()
        self.fit_dialog = Ui_Dialog()
        self.fit_dialog.setupUi(self.dialog)
        self.dialog_f = QtWidgets.QDialog()
        self.FEFF_dialog = Ui_FEFF()
        self.FEFF_dialog.setupUi(self.dialog_f)
        self.dialog_multifit = QtWidgets.QDialog()
        self.multifit_dialog = Ui_multifit()
        self.multifit_dialog.setupUi(self.dialog_multifit)

        self.dialog_suffix = QtWidgets.QDialog()
        self.suffix_d = ui_Text()
        self.suffix_d.setupUi(self.dialog_suffix)

        self.tableview = QtWidgets.QDialog()
        self.uiTableView = ui_tableview()
        self.uiTableView.setupUi(self.tableview)

        self.u.checkBox.setCheckState(QtCore.Qt.Checked)
        #self.u.comboBox.addItems(['3','2','1','0'])
        self.u.widget.setLayout(params.grid)
        self.u.w_fitResult.setLayout(params.grid2)
        self.u.radioButton.toggle()
        widget = QtWidgets.QWidget()
        self.layout = QtWidgets.QVBoxLayout()
        widget.setLayout(self.layout)
        self.u.scrollArea.setWidget(widget)

        widget2 = QtWidgets.QWidget()
        self.layout2 = QtWidgets.QVBoxLayout()
        widget2.setLayout(self.layout2)
        self.u.scrollArea_2.setWidget(widget2)

        self.QError = QtWidgets.QErrorMessage()
        self.Handler = self.QError.qtHandler()


        self.u.menubar.setStyleSheet("color: gray")
        self.u.pushButton_3.setEnabled(False)
        self.u.cB_multifit.setEnabled(False)
        self.u.pB_setXaxis.setEnabled(False)

        

        @QtCore.Slot()
        def Enable_multifit():
            if not self.u.cB_multifit.isEnabled():
                self.u.cB_multifit.setEnabled(True)
            else:
                self.u.cB_multifit.setEnabled(False)

        self.u.actionEnable_multifit.toggled.connect(Enable_multifit)

        def calc_freeParameters():
            delta_k = abs(self.u.dSB_klow.value()-self.u.dSB_khigh.value())
            delta_r = abs(self.u.dSB_rlow.value()-self.u.dSB_rhigh.value())
            Maxparam = math.floor(2*delta_k*delta_r/math.pi+1)
            self.u.lcdNumber.display(Maxparam)

        calc_freeParameters()

        self.Table = QtWidgets.QTableWidget()
        self.Table.setRowCount(20)
        self.Table.setColumnCount(18)
        for i in range(0,20):
            params.FitConditions['FEFF file'].append('')
            self.Table.setItem(i,2,QtWidgets.QTableWidgetItem("EMPTY"))
            self.Table.item(i,2).setForeground(QtGui.QColor('gray'))
        labels = ['Use?','SetFEFF','PATH']
        self.signal = QtCore.Signal(str)
        for term in ['N','dE','dR','ss','C3']:
            paramName = 'Name: '+term
            paramValue = 'Val.: '+term
            paramState = 'State: '+term
            labels+= [paramName,paramState,paramValue]
        for i in range(0,12):
            if i%4 == 1:
                self.Table.setColumnWidth(i+3,80)
            else:
                self.Table.setColumnWidth(i+3,70)
        self.GroupBox = QtWidgets.QButtonGroup()
        for i in range(0,self.Table.rowCount()):
            pB = QtWidgets.QPushButton('Open')
            pB.setObjectName('pB_'+'PATH_'+str(i))
            self.Table.setCellWidget(i,1,pB)
            params.FitConditions['pB'] += [pB]
            pB.setEnabled(False)
            self.GroupBox.addButton(pB)
        self.GroupCheckBox = QtWidgets.QButtonGroup()
        self.GroupCheckBox.setExclusive(False)
        for i in range(0,self.Table.rowCount()):
            cB = QtWidgets.QCheckBox(str(i+1),self)
            cB.setObjectName('cB_'+'PATH_'+str(i))
            self.Table.setCellWidget(i,0,cB)
            params.FitConditions['cB'] +=[cB]
            self.GroupCheckBox.addButton(cB)
        self.Table.setColumnWidth(0,50)
        self.Table.setColumnWidth(1,80)
        self.Table.setHorizontalHeaderLabels(labels)

        self.Table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        def openMenu(position):
            num_of_row = self.Table.currentRow()
            menu = QtWidgets.QMenu()
            actionChangeSubscript = menu.addAction("Change Subscripts of this row")
            action = menu.exec_(self.Table.viewport().mapToGlobal(position))
            if action == actionChangeSubscript:
                if self.Table.item(num_of_row, 2).text() != 'EMPTY':
                    self.dialog_suffix.exec_()

        def change_suffix():
            num_of_row = self.Table.currentRow()
            # print num_of_row
            for i in [3, 6, 9, 12]:
                if self.Table.item(num_of_row, 2).text() != 'EMPTY':
                    suffix = self.suffix_d.lineEdit.text().replace(" ", '')
                    name = self.Table.item(num_of_row, i).text()
                    if re.match(r"(.+)_\w+", name) != None:
                        name_1 = re.match(r"(.+)_\w+", name).group(1)
                        self.Table.setItem(num_of_row, i, QtWidgets.QTableWidgetItem(name_1 + '_' + suffix))
                    elif re.match(r"(.+)_$", name) != None:
                        self.Table.setItem(num_of_row, i, QtWidgets.QTableWidgetItem(name + suffix))
            self.dialog_suffix.done(1)

        self.suffix_d.pushButton.clicked.connect(change_suffix)

        self.Table.customContextMenuRequested.connect(openMenu)



        #self.Table.mousePressEvent()
        # def self.Table.mousePressEvent(, event):
        #     if event.button() == QtCore.Qt.RightButton:
        #         print ("Hello")
        #         print (self.Table.underMouse())



        self.multifit_dialog.tableWidget.setRowCount(22)
        rowLabel = ['DATA','USE?']
        for i in range(2,22):
            rowLabel.append('PATH '+str(i))
        self.multifit_dialog.tableWidget.setVerticalHeaderLabels(rowLabel)
        self.multifit_dialog.tableWidget.setColumnCount(10)
        columnsLabel = []
        for i in range(1,11):
            columnsLabel.append('Condition:'+str(i))
        self.multifit_dialog.tableWidget.setHorizontalHeaderLabels(columnsLabel)
        for i in range(0,10):
            for j in range(1,22):
                cB = QtWidgets.QCheckBox()
                if j == 1:
                    cB.setObjectName('USE:Condition'+str(i+1))
                else:
                    cB.setObjectName('Condition'+str(i+1)+':PATH'+str(j-1))
                self.multifit_dialog.tableWidget.setCellWidget(j,i,cB)


        self.groupButton_RB = QtWidgets.QButtonGroup()
        for term in [self.u.radioButton,self.u.radioButton_2,self.u.radioButton_3]:
            self.groupButton_RB.addButton(term)

        self.exafs_cB = QtWidgets.QButtonGroup()
        self.timer = QtCore.QBasicTimer()
        self.u.progressBar.setRange(0,100)
        self.u.progressBar.setValue(0)
        self.mylarch = larch.Interpreter(with_plugins=False)


        def setButtonG_state():
            if self.u.checkBox_3.isChecked():
                for cb in self.exafs_cB.buttons():
                    cb.setCheckState(QtCore.Qt.Unchecked)
                self.exafs_cB.setExclusive(True)
            else:
                self.exafs_cB.setExclusive(False)

        # def makeEnabled(checkstate):
        #     self.fit_dialog.lE_params.setEnabled(checkstate)

        self.fit_dialog.scrollArea.setWidget(self.Table)
        self.font = QtGui.QFont('Arial',12)
        self.u.checkBox_3.toggled.connect(setButtonG_state)
        self.u.checkBox_3.setCheckState(QtCore.Qt.Checked)
        self.fit_dialog.cB_use_anotherParams.toggled.connect(self.fit_dialog.lE_params.setEnabled)


        def hide_dialog():
            self.dialog.done(1)
            self.u.checkBox.setCheckState(QtCore.Qt.Unchecked)

        def show_hide_dialog():
            if self.u.checkBox.isChecked():
                self.dialog.show()
            else:
                self.dialog.done(1)

        def setFigure(widget,str_xlabel,str_ylabel):
            grid = widget.layout()
            while grid.count() > 0:
                grid.removeItem(grid.itemAt(0))
            fig = Figure(figsize=(320, 320), dpi=72, facecolor=(1, 1, 1), edgecolor=(0, 0, 0))
            ax = fig.add_subplot(111)
            ax.set_xlabel(str_xlabel)
            ax.set_ylabel(str_ylabel)
            canvas = FigureCanvas(fig)
            #navibar = NavigationToolbar(canvas, widget)
            navibar = NavigationToolbar(canvas,parent=widget)
            grid.addWidget(canvas, 0, 0)
            grid.addWidget(navibar)
            return fig, ax, canvas

        def refresh_subPlot(fig,str_xbalel,str_ylabel):
            axis = fig.axes
            for ax in axis:
                fig.delaxes(ax)
            ax = fig.add_subplot(111)
            ax.set_xlabel(str_xbalel)
            ax.set_ylabel(str_ylabel)
            return ax

        self.fig, self.ax, self.canvas = setFigure(self.u.widget,'$k / \AA^{-1}$','$k^{3}\chi$(k)')
        #print self.u.widget_2
        self.fig2, self.ax2, self.canvas2 = setFigure(self.u.w_fitResult,'Y','X')

        def dialog_for_OpenFile(dir,str_caption,str_filter):
            dat_dir = home_dir.homePath()
            if dir == "":
                dat_dir = home_dir.homePath()
            elif dir != "":
                dat_dir = dir
            FO_dialog = QtWidgets.QFileDialog(self)
            file = FO_dialog.getOpenFileName(parent=None, caption=str_caption, filter=str_filter,dir=dat_dir)
            #finfo = QtCore.QFileInfo(file[0])
            #finfo.path()
            return file, os.path.abspath(file[0])

        def dialog_for_OpenFiles(dir,str_caption,str_filter):
            dat_dir = home_dir.homePath()
            if dir == "":
                dat_dir = home_dir.homePath()
            elif dir != "":
                dat_dir = dir
            FO_dialog = QtWidgets.QFileDialog(self)
            #print ("FileDialog:L364")
            files = FO_dialog.getOpenFileNames(parent=None, caption=str_caption, filter=str_filter,dir=dat_dir)
            #print ("FileDialog:L364")
            print (files)
            #finfo = QtCore.QFileInfo(files[0][0])
            ######finf crush#####
            #finfo.path()
            return files, os.path.dirname(files[0][0])

        def plot_ModelEXAFS(PlotSpace,ax,canvas):
            fitParams = larch_builtins._group(self.mylarch)
            xas = larch_builtins._group(self.mylarch)
            fitParams.s0_2 = larchfit.param(self.fit_dialog.doubleSpinBox.value())
            if self.fit_dialog.cB_use_anotherParams.isChecked() and self.fit_dialog.lE_params.text() != '':
                tlist = self.fit_dialog.lE_params.text().split(';')
                for term in tlist:
                    t_array = term.split('=')
                    param_name = t_array[0].replace(" ", "")
                    param_condition = t_array[1][1:-1].replace(" ", "").replace('(', "").replace(')', "").split(',')
                    setattr(fitParams, param_name, larchfit.guess(float(param_condition[0])))
            # self.paramNames = []
            # self.params_for_N = []
            # self.params_for_dE = []
            # self.params_for_dR = []
            # self.params_for_ss = []
            # self.params_for_C3 = []
            feffpathlist = []
            for cB in self.GroupCheckBox.buttons():
                if cB.isChecked():
                    index_ = self.GroupCheckBox.buttons().index(cB)
                    feffinp = params.FitConditions['FEFF file'][index_]
                    path = feffpath(feffinp, _larch=self.mylarch)
                    # s02 = Name_for_N+'*'+'s0_2', e0 = Name_for_dE,sigma2 = Name_for_ss, deltar  = Name_for_dR,
                    Name_for_N = self.Table.item(index_, 3).text()
                    State_for_N = self.Table.cellWidget(index_, 4)
                    Value_for_N = self.Table.item(index_, 5).text()
                    if State_for_N.currentText() == 'def':
                        setattr(fitParams, Name_for_N, larchfit.param(expr=Value_for_N))
                    else:
                        setattr(fitParams, Name_for_N, larchfit.param(float(Value_for_N)))

                    setattr(fitParams, 'degen_path_' + str(index_), path.degen)
                    # setattr(self.fitParams,'net_'+Name_for_N,larchfit.param(expr=Value_for_N+'*'+str(self.fit_dialog.doubleSpinBox.value())))
                    Name_for_dE = self.Table.item(index_, 6).text()
                    State_for_dE = self.Table.cellWidget(index_, 7)
                    Value_for_dE = self.Table.item(index_, 8).text()
                    if State_for_dE.currentText() == 'def':
                        setattr(fitParams, Name_for_dE, larchfit.param(expr=Value_for_dE))
                    else:
                        setattr(fitParams, Name_for_dE, larchfit.param(float(Value_for_dE)))
                    Name_for_dR = self.Table.item(index_, 9).text()
                    State_for_dR = self.Table.cellWidget(index_, 10)
                    Value_for_dR = self.Table.item(index_, 11).text()
                    if State_for_dR.currentText() == 'def':
                        setattr(fitParams, Name_for_dR, larchfit.param(expr=Value_for_dR))
                    else:
                        setattr(fitParams, Name_for_dR, larchfit.param(float(Value_for_dR)))
                    Name_for_ss = self.Table.item(index_, 12).text()
                    State_for_ss = self.Table.cellWidget(index_, 13)
                    Value_for_ss = self.Table.item(index_, 14).text()
                    if State_for_ss.currentText() == 'def':
                        setattr(fitParams, Name_for_ss, larchfit.param(expr=Value_for_ss))
                    else:
                        setattr(fitParams, Name_for_ss, larchfit.param(float(Value_for_ss)))
                    Name_for_C3 = self.Table.item(index_, 15).text()
                    State_for_C3 = self.Table.cellWidget(index_, 16)
                    Value_for_C3 = self.Table.item(index_, 17).text()
                    if State_for_C3.currentText() == 'def':
                        setattr(fitParams, Name_for_C3, larchfit.param(expr=Value_for_C3))
                    else:
                        setattr(fitParams, Name_for_C3, larchfit.param(float(Value_for_C3)))
                    path.s02 = Name_for_N + '*' + 's0_2' + '/' + 'degen_path_' + str(index_)
                    path.e0 = Name_for_dE
                    path.sigma2 = Name_for_ss
                    path.deltar = Name_for_dR
                    path.third = Name_for_C3
                    feffpathlist.append(path)
            FeffitTransform = feffit_transform(fitspace=self.u.comboBox_3.currentText(),
                                                    kmin=self.u.dSB_klow.value(),
                                                    kmax=self.u.dSB_khigh.value(),
                                                    kw=float(self.u.comboBox.currentText()),
                                                    dk=self.u.dB_window_k.value(),
                                                    window=self.u.comboBox_2.currentText(),
                                                    rmin=self.u.dSB_rlow.value(),
                                                    rmax=self.u.dSB_rhigh.value(),
                                                    _larch=self.mylarch,
                                                    dr=self.u.dB_window_r.value())
            xafsdat = larch_builtins._group(self.mylarch)
            key = self.exafs_cB.buttons()[0].text()
            xafsdat.k = params.d_chis[key][0][:]
            xafsdat.chi = params.d_chis[key][1][:]
            dset = feffit_dataset(data=xafsdat, pathlist=feffpathlist, transform=FeffitTransform,
                                  _larch=self.mylarch)
            out = feffit(fitParams, dset, _larch=self.mylarch)
            # _ff2chi(feffpathlist,fitParams,xas,_larch=self.mylarch)

            if PlotSpace == 'k':
                k_fit = dset.model.k
                chi_fit = dset.model.chi
                ax.plot(k_fit, chi_fit * k_fit ** float(self.u.comboBox.currentText()),
                        'r--', label='model',
                        linewidth=1)
            elif PlotSpace == 'r':
                k_fit = dset.model.k
                chi_fit = dset.model.chi
                wind = self.u.comboBox_2.currentText()
                dk_wind = self.u.dB_window_k.value()
                r_fit, chir_fit, chir_mag_fit, chir_im_fit = LarchF.calcFT(k_fit, chi_fit,
                                                                           float(self.u.comboBox.currentText()),
                                                                           self.u.dSB_klow.value(),
                                                                           self.u.dSB_khigh.value(),
                                                                           wind, dk_wind)
                ax.plot(r_fit, chir_mag_fit, 'r--', label='model: mag', linewidth=2)
                ax.plot(r_fit, chir_im_fit, 'm--', label='model: img', linewidth=2)
            elif PlotSpace == 'q':
                k_fit = dset.model.k
                chi_fit = dset.model.chi
                wind = self.u.comboBox_2.currentText()
                dk_wind = self.u.dB_window_k.value()
                dr_wind = self.u.dB_window_r.value()
                r_fit, chir_fit, chir_mag_fit, chir_im_fit = LarchF.calcFT(k_fit, chi_fit,
                                                                           float(self.u.comboBox.currentText()),
                                                                           self.u.dSB_klow.value(),
                                                                           self.u.dSB_khigh.value(), wind,
                                                                           dk_wind)
                q_fit, chiq_fit = LarchF.calc_rFT(r_fit, chir_fit, self.u.dSB_rlow.value(),
                                                  self.u.dSB_rhigh.value(), self.u.dSB_khigh.value() + 0.5, wind,
                                                  dr_wind)
                ax.plot(q_fit, chiq_fit, 'r--', label='model', linewidth=2)
            canvas.draw()
            # else:
            #     msgBox = QtWidgets.QMessageBox()
            #     msgBox.setText("The fitting results doesn't exist in this file.\nPlease choose another file")
            #     msgBox.exec_()




        def plot_fitResult(rB,cB,PlotSpace,ax,canvas):
            print ("L321")
            relust_file = rB.objectName()
            print ("L322")
            print (relust_file)
            if os.path.isfile(relust_file):
                result = h5py.File(relust_file,'r')
                if cB.text() in result:
                    if PlotSpace == 'k':
                        k_fit = result[cB.text()]['chi_fit'][:,0]
                        chi_fit = result[cB.text()]['chi_fit'][:,1]
                        ax.plot(k_fit,chi_fit*k_fit**float(self.u.comboBox.currentText()),'r',label='fit',linewidth=2)
                    elif PlotSpace == 'r':
                        k_fit = result[cB.text()]['chi_fit'][:,0]
                        chi_fit = result[cB.text()]['chi_fit'][:,1]
                        wind = self.u.comboBox_2.currentText()
                        dk_wind = self.u.dB_window_k.value()
                        r_fit, chir_fit, chir_mag_fit, chir_im_fit = LarchF.calcFT(k_fit,chi_fit,float(self.u.comboBox.currentText()),
                                                                                   self.u.dSB_klow.value(),self.u.dSB_khigh.value(),
                                                                                   wind,dk_wind)
                        # r_fit = result[cB.text()]['chir_fit'][:,0]
                        # chir_mag = result[cB.text()]['chir_fit'][:,1]
                        # chir_im = result[cB.text()]['chir_fit'][:,2]
                        ax.plot(r_fit,chir_mag_fit,color='r',label='fit: mag',linewidth=2)
                        ax.plot(r_fit,chir_im_fit,color='m',label='fit: img',linewidth=2)
                    elif PlotSpace == 'q':
                        k_fit = result[cB.text()]['chi_fit'][:, 0]
                        chi_fit = result[cB.text()]['chi_fit'][:, 1]
                        wind = self.u.comboBox_2.currentText()
                        dk_wind = self.u.dB_window_k.value()
                        dr_wind = self.u.dB_window_r.value()
                        r_fit, chir_fit, chir_mag_fit, chir_im_fit = LarchF.calcFT(k_fit, chi_fit,
                                                                                   float(self.u.comboBox.currentText()),
                                                                                   self.u.dSB_klow.value(),
                                                                                   self.u.dSB_khigh.value(), wind,
                                                                                   dk_wind)
                        q_fit, chiq_fit = LarchF.calc_rFT(r_fit, chir_fit, self.u.dSB_rlow.value(), self.u.dSB_rhigh.value(), self.u.dSB_khigh.value()+0.5,wind,dr_wind)
                        ax.plot(q_fit,chiq_fit,'r',label='fit',linewidth=2)
                    canvas.draw()
                else:
                    msgBox = QtWidgets.QMessageBox()
                    msgBox.setText("The fitting results doesn't exist in this file.\nPlease choose another file")
                    msgBox.exec_()
            else:
                pass


        def plot_each(cB,integer):
            #print cB
            k, chi = params.d_chis[cB.text()]
            #print (k)
            wind = self.u.comboBox_2.currentText()
            dk_wind = self.u.dB_window_k.value()
            dr_wind = self.u.dB_window_r.value()
            r, chir, chir_mag, chir_im = LarchF.calcFT(k,chi,float(self.u.comboBox.currentText()),self.u.dSB_klow.value(),self.u.dSB_khigh.value(),wind,dk_wind)
            q, chi_q = LarchF.calc_rFT(r,chir,self.u.dSB_rlow.value(),self.u.dSB_rhigh.value(),self.u.dSB_khigh.value()+2.0,wind,dr_wind)
            str_ylabel = '$k^{'+self.u.comboBox.currentText()+'}\chi$(k)'
            #print ("L558")
            if self.u.radioButton.isChecked():
                if integer == -1:
                    self.ax= refresh_subPlot(self.fig,'$k / \AA^{-1}$',str_ylabel)
                else:
                    while len(self.ax.lines) > 0:
                        self.ax.lines.pop()
                self.ax.plot(k,chi*k**float(self.u.comboBox.currentText()),color='b',linewidth=2)
                x = np.linspace(0.0, 16.0, 161)
                xmin = self.u.dSB_klow.value()
                xmax = self.u.dSB_khigh.value()
                delta_k = self.u.dB_window_k.value()
                wtype = self.u.comboBox_2.currentText()
                amp = (chi*k**float(self.u.comboBox.currentText())).max()*1.25
                FTw = LarchF.calcFTwindow(x, xmin, xmax, delta_k, wtype)
                self.ax.plot(x,FTw*amp,color='g',linewidth=2)
                if self.u.checkBox_4.isChecked() and len(params.results_rb.buttons()) != 0:
                    plot_fitResult(params.results_rb.checkedButton(),cB,'k',self.ax,self.canvas)
                if self.u.cB_plotModel.isChecked() and not self.u.checkBox_4.isChecked():
                    plot_ModelEXAFS('k',self.ax,self.canvas)
            elif self.u.radioButton_2.isChecked():
                if integer == -1:
                    self.ax = refresh_subPlot(self.fig,'$r / \AA$','FT['+str_ylabel+']')
                else:
                    while len(self.ax.lines) > 0:
                        self.ax.lines.pop()
                self.ax.set_xlim([0,6])
                self.ax.plot(r,chir_mag,color='b',linewidth=2)
                self.ax.plot(r,chir_im,color='k',linewidth=2)
                x = np.linspace(0.0, 16.0, 161)
                xmin = self.u.dSB_rlow.value()
                xmax = self.u.dSB_rhigh.value()
                delta_r = self.u.dB_window_r.value()
                wtype = self.u.comboBox_2.currentText()
                amp = chir_mag.max() * 1.25
                FTw = LarchF.calcFTwindow(x, xmin, xmax, delta_r, wtype)
                self.ax.plot(x, FTw * amp, color='g', linewidth=2)
                if self.u.checkBox_4.isChecked() and len(params.results_rb.buttons()) != 0:
                    plot_fitResult(params.results_rb.checkedButton(),cB,'r',self.ax,self.canvas)
                if  self.u.cB_plotModel.isChecked() and not self.u.checkBox_4.isChecked():
                    plot_ModelEXAFS('r', self.ax, self.canvas)
            elif self.u.radioButton_3.isChecked():
                if integer == -1:
                    self.ax = refresh_subPlot(self.fig,'$q / \AA^{-1}$',str_ylabel.replace('k','q'))
                    # self.fig, self.ax, self.canvas = setFigure(self.u.widget,'$q / \AA^{-1}$',str_ylabel.replace('k','q'))
                else:
                    while len(self.ax.lines) > 0:
                        self.ax.lines.pop()
                self.ax.plot(q,chi_q,color='b',linewidth=2)
                x = np.linspace(0.0, 16.0, 161)
                xmin = self.u.dSB_klow.value()
                xmax = self.u.dSB_khigh.value()
                delta_q = self.u.dB_window_k.value()
                wtype = self.u.comboBox_2.currentText()
                amp = chi_q.max() * 1.25
                FTw = LarchF.calcFTwindow(x, xmin, xmax, delta_q, wtype)
                self.ax.plot(x, FTw * amp, color='g', linewidth=2)
                if self.u.checkBox_4.isChecked():
                    plot_fitResult(params.results_rb.checkedButton(),cB,'q',self.ax,self.canvas)
                if self.u.cB_plotModel.isChecked() and not self.u.checkBox_4.isChecked():
                    plot_ModelEXAFS('q', self.ax, self.canvas)
            self.ax.legend(loc=1)
            self.canvas.draw()
            

        def plot_checked(integer):
            str_ylabel = '$k^{'+self.u.comboBox.currentText()+'}\chi$(k)'
            if self.u.radioButton.isChecked():
                if integer == -1:
                    print ('Here')
                    self.ax= refresh_subPlot(self.fig, '$k / \AA^{-1}$',str_ylabel)
                else:
                    while len(self.ax.lines) > 0:
                        self.ax.lines.pop()
                for cB in self.exafs_cB.buttons():
                    if cB.isChecked():
                        #file = cB.objectName()
                        k, chi = params.d_chis[cB.text()]
                        index_ = self.exafs_cB.buttons().index(cB)
                        self.ax.plot(k,chi*k**float(self.u.comboBox.currentText()),color=params.colors[index_])
                #self.canvas.draw()
            elif self.u.radioButton_2.isChecked():
                i = 0
                if integer == -1:
                    self.ax= refresh_subPlot(self.fig,'$r / \AA$','FT['+str_ylabel+']')
                else:
                    while len(self.ax.lines) > 0:
                        self.ax.lines.pop()
                self.ax.set_xlim([0,6])
                for cB in self.exafs_cB.buttons():
                    if cB.isChecked():
                        #file = cB.objectName()
                        k, chi = params.d_chis[cB.text()]
                        wind = self.u.comboBox_2.currentText()
                        dk_wind = self.u.dB_window_k.value()
                        r, chir, chir_mag, chir_im = LarchF.calcFT(k,chi,float(self.u.comboBox.currentText()),self.u.dSB_klow.value(),self.u.dSB_khigh.value(),wind,dk_wind)
                        index_ = self.exafs_cB.buttons().index(cB)
                        self.ax.plot(r,chir_mag,color=params.colors[index_])
                #self.canvas.draw()
            elif self.u.radioButton_3.isChecked():
                if integer == -1:
                    self.ax= refresh_subPlot(self.fig,'$q / \AA^{-1}$',str_ylabel.replace('k','q'))
                else:
                    while len(self.ax.lines) > 0:
                        self.ax.lines.pop()
                for cB in self.exafs_cB.buttons():
                    if cB.isChecked():
                        #file = cB.objectName()
                        k, chi = params.d_chis[cB.text()]
                        wind = self.u.comboBox_2.currentText()
                        dk_wind = self.u.dB_window_k.value()
                        dr_wind = self.u.dB_window_r.value()
                        r, chir, chir_mag, chir_im = LarchF.calcFT(k,chi,float(self.u.comboBox.currentText()),
                                                                   self.u.dSB_klow.value(),self.u.dSB_khigh.value(),
                                                                   wind,dk_wind)
                        q, chi_q = LarchF.calc_rFT(r,chir,self.u.dSB_rlow.value(),self.u.dSB_rhigh.value(),self.u.dSB_khigh.value()+2.0,wind,dr_wind)
                        index_ = self.exafs_cB.buttons().index(cB)
                        self.ax.plot(q, chi_q,color=params.colors[index_])
            self.canvas.draw()


        def read_chi_files():
            while len(self.exafs_cB.buttons()) != 0:
                b = self.layout.takeAt(len(self.exafs_cB.buttons()) - 1)
                del params.d_chis[b.widget().text()]
                self.exafs_cB.removeButton(b.widget())
                b.widget().deleteLater()
            while len(params.results_rb.buttons()) !=0:
                b = self.layout2.takeAt(len(params.results_rb.buttons()) -1)
                params.results_rb.removeButton(b.widget())
                b.widget().deleteLater()
            files, params.dir = dialog_for_OpenFiles(params.dir,'Open chi files',"chi files(*.xi *.chi *chik *.rex)")
            i = 0
            for f in natsort.natsorted(files[0]):
                #finfo = QtCore.QFileInfo(f)
                cb = QtWidgets.QCheckBox(str(i+1)+':'+os.path.basename(f))
                params.d_chis[str(i+1)+':'+os.path.basename(f)] = LarchF.read_chi_file(os.path.abspath(f))
                cb.setObjectName(os.path.abspath(f))
                style = "color: "+params.colors[i%len(params.colors)]
                cb.setStyleSheet(style)
                self.exafs_cB.addButton(cb)
                self.layout.addWidget(cb)
                i+=1
            self.exafs_cB.buttons()[0].setCheckState(QtCore.Qt.Checked)
            # print("L700")
            checkstate()
            self.wSignal.emit()
            #self.u.pB_refresh.click()
            # if self.u.checkBox_3.isChecked():
            #     # print ("L703")
            #     plot_each(self.exafs_cB.checkedButton(),-1)
            #     #self.canvas.draw()
            # else:
            #     plot_checked(-1)
            #     #self.canvas.draw()

        def change_rb(button):
            if self.u.checkBox_3.isChecked():
                plot_each(self.exafs_cB.checkedButton(), self.exafs_cB.id(button)) if len(self.exafs_cB.buttons()) !=0 else 0
            else:
                plot_checked(self.exafs_cB.id(button))  if len(self.exafs_cB.buttons()) !=0 else 0


        def plotConditionChanged():
            if self.u.checkBox_3.isChecked():
                plot_each(self.exafs_cB.checkedButton(), -1) if len(self.exafs_cB.buttons()) !=0 else 0
            else:
                plot_checked(-1)  if len(self.exafs_cB.buttons()) !=0 else 0

        def change_plot_space():
            if self.u.comboBox_3.currentText() == 'k':
                self.u.radioButton.toggle()
            elif self.u.comboBox_3.currentText() == 'r':
                self.u.radioButton_2.toggle()
            elif self.u.comboBox_3.currentText() == 'q':
                self.u.radioButton_3.toggle()

        @QtCore.Slot()
        def add_FEFF_path(button):
            self.FEFF_dialog.comboBox.clear()
            params.index_ = params.FitConditions['pB'].index(button)
            dat_dir = home_dir.homePath()
            if params.feffdir == '':
                dat_dir = home_dir.homePath()
            elif dir != "":
                dat_dir = params.feffdir
            FO_dialog = QtWidgets.QFileDialog(self)
            #print (FO_dialog.filters())
            file = FO_dialog.getOpenFileName(parent=None,filter = "FEFF input(feff.inp)",caption="Open feff.inp",dir=dat_dir)
            if file[0]!='':
                self.FEFF_dialog.textBrowser_2.clear()
                params.feffdir = os.path.dirname(os.path.abspath(file[0]))
                self.FEFF_dialog.textBrowser_2.append(params.feffdir)
                self.FEFF_dialog.textBrowser.clear()
                str_ = "{:16s}{:16s}{:16s}{:16s}{:16s}".format('PATH:',  'Route:',  'Distance:', 'Relative AMP', 'Degeneracy')
                self.FEFF_dialog.textBrowser.append(str_)
                self.dialog_f.show()
                if not os.path.isfile(os.path.dirname(file[0])+'/paths.dat'):
                    rFEFF = feffrunner.feffrunner(file[0],_larch=self.mylarch)
                    rFEFF.run()
                txt_array = readFEFF.read_FEFF(file[0])
                list = []
                for key in natsort.natsorted(txt_array.keys()):
                    self.FEFF_dialog.textBrowser.append(txt_array[key])
                    t_array = txt_array[key].split(':')
                    list.append(t_array[0]+':'+t_array[1]+':'+t_array[2])
                self.FEFF_dialog.comboBox.addItems(list)
                self.FEFF_dialog.textBrowser.verticalScrollBar().setValue(0)

        def close_dialog_f():
            # item = self.Table.item(params.index_,3)
            # print item
            if self.Table.item(params.index_,2).text() == "EMPTY":
                for i in range(3,18):
                    self.Table.removeCellWidget(params.index_,i)
                title = re.sub("\s+",'',self.FEFF_dialog.comboBox.currentText())
                self.Table.setItem(params.index_,2,QtWidgets.QTableWidgetItem(title))
                self.Table.item(params.index_,2).setForeground(QtGui.QColor('black'))
                num_of_feffpath = "{:04d}".format(self.FEFF_dialog.comboBox.currentIndex() + 1)
                params.FitConditions['FEFF file'][params.index_] = params.feffdir+'/'+'feff'+num_of_feffpath+'.dat'
                print (os.path.basename(params.FitConditions['FEFF file'][params.index_]))
                for term in ['N','dE','dR','ss','C3']:
                    i = 0
                    while i < 3:
                        if i == 0:
                            name = term+'_'+str(params.index_+1)
                            self.Table.setItem(params.index_,3+3*['N','dE','dR','ss','C3'].index(term)+i,QtWidgets.QTableWidgetItem(name))
                            self.Table.item(params.index_,3+3*['N','dE','dR','ss','C3'].index(term)+i).setFont(self.font)
                            self.Table.item(params.index_,3+3*['N','dE','dR','ss','C3'].index(term)+i).setForeground(QtGui.QColor('blue'))
                        elif i == 1:
                            comboBox = QtWidgets.QComboBox()
                            comboBox.addItems(['guess','set','def'])
                            if term == 'C3':
                                comboBox.setCurrentIndex(1)
                            self.Table.setCellWidget(params.index_,3+3*['N','dE','dR','ss','C3'].index(term)+i,comboBox)
                        elif i == 2:
                            value = 0.0
                            if term == 'N':
                                value = 1.0
                                string = "{:.1f}".format(value)
                                self.Table.setItem(params.index_,3+3*['N','dE','dR','ss','C3'].index(term)+i,QtWidgets.QTableWidgetItem(string))
                                self.Table.item(params.index_,3+3*['N','dE','dR','ss','C3'].index(term)+i).setFont(self.font)
                            elif term == 'dR':
                                value = 0.00
                                string = "{:.2f}".format(value)
                                self.Table.setItem(params.index_,3+3*['N','dE','dR','ss','C3'].index(term)+i,QtWidgets.QTableWidgetItem(string))
                                self.Table.item(params.index_,3+3*['N','dE','dR','ss','C3'].index(term)+i).setFont(self.font)
                            elif term == 'ss':
                                value = 0.003
                                string = "{:.3f}".format(value)
                                self.Table.setItem(params.index_,3+3*['N','dE','dR','ss','C3'].index(term)+i,QtWidgets.QTableWidgetItem(string))
                                self.Table.item(params.index_,3+3*['N','dE','dR','ss','C3'].index(term)+i).setFont(self.font)
                            elif term == 'C3':
                                value = 0.0
                                string = "{:.3f}".format(value)
                                self.Table.setItem(params.index_, 3 + 3 * ['N', 'dE', 'dR', 'ss', 'C3'].index(term) + i,QtWidgets.QTableWidgetItem(string))
                                self.Table.item(params.index_,3 + 3 * ['N', 'dE', 'dR', 'ss', 'C3'].index(term) + i).setFont(self.font)
                            else:
                                string = "{:.1f}".format(value)
                                self.Table.setItem(params.index_,3+3*['N','dE','dR','ss'].index(term)+i,QtWidgets.QTableWidgetItem(string))
                                self.Table.item(params.index_,3+3*['N','dE','dR','ss'].index(term)+i).setFont(self.font)
                        i += 1
            else:
                title = re.sub("\s+", '', self.FEFF_dialog.comboBox.currentText())
                self.Table.setItem(params.index_, 2, QtWidgets.QTableWidgetItem(title))
                num_of_feffpath = "{:04d}".format(self.FEFF_dialog.comboBox.currentIndex() + 1)
                params.FitConditions['FEFF file'][params.index_] = params.feffdir + '/' + 'feff' + num_of_feffpath + '.dat'
            ###Make params####
            self.dialog_f.done(1)
            self.dialog.setFocus()
            checkstate()


        def setOutputFile():
            dat_dir = home_dir.homePath()
            if params.feffdir == '':
                dat_dir = home_dir.homePath()
            elif dir != "":
                dat_dir = params.dir
            FO_dialog = QtWidgets.QFileDialog(self)
            #print (FO_dialog.filters())
            ofile = FO_dialog.getSaveFileName(parent=None,filter = "Output File(*.csv *.dat)",dir=dat_dir)
            if ofile[0] != '':
                self.u.textBrowser.clear()
                self.u.textBrowser.append(os.path.abspath(ofile[0]))
                checkstate()


        def checkstate():
            sign = 0
            # print ("L840")
            for cB in self.GroupCheckBox.buttons():
                if params.FitConditions['FEFF file'][self.GroupCheckBox.buttons().index(cB)] != '':
                    sign = 1
                    break
            if self.u.textBrowser.toPlainText() != '' and len(self.exafs_cB.buttons()) != 0 and sign:
                self.u.pushButton_3.setEnabled(True)
            #print ("L847")

        @QtCore.Slot()
        def pB_set_Enabled(checkbox):
            if checkbox.isChecked():
                params.FitConditions['pB'][params.FitConditions['cB'].index(checkbox)].setEnabled(True)
            else:
                params.FitConditions['pB'][params.FitConditions['cB'].index(checkbox)].setEnabled(False)

        def close_multifit_dialog():
            self.dialog_multifit.done(1)
            self.u.cB_multifit.setCheckState(QtCore.Qt.Unchecked)
        def use_multifit():
            if self.u.cB_multifit.isChecked():
                self.dialog_multifit.show()
                if self.u.textBrowser.toPlainText() != '':
                    self.multifit_dialog.textBrowser.clear()
                    self.multifit_dialog.textBrowser.append(self.u.textBrowser.toPlainText())
            else:
                self.dialog_multifit.done(1)

        def openOutPutFile():
            dat_dir = home_dir.homePath()
            if params.dir == "":
               pass
            else:
                dat_dir = params.dir
            FO_dialog = QtWidgets.QFileDialog(self)
            file = FO_dialog.getSaveFileName(parent=None, caption='set output file name', filter='Result File(*.csv)',dir=dat_dir)
            if file[0] != '':
                self.multifit_dialog.textBrowser.clear()
                self.multifit_dialog.textBrowser.append(file[0])


        def plot_paramResult(DF,currentText):
            #print ("L659")
            self.fig2, self.ax2, self.canvas2 = setFigure(self.u.w_fitResult,'X',currentText)
            #print ("L661")
            if self.u.tB_xaxis.toPlainText() != '':
                pass
            else:
                x_array = range(1,len(DF['data'].values)+1)
                #print DF[:,currentText].as_matrix
                if currentText =='R-factor':
                    self.ax2.plot(x_array,DF[currentText].values,label=currentText,marker='o',color='r',markersize=10)
                else:
                    if 'delta('+currentText+')' in DF.keys():
                        if currentText in self.params_for_dR:
                            self.ax2.errorbar(x_array,DF[currentText].values,yerr=DF['delta('+currentText+')'].values,label='R_0'+currentText,marker='o',color='r',markersize=10)
                        else:
                            self.ax2.errorbar(x_array,DF[currentText].values,yerr=DF['delta('+currentText+')'].values,label=currentText,marker='o',color='r',markersize=10)
                    else:
                        self.ax2.plot(x_array,DF[currentText].values,label=currentText,marker='o',color='r',markersize=10)
                #print ("L677")
                self.ax2.legend(loc=1)
                #print ("L679")
            #self.canvas2.draw()

        def child_plot_paramResult():
            currentText = self.u.combo_fitParam.currentText()
            self.fig2.delaxes(self.ax2)
            self.ax2 = self.fig2.add_subplot(111)
            self.ax2.set_xlabel('X')
            self.ax2.set_ylabel(currentText)
            if self.u.tB_xaxis.toPlainText() != '':
                f = open(self.u.tB_xaxis.toPlainText(),'r')
                text = f.readlines()[0]
                print (text.rstrip())
                label = 'X'
                unit = ''
                if re.search(r"Label\s*\:\s*(\w+)\,\s*Unit\s*\:\s*(\w+)",text):
                    label = re.search(r"Label\s*\:\s*(\w+)\,\s*Unit\s*\:\s*(\w+)",text).group(1)
                    unit = re.search(r"Label\s*\:\s*(\w+)\,\s*Unit\s*\:\s*(\w+)",text).group(2)
                df_axis = pd.read_csv(self.u.tB_xaxis.toPlainText(),delimiter=r"\s+|\,")
                print (df_axis.keys())
                x_array = df_axis['x-axis'].values
                if isinstance(x_array[0],str):
                    self.ax2.set_xticks(range(len(x_array)))
                    self.ax2.set_xticklabels(x_array)
                if currentText =='R-factor':
                    self.ax2.plot(range(len(x_array)),self.df_fit[currentText].values,label=currentText,marker='o',color='r',markersize=10)
                else:
                    if currentText in self.params_for_dR:
                        self.ax2.set_ylabel('R_0+'+currentText)
                        if 'delta('+currentText+')' in self.df_fit.keys():
                            self.ax2.errorbar(range(len(x_array)),self.df_fit[currentText].values,yerr=self.df_fit['delta('+currentText+')'].values,label='R_0+'+currentText,marker='o',color='r',markersize=10)
                        else:
                            self.ax2.plot(range(len(x_array)),self.df_fit[currentText].values,label='R_0+'+currentText,marker='o',color='r',markersize=10)
                    else:
                        if 'delta('+currentText+')' in self.df_fit.keys():
                            self.ax2.errorbar(range(len(x_array)),self.df_fit[currentText].values,yerr=self.df_fit['delta('+currentText+')'].values,label=currentText,marker='o',color='r',markersize=10)
                        else:
                            self.ax2.errorbar(range(len(x_array)),self.df_fit[currentText].values,yerr=self.df_fit['delta('+currentText+')'].values,label=currentText,marker='o',color='r',markersize=10)
            else:
                x_array = range(1,len(self.df_fit['data'].values)+1)
                if currentText =='R-factor':
                    self.ax2.plot(x_array,self.df_fit[currentText].values,label=currentText,marker='o',color='r',markersize=10)
                else:
                    if 'delta('+currentText+')' in self.df_fit.keys():
                        self.ax2.errorbar(x_array,self.df_fit[currentText].values,yerr=self.df_fit['delta('+currentText+')'].values,label=currentText,marker='o',color='r',markersize=10)
                    else:
                        self.ax2.plot(x_array,self.df_fit[currentText].values,label=currentText,marker='o',color='r',markersize=10)
                self.ax2.legend(loc=1)
            self.canvas2.draw()


        def openFitResults():
            if self.u.tB_result.toPlainText() !='':
                self.u.tB_result.clear()
            self.u.pB_setXaxis.setEnabled(False)
            file, absPATH = dialog_for_OpenFile(params.dir,'open a result file', 'Result File(*.csv)')
            self.u.tB_result.append(absPATH)
            #print ("L727")
            self.df_fit = pd.read_csv(self.u.tB_result.toPlainText(),delimiter=r"\s+")
            #print ("L729")
            print (self.df_fit.keys())
            self.u.combo_fitParam.clear()
            self.u.tB_xaxis.clear()
            #print ("L733")
            for term in self.df_fit.columns.values:
                if re.search(r"(\+\/\-|delta\(.+\)|data)",term) == None:
                    self.u.combo_fitParam.addItem(term)
            if not self.u.pB_setXaxis.isEnabled():
                self.u.pB_setXaxis.setEnabled(True)
            print ("L741")
            plot_paramResult(self.df_fit,self.u.combo_fitParam.currentText())
            print ("L743")

        def setXaxisFileName():
            if self.u.tB_xaxis.toPlainText() != '':
                self.u.tB_xaxis.clear()
            file, absPATH = dialog_for_OpenFile(params.dir,'open a result file', 'Result File(*.csv)')
            if os.path.isfile(absPATH):
                self.u.tB_xaxis.append(absPATH)
            child_plot_paramResult()

        def execSaveConditions():
            dat_dir = home_dir.homePath()
            if params.dir == "":
                pass
            else:
                dat_dir = params.dir
            FO_dialog = QtWidgets.QFileDialog(self)
            file = FO_dialog.getSaveFileName(parent=None, caption='set output file name',
                                             filter='YAML File(*.yaml)',
                                             dir=dat_dir)
            if file[0] !='':
                self.SaveConditions(file[0])


        def reloadConditions():
            dat_dir = home_dir.homePath()
            if params.dir == "":
               pass
            else:
                dat_dir = params.dir
            FO_dialog = QtWidgets.QFileDialog(self)
            file = FO_dialog.getOpenFileName(parent=None, caption='set output file name', filter='YAML File(*.yaml)',dir=dat_dir)
            if os.path.isfile(file[0]):
                f = open(file[0],'r')
                Dict = yaml.load(f)
                f.close()
                self.fit_dialog.doubleSpinBox.setValue(float(Dict['S02']))
                if self.fit_dialog.lE_params.isEnabled() and self.fit_dialog.lE_params.text() != '':
                    self.fit_dialog.lE_params.clear()
                self.fit_dialog.lE_params.insert(Dict['extra_param'])
                for key in ['dSB_klow','dSB_khigh','dSB_rlow','dSB_rhigh','dB_window_k','dB_window_r']:
                    getattr(self.u,key).setValue(Dict[key])
                if Dict['plotSpace'] == 'k':
                    self.groupButton_RB.buttons()[0].toggle()
                elif Dict['plotSpace'] == 'r':
                    self.groupButton_RB.buttons()[1].toggle()
                elif Dict['plotSpace'] == 'q':
                    self.groupButton_RB.buttons()[2].toggle()
                self.u.comboBox_3.setCurrentIndex(['k','r','q'].index(Dict['fitSpace']))
                self.u.comboBox.setCurrentIndex(['3','2','1'].index(Dict['kweight']))
                self.u.comboBox_2.setCurrentIndex(['kaiser','hanning','welch'].index(Dict['window']))
                array_path =[]
                for key in natsort.natsorted(Dict.keys()):
                    if 'path' in key:
                        array_path.append(key)
                for path_n in natsort.natsorted(array_path):
                    i = natsort.natsorted(array_path).index(path_n)
                    self.GroupCheckBox.buttons()[i].setCheckState(QtCore.Qt.Checked)
                    params.FitConditions['FEFF file'][i] = Dict[path_n]['path_to_feff']
                    self.Table.setItem(i,2,QtWidgets.QTableWidgetItem(Dict[array_path[i]]['discription']))
                    for term in ['N','dE','dR','ss','C3']:
                        num = 3+3*['N','dE','dR','ss','C3'].index(term)
                        self.Table.setItem(i,num,QtWidgets.QTableWidgetItem(Dict[array_path[i]][term]['name']))
                        self.Table.item(i,num).setFont(self.font)
                        self.Table.item(i,num).setForeground(QtGui.QColor('blue'))
                        comboBox = QtWidgets.QComboBox()
                        comboBox.addItems(['guess','set','def'])
                        comboBox.setCurrentIndex(['guess','set','def'].index(Dict[array_path[i]][term]['state']))
                        self.Table.setCellWidget(i,num+1,comboBox)
                        self.Table.setItem(i,num+2,QtWidgets.QTableWidgetItem(Dict[array_path[i]][term]['value']))

        def show_hide_tableview():
            if self.u.checkBox_2.isChecked():
                self.tableview.show()
            else:
                self.tableview.hide()


        self.u.checkBox.toggled.connect(show_hide_dialog)
        self.fit_dialog.pushButton.clicked.connect(hide_dialog)
        self.u.comboBox.currentIndexChanged.connect(plotConditionChanged)
        for cB in [self.u.dSB_klow,self.u.dSB_khigh]:
            cB.valueChanged.connect(plotConditionChanged)
        for sB in ['dSB_klow','dSB_klow','dSB_rlow','dSB_rhigh']:
            getattr(self.u,sB).valueChanged.connect(calc_freeParameters)
        self.u.checkBox_4.toggled.connect(plotConditionChanged)
        self.u.cB_plotModel.toggled.connect(plotConditionChanged)
        self.u.pB_refresh.clicked.connect(plotConditionChanged)
        self.u.comboBox_3.currentIndexChanged.connect(change_plot_space)
        self.u.checkBox_2.clicked.connect(show_hide_tableview)
        self.u.pushButton.clicked.connect(read_chi_files)
        self.FEFF_dialog.pushButton.clicked.connect(close_dialog_f)
        self.GroupCheckBox.buttonClicked[QtWidgets.QAbstractButton].connect(pB_set_Enabled)
        self.GroupBox.buttonClicked[QtWidgets.QAbstractButton].connect(add_FEFF_path)
        self.exafs_cB.buttonClicked[QtWidgets.QAbstractButton].connect(change_rb)
        self.groupButton_RB.buttonClicked[QtWidgets.QAbstractButton].connect(change_rb)
        self.u.combo_fitParam.currentIndexChanged.connect(child_plot_paramResult)
        self.u.pushButton_4.clicked.connect(setOutputFile)
        self.u.pushButton_3.clicked.connect(self.DoAction)
        self.u.pB_openResult.clicked.connect(openFitResults)
        self.u.pB_setXaxis.clicked.connect(setXaxisFileName)
        self.multifit_dialog.pushButton.clicked.connect(close_multifit_dialog)
        self.u.cB_multifit.clicked.connect(use_multifit)
        self.multifit_dialog.pushButton_2.clicked.connect(openOutPutFile)
        self.multifit_dialog.pushButton_3.clicked.connect(self.DoAction)
        self.fit_dialog.pB_savecondtion.clicked.connect(execSaveConditions)
        self.fit_dialog.pB_reload.clicked.connect(reloadConditions)
        self.uiTableView.pushButton.clicked.connect(self.tableview.hide)
        self.wSignal.connect(plotConditionChanged)
        self.dialog.show()
        self.show()

    # def mousePressEvent(self.Table, event):
    #     if event.button() == QtCore.Qt.RightButton:
    #         print ("Hello")
    #         print (self.Table.underMouse())
    def SaveConditions(self, fname):
        Dict = {}
        Dict['S02'] = self.fit_dialog.doubleSpinBox.value()
        Dict['extra_param'] = self.fit_dialog.lE_params.text()
        print(self.GroupCheckBox.buttons())
        for cB in self.GroupCheckBox.buttons():
            if cB.isChecked():
                index_ = self.GroupCheckBox.buttons().index(cB)
                Dict['path' + str(index_ + 1)] = {}
                Dict['path' + str(index_ + 1)]['discription'] = self.Table.item(index_, 2).text()
                Dict['path' + str(index_ + 1)]['N'] = {'name': self.Table.item(index_, 3).text(),
                                                       'state': self.Table.cellWidget(index_, 4).currentText(),
                                                       'value': self.Table.item(index_, 5).text()}
                Dict['path' + str(index_ + 1)]['dE'] = {'name': self.Table.item(index_, 6).text(),
                                                        'state': self.Table.cellWidget(index_, 7).currentText(),
                                                        'value': self.Table.item(index_, 8).text()}
                Dict['path' + str(index_ + 1)]['dR'] = {'name': self.Table.item(index_, 9).text(),
                                                        'state': self.Table.cellWidget(index_, 10).currentText(),
                                                        'value': self.Table.item(index_, 11).text()}
                Dict['path' + str(index_ + 1)]['ss'] = {'name': self.Table.item(index_, 12).text(),
                                                        'state': self.Table.cellWidget(index_, 13).currentText(),
                                                        'value': self.Table.item(index_, 14).text()}
                Dict['path' + str(index_ + 1)]['C3'] = {'name': self.Table.item(index_, 15).text(),
                                                        'state': self.Table.cellWidget(index_, 16).currentText(),
                                                        'value': self.Table.item(index_, 17).text()}
                Dict['path' + str(index_ + 1)]['path_to_feff'] = params.FitConditions['FEFF file'][index_]

        Dict['dSB_klow'] = self.u.dSB_klow.value()
        Dict['dSB_khigh'] = self.u.dSB_khigh.value()
        Dict['dSB_rlow'] = self.u.dSB_rlow.value()
        Dict['dSB_rhigh'] = self.u.dSB_rhigh.value()
        Dict['plotSpace'] = self.groupButton_RB.checkedButton().text()
        Dict['fitSpace'] = self.u.comboBox_3.currentText()
        Dict['kweight'] = self.u.comboBox.currentText()
        Dict['window'] = self.u.comboBox_2.currentText()
        Dict['dB_window_k'] = self.u.dB_window_k.value()
        Dict['dB_window_r'] = self.u.dB_window_r.value()
        print(yaml.safe_dump(Dict, default_flow_style=False))
        f = open(fname, 'w')
        f.write(yaml.safe_dump(Dict, default_flow_style=False))
        f.close()

    def timerEvent(self,e):
        def setFigure(widget,str_xlabel,str_ylabel):
            grid = widget.layout()
            while grid.count() > 0:
                grid.removeItem(grid.itemAt(0))
            fig = Figure(figsize=(320, 320), dpi=72, facecolor=(1, 1, 1), edgecolor=(0, 0, 0))
            ax = fig.add_subplot(111)
            ax.set_xlabel(str_xlabel)
            ax.set_ylabel(str_ylabel)
            canvas = FigureCanvas(fig)
            navibar = NavigationToolbar(canvas, widget)
            grid.addWidget(canvas, 0, 0)
            grid.addWidget(navibar)
            return fig, ax, canvas

        def plot_paramResult(DF,currentText):
            print ("L903")
            self.fig2, self.ax2, self.canvas2 = setFigure(self.u.w_fitResult,'X',currentText)
            print ("L905")
            if self.u.tB_xaxis.toPlainText() != '':
                pass
            else:
                x_array = range(1,len(DF['data'].values)+1)
                #print DF[:,currentText].as_matrix
                if currentText =='R-factor':
                    self.ax2.plot(x_array,DF[currentText].values,label=currentText,marker='o',color='r',markersize=10)
                else:
                    if 'delta('+currentText+')' in DF.keys():
                        if currentText in self.params_for_dR:
                            self.ax2.set_ylabel('R_0+'+currentText)
                            self.ax2.errorbar(x_array,DF[currentText].values,yerr=DF['delta('+currentText+')'].values,label='R_0+'+currentText,marker='o',color='r',markersize=10)
                        else:
                            self.ax2.errorbar(x_array,DF[currentText].values,yerr=DF['delta('+currentText+')'].values,label=currentText,marker='o',color='r',markersize=10)
                    else:
                        paramLabel = currentText
                        if currentText in self.params_for_dR:
                            self.ax2.set_ylabel('R_0+'+currentText)
                            paramLabel = 'R_0+'+currentText
                        self.ax2.plot(x_array,DF[currentText].values,label=paramLabel,marker='o',color='r',markersize=10)
                self.ax2.legend(loc=1)
            #self.canvas2.draw()

        def openFitResults():
            # if self.u.tB_result.toPlainText() !='':
            #     self.u.tB_result.clear()
            # self.u.pB_setXaxis.setEnabled(False)
            # file, absPATH = dialog_for_OpenFile(params.dir,'open a result file', 'Result File(*.csv)')
            # self.u.tB_result.append(absPATH)
            print("L929")
            self.df_fit = pd.read_csv(self.u.tB_result.toPlainText(),delimiter=r"\s+")
            self.u.combo_fitParam.clear()
            self.u.tB_xaxis.clear()
            for term in self.df_fit.columns.values:
                if term == 'R-factor':
                    self.u.combo_fitParam.insertItem(0,term)
                elif re.search(r"(\+\/\-|delta\(.+\)|data)",term) == None:
                    self.u.combo_fitParam.addItem(term)
            if not self.u.pB_setXaxis.isEnabled():
                self.u.pB_setXaxis.setEnabled(True)
            # print self.df_fit.keys()
            # tableModel = ItemTableModel(self.df_fit['data'].values,self.df_fit.keys())
            model = QtGui.QStandardItemModel()
            horizontalLabels = []
            for term in self.df_fit.keys():
                horizontalLabels.append(term)
            horizontalLabels.remove('data')
            model.setHorizontalHeaderLabels(horizontalLabels)
            # KEYS = []
            # for term in self.df_fit.keys():
            #     KEYS.append(term)
            vertivalLabels = []
            for term in self.df_fit['data'].values:
                vertivalLabels.append(term)
            model.setVerticalHeaderLabels(vertivalLabels)
            # for i in range(0,len(self.df_fit['data'].values)):
            #     items = []
            #     for key in self.df_fit.keys():
            #         items.append(QtWidgets.QStandardItem(self.df_fit[key][i]))
            #     model.appendColumn(items)
            print("L960")
            for i in range(0, len(self.df_fit['data'].values)):
                for key in horizontalLabels:
                    if key == 'data':
                        pass
                    else:
                        model.setItem(i, horizontalLabels.index(key), QtGui.QStandardItem(str(self.df_fit[key][i])))
            self.uiTableView.tableView.setModel(model)
            # tableview = QtWidgets.QTableView()
            # tableview.setModel(tableModel)
            # self.layout_TableView.addWidget(tableview)
            plot_paramResult(self.df_fit,self.u.combo_fitParam.currentText())
            print("L972")

        if self.u.progressBar.value() < self.u.progressBar.maximum():
            if self.u.cB_multifit.isChecked():
                pass
            else:
                xafsdat = larch_builtins._group(self.mylarch)
                key = self.exafs_cB.buttons()[self.array_index[self.u.progressBar.value()]-1].text()
                xafsdat.k = params.d_chis[key][0][:]
                xafsdat.chi = params.d_chis[key][1][:]
                dset  = feffit_dataset(data=xafsdat, pathlist = self.pathlist, transform=self.FeffitTransform, _larch=self.mylarch)
                out = feffit(self.fitParams,dset,_larch=self.mylarch)
                line = feffit_report(out,_larch=self.mylarch)
                for term in self.extra_params:
                    if re.match("delta.*",term) != None:
                        pass
                    elif getattr(self.fitParams,term).vary == True:
                        # print ("####Extra Variable#####")
                        # print ("uvalue:" + str(getattr(self.fitParams,term).uvalue))
                        # print("stderr:" + str(getattr(self.fitParams, term).stderr))
                        t_array = str(getattr(self.fitParams,term).uvalue).split('+/-')
                        self.Reserver.loc[key,term] = t_array[0]
                        self.Reserver.loc[key,'delta('+term+')'] = t_array[1]
                    else:
                        self.Reserver.loc[key,term] = str(getattr(self.fitParams,term).value)
                for term in self.paramNames:
                    #print (term)
                    if re.match("delta.*",term) != None:
                        pass
                    # elif term in self.extra_params:
                    #     pass
                    elif term == self.paramNames[-2]:
                        self.Reserver.loc[key,term] = re.search("r\-factor\s+\=\s+(\d+\.\d+)",line).group(1)
                    elif term == self.paramNames[-1]:
                        self.Reserver.loc[key,term] = line
                    else:
                        if getattr(self.fitParams,term).vary == True:
                            if getattr(self.fitParams,term).uvalue is None:
                                if term in self.params_for_dR:
                                    for i in range(0,20):
                                        if term == self.Table.item(i,9).text():
                                            # print self.Table.item(i,9).text()
                                            print (self.Table.item(i,2).text())
                                            self.Reserver.loc[key,term] = getattr(self.fitParams,term).value + float(re.search("\w+\=(\d+\.\d+)",self.Table.item(i,2).text()).group(1))
                                            break
                                    self.Reserver.loc[key,'delta('+term+')'] = 0.000
                                    # self.Reserver.loc[key,term] = str(getattr(self.fitParams,term).value)
                                else:
                                    self.Reserver.loc[key,term] = getattr(self.fitParams,term).value
                                    self.Reserver.loc[key,'delta('+term+')'] = 0.000
                            # print term
                            # print str(getattr(self.fitParams,term).value)
                            # print str(getattr(self.fitParams,term).uvalue)
                            else:
                                if term in self.params_for_dR:
                                    t_array = str(getattr(self.fitParams,term).uvalue).split('+/-')
                                    self.Reserver.loc[key,term] = float(t_array[0])
                                    for i in range(0,20):
                                        if term == self.Table.item(i,9).text():
                                            # print self.Table.item(i,9).text()
                                            print (self.Table.item(i,2).text())
                                            self.Reserver.loc[key,term] = float(t_array[0]) + float(re.search("\w+\=(\d+\.\d+)",self.Table.item(i,2).text()).group(1))
                                            break
                                        else:
                                            pass
                                    self.Reserver.loc[key,'delta('+term+')'] = float(t_array[1])
                                else:
                                    t_array = str(getattr(self.fitParams,term).uvalue).split('+/-')
                                    self.Reserver.loc[key,term] = float(t_array[0])
                                    self.Reserver.loc[key,'delta('+term+')'] = float(t_array[1])
                        elif getattr(self.fitParams,term).vary == False:
                            if getattr(self.fitParams,term).expr != None:
                                str_eqn = getattr(self.fitParams,term).expr
                                for nval in self.extra_params:
                                    if not "delta" in nval:
                                        if getattr(self.fitParams,nval).uvalue is None:
                                            str_eqn = str_eqn.replace(nval,"self.fitParams."+nval+'.value')
                                        else:
                                            str_eqn = str_eqn.replace(nval, "self.fitParams." + nval + '.uvalue')
                                #i = 0
                                # str_eqn = getattr(self.fitParams,term).expr
                                # sign = 1
                                # while sign:
                                #     t_array = re.split('\+|\*|\/|\-|\(|\)',str_eqn)
                                #     for sub_term in t_array:
                                #         params_def_copy = self.params_def[:]
                                #         params_def_copy.remove(term)
                                #         re_express = r"(\+|\*|\/|\-|\(|\)|\s+)?"+"("+re.escape(sub_term.replace(" ",''))+")"+"(\+|\*|\/|\-|\(|\)|\s+)?"
                                #         if sub_term.replace(" ",'') in params_def_copy and re.search(re_express,str_eqn):
                                #             g0 = re.search(re_express,str_eqn).groups()[0]
                                #             g1 = re.search(re_express,str_eqn).groups()[1]
                                #             g2 = re.search(re_express,str_eqn).groups()[2]
                                #             r_stirng = ""
                                #             if g0 != None:
                                #                 r_stirng += g0
                                #             r_stirng += getattr(self.fitParams,g1).expr
                                #             if g2 != None:
                                #                 r_stirng += g2
                                #             str_eqn = re.sub(re_express,r_stirng,str_eqn)
                                #     t_array = re.split('\+|\*|\/|\-|\(|\)',str_eqn)
                                #     sign = 0
                                #     for sub_term in t_array:
                                #         if sub_term.replace(" ",'') in self.params_def:
                                #             sign = 1
                                #         else:
                                #             sign = 0
                                # t_array = re.split('\+|\*|\/|\-|\(|\)',str_eqn)
                                # for sub_term in t_array:
                                #     re_express = r"(\+|\*|\/|\-|\(|\)|\s+)?"+"("+re.escape(sub_term.replace(" ",''))+")"+"(\+|\*|\/|\-|\(|\)|\s+)?"
                                #     if sub_term.replace(" ",'') in self.params_guess[:]+self.params_set[:] and re.search(re_express,str_eqn):
                                #         g0 = re.search(re_express,str_eqn).groups()[0]
                                #         g1 = re.search(re_express,str_eqn).groups()[1]
                                #         g2 = re.search(re_express,str_eqn).groups()[2]
                                #         r_stirng = ""
                                #         if g0 != None:
                                #             r_stirng += g0
                                #         r_stirng += "self.fitParams."+g1+'.value'
                                #         if g2 != None:
                                #             r_stirng += g2
                                #         str_eqn = re.sub(re_express,r_stirng,str_eqn)

                                if term in self.params_for_dR:
                                    # t_array = str(getattr(self.fitParams,term).uvalue).split('+/-')
                                    # self.Reserver.loc[key,term] = t_array[0]
                                    for i in range(0,20):
                                        if term == self.Table.item(i,9).text():
                                            # eval(str_eqn)
                                            if '+/-' in str(eval(str_eqn)):
                                                self.Reserver.loc[key, term] = float(re.search("\w+\=(\d+\.\d+)", self.Table.item(i, 2).text()).group(1)) + \
                                                                                   float(str(eval(str_eqn)).split('+/-')[0])
                                                self.Reserver.loc[key, 'delta(' + term + ')'] = float(str(eval(str_eqn)).split('+/-')[1])
                                            else:
                                                self.Reserver.loc[key, term] = float(re.search("\w+\=(\d+\.\d+)", self.Table.item(i, 2).text()).group(1)) + \
                                                                                   float(str(eval(str_eqn)).split('+/-')[0])
                                                self.Reserver.loc[key, 'delta(' + term + ')'] = 0.000
                                            break
                                        else:
                                            pass
                                else:
                                    print (eval(str_eqn))
                                    self.Reserver.loc[key, term] = float(str(eval(str_eqn)).split('+/-')[0])
                                    self.Reserver.loc[key, 'delta(' + term + ')'] = float(str(eval(str_eqn)).split('+/-')[1])
                            else:
                                if term in self.params_for_dR:
                                    t_array = str(getattr(self.fitParams,term).uvalue).split('+/-')
                                    self.Reserver.loc[key,term] = float(t_array[0])
                                    for i in range(0,20):
                                        if term == self.Table.item(i,9).text():
                                            print (re.search("\w+\=(\d+\.\d+)",self.Table.item(i,2).text()).group(1))
                                            self.Reserver.loc[key,term] = float(re.search("\w+\=(\d+\.\d+)",self.Table.item(i,2).text()).group(1)) +\
                                                                              getattr(self.fitParams,term).value
                                            self.Reserver.loc[key, 'delta(' + term + ')'] = 0.000
                                            break
                                        else:
                                            pass
                                else:
                                    self.Reserver.loc[key,term] = getattr(self.fitParams,term).value
                                    self.Reserver.loc[key, 'delta(' + term + ')'] = 0.000
                logfile = open(self.path_to_log+re.search("\d+\:(.+)\.\w+$",key).group(1)+'.log','w')
                #if isinstance(line, unicode):
                #    logfile.write(line.encode('utf-8'))
                #else:
                #    logfile.write(line)
                logfile.write(line)
                #print type(line)
                logfile.close()
                self.u.progressBar.setValue(self.u.progressBar.value()+1)
                self.hdf5.create_group(key)
                self.hdf5.create_dataset('/'+key+':log',data=np.string_(line))
                self.hdf5.create_dataset('/'+key+'/chi_dat',data=np.array([dset.data.k,dset.data.chi]).T)
                self.hdf5.create_dataset('/'+key+'/chi_fit',data=np.array([dset.model.k,dset.model.chi]).T)
                self.hdf5.create_dataset('/'+key+'/chir_dat',data=np.array([dset.data.r,dset.data.chir_mag,dset.data.chir_im]).T)
                self.hdf5.create_dataset('/'+key+'/chir_fit',data=np.array([dset.model.r,dset.model.chir_mag,dset.model.chir_im]).T)
                if not self.u.checkBox_5.isChecked():
                    if self.fit_dialog.cB_use_anotherParams.isChecked() and self.fit_dialog.lE_params.text() != '':
                        tlist = self.fit_dialog.lE_params.text().split(';')
                        # txt = ''
                        # for term in string.split(';'):
                        #     txt += '(' + term +'),'
                        # or_dict = OrderedDict(eval('['+txt+']'))
                        for term in tlist:
                            t_array = term.split('=')
                            param_name = t_array[0].replace(" ", "").replace("'", "")
                            param_condition = t_array[1].replace(" ", "").replace('[', "").replace(']', "").replace('(',
                                                                                                                    "").replace(
                                ')', "").split(',')
                            if len(param_condition) == 3:
                                p_min = param_condition[2].split(':')[0]
                                p_max = param_condition[2].split(':')[1]
                                if p_min != '' and p_max != '':
                                    setattr(self.fitParams, param_name,
                                            larchfit.guess(float(param_condition[0]), min=float(p_min),
                                                           max=float(p_max)))
                                elif p_min != '' and p_max == '':
                                    setattr(self.fitParams, param_name, larchfit.guess(float(param_condition[0]),
                                                                                       min=float(p_min)))
                                elif p_min == '' and p_max != '':
                                    setattr(self.fitParams, param_name, larchfit.guess(float(param_condition[0]),
                                                                                       min=float(p_max)))
                                else:
                                    setattr(self.fitParams, param_name, larchfit.guess(float(param_condition[0])))
                                print (getattr(self.fitParams, param_name).value)
                                # self.extra_params.append(param_name)
                                # self.extra_params.append('delta(' + param_name + ')')
                            else:
                                if param_condition[1].replace("'", "") == 'guess' and len(param_condition) == 2:
                                    setattr(self.fitParams, param_name, larchfit.guess(float(param_condition[0])))
                                    print (getattr(self.fitParams, param_name).value)
                                    # self.extra_params.append(param_name)
                                    # self.extra_params.append('delta(' + param_name + ')')
                                elif param_condition[1].replace("'", "") == 'set':
                                    setattr(self.fitParams, param_name, larchfit.param(float(param_condition[0])))
                                    # self.extra_params.append(param_name)
                    for cB in self.GroupCheckBox.buttons():
                        if cB.isChecked():
                            index_ = self.GroupCheckBox.buttons().index(cB)
                            if self.fit_dialog.checkBox.isChecked():
                                self.fitParams.s0_2 = larchfit.guess(self.fit_dialog.doubleSpinBox.value())
                            Name_for_N = self.Table.item(index_,3).text()
                            #print Name_for_N
                            State_for_N = self.Table.cellWidget(index_,4)
                            #print State_for_N
                            Value_for_N = self.Table.item(index_,5).text()
                            #print Value_for_N
                            if State_for_N.currentText() == 'guess':
                                setattr(self.fitParams,Name_for_N,larchfit.guess(float(Value_for_N)))
                            elif State_for_N.currentText() == 'set':
                                setattr(self.fitParams,Name_for_N,larchfit.param(float(Value_for_N)))
                            elif State_for_N.currentText() == 'def':
                                setattr(self.fitParams,Name_for_N,larchfit.param(expr=Value_for_N))
                            Name_for_dE = self.Table.item(index_,6).text()
                            State_for_dE = self.Table.cellWidget(index_,7)
                            Value_for_dE = self.Table.item(index_,8).text()
                            if State_for_dE.currentText() == 'guess':
                                setattr(self.fitParams,Name_for_dE,larchfit.guess(float(Value_for_dE)))
                            elif State_for_dE.currentText() == 'set':
                                setattr(self.fitParams,Name_for_dE,larchfit.param(float(Value_for_dE)))
                            elif State_for_dE.currentText() == 'def':
                                setattr(self.fitParams,Name_for_dE,larchfit.param(expr=Value_for_dE))
                            Name_for_dR = self.Table.item(index_,9).text()
                            State_for_dR = self.Table.cellWidget(index_,10)
                            Value_for_dR = self.Table.item(index_,11).text()
                            if State_for_dR.currentText() == 'guess':
                                setattr(self.fitParams,Name_for_dR,larchfit.guess(float(Value_for_dR)))
                            elif State_for_dR.currentText() == 'set':
                                setattr(self.fitParams,Name_for_dR,larchfit.param(float(Value_for_dR)))
                            elif State_for_dR.currentText() == 'def':
                                setattr(self.fitParams,Name_for_dR,larchfit.param(expr=Value_for_dR))
                            Name_for_ss = self.Table.item(index_,12).text()
                            State_for_ss = self.Table.cellWidget(index_,13)
                            Value_for_ss = self.Table.item(index_,14).text()
                            if State_for_ss.currentText() == 'guess':
                                setattr(self.fitParams,Name_for_ss,larchfit.guess(float(Value_for_ss)))
                            elif State_for_ss.currentText() == 'set':
                                setattr(self.fitParams,Name_for_ss,larchfit.param(float(Value_for_ss)))
                            elif State_for_ss.currentText() == 'def':
                                setattr(self.fitParams,Name_for_ss,larchfit.param(expr=Value_for_ss))
                            Name_for_C3 = self.Table.item(index_, 15).text()
                            State_for_C3 = self.Table.cellWidget(index_, 16)
                            Value_for_C3 = self.Table.item(index_, 17).text()
                            if State_for_C3.currentText() == 'guess':
                                setattr(self.fitParams, Name_for_C3, larchfit.guess(float(Value_for_C3)))
                            elif State_for_C3.currentText() == 'set':
                                setattr(self.fitParams, Name_for_C3, larchfit.param(float(Value_for_C3)))
                            elif State_for_C3.currentText() == 'def':
                                setattr(self.fitParams, Name_for_C3, larchfit.param(expr=Value_for_C3))
                else:
                    pass
        else:
            self.timer.stop()
            #print ('Timer stopped')
            self.hdf5.close()
            #print ('HDF5 was closed')
            #self.u.tabWidget.setCurrentIndex(1)
            n_columns = []
            # for key in self.Reserver.columns[:-2]:
            #     n_columns.append(key+' +/- delta('+key+')')
            # n_columns.append(self.Reserver.columns[-2])
            self.Reserver.loc[:,self.paramNames[:-1]+self.extra_params[:]].to_csv(path_or_buf=self.u.textBrowser.toPlainText(),
                                                                                  header=self.paramNames[:-1]+self.extra_params[:], index_label = 'data',sep=' ')
            file = fileinput.FileInput(self.u.textBrowser.toPlainText(), inplace=True, backup='.bak')
            for line in file:
                print(line.rstrip().replace('"', ''))
            file.close()
            #print ("L1264")
            if len(params.results_rb.buttons()) != 0:
                for button in params.results_rb.buttons():
                    self.layout2.removeWidget(button)
            rB = QtWidgets.QRadioButton(os.path.basename(self.u.textBrowser.toPlainText()).replace(self.ext,''))
            rB.setObjectName(self.path_to_log+'result_'+os.path.basename(self.u.textBrowser.toPlainText()).replace(self.ext,'.h5'))
            if len(params.results_rb.buttons()) == 0:
                params.results_rb.addButton(rB)
            else:
                sign = 1
                for button in params.results_rb.buttons():
                    if button.text() == rB.text():
                        sign = 0
                if sign:
                    params.results_rb.addButton(rB)
            for button in params.results_rb.buttons():
                self.layout2.addWidget(button)
            #print ("L1281")
            params.results_rb.buttons()[0].toggle()
            self.u.pushButton_3.setText('Fit')
            self.u.pushButton_3.setEnabled(False)
            self.u.tB_result.clear()
            self.u.tB_result.append(self.u.textBrowser.toPlainText())
            #print ("L1287")
            openFitResults()
            self.u.textBrowser.clear()
            self.u.tabWidget.setCurrentIndex(1)


    def DoAction(self):
        if  self.timer.isActive():
            self.timer.stop()
            self.u.pushButton_3.setText('Fit')
            self.u.pushButton_3.setEnabled(False)
            self.u.textBrowser.clear()
        else:
            if self.u.cB_multifit.isChecked():
                self.index_condition = {}
                for i in range(0,10):
                    if self.multifit_dialog.tableWidget.cellWidget(1,i).isChecked():
                        text = self.multifit_dialog.tableWidget.item(0,i).text()
                        if re.search('ALL',text):
                            self.index_condition['Condition'+str(i+1)] = range(1,len(self.exafs_cB.buttons())+1)
                        elif text == re.match(r"(\d+\-?\d*\,?\s*)+",text).group(0):
                            array = text.split(',')
                            self.index_condition['Condition'+str(i)] = []
                            for term in array:
                                if re.search('\d+\-\d+',term):
                                    t_array = term.split('-')
                                    self.index_condition['Condition'+str(i)] += range(int(t_array[0]),int(t_array[1])+1)[:]
                                else:
                                    self.index_condition['Condition'+str(i)].append(int(term))
                print (self.index_condition)
            else:
                self.u.progressBar.setValue(0)
                self.array_index = []
                self.extra_params = []
                self.fitParams = larch_builtins._group(self.mylarch)
                self.fitParams.s0_2 = larchfit.param(self.fit_dialog.doubleSpinBox.value())
                if self.fit_dialog.checkBox.isChecked():
                    self.fitParams.s0_2 = larchfit.guess(self.fit_dialog.doubleSpinBox.value())
                if self.fit_dialog.cB_use_anotherParams.isChecked() and self.fit_dialog.lE_params.text() != '':
                    tlist = self.fit_dialog.lE_params.text().split(';')
                    # txt = ''
                    # for term in string.split(';'):
                    #     txt += '(' + term +'),'
                    # or_dict = OrderedDict(eval('['+txt+']'))
                    for term in tlist:
                        t_array = term.split('=')
                        param_name = t_array[0].replace(" ","")
                        param_condition = t_array[1][1:-1].replace(" ","").replace('(',"").replace(')',"").split(',')
                        print(param_condition)
                        print (param_condition)
                        if len(param_condition) == 3:
                            p_min = param_condition[2].split(':')[0]
                            p_max = param_condition[2].split(':')[1]
                            if p_min !='' and p_max !='':
                                setattr(self.fitParams, param_name, larchfit.guess(float(param_condition[0]),min=float(p_min),max=float(p_max)))
                            elif p_min !='' and p_max =='':
                                setattr(self.fitParams, param_name, larchfit.guess(float(param_condition[0]),
                                        min=float(p_min)))
                            elif p_min =='' and p_max !='':
                                setattr(self.fitParams, param_name, larchfit.guess(float(param_condition[0]),
                                        min=float(p_max)))
                            else:
                                setattr(self.fitParams, param_name, larchfit.guess(float(param_condition[0])))
                            print (getattr(self.fitParams, param_name).value)
                            self.extra_params.append(param_name)
                            self.extra_params.append('delta(' + param_name + ')')
                        else:
                            if param_condition[1].replace("'","") == 'guess' and len(param_condition) == 2:
                                setattr(self.fitParams,param_name,larchfit.guess(float(param_condition[0])))
                                print (getattr(self.fitParams,param_name).value)
                                self.extra_params.append(param_name)
                                self.extra_params.append('delta('+param_name+')')
                            elif param_condition[1].replace("'","") == 'set':
                                setattr(self.fitParams,param_name,larchfit.param(float(param_condition[0])))
                                self.extra_params.append(param_name)
                                self.extra_params.append('delta(' + param_name + ')')
                print (self.extra_params)
                self.pathlist = []
                self.paramNames = []
                self.params_for_N = []
                self.params_for_dE = []
                self.params_for_dR = []
                self.params_for_ss = []
                self.params_for_C3 = []
                for cB in self.GroupCheckBox.buttons():
                    if cB.isChecked():
                        index_ = self.GroupCheckBox.buttons().index(cB)
                        feffinp = params.FitConditions['FEFF file'][index_]
                        path = feffpath(feffinp,_larch=self.mylarch)
                        #s02 = Name_for_N+'*'+'s0_2', e0 = Name_for_dE,sigma2 = Name_for_ss, deltar  = Name_for_dR,
                        Name_for_N = self.Table.item(index_,3).text()
                        self.params_for_N.append(Name_for_N)
                        #print Name_for_N
                        State_for_N = self.Table.cellWidget(index_,4)
                        #print State_for_N
                        Value_for_N = self.Table.item(index_,5).text()
                        # self.paramNames += [Name_for_N, 'delta(' + Name_for_N + ')']
                        #print Value_for_N
                        if State_for_N.currentText() == 'guess':
                            setattr(self.fitParams,Name_for_N,larchfit.guess(float(Value_for_N)))
                            self.paramNames +=[Name_for_N,'delta('+Name_for_N+')']
                        elif State_for_N.currentText() == 'set':
                            setattr(self.fitParams,Name_for_N,larchfit.param(float(Value_for_N)))
                            self.paramNames +=[Name_for_N,'delta('+Name_for_N+')']
                        elif State_for_N.currentText() == 'def':
                            setattr(self.fitParams,Name_for_N,larchfit.param(expr=Value_for_N))
                            self.paramNames +=[Name_for_N,'delta('+Name_for_N+')']
                        setattr(self.fitParams,'degen_path_'+str(index_),path.degen)
                        #setattr(self.fitParams,'net_'+Name_for_N,larchfit.param(expr=Value_for_N+'*'+str(self.fit_dialog.doubleSpinBox.value())))
                        Name_for_dE = self.Table.item(index_,6).text()
                        self.params_for_dE.append(Name_for_dE)
                        State_for_dE = self.Table.cellWidget(index_,7)
                        Value_for_dE = self.Table.item(index_,8).text()
                        if State_for_dE.currentText() == 'guess':
                            setattr(self.fitParams,Name_for_dE,larchfit.guess(float(Value_for_dE)))
                            self.paramNames +=[Name_for_dE,'delta('+Name_for_dE+')']
                        elif State_for_dE.currentText() == 'set':
                            setattr(self.fitParams,Name_for_dE,larchfit.param(float(Value_for_dE)))
                            self.paramNames +=[Name_for_dE,'delta('+Name_for_dE+')']
                        elif State_for_dE.currentText() == 'def':
                            setattr(self.fitParams,Name_for_dE,larchfit.param(expr=Value_for_dE))
                            self.paramNames +=[Name_for_dE,'delta('+Name_for_dE+')']
                        Name_for_dR = self.Table.item(index_,9).text()
                        self.params_for_dR.append(Name_for_dR)
                        State_for_dR = self.Table.cellWidget(index_,10)
                        Value_for_dR = self.Table.item(index_,11).text()
                        if State_for_dR.currentText() == 'guess':
                            setattr(self.fitParams,Name_for_dR,larchfit.guess(float(Value_for_dR)))
                            self.paramNames +=[Name_for_dR,'delta('+Name_for_dR+')']
                        elif State_for_dR.currentText() == 'set':
                            setattr(self.fitParams,Name_for_dR,larchfit.param(float(Value_for_dR)))
                            self.paramNames +=[Name_for_dR,'delta('+Name_for_dR+')']
                        elif State_for_dR.currentText() == 'def':
                            setattr(self.fitParams,Name_for_dR,larchfit.param(expr=Value_for_dR))
                            self.paramNames +=[Name_for_dR,'delta('+Name_for_dR+')']
                        Name_for_ss = self.Table.item(index_,12).text()
                        self.params_for_ss.append(Name_for_ss)
                        State_for_ss = self.Table.cellWidget(index_,13)
                        Value_for_ss = self.Table.item(index_,14).text()
                        if State_for_ss.currentText() == 'guess':
                            setattr(self.fitParams,Name_for_ss,larchfit.guess(float(Value_for_ss)))
                            self.paramNames +=[Name_for_ss,'delta('+Name_for_ss+')']
                        elif State_for_ss.currentText() == 'set':
                            setattr(self.fitParams,Name_for_ss,larchfit.param(float(Value_for_ss)))
                            self.paramNames +=[Name_for_ss,'delta('+Name_for_ss+')']
                        elif State_for_ss.currentText() == 'def':
                            setattr(self.fitParams,Name_for_ss,larchfit.param(expr=Value_for_ss))
                            self.paramNames +=[Name_for_ss,'delta('+Name_for_ss+')']
                        Name_for_C3 = self.Table.item(index_, 15).text()
                        self.params_for_C3.append(Name_for_C3)
                        State_for_C3 = self.Table.cellWidget(index_, 16)
                        Value_for_C3 = self.Table.item(index_, 17).text()
                        if State_for_C3.currentText() == 'guess':
                            setattr(self.fitParams, Name_for_C3, larchfit.guess(float(Value_for_C3)))
                            self.paramNames += [Name_for_C3, 'delta(' + Name_for_C3 + ')']
                        elif State_for_C3.currentText() == 'set':
                            setattr(self.fitParams, Name_for_C3, larchfit.param(float(Value_for_C3)))
                            self.paramNames += [Name_for_C3, 'delta(' + Name_for_C3 + ')']
                        elif State_for_C3.currentText() == 'def':
                            setattr(self.fitParams, Name_for_C3, larchfit.param(expr=Value_for_C3))
                            self.paramNames += [Name_for_C3, 'delta(' + Name_for_C3 + ')']
                        path.s02 = Name_for_N+'*'+'s0_2'+'/'+'degen_path_'+str(index_)
                        path.e0 = Name_for_dE
                        path.sigma2 = Name_for_ss
                        path.deltar  = Name_for_dR
                        path.third = Name_for_C3
                        if self.fit_dialog.cB_use_anotherParams.isChecked():
                            condition_dict = {Name_for_N: 'path.s02', Name_for_dE: 'path.e0',
                                         Name_for_dR: 'path.deltar', Name_for_ss:'path.sigma2',Name_for_C3:'path.third'}
                            for term in condition_dict.keys():
                                if getattr(self.fitParams,term).expr != None:
                                    for extParam in self.extra_params:
                                        if extParam in getattr(self.fitParams,term).expr:
                                            if term == Name_for_N:
                                                 path.s02 = '('+getattr(self.fitParams,term).expr+')'+'*'+'s0_2'+'/'+'degen_path_'+str(index_)
                                            elif term == Name_for_dE:
                                                path.e0 = getattr(self.fitParams,term).expr
                                            elif term == Name_for_dR:
                                                path.deltar = getattr(self.fitParams,term).expr
                                            elif term == Name_for_ss:
                                                path.sigma2 = getattr(self.fitParams,term).expr
                                            elif term == Name_for_C3:
                                                path.third = getattr(self.fitParams, term).expr
                        self.pathlist.append(path)
                if self.fit_dialog.checkBox.isChecked():
                    self.paramNames.insert(0,'s0_2')
                    self.paramNames.insert(1,'delta(s0_2)')
                self.paramNames += ['R-factor','log']
                self.Reserver = pd.DataFrame(columns=self.paramNames+self.extra_params)
                array_index = []
                if re.search('ALL',self.u.lineEdit.text()):
                    array_index = range(1,len(self.exafs_cB.buttons())+1)
                elif self.u.lineEdit.text() == re.match(r"(\d+\-?\d*\,?\s*)+",self.u.lineEdit.text()).group(0):
                    array = self.u.lineEdit.text().split(',')
                    for term in array:
                        if re.search('\d+\-\d+',term):
                            t_array = term.split('-')
                            array_index += range(int(t_array[0]),int(t_array[1])+1)[:]
                        else:
                            array_index.append(int(term))
                self.array_index = list(set(array_index))
                print (self.array_index)
                self.u.progressBar.setRange(0,len(self.array_index))
                self.FeffitTransform = feffit_transform(fitspace=self.u.comboBox_3.currentText(),
                                                        kmin=self.u.dSB_klow.value(),
                                                        kmax=self.u.dSB_khigh.value(),
                                                        kw= float(self.u.comboBox.currentText()),
                                                        dk=self.u.dB_window_k.value(),
                                                        window=self.u.comboBox_2.currentText(),
                                                        rmin=self.u.dSB_rlow.value(),
                                                        rmax=self.u.dSB_rhigh.value(),
                                                        _larch=self.mylarch,
                                                        dr=self.u.dB_window_r.value())
                self.ext =  re.search("\.\w+$",self.u.textBrowser.toPlainText()).group(0)
                if not os.path.isdir(os.path.dirname(self.u.textBrowser.toPlainText())+'/Log'):
                    os.mkdir(os.path.dirname(self.u.textBrowser.toPlainText())+'/Log')
                self.path_to_log = os.path.dirname(self.u.textBrowser.toPlainText())+'/Log/'
                if os.path.isfile(self.path_to_log+'result_'+os.path.basename(self.u.textBrowser.toPlainText()).replace(self.ext,'.h5')):
                    os.rename(self.path_to_log+'result_'+os.path.basename(self.u.textBrowser.toPlainText()).replace(self.ext,'.h5'),self.path_to_log+'result_'+os.path.basename(self.u.textBrowser.toPlainText()).replace(self.ext,'.h5~'))
                self.hdf5 = h5py.File(self.path_to_log+'result_'+os.path.basename(self.u.textBrowser.toPlainText()).replace(self.ext,'.h5'),'w')
                self.SaveConditions(self.path_to_log+os.path.basename(self.u.textBrowser.toPlainText()).replace(self.ext,'.yaml'))
                self.params_guess=[]
                self.params_set=[]
                self.params_def =[]
                # self.params_for_N = []
                # self.params_for_dE = []
                # self.params_for_dR = []
                # self.params_for_ss = []
                for term in self.params_for_N[:]+self.params_for_dE[:]+self.params_for_dR[:]+self.params_for_ss[:]+self.extra_params[:]:
                    #print (term)
                    if re.match("delta.*",term) != None:
                        pass
                    elif getattr(self.fitParams,term).expr == None:
                        if getattr(self.fitParams,term).vary == True:
                            self.params_guess.append(term)
                        else:
                            self.params_set.append(term)
                    else:
                        self.params_def.append(term)
                self.timer.start(1,self)
                self.u.pushButton_3.setText('Stop')
                self.u.tabWidget.setCurrentIndex(1)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    wid = MainWindow()
    sys.exit(app.exec_())
