# -*- coding:utf-8 -*-
"""
/***************************************************************************
AutoFields
A QGIS plugin
Automatic vector field updates when modifying or creating features
                             -------------------
begin                : 2016-05-22 
copyright            : (C) 2016 by Germán Carrillo (GeoTux)
email                : gcarrillo@linuxmail.org 
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
from qgis.core import QgsApplication
from PyQt4.QtCore import ( Qt, QTranslator, QFileInfo, QCoreApplication, 
    QLocale, QSettings )
from PyQt4.QtGui import QIcon, QAction, QDockWidget
import resources_rc
from AutoFieldsDockWidget import AutoFieldsDockWidget
from AutoFieldManager import AutoFieldManager
from MessageManager import MessageManager


class AutoFields: 

  def __init__( self, iface ):
    self.iface = iface
    self.messageMode = 'production' # 'production' or 'debug'
    self.installTranslator()


  def initGui( self ):  
  
    # Remove Redo buttons from menus and toolbars, they can lead to crashes due 
    #   to a corrupted undo stack.
    redoActionList = [action for action in self.iface.advancedDigitizeToolBar().actions() if action.objectName() == u'mActionRedo']
    if redoActionList:
        self.iface.advancedDigitizeToolBar().removeAction( redoActionList[0] )
        self.iface.editMenu().removeAction( redoActionList[0] )    

    QSettings().setValue( "/shortcuts/Redo", "" ) # Override Redo shortcut

    # This block (2 options for disabling the Undo panel) didn't work
    #QSettings().setValue( '/UI/Customization/enabled', True )
    #QSettings( "QGIS", "QGISCUSTOMIZATION2" ).setValue( '/Customization/Panels/Undo', False )
    #undoDock = self.iface.mainWindow().findChild( QDockWidget, u'Undo' )
    #self.iface.removeDockWidget( undoDock )  
  
    # Create action that will start plugin configuration
    self.action = QAction(QIcon( ":/plugins/AutoFields/icon.png"), \
        "Configure automatic fields...", self.iface.mainWindow() )
    # connect the action to the run method
    self.action.triggered.connect( self.run )

    # Add custom submenu to Vector menu
    self.iface.addPluginToVectorMenu( "&AutoFields", self.action )
    
    # Add a custom toolbar
    self.toolbar = self.iface.addToolBar( "AutoFields" )
    self.toolbar.setObjectName("AutoFields")
    self.toolbar.addAction( self.action )

    
    self.messageManager = MessageManager( self.messageMode, self.iface )
    
    self.autoFieldManager = AutoFieldManager( self.messageManager, self.iface )
    self.autoFieldManager.readAutoFields()

    self.dockWidget = AutoFieldsDockWidget( self.iface.mainWindow(), self.iface, self.autoFieldManager, self.messageManager )
    self.iface.addDockWidget( Qt.RightDockWidgetArea, self.dockWidget )


  def unload( self ):
    # Remove the plugin menu and toolbar
    self.iface.removePluginVectorMenu( "&AutoFields", self.action )
    self.iface.mainWindow().removeToolBar( self.toolbar )

    self.autoFieldManager.disconnectAll()
    
    self.dockWidget.disconnectAll()
    self.dockWidget.close()
    self.iface.removeDockWidget( self.dockWidget )


  def run( self ):
    self.dockWidget.show()


  def installTranslator( self ):
    userPluginPath = os.path.join( os.path.dirname( str( QgsApplication.qgisUserDbFilePath() ) ), "python/plugins/AutoFields" )
    systemPluginPath = os.path.join( str( QgsApplication.prefixPath() ), "python/plugins/AutoFields" )
    translationPath = ''

    locale = QSettings().value( "locale/userLocale", type=str )
    myLocale = str( locale[0:2] )

    if os.path.exists( userPluginPath ):
      translationPath = os.path.join( userPluginPath, 'i18n', "AutoFields_" + myLocale + ".qm" )
    else:
      translationPath = os.path.join( systemPluginPath, 'i18n', "AutoFields_" + myLocale + ".qm" )

    if QFileInfo( translationPath ).exists():
      self.translator = QTranslator()
      self.translator.load( translationPath )
      QCoreApplication.installTranslator( self.translator )

