import gi
gi.require_version("Gtk","3.0")

from gi.repository import Gtk

import serial.tools.list_ports as portlists
import serial
import argparse
import re
import logging
import os
import threading
from datetime import datetime



ERROR_CODE = "\033[1;31m"
BAUD = 115200
LOG_DIR = "logs"

#here's for importing the other files of spacelab-transmitter that are missing or not ready

#CONSTANTS
_UI_FILE_LOCAL                  = os.path.abspath(os.path.dirname(__name__)) + '/data/ui/spacelab-Serial_COM.glade'
_UI_FILE_LINUX_SYSTEM           = '/usr/share/spacelab-Serial_COM/spacelab-Serial_COM.glade'

_ICON_FILE_LOCAL                = os.path.abspath(os.path.dirname(__name__)) + '/data/img/spacelab_transmitter_256x256.png'

_LOGO_FILE_LOCAL                = os.path.abspath(os.path.dirname(__name__)) + '/data/img/spacelab-logo-full-400x200.png'

_DIR_CONFIG_LINUX               = '.spacelab-Serial_COM'
class Serial_COM:
    def __init__(self):
        self.builder = Gtk.Builder()
        
        # Importing .glade file
        if os.path.isfile(_UI_FILE_LOCAL):
            self.builder.add_from_file(_UI_FILE_LOCAL)
        else:
            self.builder.add_from_file(_UI_FILE_LINUX_SYSTEM)

        self.Serial_config = {
            "Serial_Port" : [None, "/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyUSB2", "/dev/ttyUSB3"],
            "Baud_Rate" : [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400],
            "Parity" : [serial.PARITY_NONE, serial.PARITY_EVEN, serial.PARITY_ODD, serial.PARITY_MARK, serial.PARITY_SPACE],
            "Stop_bits" : [serial.STOPBITS_ONE , serial.STOPBITS_ONE_POINT_FIVE , serial.STOPBITS_TWO],
            "Data_bits" : [serial.FIVEBITS , serial.SIXBITS , serial.SEVENBITS , serial.EIGHTBITS]
        }

        self.builder.connect_signals(self)
        self._build_widgets()
        self._load_preferences()
        self.init_Time = datetime.now()
        self.setup_logging("OBDH", LOG_DIR)

        self.run()

    def _build_widgets(self):

        # Main Window
        self.window = self.builder.get_object("CubeSAT_COM")
        if os.path.isfile(_ICON_FILE_LOCAL):
            self.window.set_icon_from_file(_ICON_FILE_LOCAL)
        else:
            pass
            # self.window.set_icon_from_file(_ICON_FILE_LINUX_SYSTEM)
        self.window.set_title("CubeSAT_COM")

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

        self.Recieved_Text = self.builder.get_object("Received_Text")

        self.Text_Commands = self.builder.get_object("Text_Commands")

        # Serial Port Settings
        self.Serial_Port_Box1 = self.builder.get_object("Serial_Port1")
        self.Baud_Rate_Box1 = self.builder.get_object("Baud_Rate1")
        self.Send_option = self.builder.get_object("Send_Switch")

        # Log Settings
        self.Log_Dir = self.builder.get_object("Log_DIR")
        self.Module = self.builder.get_object("Module")
        self.Log_Record = self.builder.get_object("Record_Switch")

        # Settings Window
        self.COMSettings = self.builder.get_object("COMSettings")
        self.COMSettings.set_title("COMSettings")

        # Settings Window Buttons
        self.Save_Preferences = self.builder.get_object("Save_Preferences")
        self.Save_Preferences.connect("clicked", self.on_Save_Preferences_clicked)

        self.Discard_Options = self.builder.get_object("Discard_Options")
        self.Discard_Options.connect("clicked", self.on_Discard_Options_clicked)

    def _load_preferences(self):
        self.button_connect.set_sensitive(True)
        self.button_disconnect.set_sensitive(False)
        self.button_preferences.set_sensitive(True)

        self.Command.set_editable(False)
        self.Recieved_Text.set_editable(False)
        self.Button_Send.set_sensitive(False)

        # Serial Port Settings
        self.Serial_Port_Box = self.builder.get_object("Serial_Port")
        self.Baud_Rate_Box = self.builder.get_object("Baud_Rate")
        self.Parity_Box = self.builder.get_object("Parity")
        self.Stop_bits_Box = self.builder.get_object("Stop_bits")
        self.Data_bits_Box = self.builder.get_object("Data_bits")
        self.Flow_Control_Box = self.builder.get_object("Flow_Control")

        self.load_Settings()

        for comport in serial.tools.list_ports.comports(): self.Serial_Port_Box1.append_text(str(comport.device))
        self.Serial_Port_Box1.set_active_id(None)

        for baud in self.Serial_config["Baud_Rate"]: self.Baud_Rate_Box1.append_text(str(baud))
        self.Baud_Rate_Box1.set_active(next((index for index, row in enumerate(self.Baud_Rate_Box1.get_model()) if row[0] == str(115200)), -1))
        
        self.Serial_Port = None
        self.Baud_Rate = 115200
        self.Parity = serial.PARITY_NONE
        self.Stop_bits = serial.STOPBITS_ONE
        self.Data_bits = serial.EIGHTBITS

    def remove_ansi_color(string: str) -> str:
        ansi_escape = re.compile(r"\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        return ansi_escape.sub("", string)

    def run(self):
        self.window.show_all()
        Gtk.main()

    def onDestroy(self, *args):
        Gtk.main_quit()    
   
    def serial_connection(self, widget):
        self.Serial = serial.Serial(port=self.Serial_Port, baudrate=self.Baud_Rate, parity=self.Parity, stopbits=self.Stop_bits, bytesize=self.Data_bits, timeout=1)#, flowcontrol=self.Flow_Control)

        self.button_connect.set_sensitive(False)
        self.button_disconnect.set_sensitive(True)
        self.button_preferences.set_sensitive(False)

        self.Command.set_editable(True)
        self.Button_Send.set_sensitive(True)
        self.Recieved_Text.set_editable(True)

        self.thread = threading.Thread(target=self.Serial_Receive_event, args=(None))   
        self.thread.daemon = True

    def serial_disconnect(self, widget):
        self.button_connect.set_sensitive(True)
        self.button_disconnect.set_sensitive(False)
        self.button_preferences.set_sensitive(True)

        self.Command.set_editable(False)
        self.Button_Send.set_sensitive(False)
        self.Recieved_Text.set_editable(False)

    def on_preferences_clicked(self, button):
        self.COMSettings.show()

    def load_Settings(self):
        for comport in serial.tools.list_ports.comports(): self.Serial_Port_Box.append_text(str(comport.device))
        self.Serial_Port_Box.set_active(next((index for index, row in enumerate(self.Serial_Port_Box.get_model()) if row[0] == "/dev/ttyUSB0"), -1))

        for baud in self.Serial_config["Baud_Rate"]: self.Baud_Rate_Box.append_text(str(baud))
        self.Baud_Rate_Box.set_active(next((index for index, row in enumerate(self.Baud_Rate_Box.get_model()) if row[0] == str(115200)), -1))

        for Parity in self.Serial_config["Parity"]:  self.Parity_Box.append_text(str(Parity))
        self.Parity_Box.set_active(next((index for index, row in enumerate(self.Parity_Box.get_model()) if row[0] == str(serial.PARITY_NONE)), -1))

        for stopbits in self.Serial_config["Stop_bits"]: self.Stop_bits_Box.append_text(str(stopbits))
        self.Stop_bits_Box.set_active(next((index for index, row in enumerate(self.Stop_bits_Box.get_model()) if row[0] == str(serial.STOPBITS_ONE)), -1))

        for databits in self.Serial_config["Data_bits"]: self.Data_bits_Box.append_text(str(databits))
        self.Data_bits_Box.set_active(next((index for index, row in enumerate(self.Data_bits_Box.get_model()) if row[0] == str(serial.EIGHTBITS)), -1))

    def Serial_Receive_event(self):
        self.Serial.open()
        while self.Recieved_Text.get_sensitive() and self.Serial.is_open():
            if self.Serial.in_waiting > 0:
                self.receive_command()
        self.Serial.close()
        return
            
    def on_Save_Preferences_clicked(self, button):
        self.Serial_Port = "/dev/ttyUSB0"
        self.Baud_Rate = next((baud for baud in self.Serial_config["Baud_Rate"] if str(baud) == self.Baud_Rate_Box.get_active_text()), 115200)
        self.Parity = next((parity for parity in self.Serial_config["Parity"] if str(parity) == self.Parity_Box.get_active_text()), serial.PARITY_NONE)
        self.Stop_bits = next((stopbits for stopbits in self.Serial_config["Stop_bits"] if str(stopbits) == self.Stop_bits_Box.get_active_text()), serial.STOPBITS_ONE)
        self.Data_bits = next((databits for databits in self.Serial_config["Data_bits"] if str(databits) == self.Data_bits_Box.get_active_text()), serial.EIGHTBITS)
        self.Serial_Port_Box1.set_active(next((index for index, row in enumerate(self.Serial_Port_Box.get_model()) if row[0] == self.Serial_Port_Box.get_active_text()), -1))
        self.Baud_Rate_Box1.set_active(next((index for index, row in enumerate(self.Baud_Rate_Box.get_model()) if row[0] == str(self.Baud_Rate_Box.get_active_text())), -1))
        self.COMSettings.hide()

    def on_Discard_Options_clicked(self, button):
        self.COMSettings.hide()

    def on_Command_key_press(self, widget, event):
        pass
        # if event.keyval == Gtk.KEY_Return or event.keyval == Gtk.KEY_KP_Enter: 
        #    self.send_command()

    def on_Button_Send_clicked(self, button):
        self.send_command()
        print("To do...")

    def on_toolbutton_clean_clicked(self, button):
        self.Recieved_Text.set_buffer("")

    def send_command(self):
        self.Serial.write(self.Command.get_text().encode())
        self.Command.set_text("")

    def receive_command(self):
        received_text = self.Recieved_Text.get_buffer()
        received_text.insert(received_text.get_end_iter(), self.Serial.readline().decode() + "\n",-1)
        self.Recieved_Text.set_buffer(received_text)
        if self.Send_option.get_active(): self.save_logs(received_text)

    def setup_logging(self,module: str, log_dir: str):
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

    # def log_trace_cli():
    #     cli_parser = argparse.ArgumentParser(
    #         prog="log_trace.py",
    #         description="Reads the floripasat-2 modules log through UART",
    #     )

    #     cli_parser.add_argument("PORT", type=str, help="serial port to listen to")

    #     cli_parser.add_argument(
    #         "-f",
    #         "--log_file",
    #         action="store",
    #         default="module",
    #         type=str,
    #         help="sets the log file name",
    #     )

    #     cli_parser.add_argument(
    #         "-d",
    #         "--log_dir",
    #         action="store",
    #         default=LOG_DIR,
    #         type=str,
    #         help="sets the log directory",
    #     )

    #     args = vars(cli_parser.parse_args())

    #     self.setup_logging(args["log_file"], args["log_dir"])

    #     dev = self.serial_connection(args["PORT"], BAUD)

    #     try:
    #         while True:
    #             log_line = self.serial_read()
    #             print(log_line, end="")
    #             save_logs(log_line)

    #     except KeyboardInterrupt:
    #         print("Keyboard interrupt detected. Exiting...")

    #     finally:
    #         dev.close()
# print([comport.device for comport in serial.tools.list_ports.comports()])


def main():
    prog = Serial_COM()
    
if __name__ == "__main__":
    main()
