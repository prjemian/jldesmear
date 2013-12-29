#!/usr/bin/env python

'''
Lake desmearing GUI using PySide (or PyQt4) and Matplotlib
'''


import os, sys
import threading
import matplotlib
matplotlib.use('Qt4Agg')

try:
    from PySide import __version__ as pyqt_version
    from PySide.QtCore import *  #@UnusedWildImport
    from PySide.QtGui import *   #@UnusedWildImport
    pyqtSignal = Signal
    pyqt_name = "PySide"
except:
    from PyQt4 import __version__ as pyqt_version
    from PyQt4.QtCore import *  #@UnusedWildImport
    from PyQt4.QtGui import *   #@UnusedWildImport
    pyqtSignal = pyqtSignal
    pyqt_name = "PyQt4"
matplotlib.rcParams['backend.qt4'] = pyqt_name

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '..') ))
from jldesmear.api import toolbox
from jldesmear.api.desmear import Weighting_Methods, Desmearing
from jldesmear.api.extrapolation import discover_extrapolations
from jldesmear.api.info import Info
import jldesmear.fileio.fileio #import makeFilters, ext_xref, formats


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
        
        tip = 'full path of selected file'
        self.entry = QLineEdit('')
        self.entry.setToolTip(tip)
        self.entry.setStatusTip(tip)

        tip = 'Open a file ...'
        b_icon = QPushButton('')
        b_icon.clicked[bool].connect(self.selectFile)
        style = b_icon.style()
        icon = style.standardIcon(QStyle.SP_FileIcon)
        b_icon.setIcon(icon)
        b_icon.setToolTip(tip)
        b_icon.setStatusTip(tip)

        layout = QHBoxLayout()
        layout.addWidget(self.entry)
        layout.addWidget(b_icon)
        layout.setStretch(0, 1)
        layout.setStretch(1, 0)
        self.setLayout(layout)

    def selectFile(self, **kw):
        '''Choose file for input'''
