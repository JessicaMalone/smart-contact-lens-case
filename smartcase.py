import json
import logging
import sys
import threading
import time
import grovepi
from agt import AlexaGadget

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

# GPIO Pins
LED = 5
BUTTON = 7
BUZZER = 8
thisLedAndOutwards = 3

testColorBlack = 0   # 0b000 #000000
testColorBlue = 1    # 0b001 #0000FF
testColorGreen = 2   # 0b010 #00FF00
testColorCyan = 3    # 0b011 #00FFFF
testColorRed = 4     # 0b100 #FF0000
testColorMagenta = 5 # 0b101 #FF00FF
testColorYellow = 6  # 0b110 #FFFF00
testColorWhite = 7   # 0b111 #FFFFFF

class SmartCaseGadget(AlexaGadget):
    """
    An Alexa Gadget that cycles through colors using RGB LED and
    reports the color to the skill upon button press
    """

    def __init__(self):
        super().__init__()
        
        self.isActive = False
        self.isSoundOnly = False
        self.isLEDOnly = False
        
        grovepi.pinMode(BUZZER,"OUTPUT")
        grovepi.pinMode(BUTTON,"INPUT")
        grovepi.pinMode(LED,"OUTPUT")
    
        grovepi.chainableRgbLed_init(LED, 2)
        grovepi.storeColor(0,0,0)
        grovepi.chainableRgbLed_pattern(LED, thisLedAndOutwards, 2)

        # Start threads
        threading.Thread(target=self._auto_thread, daemon=True).start()
    def on_connected(self, device_addr):
        """
        Gadget connected to the paired Echo device.
        :param device_addr: the address of the device we connected to
        """
        print("connected")

    def on_disconnected(self, device_addr):
        """
        Gadget disconnected from the paired Echo device.
        :param device_addr: the address of the device we disconnected from
        """
        print("disconnected")

    def on_custom_smartcasegadget_control(self, directive):
        print("got control")
        """
        Start buzzing
        """
        try:
            payload = json.loads(directive.payload.decode("utf-8"))
            print("Control payload: {}".format(payload), file=sys.stderr)
            control_type = payload["type"]
            if control_type == "where":
                self.isActive = True
            elif control_type == "light":
                self.isLEDOnly = True
            elif control_type == 'sound':
                self.isSoundOnly = True

        except KeyError:
            print("Missing expected parameters: {}".format(directive), file=sys.stderr)
            
    def _button_pressed(self):
        """
        Stop LED and buzzer
        """
        self.isActive = False

    def _auto_thread(self):
        """
        Performs random movement when patrol mode is activated.
        """
        while True:
            if self.isActive == True:
                grovepi.digitalWrite(BUZZER,1)
                grovepi.storeColor(0,0,255)
                grovepi.chainableRgbLed_pattern(LED, thisLedAndOutwards, 0)
                print ('start')
                time.sleep(1)

                # Stop buzzing for 1 second and repeat
                grovepi.digitalWrite(BUZZER,0)
                grovepi.storeColor(0,0,0)
                grovepi.chainableRgbLed_pattern(LED, thisLedAndOutwards, 0)
                print ('stop')
                time.sleep(1)
            elif self.isSoundOnly == True:
                grovepi.digitalWrite(BUZZER,1)
                print ('start')
                time.sleep(1)

                # Stop buzzing for 1 second and repeat
                grovepi.digitalWrite(BUZZER,0)
                print ('stop')
                time.sleep(1)
            elif self.isLEDOnly == True:
                grovepi.storeColor(0,0,255)
                grovepi.chainableRgbLed_pattern(LED, thisLedAndOutwards, 0)
                print ('start')
                time.sleep(1)

                # Stop buzzing for 1 second and repeat
                grovepi.storeColor(0,0,0)
                grovepi.chainableRgbLed_pattern(LED, thisLedAndOutwards, 0)
                print ('stop')
                time.sleep(1)

            if grovepi.digitalRead(BUTTON) == 1:
                self.isActive = False
                self.isLEDOnly = False
                self.isSoundOnly = False

            time.sleep(1)

if __name__ == '__main__':
    SmartCaseGadget().main()

