# -*- coding: utf-8 -*-
# PEP8:OK, LINT:OK, PY3:OK


#############################################################################
## This file may be used under the terms of the GNU General Public
## License version 2.0 or 3.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following information to ensure GNU
## General Public Licensing requirements will be met:
## http:#www.fsf.org/licensing/licenses/info/GPLv2.html and
## http:#www.gnu.org/copyleft/gpl.html.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
#############################################################################


# metadata
' Test Runner Ninja '
__version__ = ' 0.1 '
__license__ = ' GPL '
__author__ = ' juancarlospaco '
__email__ = ' juancarlospaco@ubuntu.com '
__url__ = ' github.com/juancarlospaco '
__date__ = ' 11/11/2013 '
__prj__ = ' testrunner '
__docformat__ = ' html '
__source__ = ''
__full_licence__ = ''


# imports
from os import chmod, path
from sip import setapi
from datetime import datetime

try:
    from os import startfile
except ImportError:
    from subprocess import Popen

from PyQt4.QtGui import (QLabel, QCompleter, QDirModel, QPushButton, QWidget,
    QDockWidget, QVBoxLayout, QLineEdit, QIcon, QCheckBox, QColor, QMessageBox,
    QGraphicsDropShadowEffect, QGroupBox, QComboBox, QTabWidget, QScrollArea,
    QSpinBox, QHBoxLayout, QFileDialog)

from PyQt4.QtCore import Qt, QDir, QProcess


try:
    from PyKDE4.kdeui import KTextEdit as QTextEdit
except ImportError:
    from PyQt4.QtGui import QTextEdit  # lint:ok

from ninja_ide.core import plugin


# API 2
(setapi(a, 2) for a in ("QDate", "QDateTime", "QString", "QTime", "QUrl",
                        "QTextStream", "QVariant"))


# constans
BASE = path.abspath(path.join(path.expanduser("~"), 'testrunner'))


###############################################################################


