#!/usr/bin/env python

'''
Lake desmearing GUI using PySide (or PyQt4) and Matplotlib
'''


import os, sys
import threading

try:
    from PySide.QtCore import *  #@UnusedWildImport
    from PySide.QtGui import *   #@UnusedWildImport
    pyqtSignal = Signal
except:
    from PyQt4.QtCore import *  #@UnusedWildImport
    from PyQt4.QtGui import *   #@UnusedWildImport
    pyqtSignal = pyqtSignal

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '..') ))
from jldesmear.api.desmear import Weighting_Methods
from jldesmear.api.extrapolation import discover_extrapolation_functions


class FileEntryBox(QGroupBox):
    '''FileEntryBox = QGroupBox[QLineEdit + QPushButton]'''

    def __init__(self, parent=None, title='selected file', callback=None, tip='select a file'):
        '''
        :param obj callback:  method to call if a name is selected
        '''
        super(FileEntryBox, self).__init__(parent)
        self.parent = parent
        self.callback = callback
        self.setTitle(title)
        
        self.entry = QLineEdit('')
        self.entry.setToolTip('full path of selected file')
        b_icon = QPushButton('&Open ...')
        b_icon.clicked[bool].connect(self.onOpenFile)
        style = b_icon.style()
        icon = style.standardIcon(QStyle.SP_FileIcon)
        b_icon.setIcon(icon)
        b_icon.setToolTip(tip)

        layout = QHBoxLayout()
        layout.addWidget(self.entry)
        layout.addWidget(b_icon)
        layout.setStretch(0, 1)
        layout.setStretch(1, 0)
        self.setLayout(layout)

    def onOpenFile(self, **kw):
        '''Choose a text file with 3-column smeared SAS data'''
        filters = ';;'.join([
                             'smeared SAS (*.smr)',
                             'any file (*.* *)',
                             ])
        fileName = QFileDialog().getOpenFileName(self, filter=filters)[0]
        if len(fileName) > 0:
            self.entry.setText(fileName)
            if self.callback is not None:
                self.callback(fileName)
        return fileName


