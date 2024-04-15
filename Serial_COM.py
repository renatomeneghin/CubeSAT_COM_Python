import gi
gi.require_version("Gtk","3.0")

from gi.repository import Gtk

import serial.tools.list_ports as portlists
import serial
import argparse
import re
import logging
import os

ERROR_CODE = "\033[1;31m"
BAUD = 115200
LOG_DIR = "logs"

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

# _DEFAULT_CALLSIGN               = 'PP5UF'
# _DEFAULT_LOCATION               = 'Florianópolis'
# _DEFAULT_COUNTRY                = 'Brazil'

class Serial_COM:
    def __init__(self):
        self.builder = Gtk.builder()
        # Importing .glade file
        if os.path.isfile(_UI_FILE_LOCAL):
            self.builder.add_from_file(_UI_FILE_LOCAL)
        else:
            self.builder.add_from_file(_UI_FILE_LINUX_SYSTEM)

        self.builder.connect_signals(self)

        self._build_widgets()

        self._load_preferences()

        self.ngham = pyngham.PyNGHam()

        self.decoded_packets_index = list()

    def _build_widgets(self):
        self.window = self.builder.get_object("CubeSAT_COM")
        self.window = self.builder.get_object("window_main")
        if os.path.isfile(_ICON_FILE_LOCAL):
            self.window.set_icon_from_file(_ICON_FILE_LOCAL)
        else:
            self.window.set_icon_from_file(_ICON_FILE_LINUX_SYSTEM)
        self.window.set_wmclass(self.window.get_title(), self.window.get_title())
        self.window.connect("destroy", Gtk.main_quit)

        # Serial Port Settings
        self.Serial_Port = self.builder.get_object("Serial_Port")
        self.Baud_Rate = self.builder.get_object("Baud_Rate")
        self.Parity = self.builder.get_object("Parity")
        self.Stop_bits = self.builder.get_object("Stop_bits")
        self.Data_bits = self.builder.get_object("Data_bits")
        self.Flow_Control = self.builder.get_object("Flow_Control")

    def remove_ansi_color(string: str) -> str:
        ansi_escape = re.compile(r"\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        return ansi_escape.sub("", string)

    def run(self):
        self.window.show_all()

        Gtk.main()

    def serial_connection(self):
        self.Serial = serial.Serial(port=self.Serial_Port, baudrate=self.Baud_Rate, parity=self.Parity, stopbits=self.Stop_bits, bytesize=self.Data_bits, timeout=1, flowcontrol=self.Flow_Control)
    
    def serial_disconnect(self):
        self.Serial.close()

    def onDestroy(self, *args):
        Gtk.main_quit()

    def onButtonPressed(self, button):
        print("Hello World!")

    def setup_logging(module: str, log_dir: str):
        filename = "./" + log_dir + "/" + module + ".log"

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            print(f"Creating log directory on: ./{log_dir}")

        if not os.path.exists(filename):
            with open(filename, "w") as f:
                f.write("")
            print(f"Creating log file on: {filename}")

        logging.basicConfig(
            filename=filename,
            level=logging.DEBUG,
            format="[%(asctime)s][%(levelname)s] > %(message)s",
        )


    # def remove_ansi_color(string: str) -> str:
    #     return re.compile(r"\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])").sub("", string)

    def save_logs(line: str):
        """
        Saves logs by removing ANSI color codes from the input line and logs the line with an error level if it contains an error code, otherwise logs with an info level.
        Parameters:
            line (str): The input line to be logged.
        Returns:
            None
        """
        logline = re.compile(r"\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])").sub("", line)

        if ERROR_CODE in line:
            logging.error(logline)
        else:
            logging.info(logline)


    def serial_read(self) -> str:
        return self.Serial.readline().decode()


    def log_trace_cli():
        cli_parser = argparse.ArgumentParser(
            prog="log_trace.py",
            description="Reads the floripasat-2 modules log through UART",
        )

        cli_parser.add_argument("PORT", type=str, help="serial port to listen to")

        cli_parser.add_argument(
            "-f",
            "--log_file",
            action="store",
            default="module",
            type=str,
            help="sets the log file name",
        )

        cli_parser.add_argument(
            "-d",
            "--log_dir",
            action="store",
            default=LOG_DIR,
            type=str,
            help="sets the log directory",
        )

        args = cli_parser.parse_args()

        setup_logging(args.log_file, args.log_dir)

        dev = serial_connection(args.PORT, BAUD)

        try:
            while True:
                log_line = self.serial_read()
                print(log_line, end="")
                save_logs(log_line)

        except KeyboardInterrupt:
            print("Keyboard interrupt detected. Exiting...")

        finally:
            dev.close()
# print([comport.device for comport in serial.tools.list_ports.comports()])


