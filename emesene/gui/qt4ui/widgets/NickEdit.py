# -*- coding: utf-8 -*-

#    This file is part of emesene.
#
#    emesene is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    emesene is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with emesene; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

'''This module contains the NickEdit class'''

import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore
from PyQt4.QtCore import Qt

from gui.qt4ui import Utils
from gui.qt4ui.Utils import tr

# important: at the moment emits "str" not "unicode"
# because of papyon raising exceptions. [anyway, it seems to work.]


class NickEdit(QtGui.QStackedWidget):
    '''A Nice nick / psm editor'''
    # pylint: disable=W0612
    NAME = 'MainPage'
    DESCRIPTION = 'The widget used to to edit a nick or a personal message'
    AUTHOR = 'Gabriele "Whisky" Visconti'
    WEBSITE = ''
    # pylint: enable=W0612

    nick_changed = QtCore.pyqtSignal(basestring)

    def __init__(self, allow_empty=False,
                 empty_message=tr('Click here to write'),
                 parent=None):
        QtGui.QStackedWidget.__init__(self, parent)

        self._allow_empty = allow_empty
        self._empty_message = u'<u>' + empty_message + u'</u>'
        self._is_empty_message_displayed = False
        self._text = ''

        self.line_edit = QtGui.QLineEdit()
        self.label = QLabelEmph(QtCore.QString('If you see this, " \
                            "please invoke setText on NickEdit.'))
        self.set_text(QtCore.QString())

        self.addWidget(self.line_edit)
        self.addWidget(self.label)
        self.setCurrentWidget(self.label)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Fixed)
        self.label.clicked.connect(self._on_label_clicked)
        self.line_edit.editingFinished.connect(self._on_line_edited)

    def text(self):
        '''Returns the displayed text as a QString'''
        if self._is_empty_message_displayed:
            return QtCore.QString()
        text = unicode(self._text)
        #text = Utils.unescape(text)
        return QtCore.QString(text)

    def set_text(self, text):
        '''Displays the given text'''
        #NOTE: do we have to set also the QLineEdit's text?
        #<-> method could be called while the QLEdit is active?
        self._text = unicode(text)
        text = Utils.escape(unicode(text))
        parsed_text = Utils.parse_emotes(text)
        text = QtCore.QString(text)
        if not text.isEmpty():
            self._is_empty_message_displayed = False
            self.label.setText(parsed_text)
        elif self._allow_empty:
            self._is_empty_message_displayed = True
            self.label.setText(self._empty_message)

    def _on_label_clicked(self):
        '''Slot called when the user clicks on the label of
        this widget'''
        self.line_edit.setText(self._text)
        self.setCurrentWidget(self.line_edit)
        self.line_edit.setFocus(Qt.MouseFocusReason)

    def _on_line_edited(self):
        '''Slot called when the user finishes editing the nick'''
        text = self.line_edit.text()
        self.set_text(text)
        #if the text is empty, and it is not allowed, this must be handled
        # set_text handles this, so we pass the text to set_text, and then
        # retrieve it again,
        # set_text/text unescape the string too
        self.setCurrentWidget(self.label)
        self.nick_changed.emit(str(self.text()))


class QLabelEmph(QtGui.QLabel):
    '''Convenience class for a more interesting QLabel behaviour'''
    _LE = QtCore.QString('<u><em>')
    _RI = QtCore.QString('</em></u>')

    clicked = QtCore.pyqtSignal()
    def __init__(self, text=QtCore.QString(), parent=None):
        '''Constructor'''
        QtGui.QLabel.__init__(self, parent)
        self._text = QtCore.QString()
        self.setText(text)

# -------------------- QT_OVERRIDE

    #you can pass either a pythonic string or a QString
    def setText(self, text):
        '''sets the text'''
        text = QtCore.QString(text)
        self._text = QtCore.QString(text)
        QtGui.QLabel.setText(self, text)

    #returns a QString
    def text(self):
        '''Returns the text'''
        return self._text

    def mousePressEvent(self, event):
        '''Handles mouse presses'''
        QtGui.QLabel.mousePressEvent(self, event)
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

    #received even if mouse tracking not explicitly enabled
    def enterEvent(self, event):
        '''Handles mouse-in events'''
        QtGui.QLabel.setText(self, QLabelEmph._LE +
                                   self._text +
                                   QLabelEmph._RI)
        event.accept()

    #received even if mouse tracking not explicitly enabled
    def leaveEvent(self, event):
        '''Handles mouse-out events'''
        QtGui.QLabel.setText(self, self._text)
        event.accept()
