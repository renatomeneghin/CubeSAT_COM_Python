import gi
gi.require_version("Gtk","3.0")

from gi.repository import Gtk

import serial.tools.list_ports as portlists
import serial
import argparse
import re
import logging
import os

#here's for importing the other files of spacelab-transmitter that are missing or not ready

#CONSTANTS
_UI_FILE_LOCAL                  = os.path.abspath(os.path.dirname(__file__)) + '/data/ui/spacelab-Serial_COM.glade'
_UI_FILE_LINUX_SYSTEM           = '/usr/share/spacelab-Serial_COM/spacelab-Serial_COM.glade'

_ICON_FILE_LOCAL                = os.path.abspath(os.path.dirname(__file__)) + '/data/img/spacelab_transmitter_256x256.png'
# _ICON_FILE_LINUX_SYSTEM         = '/usr/share/icons/spacelab_transmitter_256x256.png'

_LOGO_FILE_LOCAL                = os.path.abspath(os.path.dirname(__file__)) + '/data/img/spacelab-logo-full-400x200.png'
# _LOGO_FILE_LINUX_SYSTEM         = '/usr/share/spacelab_transmitter/spacelab-logo-full-400x200.png'

_DIR_CONFIG_LINUX               = '.spacelab-Serial_COM'
# _DIR_CONFIG_WINDOWS             = 'spacelab-Serial_COM'

# _SAT_JSON_FLORIPASAT_1_LOCAL    = os.path.abspath(os.path.dirname(__file__)) + '/data/satellites/floripasat-1.json'
# _SAT_JSON_FLORIPASAT_1_SYSTEM   = '/usr/share/spacelab_transmitter/floripasat-1.json'
# _SAT_JSON_GOLDS_UFSC_LOCAL    = os.path.abspath(os.path.dirname(__file__)) + '/data/satellites/GOLDS_UFSC.json'
# _SAT_JSON_GOLDS_UFSC_SYSTEM   = '/usr/share/spacelab_transmitter/GOLDS_UFSC.json'

_DEFAULT_CALLSIGN               = 'PP5UF'
_DEFAULT_LOCATION               = 'Florianópolis'
_DEFAULT_COUNTRY                = 'Brazil'

class Serial_COM:
    def __init__(self):
        self.builder = Gtk.builder()
        # Importing .glade file
        if os.path.isfile(_UI_FILE_LOCAL):
            self.builder.add_from_file(_UI_FILE_LOCAL)
        else:
            self.builder.add_from_file(_UI_FILE_LINUX_SYSTEM)

        self.builder.connect(self)

    def onDestroy(self, *args):
        Gtk.main_quit()


    def onButtonPressed(self, button):
        print("Hello World!")


# print([comport.device for comport in serial.tools.list_ports.comports()])


