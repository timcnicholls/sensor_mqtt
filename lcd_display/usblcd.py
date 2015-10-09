import serial
import time

class UsbLcd(object):

    RED   = (0xFF, 0x00, 0x00)
    GREEN = (0x00, 0xFF, 0x00)
    BLUE  = (0x00, 0x00, 0xFF)
    WHITE = (0xFF, 0xFF, 0xFF)
    YELLOW = (0xFF, 0xCC, 0x00)

    CMD_START         = 0xFE
    CMD_LCD_SIZE      = 0xD1
    CMD_CLEAR         = 0x58
    CMD_SET_SPLASH    = 0x40
    CMD_RGB_BACKLIGHT = 0xD0
    CMD_AUTOSCROLL_ON = 0x51
    CMD_AUTOSCROLL_OFF = 0x52
    CMD_BRIGHTNESS     = 0x99
    CMD_CONTRAST       = 0x50

    def __init__(self, serial_dev, baud=57600, rows=2, cols=16):

        self.ser = serial.Serial(serial_dev, baud)
        self.rows = rows
        self.cols = cols

        self.write_cmd([UsbLcd.CMD_LCD_SIZE, self.cols, self.rows])

    def write_cmd(self, cmd_list):

        cmd_list.insert(0, UsbLcd.CMD_START)
        for i in range(0, len(cmd_list)):
             self.ser.write(chr(cmd_list[i]))

    def clear(self):

        self.write_cmd([UsbLcd.CMD_CLEAR])

    def write(self, text):

        self.ser.write(text)

    def set_splash_text(self, text):

        splash_data = [ord(' ')]*(self.rows * self.cols)
        splash_data.insert(0, UsbLcd.CMD_SPLASH)

        for i in range(len(text)):
            splash_data[i+1] = ord(text[i])

        self.write_cmd(splash_data)

    def set_backlight_colour(self, rgb_val):

        # TODO validate rgb_val is tuple
        rgb_data = [UsbLcd.CMD_RGB_BACKLIGHT]
        rgb_data.extend(rgb_val)

        self.write_cmd(rgb_data)

    def set_autoscroll_mode(self, enabled=True):

        if enabled == True:
            cmd = UsbLcd.CMD_AUTOSCROLL_ON
        else:
            cmd = UsbLcd.CMD_AUTOSCROLL_OFF

        self.write_cmd([cmd])

    def set_brightness(self, brightness):

        self.write_cmd([UsbLcd.CMD_BRIGHTNESS, brightness])

    def set_contrast(self, contrast):

        self.write_cmd([UsbLcd.CMD_CONTRAST, contrast])

    def close(self):
        self.ser.close()


if __name__ == '__main__':

    disp = UsbLcd("/dev/cu.usbmodem14541", 57600)

    #disp.set_splash_text("STFC LPD Control")

    disp.clear()

    disp.write("Hello, world!")
    time.sleep(1.0)
    disp.clear()
    disp.write("Testing ...")
    time.sleep(1.0)
    disp.clear()
    disp.write("Anyone there?")
    time.sleep(1.0)

    disp.clear()
    disp.write("Backlight red")
    disp.set_backlight_colour(UsbLcd.RED)
    time.sleep(1.0)

    disp.clear()
    disp.write("Backlight green")
    disp.set_backlight_colour(UsbLcd.GREEN)
    time.sleep(1.0)

    disp.clear()
    disp.write("Backlight blue")
    disp.set_backlight_colour(UsbLcd.BLUE)
    time.sleep(1.0)

    disp.clear()
    disp.write("Backlight yellow")
    disp.set_backlight_colour(UsbLcd.YELLOW)
    time.sleep(1.0)

    disp.clear()
    disp.write("Backlight white")
    disp.set_backlight_colour(UsbLcd.WHITE)
    time.sleep(1.0)

    disp.clear()
    disp.set_autoscroll_mode(True)
    disp.write("Autoscroll test: ")
    time.sleep(1)
    disp.write("Some text.");
    time.sleep(1)
    disp.write(" Add some more...");
    time.sleep(1)
    disp.write(" which will scroll");
    time.sleep(1)
    disp.set_autoscroll_mode(False)

    disp.clear()
    disp.write("Brightness loop")
    for i in range(256):
        disp.set_brightness(i)
        time.sleep(0.01)

    disp.clear()
    disp.write("Contrast loop")
    for i in range(256):
        disp.set_contrast(i)
        time.sleep(0.01)

    time.sleep(1)

    disp.clear()
    disp.write("      Bye!      ")
    time.sleep(0.1)
    disp.close()
