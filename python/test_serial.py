import serial
import time

PORT = "COM3"
BAUD_RATE = 9600

arduino = serial.Serial(PORT, BAUD_RATE)

time.sleep(2)

print("Arduino connected!")
print()
print("Commands:")
print("0 - All OFF")
print("1 - LED 1")
print("2 - LED 1 + 2")
print("3 - LED 1 + 2 + 3")
print("4 - LED 1 + 2 + 3 + 4")
print("5 - All LEDs")
print("q - Quit")
print()

try:

    while True:

        command = input("Enter command: ")

        if command.lower() == "q":
            break

        if command in ["0", "1", "2", "3", "4", "5"]:

            # Old Arduino test protocol
            arduino.write((command + "\n").encode())

        else:
            print("Please enter 0, 1, 2, 3, 4, 5 or q.")

finally:

    arduino.close()

    print("Arduino disconnected.")