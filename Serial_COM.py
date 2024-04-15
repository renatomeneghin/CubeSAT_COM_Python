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

    def _build_widgets(self):

        # Main Window
        self.window = self.builder.get_object("CubeSAT_COM")
        if os.path.isfile(_ICON_FILE_LOCAL):
            self.window.set_icon_from_file(_ICON_FILE_LOCAL)
        else:
            pass
            # self.window.set_icon_from_file(_ICON_FILE_LINUX_SYSTEM)
        self.window.set_wmclass(self.window.get_title(), self.window.get_title())
        self.window.connect("destroy", Gtk.main_quit)

        # Action Buttons
        self.button_connect = self.builder.get_object("button_connect")
        self.button_connect.connect("clicked", self.serial_connection)

        self.button_disconnect = self.builder.get_object("button_disconnect")
        self.button_disconnect.connect("clicked", self.serial_disconnect)

        self.button_preferences = self.builder.get_object("button_preferences")
        self.button_preferences.connect("clicked", self.on_preferences_clicked)
        
        self.toolbutton_clean = self.builder.get_object("toolbutton_clean")
        self.toolbutton_clean.connect("clicked", self.on_toolbutton_clean_clicked)

        # Serial Commands
        self.Command = self.builder.get_object("Command")
        self.Command.connect("key-press-event", self.on_Command_key_press)

        self.Button_Send = self.builder.get_object("Button_Send")
        self.Button_Send.connect("clicked", self.on_Button_Send_clicked)

        self.Recieved_Text = self.builder.get_object("Recieved_Text")

        # Settings Window
        self.COMSettings = self.builder.get_object("COMSettings")

        # Settings Window Buttons
        self.Save_Preferences = self.builder.get_object("Save_Preferences")
        self.Save_Preferences.connect("clicked", self.on_Save_Preferences_clicked)

        self.Discard_Options = self.builder.get_object("Discard_Options")
        self.Discard_Options.connect("clicked", self.on_Discard_Options_clicked)

    def _load_preferences(self):
        self.Recieved_Text.set_editable(False)

        # Serial Port Settings
        self.Serial_Port_Box = self.builder.get_object("Serial_Port")
        self.Baud_Rate_Box = self.builder.get_object("Baud_Rate")
        self.Parity_Box = self.builder.get_object("Parity")
        self.Stop_bits_Box = self.builder.get_object("Stop_bits")
        self.Data_bits_Box = self.builder.get_object("Data_bits")
        self.Flow_Control_Box = self.builder.get_object("Flow_Control")

        self.Serial_Port = None
        self.Baud_Rate = 115200
        self.Parity = serial.PARITY_NONE
        self.Stop_bits = serial.STOPBITS_ONE
        self.Data_bits = serial.EIGHTBITS
        self.Flow_Control = serial.FLOWCONTROL_NONE


    def remove_ansi_color(string: str) -> str:
        ansi_escape = re.compile(r"\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        return ansi_escape.sub("", string)

    def run(self):
        self.window.show_all()
        Gtk.main()

    def onDestroy(self, *args):
        Gtk.main_quit()    
   
    def serial_connection(self):
        self.Serial = serial.Serial(port=self.Serial_Port, baudrate=self.Baud_Rate, parity=self.Parity, stopbits=self.Stop_bits, bytesize=self.Data_bits, timeout=1, flowcontrol=self.Flow_Control)
   
    def serial_disconnect(self):
        self.Serial.close()

    def on_preferences_clicked(self, button):
        self.COMSettings.show()
        self.load_Settings()

    def load_Settings(self):
        self.Serial_Port_Box.set_entry_text([comport.device for comport in serial.tools.list_ports.comports()])

        self.Serial_Port_Box.set_active_id(self.Serial_Port)
        self.Baud_Rate_Box.set_active_id(self.Baud_Rate)
        self.Parity_Box.set_active_id(self.Parity)
        self.Stop_bits_Box.set_active_id(self.Stop_bits)
        self.Data_bits_Box.set_active_id(self.Data_bits)
        self.Flow_Control_Box.set_active_id(self.Flow_Control)

        
    def on_Save_Preferences_clicked(self, button):
        self.Serial_Port = self.Serial_Port_Box.get_active_text()
        self.Baud_Rate = int(self.Baud_Rate_Box.get_active_text())
        self.Parity = self.Parity_Box.get_active_text()
        self.Stop_bits = int(self.Stop_bits_Box.get_active_text())
        self.Data_bits = int(self.Data_bits_Box.get_active_text())
        self.Flow_Control = self.Flow_Control_Box.get_active_text()
        self.COMSettings.hide()

    def on_Discard_Options_clicked(self, button):
        self.COMSettings.hide()

    def on_Command_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Return or event.keyval == Gdk.KEY_KP_Enter: 
            self.send_command()

    def on_Button_Send_clicked(self, button):
        self.send_command()

    def on_toolbutton_clean_clicked(self, button):
        self.Recieved_Text.set_text("")

    def send_command(self):
        self.Serial.write(self.Command.get_text().encode())
        self.Command.set_text("")

    def receive_command(self):
        self.Recieved_Text.set_text(self.serial_read())

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