#         filters = ';;'.join([
#                              'Input parameters (*.inp)',
#                              'cansas1d:1.1 (*.xml)',
#                              'HDF5/NeXus (*.hdf *.hdf5 *.h5 *.nx *.nxs)',
#                              'smeared SAS (*.smr)',
#                              'any file (*.* *)',
#                              ])
        filters = jldesmear.fileio.fileio.makeFilters()
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
        self.status = None

        self.mf = self._init_Main_Frame(self)
        #self.setGeometry(75, 50, 500, 300)
        self.setCentralWidget(self.mf)
        
        self._init_actions()
        self._init_menus()
        self.setStatus()

    def closeEvent(self, *args):
        '''received a request to close application, shall we allow it?'''
        if self.dirty:
            pass
        else:
            self.close()

    def _init_actions(self):
        '''define the actions for the GUI'''
        def _setup(label, shortcut, tip, handler):
            action = QAction(label, None)
            if shortcut is not None:
                action.setShortcut(shortcut)
            action.setStatusTip(tip)
            action.triggered.connect(handler)
            return action
        
        self.action_new = _setup('&New ...', QKeySequence.New, 'Start a new project', self.onNewProject)
        self.action_open = _setup('&Open ...', QKeySequence.Open, 'Open a file', self.onOpen)
        self.action_save = _setup('&Save', QKeySequence.Save, 'Save parameters to a file', self.onSaveFile)
        self.action_saveas = _setup('Save &As ...', QKeySequence.SaveAs, 'Save parameters to a new file', self.onSaveAsFile)
        self.action_saveDSM = _setup('Save &DSM', None, 'Save desmeared data to a file', self.onSaveDsmFile)
        self.action_exit = _setup('E&xit', QKeySequence.Quit, 'Exit the application', self.closeEvent)

        # TODO: needs Edit menu actions if menu items are created

        self.action_about = _setup('About ...', None, 'Describe the application', self.doAboutBox)
        self.action_aboutQt = _setup('About Qt', None, 'Describe the Qt support', self.doAboutQtBox)
        
        self.b_stop.clicked.connect(self.do_stop)
        self.b_pause.clicked.connect(self.do_pause)
        self.b_do_N.clicked.connect(self.do_N_iterations)
        self.b_do_once.clicked.connect(self.do_1_iteration)
        self.b_restart.clicked.connect(self.init_session)
        
        self.b_clear_console.clicked.connect(self.do_Clear_Console)
        self.b_clear_plots.clicked.connect(self.do_Clear_Plots)
        
    def _init_menus(self):
        '''define the menus for the GUI'''
        fileMenu = self.menuBar().addMenu('&File')
        fileMenu.addAction(self.action_new)
        fileMenu.addSeparator()
        fileMenu.addAction(self.action_open)
        fileMenu.addSeparator()
        fileMenu.addAction(self.action_save)
        fileMenu.addAction(self.action_saveas)
        fileMenu.addSeparator()
        fileMenu.addAction(self.action_saveDSM)
        fileMenu.addSeparator()
        fileMenu.addAction(self.action_exit)
        
        editMenu = self.menuBar().addMenu('&Edit')
        editMenu.addSeparator()
        
        helpMenu = self.menuBar().addMenu('&Help')
        helpMenu.addAction(self.action_about)
        helpMenu.addSeparator()
        helpMenu.addAction(self.action_aboutQt)
    
    def _init_Main_Frame(self, parent):
        fr = QFrame(parent)

        layout = QVBoxLayout()
        fr.setLayout(layout)

        self.fileentry = FileEntryBox(fr, 
            title='Command Input parameters file', 
            tip='select a file with desmearing parameters',
            callback=self.openFileCallback)
        panel = self._init_Big_Panel(fr)
        
        # TODO: need entry for input data file
        # TODO: need entry for output data file
        
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
        self.slitlength.setStatusTip(tip)
        layout.addWidget(QLabel('l_o'), row, 0)
        layout.addWidget(self.slitlength, row, 1)
        self.slitlength.setText('0.1')

        row += 1
        tip = 'functional form of extrapolation for desmearing'
        functions = discover_extrapolations()
        self.extrapolation = QComboBox()
        self.extrapolation.insertItems(999, sorted(functions.keys()))
        self.extrapolation.setToolTip(tip)
        self.extrapolation.setStatusTip(tip)
        layout.addWidget(QLabel('extrap'), row, 0)
        layout.addWidget(self.extrapolation, row, 1)
        self.setExtrapolationMethod('constant')

        row += 1
        tip = 'evaluate extrapolation constants based on data for q > q_F'
        self.qFinal = QLineEdit()
        self.qFinal.setToolTip(tip)
        self.qFinal.setStatusTip(tip)
        layout.addWidget(QLabel('q_F'), row, 0)
        layout.addWidget(self.qFinal, row, 1)
        self.qFinal.setText('0.1')

        row += 1
        tip = 'functional form of desmearing feedback, always use "fast"'
        self.feedback = QComboBox()
        self.feedback.insertItems(999, sorted(Weighting_Methods.keys()))
        self.feedback.setCurrentIndex(2)
        self.feedback.setToolTip(tip)
        self.feedback.setStatusTip(tip)
        layout.addWidget(QLabel('feedback'), row, 0)
        layout.addWidget(self.feedback, row, 1)
        self.setFeedbackMethod('fast')

        row += 1
        tip = 'specifies number of desmearing iterations, N_i'
        self.num_iterations = QSpinBox()
        self.num_iterations.setRange(2, 1000)
        self.num_iterations.setToolTip(tip)
        self.num_iterations.setStatusTip(tip)
        layout.addWidget(QLabel('N_i'), row, 0)
        layout.addWidget(self.num_iterations, row, 1)
        self.num_iterations.setValue(10)
        
        return box

    def _init_Controls_Panel(self, parent):
        '''widgets to control desmearing'''
        def iconButton(tip, pixmap):
            btn = QPushButton()
            btn.setToolTip(tip)
            btn.setStatusTip(tip)
            btn.setIcon(btn.style().standardIcon(pixmap))
            return btn
        box = QGroupBox('Desmearing controls', parent)

        layout = QHBoxLayout()
        box.setLayout(layout)
        
        tip = 'stop iterations'
        self.b_stop = iconButton(tip, QStyle.SP_MediaStop)
        layout.addWidget(self.b_stop)
        
        tip = 'pause iterations'
        self.b_pause = iconButton(tip, QStyle.SP_MediaPause)
        layout.addWidget(self.b_pause)
        
        tip = 'desmear one iteration'
        self.b_do_once = iconButton(tip, QStyle.SP_MediaPlay)
        layout.addWidget(self.b_do_once)
        
        tip = 'desmear N iterations'
        self.b_do_N = iconButton(tip, QStyle.SP_MediaSeekForward)
        layout.addWidget(self.b_do_N)
        
        layout.addStretch(50)
        
        tip = 're(start) by clearing all results and reloading data'
        self.b_restart = iconButton(tip, QStyle.SP_BrowserReload)
        layout.addWidget(self.b_restart)

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
        
        tip = 'remove all content from the console window'
        self.b_clear_console = QPushButton('clear all console text')
        self.b_clear_console.setToolTip(tip)
        self.b_clear_console.setStatusTip(tip)
        layout.addWidget(self.b_clear_console)
        
        return fr
    
    def _init_Plots_Panel(self, parent):
        '''contains plots'''
        fr = QFrame(parent)

        layout = QVBoxLayout()
        fr.setLayout(layout)

        splitter = QSplitter(fr)
        splitter.setOrientation(Qt.Horizontal)
        splitter.addWidget(self._init_Data_Plots_Panel(fr))
        splitter.addWidget(self._init_ChiSqr_Plot_Panel(fr)) 
        layout.addWidget(splitter)
        
        tip = 'remove all data from the plots'
        self.b_clear_plots = QPushButton('clear all plots')
        self.b_clear_plots.setToolTip(tip)
        self.b_clear_plots.setStatusTip(tip)
        layout.addWidget(self.b_clear_plots)
        
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

    def plot_panel(self, parent, title):
        '''generic creation of a plot panel in a titled box (QGroupBox)'''
        fr = QGroupBox(title, parent)

        layout = QHBoxLayout()
        fr.setLayout(layout)
        
        figure = matplotlib.figure.Figure()
        canvas = FigureCanvas(figure)
        canvas.setParent(fr)
        layout.addWidget(canvas)
  
        return fr, figure

    def _init_Sas_Plot_Panel(self, parent):
        '''contains I(Q) plot'''
        fr, self.sas_plot = self.plot_panel(parent, '~I(Q) and I(Q)')
        return fr
    
    def _init_Residuals_Plot_Panel(self, parent):
        '''contains z(Q) plot'''
        fr, self.z_plot = self.plot_panel(parent, 'z(Q)')
        return fr
    
    def _init_ChiSqr_Plot_Panel(self, parent):
        '''contains ChiSqr vs. iteration plot'''
        fr, self.chisqr_plot = self.plot_panel(parent, 'ChiSqr vs. iteration')
        return fr

    def setStatus(self, message = 'Ready', duration_ms=-1):
        '''setup the status bar for the GUI or set a new status message'''
        # TODO: add logging
        if self.status is None:
            self.status = self.statusBar()
            self.status.setSizeGripEnabled(True)
            self.status_label = QLabel('normal message')
            self.status.addPermanentWidget(self.status_label)
        if duration_ms < 0:
            self.status_label.setText(message)
        else:
            self.statusBar().showMessage(message, duration_ms)
    
    def appendConsole(self, msg):
        '''write more text to the console widget'''
        self.console.append(msg)
        cursor = self.console.textCursor()
        self.console.setTextCursor(cursor)

    def onOpen(self):
        '''Choose a file with SAS desmearing parameters'''
        self.fileentry.selectFile()
    
    def openFileCallback(self, filename, filefilter):
        '''open a Command Input file with SAS desmearing parameters'''
        ext = os.path.splitext(filename)[1]
        xref = jldesmear.fileio.fileio.ext_xref
        if ext in xref and xref[ext] == 'CommandInput':
            self.setStatus('selected file: ' + filename)
            self.dsm = None
            
            # read a .inp file
            cls = jldesmear.fileio.fileio.formats[xref[ext]]
            cmd_inp = cls()
            cmd_inp.read(filename)
            
            self.setInputDataFile(cmd_inp.info.infile)
            self.setOutputDataFile(cmd_inp.info.outfile)
            self.setSlitLength(cmd_inp.info.slitlength)
            self.setExtrapolationMethod(cmd_inp.info.extrapname)
            self.setQFinal(cmd_inp.info.sFinal)
            self.setNumIterations(cmd_inp.info.NumItr)
            self.setFeedbackMethod(cmd_inp.info.LakeWeighting)
            
            # load the SAS data
            q, E, dE = cmd_inp.read_SMR(cmd_inp.info.infile)
            self.dsm = Desmearing(q, E, dE, cmd_inp.info)
            self.updatePlots(self.dsm)
            self.dirty = False
            
            self.init_session()

            self.setStatus('loaded file: ' + filename)
    
    def onNewProject(self):
        '''start a new project'''
        self.setStatus('start a new project')
        self.setStatus('method not defined yet', 10000)
    
    def onSaveFile(self):
        '''save desmearing parameters to a file'''
        if self.dsm is None: return
        info = self.dsm.params
        if 'fileio_class' not in dir(info):
            raise RuntimeError, 'programmer trouble: something replaced the params'
        info.fileio_class.save(self.dsm.params.filename)
        self.setStatus('saved file: ' + self.dsm.params.filename)
        self.dirty = False

    
    def onSaveAsFile(self):
        '''save desmearing parameters to a new file'''
        if self.dsm is None: return
        info = self.dsm.params
        if 'fileio_class' not in dir(info):
            raise RuntimeError, 'programmer trouble: something replaced the params'
        path = os.path.dirname(self.dsm.params.filename)
        dlog = QFileDialog()
        dlog.setDirectory(path)
        filefilter = str(self.dsm.params.fileio_class)
        outfile, filefilter = dlog.getSaveFileName(dir=self.dsm.params.filename, filter=filefilter)
        if len(outfile) > 0:
            info.fileio_class.save(outfile)
            self.dirty = False
            self.setStatus('saved file: ' + outfile)

    def onSaveDsmFile(self):
        '''save desmeared data to a file'''
        if self.dsm is None: return
        info = self.dsm.params
        if 'fileio_class' not in dir(info):
            raise RuntimeError, 'programmer trouble: something replaced the params'
        path = os.path.dirname(self.dsm.params.outfile)
        dlog = QFileDialog()
        dlog.setDirectory(path)
        outfile = dlog.getSaveFileName(dir=self.dsm.params.outfile)[0]
        if len(outfile) > 0:
            info.fileio_class.save_DSM(outfile, self.dsm)
            #self.dirty = False
            self.setStatus('saved data file: ' + outfile)

    def init_session(self):
        '''setup a new desmearing session using existing parameters and plot the data'''
        def session_callback(dsm):
            msg = "#" + str(dsm.iteration_count)
            msg += "  ChiSqr=" + str(dsm.ChiSqr[-1])
            msg += "  " + str(dsm.params.extrap)
            if self.console is not None:
                self.appendConsole(msg)
                self.updatePlots(self.dsm)
            self.setStatus(msg)

        if self.dsm is None or self.dsm.params is None:
            params = Info()
        else:
            params = self.dsm.params

        try:
            params.infile = self.getInputDataFile()
        except AttributeError:
            self.setStatus('no data to clear from plots')
            return
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
        # TODO: this is very slow
        # plot E(q)
        self.sas_plot.clf(keep_observers=True)
        axis = self.sas_plot.add_subplot(111)
        axis.plot(dsm.q, dsm.I, color='black')
        axis.plot(dsm.q, dsm.S, color='blue')
        axis.plot(dsm.q, dsm.C, color='red')
        axis.set_xscale('log')
        axis.set_yscale('log')
        axis.autoscale_view(tight=True)
        self.sas_plot.canvas.draw()
        
        # plot z(q)
        self.z_plot.clf(keep_observers=True)
        axis = self.z_plot.add_subplot(111)
        axis.plot(dsm.q, dsm.z, 'o')
        axis.set_xscale('log')
        axis.autoscale_view(tight=True)
        self.z_plot.canvas.draw()
        
        self.chisqr_plot.clf(keep_observers=True)
        axis = self.chisqr_plot.add_subplot(111)
        x = range(len(dsm.ChiSqr))
        axis.plot(x, dsm.ChiSqr, 'o-')
        axis.set_yscale('log')
        axis.autoscale_view(tight=True)
        self.chisqr_plot.canvas.draw()
    
    def do_pause(self, *args, **kws):
        '''pause button was pressed by the user'''
        self.setStatus('pause button was pressed')
        self.setStatus('method not defined yet', 10000)
    
    def do_stop(self, *args, **kws):
        '''stop button was pressed by the user'''
        self.setStatus('stop button was pressed')
        self.setStatus('method not defined yet', 10000)
    
    def do_1_iteration(self, *args, **kws):
        '''1 button (iterate once) was pressed by the user'''
        if self.dsm:
            self.setStatus('desmear one iteration')
            IterativeDesmear(self.dsm, 1).start()
            self.dirty = True
    
    def do_N_iterations(self, *args, **kws):
        '''N button (iterate N times) was pressed by the user'''
        if self.dsm:
            self.setStatus('desmear N iterations')
            N = self.getNumIterations()
            IterativeDesmear(self.dsm, N).start()
            self.dirty = True
            
    def do_Clear_Console(self):
        question = 'Really clear the console?'
        if self.dirty and self.confirmation('clear console text', question):
            self.console.setText('<console cleared>')
            self.setStatus('console cleared')
            
    def do_Clear_Plots(self):
        question = 'Really clear all plot data?'
        if self.dirty and self.confirmation('clear plot data', question):
            for plot in (self.sas_plot, self.z_plot, self.chisqr_plot):
                plot.clf(keep_observers=True)
                plot.canvas.draw()
            self.setStatus('plot data was cleared')

    def doAboutBox(self, *args, **kws):
        '''show the about box'''
        self.setStatus('describe this application')
        title = u'about ' +  jldesmear.__project__
        support = [pyqt_name + ' version: ' + pyqt_version,]
        support.append('Matplotlib version: ' + matplotlib.__version__)
        support.append('Numpy version: ' + matplotlib.__version__numpy__)
        text = jldesmear.__about__() + '\n'*2 + '\n'.join(support)
        QMessageBox.about(self, title, text)

    def doAboutQtBox(self, *args, **kws):
        '''show the about box'''
        self.setStatus('describe this application')
        title = u'about Qt'
        QMessageBox.aboutQt(self, title)
    
    def confirmation(self, title, text, cancel_default=True):
        '''request confirmation from user before an action, return True if Ok'''
        flags = QMessageBox.Ok
        flags |= QMessageBox.Cancel
        
        if cancel_default:
            default_button = QMessageBox.Cancel
        else:
            default_button = QMessageBox.Ok

        result = QMessageBox.question(self, title, text, flags, default_button)
        if result == QMessageBox.Ok:
            self.setStatus('Ok selected', 2000)
        elif result == QMessageBox.Cancel:
            self.setStatus('Cancel selected', 2000)
        return result == QMessageBox.Ok

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