class MainFrame(QFrame):

    def __init__(self, parent=None):
        super(MainFrame, self).__init__(parent)
        self.parent = parent

        self.fileentry = FileEntryBox(self, 
            title='Input (smeared) data file', 
            tip='select a smeared SAS data file to be desmeared',
            callback=self.openFileCallback)
        panel = self.create_Big_Panel(self)

        layout = QVBoxLayout()
        layout.addWidget(self.fileentry)
        layout.addWidget(panel)
        layout.setStretch(0, 0)
        layout.setStretch(1, 1)
        self.setLayout(layout)
    
    def create_Big_Panel(self, parent):
        '''contains parameter entries and plots'''
        fr = QFrame(parent)
        
        parms = self.create_Parms_Panel(fr)
        parms.setFrameStyle(QFrame.StyledPanel)
        plots = self.create_Plots_Panel(fr)
        plots.setFrameStyle(QFrame.StyledPanel)

        splitter = QSplitter(fr)
        splitter.setOrientation(Qt.Horizontal)
        splitter.addWidget(parms)
        splitter.addWidget(plots)

        layout = QVBoxLayout()
        layout.addWidget(splitter)
        fr.setLayout(layout)
        
        return fr
    
    def create_Parms_Panel(self, parent):
        '''contains parameter entries and controls'''
        fr = QFrame(parent)
        
        layout = QVBoxLayout()
        fr.setLayout(layout)

        adjustables = self.create_Adjustables_Panel(fr)
        controls = self.create_Controls_Panel(fr)
        console = self.create_Console_Panel(fr)

        layout.addWidget(adjustables)
        layout.addWidget(controls)
        layout.addWidget(console)
        
        return fr
    
    def create_Adjustables_Panel(self, parent):
        '''contains adjustable parameters'''
        box = QGroupBox('Adjustable parameters', parent)

        layout = QGridLayout()
        box.setLayout(layout)
        
        row = 0
        tip = 'desmearing slit length, l_o'
        self.slitlength = QLineEdit()
        self.slitlength.setToolTip(tip)
        layout.addWidget(QLabel('l_o'), row, 0)
        layout.addWidget(self.slitlength, row, 1)

        # TODO: need setter/getter methods
        row += 1
        tip = 'functional form of extrapolation for desmearing'
        functions = discover_extrapolation_functions()
        self.extrapolation = QComboBox()
        self.extrapolation.insertItems(999, sorted(functions.keys()))
        self.extrapolation.setToolTip(tip)
        layout.addWidget(QLabel('extrap'), row, 0)
        layout.addWidget(self.extrapolation, row, 1)

        row += 1
        tip = 'evaluate extrapolation constants based on data for q > q_F'
        self.qFinal = QLineEdit()
        self.qFinal.setToolTip(tip)
        layout.addWidget(QLabel('q_F'), row, 0)
        layout.addWidget(self.qFinal, row, 1)

        # TODO: need setter/getter methods
        row += 1
        tip = 'functional form of desmearing feedback, always use "fast"'
        self.feedback = QComboBox()
        self.feedback.insertItems(999, sorted(Weighting_Methods.keys()))
        self.feedback.setCurrentIndex(2)
        self.feedback.setToolTip(tip)
        layout.addWidget(QLabel('feedback'), row, 0)
        layout.addWidget(self.feedback, row, 1)

        row += 1
        tip = 'specifies number of desmearing iterations, N_i'
        self.num_iterations = QSpinBox()
        self.num_iterations.setRange(2, 1000)
        self.num_iterations.setToolTip(tip)
        layout.addWidget(QLabel('N_i'), row, 0)
        layout.addWidget(self.num_iterations, row, 1)
        
        return box

    def create_Controls_Panel(self, parent):
        '''contains controls'''
        def squareWidget(w):
            w.setMinimumWidth(w.sizeHint().height())
        box = QGroupBox('Desmearing controls', parent)

        layout = QHBoxLayout()
        box.setLayout(layout)
        
        tip = 'desmear N iterations'
        b_do_N = QPushButton('N')
        b_do_N.setToolTip(tip)
        layout.addWidget(b_do_N)
        squareWidget(b_do_N)
        
        tip = 'desmear one iteration'
        b_do_once = QPushButton('1')
        b_do_once.setToolTip(tip)
        layout.addWidget(b_do_once)
        squareWidget(b_do_once)
        
        layout.addStretch(50)
        
        tip = 're(start) by clearing all results and reloading data'
        b_restart = QPushButton('!')
        b_restart.setToolTip(tip)
        layout.addWidget(b_restart)
        squareWidget(b_restart)

        return box
    
    def create_Console_Panel(self, parent):
        '''contains console output'''
        fr = QGroupBox('Console', parent)

        layout = QHBoxLayout()
        fr.setLayout(layout)
        
        # TODO: multiline text view
        
        return fr
    
    def create_Plots_Panel(self, parent):
        '''contains plots'''
        fr = QFrame(parent)

        layout = QHBoxLayout()
        fr.setLayout(layout)
        
        data_plots = self.create_Data_Plots_Panel(fr)
        self.chisqr_plot = self.create_ChiSqr_Plot_Panel(fr)

        splitter = QSplitter(fr)
        splitter.setOrientation(Qt.Horizontal)
        splitter.addWidget(data_plots)
        splitter.addWidget(self.chisqr_plot) 
        layout.addWidget(splitter)
        
        return fr
    
    def create_Data_Plots_Panel(self, parent):
        '''contains I(Q) and z(Q) plots'''
        fr = QFrame(parent)

        layout = QVBoxLayout()
        fr.setLayout(layout)
        
        self.sas_plot = self.create_Sas_Plot_Panel(fr)
        self.z_plot = self.create_Residuals_Plot_Panel(fr)

        splitter = QSplitter(fr)
        splitter.setOrientation(Qt.Vertical)
        splitter.addWidget(self.sas_plot)
        splitter.addWidget(self.z_plot) 
        layout.addWidget(splitter)
        
        return fr
    
    def create_Sas_Plot_Panel(self, parent):
        '''contains I(Q) plot'''
        fr = QGroupBox('~I(Q) and I(Q)', parent)

        layout = QHBoxLayout()
        fr.setLayout(layout)
        
        # TODO: ~I(Q) & I(Q)
        
        return fr
    
    def create_Residuals_Plot_Panel(self, parent):
        '''contains z(Q) plot'''
        fr = QGroupBox('z(Q)', parent)

        layout = QHBoxLayout()
        fr.setLayout(layout)
        
        # TODO: z(Q)
        
        return fr
    
    def create_ChiSqr_Plot_Panel(self, parent):
        '''contains ChiSqr vs. iteration plot'''
        fr = QGroupBox('ChiSqr vs. iteration', parent)

        layout = QHBoxLayout()
        fr.setLayout(layout)
        
        # TODO: ChiSqr v. iteration
        
        return fr
    
    def setStatus(self, msg):
        self.parent.setStatus(msg)

    def onOpenFile(self):
        '''Choose a text file with 3-column smeared SAS data'''
        self.fileentry.onOpenFile()
    
    def openFileCallback(self, fileName):
        self.setStatus('selected file: ' + fileName)
        self.loadFile(fileName)
        self.dirty = False

    def loadFile(self, filename):
        '''Open a file with 3-column smeared SAS data'''
        if os.path.exists(filename):
            self.setStatus('did not open file: ' + filename)


