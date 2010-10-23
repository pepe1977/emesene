# -*- coding: utf-8 -*-

'''This module contains the NickEdit class'''

import PyKDE4.kdeui     as KdeGui
import PyKDE4.kdecore   as KdeCore
from PyKDE4.kdecore import i18n
import PyQt4.QtGui      as QtGui
import PyQt4.QtCore     as QtCore
from PyQt4.QtCore   import Qt

import xml

# important: at the moment emits "str" not "unicode"
# because of papyon raising exceptions. [anyway, it seems to work.]


class NickEdit(QtGui.QStackedWidget):
    '''A Nice nick / psm editor'''
    nick_changed = QtCore.pyqtSignal(basestring)
    def __init__(self, allow_empty=False, 
                 empty_message=i18n(QtCore.QString("Click here to write")),
                 parent=None):
        QtGui.QStackedWidget.__init__(self, parent)

        self._allow_empty = allow_empty
        self._empty_message = QtCore.QString("<u>") + \
                              empty_message + \
                              QtCore.QString("</u>")
        self._is_empty_message_displayed = False

        self.line_edit = KdeGui.KLineEdit()
        self.label = QLabelEmph(i18n(QtCore.QString("If you see this, " \
                            "please invoke setText on KNickEdit.")))

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
        text = unicode(self.label.text())
        text = xml.sax.saxutils.unescape(text)
        return QtCore.QString(text)
        
        
    def set_text(self, text):
        '''Displays the given text'''
        #NOTE: do we have to set also the KLineEdit's text? 
        #<-> method could be called while the KLEdit is active? 
        text = xml.sax.saxutils.escape(unicode(text)) 
        text = QtCore.QString(text)
        if not text.isEmpty():
            self._is_empty_message_displayed = False
            self.label.setText(text)
        elif self._allow_empty:
            self._is_empty_message_displayed = True
            self.label.setText(self._empty_message)


    def _on_label_clicked(self):
        '''Slot called when the user clicks on the label of 
        this widget'''
        text = self.text() # handles unescaping
        self.line_edit.setText(text) #remove this unicode once fixed
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
    _LE = QtCore.QString("<u><em>")
    _RI = QtCore.QString("</em></u>")
    
    clicked = QtCore.pyqtSignal()
    def __init__(self, text=QtCore.QString(), parent = None):
        '''Constructor'''
        QtGui.QLabel.__init__(self, parent)
        self._text = QtCore.QString()
        self.setText(text)
        
# -------------------- QT_OVERRIDE
    
    #you can pass either a pythonic string or a QString
    def setText(self, text): 
        # pylint: disable=C0103
        '''sets the text'''
        text = QtCore.QString(text)
        self._text = QtCore.QString(text) 
        QtGui.QLabel.setText(self, text)

    #returns a QString
    def text(self): 
        # pylint: disable=C0103
        '''Returns the text'''
        return self._text
        
    def mousePressEvent(self, event):
        # pylint: disable=C0103
        '''Handles mouse presses'''
        QtGui.QLabel.mousePressEvent(self, event)
        if event.button() == Qt.LeftButton:
            self.clicked.emit()    
            
    #received even if mouse tracking not explicitly enabled
    def enterEvent(self, event): 
        # pylint: disable=C0103
        '''Handles mouse-in events'''
        QtGui.QLabel.setText(self, QLabelEmph._LE + 
                                   self._text + 
                                   QLabelEmph._RI)
        event.accept()
        
    #received even if mouse tracking not explicitly enabled
    def leaveEvent(self, event): 
        # pylint: disable=C0103
        '''Handles mouse-out events'''
        QtGui.QLabel.setText(self, self._text)
        event.accept()

