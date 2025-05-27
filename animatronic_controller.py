import time

# Optional Raspberry Pi GPIO LED Support
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False

# Optional Arduino Serial (for servo, RGB, etc.)
try:
    import serial
    SERIAL_AVAILABLE = True
    arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
except:
    SERIAL_AVAILABLE = False
    arduino = None

class AnimatronicController:
    def __init__(self):
        self.led_pins = {
            "joy": 17,
            "rage": 27,
            "calm": 22,
            "sacred": 23
        }

        if GPIO_AVAILABLE:
            for pin in self.led_pins.values():
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.LOW)

    def trigger_emotion(self, emotion):
        print(f"[🤖] Expressing emotion: {emotion}")

        # GPIO LED Flash
        if GPIO_AVAILABLE:
            pin = self.led_pins.get(emotion)
            if pin:
                self._flash_led(pin)

        # Arduino command
        if SERIAL_AVAILABLE and arduino:
            try:
                arduino.write(f"{emotion}\n".encode())
                print("[📡] Sent to Arduino.")
            except Exception as e:
                print(f"[⚠️] Arduino send failed: {e}")

    def _flash_led(self, pin, duration=1.0):
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(duration)
        GPIO.output(pin, GPIO.LOW)

    def cleanup(self):
        if GPIO_AVAILABLE:
            GPIO.cleanup()
            print("[🔌] GPIO cleanup complete.")

# --- Manual CLI Test ---
if __name__ == "__main__":
    controller = AnimatronicController()
    try:
        emotions = ["joy", "rage", "calm", "sacred"]
        for e in emotions:
            controller.trigger_emotion(e)
            time.sleep(2)
    finally:
        controller.cleanup()

