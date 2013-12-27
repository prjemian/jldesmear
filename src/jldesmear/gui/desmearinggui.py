#!/usr/bin/env python

'''
Lake desmearing GUI using PySide (or PyQt4) and Matplotlib
'''


import os, sys
import threading
import jldesmear
from jldesmear.api import toolbox
import matplotlib
matplotlib.use('Qt4Agg')

try:
    from PySide.QtCore import *  #@UnusedWildImport
    from PySide.QtGui import *   #@UnusedWildImport
    pyqtSignal = Signal
    matplotlib.rcParams['backend.qt4'] = "PySide"
except:
    from PyQt4.QtCore import *  #@UnusedWildImport
    from PyQt4.QtGui import *   #@UnusedWildImport
    pyqtSignal = pyqtSignal
    matplotlib.rcParams['backend.qt4'] = "PyQt4"

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '..') ))
from jldesmear.api.desmear import Weighting_Methods, Desmearing
from jldesmear.api.extrapolation import discover_extrapolation_functions
from jldesmear.api.info import Info


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
        '''Choose file for input'''
        filters = ';;'.join([
                             'Input parameters (*.inp)',
                             'cansas1d:1.1 (*.xml)',
                             'HDF5/NeXus ( *.hdf *.hdf5 *.h5 *.nx *.nxs)',
                             'smeared SAS (*.smr)',
                             'any file (*.* *)',
                             ])
        fileName, filefilter = QFileDialog().getOpenFileName(self, filter=filters)
        if len(fileName) > 0:
            self.entry.setText(fileName)
            if self.callback is not None:
                self.callback(fileName, filefilter)
        return fileName


