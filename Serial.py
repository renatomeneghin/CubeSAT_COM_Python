

import serial.tools.list_ports as portlists
import serial
import argparse
import re
import logging
import os

def onDestroy(self, *args):
    Gtk.main_quit()


def onButtonPressed(self, button):
    print("Hello World!")


print([comport.device for comport in serial.tools.list_ports.comports()])

