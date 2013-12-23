#!/usr/bin/env python

'''
Lake desmearing GUI using PySide (or PyQt4) and Matplotlib
'''


import os, sys
import threading

try:
    from PyQt4.QtCore import *  #@UnusedWildImport
    from PyQt4.QtGui import *   #@UnusedWildImport
    pyqtSignal = pyqtSignal
except:
    from PySide.QtCore import *  #@UnusedWildImport
    from PySide.QtGui import *   #@UnusedWildImport
    pyqtSignal = Signal

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '..') ))
import api.toolbox  #@UnusedImport
import api.desmear  #@UnusedImport
import api.info     #@UnusedImport


class FileEntry(QFrame):
    '''FileEntry = QLineEdit + QPushButton'''

    def __init__(self, parent=None, callback=None):
        '''
        :param obj callback:  method to call if a name is selected
        '''
        super(FileEntry, self).__init__(parent)
        self.parent = parent
        self.callback = callback
        
        self.entry = QLineEdit('data file name here')
        #self.icon_button = QPushButton(icon, 'select ...')
        icon_button = QPushButton('&Open ...')
        icon_button.clicked[bool].connect(self.onOpenFile)

        layout = QHBoxLayout()
        layout.addWidget(self.entry)
        layout.addWidget(icon_button)
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

        self.fileentry = FileEntry(self, callback=self.openFileCallback)
        panel = self.create_Big_Panel(self)
        panel.setFrameStyle(QFrame.StyledPanel)

        layout = QVBoxLayout()
        layout.addWidget(self.fileentry)
        layout.addWidget(panel)
        layout.setStretch(0, 0)
        layout.setStretch(1, 1)
        self.setLayout(layout)
    
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
    
    def create_Big_Panel(self, parent):
        '''contains parameter entries and plots'''
        fr = QFrame(parent)
        
        parms = QFrame(fr)
        parms.setFrameStyle(QFrame.StyledPanel)
        plots = QFrame(fr)
        plots.setFrameStyle(QFrame.StyledPanel)

        splitter = QSplitter(fr)
        splitter.setOrientation(Qt.Horizontal)
        splitter.addWidget(parms)
        splitter.addWidget(plots)

        layout = QVBoxLayout()
        layout.addWidget(splitter)
        fr.setLayout(layout)
        
        return fr


class JLdesmearGui(QMainWindow):

    def __init__(self, parent=None):
        super(JLdesmearGui, self).__init__(parent)
        self.parent = parent
        
        self.dirty = False

        self.fr = MainFrame(self)
        self.setGeometry(75, 50, 500, 300)
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