class Main(plugin.Plugin):
    " Main Class "
    def initialize(self, *args, **kwargs):
        " Init Main Class "
        super(Main, self).initialize(*args, **kwargs)
        self.completer, self.dirs = QCompleter(self), QDirModel(self)
        self.dirs.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot)
        self.completer.setModel(self.dirs)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.process, self.mainwidget = QProcess(), QTabWidget()
        self.process.readyReadStandardOutput.connect(self.readOutput)
        self.process.readyReadStandardError.connect(self.readErrors)
        self.process.finished.connect(self._process_finished)
        self.process.error.connect(self._process_finished)
        self.mainwidget.tabCloseRequested.connect(lambda:
            self.mainwidget.setTabPosition(1)
            if self.mainwidget.tabPosition() == 0
            else self.mainwidget.setTabPosition(0))
        self.mainwidget.setStyleSheet('QTabBar{font-weight:bold;}')
        self.mainwidget.setMovable(True)
        self.mainwidget.setTabsClosable(True)
        self.dock, self.scrollable = QDockWidget(), QScrollArea()
        self.scrollable.setWidgetResizable(True)
        self.scrollable.setWidget(self.mainwidget)
        self.dock.setWindowTitle(__doc__)
        self.dock.setStyleSheet('QDockWidget::title{text-align: center;}')
        self.dock.setWidget(self.scrollable)
        self.locator.get_service('misc').add_widget(self.dock,
                                 QIcon.fromTheme("face-sad"), __doc__)
        self.tab1, self.tab2, self.tab3 = QGroupBox(), QGroupBox(), QGroupBox()
        self.tab4, self.tab5, self.tab6 = QGroupBox(), QGroupBox(), QGroupBox()
        for a, b in ((self.tab1, 'Basics'), (self.tab2, 'Coverage'),
            (self.tab3, 'Extensions'), (self.tab5, 'Regex'),
             (self.tab4, 'Paths'), (self.tab6, 'Run')):
            a.setTitle(b)
            a.setToolTip(b)
            self.mainwidget.addTab(a, QIcon.fromTheme("face-sad"), b)
        QPushButton(QIcon.fromTheme("help-about"), 'About', self.dock
          ).clicked.connect(lambda: QMessageBox.information(self.dock, __doc__,
          ''.join((__doc__, __version__, __license__, 'by', __author__))))

        groupl, groupr, co = QWidget(), QWidget(), QGroupBox()
        self.qckb1 = QCheckBox('Open target directory later')
        self.qckb2 = QCheckBox('Save a LOG file to target later')
        self.qckb3 = QCheckBox('Verbose operation')
        self.qckb4 = QCheckBox('Force Stop on Error')
        self.qckb5 = QCheckBox('Scan Executable files for Tests')
        vboxgl, vboxgr = QVBoxLayout(groupl), QVBoxLayout(groupr)
        for a in (self.qckb1, self.qckb2, self.qckb3, self.qckb4, self.qckb5):
            vboxgl.addWidget(a)
            a.setToolTip(a.text())
        self.qckb6 = QCheckBox('No Byte Compile to .PYC or Delete .PYC later')
        self.qckb7 = QCheckBox('Dont touch sys.path when running tests')
        self.qckb8 = QCheckBox('Traverse all paths of a package')
        self.qckb9 = QCheckBox('Dont capture STDOUT, print STDOUT on the fly')
        self.qckb10 = QCheckBox('Clear all Logging handlers')
        for a in (self.qckb6, self.qckb7, self.qckb8, self.qckb9, self.qckb10):
            vboxgr.addWidget(a)
            a.setToolTip(a.text())
        vboxcon, self.framew = QHBoxLayout(co), QComboBox()
        [vboxcon.addWidget(a) for a in (groupl, groupr)]
        self.chrt = QCheckBox('LOW CPU priority for Backend Process')
        self.framew.addItems(['nosetests', 'PyTest', 'DocTest', 'Unittest',
                              'Django_Test', 'Django-Nose', 'None'])
        self.framew.currentIndexChanged.connect(lambda:  #FIXME refactor for 3
            QMessageBox.information(self.dock, __doc__, '<b>Only Nose for now'))
        self.framew.currentIndexChanged.connect(lambda:  #FIXME refactor for 3
            self.framew.setCurrentIndex(0))
        vboxg1 = QVBoxLayout(self.tab1)
        for each_widget in (QLabel('<b>Framework'), self.framew, self.chrt, co):
            vboxg1.addWidget(each_widget)

        self.t2ck1, self.t2sp1 = QCheckBox('Activate Coverage'), QSpinBox()
        self.t2ck2 = QCheckBox('Erase previously collected Coverage before run')
        self.t2ck3 = QCheckBox('Include all tests modules in Coverage reports')
        self.t2ck4 = QCheckBox('Include all python files on working directory')
        self.t2ck5 = QCheckBox('Produce HTML Coverage reports information')
        self.t2ck6 = QCheckBox('Include Branch Coverage in Coverage reports')
        self.t2sp1.setRange(10, 90)
        self.t2sp1.setValue(75)
        vboxg2 = QVBoxLayout(self.tab2)
        for each_widget in (QLabel('<b>Min Percentage'), self.t2sp1, self.t2ck1,
            self.t2ck2, self.t2ck3, self.t2ck4, self.t2ck5, self.t2ck6):
            vboxg2.addWidget(each_widget)

        groupi, groupd, vbxg3 = QGroupBox(), QGroupBox(), QHBoxLayout(self.tab3)
        vboxgi, vboxgd = QVBoxLayout(groupi), QVBoxLayout(groupd)
        self.t3ck1 = QCheckBox('Activate DocTest to find and run doctests')
        self.t3ck2 = QCheckBox('Look for any doctests in tests modules too')
        self.t3ck3 = QCheckBox('Activate isolation (Do Not use with Coverage!)')
        self.t3ck4 = QCheckBox('Use Detailed Errors, evaluate failed asserts')
        for a in (self.t3ck1, self.t3ck2, self.t3ck3, self.t3ck4):
            vboxgi.addWidget(a)
            a.setToolTip(a.text())
        self.t3ck5 = QCheckBox('Disable special handling of SkipTest exception')
        self.t3ck6 = QCheckBox('Run the tests that failed in the last test run')
        self.t3ck7 = QCheckBox('Use AllModules, Collect tests from all modules')
        self.t3ck8 = QCheckBox('Collect tests names only, do Not run any tests')
        for a in (self.t3ck5, self.t3ck6, self.t3ck7, self.t3ck8):
            vboxgd.addWidget(a)
            a.setToolTip(a.text())
        [vbxg3.addWidget(a) for a in (groupi, groupd)]

        self.t4le1, self.t4le2 = QLineEdit(), QLineEdit(path.expanduser("~"))
        self.t4le1.setCompleter(self.completer)
        self.t4le2.setCompleter(self.completer)
        self.t4le1.setPlaceholderText(' /full/path/to/a/folder/ ')
        self.t4le2.setPlaceholderText(' /full/path/to/a/folder/ ')
        le1b = QPushButton(QIcon.fromTheme("folder-open"), 'Open')
        le1b.setMinimumSize(50, 50)
        le1b.clicked.connect(lambda: self.t4le1.setText(
            QFileDialog.getExistingDirectory(None, '', path.expanduser("~"))))
        le2b = QPushButton(QIcon.fromTheme("folder-open"), 'Open')
        le2b.clicked.connect(lambda: self.t4le2.setText(
            QFileDialog.getExistingDirectory(None, '', path.expanduser("~"))))
        vboxg4 = QVBoxLayout(self.tab4)
        for a in (QLabel('<b>Directory to look for Tests'), self.t4le1, le1b,
            QLabel('<b>Directory to generate HTML Coverage'), self.t4le2, le2b):
            vboxg4.addWidget(a)
            a.setToolTip(a.text())

        self.t5le1 = QLineEdit(r'(?:^|[\b_\./-])[Tt]est')
        self.t5le2 = QLineEdit()
        self.t5le3, vboxg5 = QLineEdit(), QVBoxLayout(self.tab5)
        r = QPushButton('Reset')
        r.clicked.connect(lambda: self.t5le1.setText(r'(?:^|[\b_\./-])[Tt]est'))
        for a in (QLabel('<b>Matching Name Regex to be test'), self.t5le1, r,
            QLabel('<b>Force Include Regex Tests'), self.t5le2,
            QLabel('<b>Force Exclude Regex Tests'), self.t5le3):
            vboxg5.addWidget(a)
            a.setToolTip(a.text())

        self.output = QTextEdit(''' Engineering is the art of making what you
            want from things you can get.    -Dhobi''')
        self.runbtn = QPushButton(QIcon.fromTheme("face-sad"), 'Start Testing!')
        self.runbtn.setMinimumSize(75, 50)
        self.runbtn.clicked.connect(self.run)
        glow = QGraphicsDropShadowEffect(self)
        glow.setOffset(0)
        glow.setBlurRadius(99)
        glow.setColor(QColor(99, 255, 255))
        self.runbtn.setGraphicsEffect(glow)
        self.kbt = QPushButton(QIcon.fromTheme("application-exit"), 'Kill')
        self.kbt.clicked.connect(lambda: self.process.kill())
        vboxg6 = QVBoxLayout(self.tab6)
        for each_widget in (QLabel('Logs'), self.output, self.runbtn, self.kbt):
            vboxg6.addWidget(each_widget)
        [a.setChecked(True) for a in (self.chrt, self.qckb2, self.qckb3,
                                      self.qckb10, self.t2ck1, self.t2ck2,
                                      self.t2ck5, self.t3ck1, self.t3ck4)]
        self.mainwidget.setCurrentIndex(4)

    def readOutput(self):
        """Read and append output to the logBrowser"""
        self.output.append(str(self.process.readAllStandardOutput()))

    def readErrors(self):
        """Read and append errors to the logBrowser"""
        self.output.append(str(self.process.readAllStandardError()))

    def run(self):
        """Main function calling vagrant to generate the vm"""
        if not len(self.t4le1.text()):
            QMessageBox.information(self.dock, __doc__,
                '<b style="color:red">ERROR: Target Folder can not be Empty !')
            return
        self.output.clear()
        self.output.append('INFO: OK: Starting at {}'.format(datetime.now()))
        self.runbtn.setDisabled(True)
        #nose = True if self.framew.currentText() in 'nosetests' else False
        cmd = ' '.join(('chrt -i 0' if self.chrt.isChecked() else '',
            # tab 1
            self.framew.currentText(),
            '--verbose' if self.qckb3.isChecked() else '--quiet',
            '--stop' if self.qckb4.isChecked() else '',
            '--exe' if self.qckb5.isChecked() else '--noexe',
            '--no-byte-compile' if self.qckb6.isChecked() else '',
            '--no-path-adjustment' if self.qckb7.isChecked() else '',
            '--traverse-namespace' if self.qckb8.isChecked() else '',
            '--nocapture' if self.qckb9.isChecked() else '',
            '--logging-clear-handlers' if self.qckb10.isChecked() else '',
            # tab 2
            '--with-coverage' if self.t2ck1.isChecked() else '',
            '--cover-erase' if self.t2ck2.isChecked() else '',
            '--cover-tests' if self.t2ck3.isChecked() else '',
            '--cover-inclusive' if self.t2ck4.isChecked() else '',
            '--cover-html' if self.t2ck5.isChecked() else '--cover-xml',
            '--cover-branches' if self.t2ck6.isChecked() else '',
            '--cover-min-percentage={}'.format(self.t2sp1.value()),
            # tab 3
            '--with-doctest' if self.t3ck1.isChecked() else '',
            '--doctest-tests' if self.t3ck2.isChecked() else '',
            '--with-isolation' if self.t3ck3.isChecked() else '',
            '--detailed-errors' if self.t3ck4.isChecked() else '',
            '--no-skip' if self.t3ck5.isChecked() else '',
            '--failed' if self.t3ck6.isChecked() else '',
            '--all-modules' if self.t3ck7.isChecked() else '',
            '--collect-only' if self.t3ck8.isChecked() else '',
            # tab 4
            '--where="{}"'.format(self.t4le1.text()),
            '--cover-html-dir="{}"'.format(self.t4le2.text()) if self.t2ck5.isChecked() else '--cover-xml-file={}'.format(path.join(self.t4le2.text(), 'coverage_ninja.xml')),
            # tab 5
            '--match="{}"'.format(self.t5le1.text().encode('utf-8')) if len(self.t5le1.text()) else '',
            '--include="{}"'.format(self.t5le2.text()) if len(self.t5le2.text()) else '',
            '--exclude="{}"'.format(self.t5le3.text()) if len(self.t5le3.text()) else '',
        ))
        self.output.append('INFO: OK: Command: {}'.format(cmd))
        with open(path.join(self.t4le2.text(), 'tests_run_ninja.sh'), 'w') as f:
            self.output.append('INFO: OK : Writing tests_run_ninja.sh')
            f.write('#!/usr/bin/env bash\n# -*- coding: utf-8 -*-\n\n' + cmd)
        try:
            chmod(path.join(self.t4le2.text(), 'tests_run_ninja.sh'), 0775)
        except:
            chmod(path.join(self.t4le2.text(), 'tests_run_ninja.sh'), 0o775)
        self.output.append('INFO: OK: Running Tests !')
        self.process.start(cmd)
        if not self.process.waitForStarted():
            self.output.append('ERROR: FAIL: Unkown Error !')
            self.runbtn.setEnabled(True)
            return
        self.runbtn.setEnabled(True)

    def _process_finished(self):
        """finished sucessfully"""
        self.output.append('INFO: OK: Finished at {}'.format(datetime.now()))
        if self.qckb2.isChecked() is True:
            with open(path.join(self.t4le2.text(), 'test_ninja.log'), 'w') as f:
                self.output.append('INFO: OK: Writing .LOG')
                f.write(self.output.toPlainText())
        if self.qckb1.isChecked() is True:
            self.output.append('INFO:Opening Target Folder')
            try:
                startfile(self.t4le2.text())
            except:
                Popen(["xdg-open", self.t4le2.text()])

    def finish(self):
        ' clear when finish '
        self.process.kill()


###############################################################################


if __name__ == "__main__":
    print(__doc__)
