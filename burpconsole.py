# -*- coding: utf-8 -*-
'''
burpconsole
~~~~~~~~~~~

This module provides a Jython Interpreter Console Tab to Burp.
'''
from java.awt.event import ActionListener
from javax.swing import JMenuItem, JScrollPane

from burp import IBurpExtender, IContextMenuFactory, ITab

from array import array
import inspect
import os
import sys

# Patch dir this file was loaded from into the path
# (Burp doesn't do it automatically)
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(
        inspect.getfile(inspect.currentframe()))), '.'))

from console import Console


class BurpExtender(IBurpExtender, IContextMenuFactory, ITab):

    def registerExtenderCallbacks(self, callbacks):
        self.callbacks = callbacks
        self.helpers = callbacks.helpers

        self.console = Console(self, namespace={
            'callbacks': callbacks,
            'helpers': callbacks.helpers,
            })

        self.scrollpane = JScrollPane()
        self.scrollpane.setViewportView(self.console.textpane)

        callbacks.setExtensionName("Jython Console")
        callbacks.addSuiteTab(self)
        callbacks.registerContextMenuFactory(self)
        callbacks.customizeUiComponent(self.getUiComponent())

    def getUiComponent(self):
        return self.scrollpane

    def getTabCaption(self):
        return "Console"

    def createMenuItems(self, invocation):
        menus = []
        messages = invocation.getSelectedMessages()

        if messages:
            items = self.interpreter.getLocals().get('items', [])
            context = 'Assign' if not items else 'Append'
            menu = JMenuItem("%s to local variable items in Console" % (context, ))
            menu.addActionListener(AssignLocalsActionListener(self, 'items', messages))
            menus.append(menu)

        return menus

    @property
    def interpreter(self):
        return self.console.interp


class AssignLocalsActionListener(ActionListener):
    def __init__(self, extender, name, value):
        self.extender = extender
        self.name = name
        self.value = value

    def actionPerformed(self, event):
        obj = self.extender.interpreter.get(self.name)

        if isinstance(obj, (list, array)):
            obj.extend(list(self.value))
        else:
            obj = self.value

        self.extender.interpreter.set(self.name, obj)

        return