class JLdesmearGui(QMainWindow):

    def __init__(self, parent=None):
        super(JLdesmearGui, self).__init__(parent)
        self.parent = parent
        
        self.dirty = False

        self.fr = MainFrame(self)
        #self.setGeometry(75, 50, 500, 300)
        self.setCentralWidget(self.fr)
        
        self.createActions()
        self.createMenus()
        self.setStatus()

    def closeEvent(self, *args):
        '''received a request to close application, shall we allow it?'''
        if self.dirty:
            pass
        else:
            self.close()

    def createActions(self):
        '''define the actions for the GUI'''
        # TODO: needs Edit menu actions
        # TODO: needs Help menu actions
        
        self.action_open = QAction(self.tr('&Open'), None)
        self.action_open.setShortcut(QKeySequence.Open)
        self.action_open.setStatusTip(self.tr('Open a file with motor PVs'))
        self.action_open.triggered.connect(self.fr.onOpenFile)
        
        self.action_exit = QAction(self.tr('E&xit'), None)
        self.action_exit.setShortcut(QKeySequence.Quit)
        self.action_exit.setStatusTip(self.tr('Exit the application'))
        self.action_exit.triggered.connect(self.closeEvent)
        
    def createMenus(self):
        '''define the menus for the GUI'''
        fileMenu = self.menuBar().addMenu(self.tr('&File'))
        fileMenu.addAction(self.action_open)
        fileMenu.addSeparator()
        fileMenu.addAction(self.action_exit)
        
        # TODO: needs Edit menu
        
        helpMenu = self.menuBar().addMenu(self.tr('Help'))
        helpMenu.addSeparator()
        #helpMenu.addAction(self.about_dialog)

    def setStatus(self, message = 'Ready'):
        '''setup the status bar for the GUI or set a new status message'''
        self.statusBar().showMessage(self.tr(message))


class IterativeDesmear(threading.Thread):
    ''' 
    Run ``n`` iterations of the desmearing operation in a separate thread.
    Running in a separate thread with callbacks allows the 
    GUI widgets to be updated after each iteration.
        
    :param obj dsm: Desmearing object
    :param int n: number of iterations to perform
    
    Start this thread with code such as this example::
    
        IterativeDesmear(self.obj_dsm, self.NumItr).start()

    '''
    
    def __init__(self, dsm, n):
        threading.Thread.__init__(self)
        self.dsm = dsm
        self.n = n

    def run(self):
        for _ in range(self.n):
            self.dsm.iterate_and_callback()


def main():
    app = QApplication(sys.argv)
    myapp = JLdesmearGui()
    myapp.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################
