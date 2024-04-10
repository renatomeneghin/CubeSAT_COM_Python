import serial.tools.list_ports as portlists
import serial

print([comport.device for comport in serial.tools.list_ports.comports()])