class JLdesmearGui(QMainWindow):

    def __init__(self, parent=None):
        super(JLdesmearGui, self).__init__(parent)
        self.parent = parent
        self.setWindowTitle(jldesmear.__project__ + ' GUI')
        
        self.dirty = False
        self.dsm = None
        self.console = None

        self.mf = self._init_Main_Frame(self)
        #self.setGeometry(75, 50, 500, 300)
        self.setCentralWidget(self.mf)
        
        self._init_actions()
        self._init_menus()
        self.setStatus()
        
        self._init_Developer()
    
    def _init_Developer(self):
        def get_buf_item(key, item=0):
            return buf[key].split()[item]
        ext = '.inp'
        fn = toolbox.GetTest1DataFilename(ext)
        if not fn.endswith(ext): return
        
        # read a .inp file
        '''
        test1.smr
        test1.dsm
        0.08
        linear
        0.08
        20
        fast
        '''
        owd = os.getcwd()
        self.fileentry.entry.setText(fn)
        buf = open(os.path.abspath(fn), 'r').readlines()
        path = os.path.dirname(fn)
        os.chdir(path)
        
        self.setInputDataFile(os.path.abspath(os.path.join(path, get_buf_item(0))))
        self.setOutputDataFile(os.path.abspath(os.path.join(path, get_buf_item(1))))
        self.setSlitLength(get_buf_item(2))
        self.setExtrapolationMethod(get_buf_item(3))
        self.setQFinal(get_buf_item(4))
        self.setNumIterations(get_buf_item(5))
        self.setFeedbackMethod(get_buf_item(6))
        
        os.chdir(owd)
        

    def closeEvent(self, *args):
        '''received a request to close application, shall we allow it?'''
        if self.dirty:
            pass
        else:
            self.close()

    def _init_actions(self):
        '''define the actions for the GUI'''
        # TODO: needs Edit menu actions
        # TODO: needs Help menu actions
        
        self.action_open = QAction(self.tr('&Open'), None)
        self.action_open.setShortcut(QKeySequence.Open)
        self.action_open.setStatusTip(self.tr('Open a file'))
        self.action_open.triggered.connect(self.onOpenFile)
        
        self.action_exit = QAction(self.tr('E&xit'), None)
        self.action_exit.setShortcut(QKeySequence.Quit)
        self.action_exit.setStatusTip(self.tr('Exit the application'))
        self.action_exit.triggered.connect(self.closeEvent)
        
        self.b_do_N.clicked.connect(self.do_N_iterations)
        self.b_do_once.clicked.connect(self.do_1_iteration)
        self.b_restart.clicked.connect(self.init_session)
        self.b_clear_console.clicked.connect(self.do_Clear_Console)
        
        # TODO: save results
        
    def _init_menus(self):
        '''define the menus for the GUI'''
        fileMenu = self.menuBar().addMenu(self.tr('&File'))
        fileMenu.addAction(self.action_open)
        fileMenu.addSeparator()
        fileMenu.addAction(self.action_exit)
        
        # TODO: needs Edit menu
        
        helpMenu = self.menuBar().addMenu(self.tr('Help'))
        helpMenu.addSeparator()
        #helpMenu.addAction(self.about_dialog)
    
    def _init_Main_Frame(self, parent):
        fr = QFrame(parent)

        layout = QVBoxLayout()
        fr.setLayout(layout)

        self.fileentry = FileEntryBox(fr, 
            title='Input parameters file', 
            tip='select a file with desmearing parameters',
            callback=self.openFileCallback)
        panel = self._init_Big_Panel(fr)
        
        # TODO: need a box with widgets that depend on the type of self.fileentry
        '''
           .inp file    : text file with input parameters
           cansas1d/1.1 : need to select smeared & desmeared data path & parameters path
           HDF5/NeXus   : need to select smeared & desmeared data path & parameters path
        '''

        layout.addWidget(self.fileentry)
        layout.addWidget(panel)
        layout.setStretch(0, 0)
        layout.setStretch(1, 1)

        return fr

    def _init_Big_Panel(self, parent):
        '''contains parameter entries and plots'''
        fr = QFrame(parent)
        
        parms = self._init_Parms_Panel(fr)
        parms.setFrameStyle(QFrame.StyledPanel)
        plots = self._init_Plots_Panel(fr)
        plots.setFrameStyle(QFrame.StyledPanel)

        splitter = QSplitter(fr)
        splitter.setOrientation(Qt.Horizontal)
        splitter.addWidget(parms)
        splitter.addWidget(plots)

        layout = QVBoxLayout()
        layout.addWidget(splitter)
        fr.setLayout(layout)
        
        return fr
    
    def _init_Parms_Panel(self, parent):
        '''contains parameter entries and controls'''
        fr = QFrame(parent)
        
        layout = QVBoxLayout()
        fr.setLayout(layout)

        adjustables = self._init_Adjustables_Panel(fr)
        controls = self._init_Controls_Panel(fr)
        console = self._init_Console_Panel(fr)

        layout.addWidget(adjustables)
        layout.addWidget(controls)
        layout.addWidget(console)
        
        return fr
    
    def _init_Adjustables_Panel(self, parent):
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
        self.slitlength.setText('0.1')

        # TODO: need setter/getter methods
        row += 1
        tip = 'functional form of extrapolation for desmearing'
        functions = discover_extrapolation_functions()
        self.extrapolation = QComboBox()
        self.extrapolation.insertItems(999, sorted(functions.keys()))
        self.extrapolation.setToolTip(tip)
        layout.addWidget(QLabel('extrap'), row, 0)
        layout.addWidget(self.extrapolation, row, 1)
        self.setExtrapolationMethod('constant')

        row += 1
        tip = 'evaluate extrapolation constants based on data for q > q_F'
        self.qFinal = QLineEdit()
        self.qFinal.setToolTip(tip)
        layout.addWidget(QLabel('q_F'), row, 0)
        layout.addWidget(self.qFinal, row, 1)
        self.qFinal.setText('0.1')

        # TODO: need setter/getter methods
        row += 1
        tip = 'functional form of desmearing feedback, always use "fast"'
        self.feedback = QComboBox()
        self.feedback.insertItems(999, sorted(Weighting_Methods.keys()))
        self.feedback.setCurrentIndex(2)
        self.feedback.setToolTip(tip)
        layout.addWidget(QLabel('feedback'), row, 0)
        layout.addWidget(self.feedback, row, 1)
        self.setFeedbackMethod('fast')

        row += 1
        tip = 'specifies number of desmearing iterations, N_i'
        self.num_iterations = QSpinBox()
        self.num_iterations.setRange(2, 1000)
        self.num_iterations.setToolTip(tip)
        layout.addWidget(QLabel('N_i'), row, 0)
        layout.addWidget(self.num_iterations, row, 1)
        self.num_iterations.setValue(10)
        
        return box

    def _init_Controls_Panel(self, parent):
        '''contains controls'''
        def squareWidget(w):
            w.setMinimumWidth(w.sizeHint().height())
        box = QGroupBox('Desmearing controls', parent)

        layout = QHBoxLayout()
        box.setLayout(layout)
        
        tip = 'desmear N iterations'
        self.b_do_N = QPushButton('N')
        self.b_do_N.setToolTip(tip)
        layout.addWidget(self.b_do_N)
        squareWidget(self.b_do_N)
        
        tip = 'desmear one iteration'
        self.b_do_once = QPushButton('1')
        self.b_do_once.setToolTip(tip)
        layout.addWidget(self.b_do_once)
        squareWidget(self.b_do_once)
        
        layout.addStretch(50)
        
        tip = 're(start) by clearing all results and reloading data'
        self.b_restart = QPushButton('!')
        self.b_restart.setToolTip(tip)
        layout.addWidget(self.b_restart)
        squareWidget(self.b_restart)

        return box
    
    def _init_Console_Panel(self, parent):
        '''contains console output'''
        fr = QGroupBox('Console', parent)

        layout = QVBoxLayout()
        fr.setLayout(layout)
        
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.ensureCursorVisible()
        layout.addWidget(self.console)
        
        self.b_clear_console = QPushButton('clear all console text')
        layout.addWidget(self.b_clear_console)
        
        return fr
    
    def _init_Plots_Panel(self, parent):
        '''contains plots'''
        fr = QFrame(parent)

        layout = QHBoxLayout()
        fr.setLayout(layout)

        splitter = QSplitter(fr)
        splitter.setOrientation(Qt.Horizontal)
        splitter.addWidget(self._init_Data_Plots_Panel(fr))
        splitter.addWidget(self._init_ChiSqr_Plot_Panel(fr)) 
        layout.addWidget(splitter)
        
        return fr
    
    def _init_Data_Plots_Panel(self, parent):
        '''contains I(Q) and z(Q) plots'''
        fr = QFrame(parent)

        layout = QVBoxLayout()
        fr.setLayout(layout)

        splitter = QSplitter(fr)
        splitter.setOrientation(Qt.Vertical)
        splitter.addWidget(self._init_Sas_Plot_Panel(fr))
        splitter.addWidget(self._init_Residuals_Plot_Panel(fr)) 
        layout.addWidget(splitter)
        
        return fr
    
    def _create_and_add_plot(self, fr, layout):
        figure = matplotlib.figure.Figure()
        canvas = FigureCanvas(figure)
        canvas.setParent(fr)
        layout.addWidget(canvas)
        return figure

    def _init_Sas_Plot_Panel(self, parent):
        '''contains I(Q) plot'''
        fr = QGroupBox('~I(Q) and I(Q)', parent)

        layout = QHBoxLayout()
        fr.setLayout(layout)
        
        self.sas_plot = self._create_and_add_plot(fr, layout)
  
        return fr
    
    def _init_Residuals_Plot_Panel(self, parent):
        '''contains z(Q) plot'''
        fr = QGroupBox('z(Q)', parent)

        layout = QHBoxLayout()
        fr.setLayout(layout)
        
        self.z_plot = self._create_and_add_plot(fr, layout)
        
        return fr
    
    def _init_ChiSqr_Plot_Panel(self, parent):
        '''contains ChiSqr vs. iteration plot'''
        fr = QGroupBox('ChiSqr vs. iteration', parent)

        layout = QHBoxLayout()
        fr.setLayout(layout)
        
        self.chisqr_plot = self._create_and_add_plot(fr, layout)
        
        return fr

    def setStatus(self, message = 'Ready'):
        '''setup the status bar for the GUI or set a new status message'''
        self.statusBar().showMessage(self.tr(message))
    
    def appendConsole(self, msg):
        '''write more text to the console widget'''
        self.console.append(msg)
        cursor = self.console.textCursor()
        self.console.setTextCursor(cursor)

    def onOpenFile(self):
        '''Choose a text file with 3-column smeared SAS data'''
        self.fileentry.onOpenFile()
    
    def openFileCallback(self, fileName, filefilter):
        # TODO: find out what kind of file was opened
        # Hint is in the filefilter but don't trust it.
        self.setStatus('selected file: ' + fileName)
        self.loadFile(fileName)
        self.dirty = False
        self.dsm = None

    def loadFile(self, filename):
        '''Open a file with 3-column smeared SAS data'''
        if os.path.exists(filename):
            self.setStatus('did not open file: ' + filename)
    
    def init_session(self):
        '''setup a new desmearing session using existing parameters and plot the data'''
        def session_callback(dsm):
            msg = "#" + str(dsm.iteration_count)
            msg += "  ChiSqr=" + str(dsm.ChiSqr[-1])
            msg += "  " + str(dsm.params.extrap)
            if self.console is not None:
                self.appendConsole(msg)
                self.updatePlots(self.dsm)
            else:
                print msg

        params = Info()

        params.infile = self.getInputDataFile()
        params.outfile = self.getOutputDataFile()
        params.slitlength = self.getSlitLength()
        params.sFinal = self.getQFinal()
        params.NumItr = self.getNumIterations()
        params.extrapname = self.getExtrapolationMethod()
        params.LakeWeighting = self.getFeedbackMethod()
        params.extrap = self.getExtrapolationMethod()
        params.quiet = True
        params.callback = session_callback
        
        self.appendConsole('reading SAS data from ' + params.infile)
        q, E, dE = toolbox.GetDat(params.infile)
        
        # TODO: verify parameters are within range of data before continuing!

        self.appendConsole('Preparing for desmearing')
        self.dsm = Desmearing(q, E, dE, params)
        self.updatePlots(self.dsm)
    
    def updatePlots(self, dsm):
        '''update the plots with new data'''
        # plot E(q)
        self.sas_plot.clf(keep_observers=True)
        axis = self.sas_plot.add_subplot(111)
        axis.plot(dsm.q, dsm.I, color='black')
        axis.plot(dsm.q, dsm.S, color='blue')
        axis.plot(dsm.q, dsm.C, color='red')
        axis.set_xscale('log')
        axis.set_yscale('log')
        self.sas_plot.canvas.draw()
        
        # plot z(q)
        self.z_plot.clf(keep_observers=True)
        axis = self.z_plot.add_subplot(111)
        axis.plot(dsm.q, dsm.z, 'o')
        axis.set_xscale('log')
        self.z_plot.canvas.draw()
        
        self.chisqr_plot.clf(keep_observers=True)
        axis = self.chisqr_plot.add_subplot(111)
        x = range(len(dsm.ChiSqr))
        axis.plot(x, dsm.ChiSqr, 'o-')
        axis.set_yscale('log')
        self.chisqr_plot.canvas.draw()
    
    def do_1_iteration(self, *args, **kws):
        '''1 button (iterate once) was pressed by the user'''
        if self.dsm:
            IterativeDesmear(self.dsm, 1).start()
            self.dirty = True
    
    def do_N_iterations(self, *args, **kws):
        '''N button (iterate N times) was pressed by the user'''
        if self.dsm:
            N = self.getNumIterations()
            IterativeDesmear(self.dsm, N).start()
            self.dirty = True
            
    def do_Clear_Console(self):
        # TODO: first, a confirm dialog
        self.console.setText('<console cleared>')
    
    def selectQComboBoxItemByText(self, obj, text):
        '''select a QComboBox object by text value'''
        if not isinstance(obj, QComboBox):
            raise RuntimeError, 'Programmer error'
        item = obj.findText(text)
        if item > -1:
            obj.setCurrentIndex(item)
        return item
    
    def setInputDataFile(self, value):
        self.inputdatafile = value
    
    def getInputDataFile(self):
        return self.inputdatafile
    
    def setOutputDataFile(self, value):
        self.outputdatafile = value
    
    def getOutputDataFile(self):
        return self.outputdatafile
    
    def setSlitLength(self, value):
        self.slitlength.setText(str(value))
    
    def getSlitLength(self, default=0.1):
        try:
            value = float(self.slitlength.text())
        except:
            value = default
        return value
    
    def setQFinal(self, value):
        self.qFinal.setText(str(value))
    
    def getQFinal(self, default=0.1):
        try:
            value = float(self.qFinal.text())
        except:
            value = default
        return value
    
    def setNumIterations(self, value):
        self.num_iterations.setValue(int(value))
    
    def getNumIterations(self, default=10):
        try:
            value = int(self.num_iterations.value())
        except:
            value = default
        return value
    
    def setExtrapolationMethod(self, method):
        self.selectQComboBoxItemByText(self.extrapolation, method)
    
    def getExtrapolationMethod(self):
        return self.extrapolation.currentText()
    
    def setFeedbackMethod(self, method):
        self.selectQComboBoxItemByText(self.feedback, method)
    
    def getFeedbackMethod(self):
        return self.feedback.currentText()


class IterativeDesmear(threading.Thread):
    ''' 
    Run ``n`` iterations of the desmearing operation in a separate thread.
    Running in a separate thread with callbacks allows the 
    GUI widgets to be updated after each iteration.
        
    :param obj dsm: existing Desmearing object
    :param int n: number of iterations to perform
    
    Start this thread with code such as this example::
    
        IterativeDesmear(Desmear_object, number_of_iterations).start()

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
