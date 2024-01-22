import multiprocessing

import mido
import usb
from mido.backends.rtmidi import Output
from usb.core import USBError

USB_ID_VENDOR: int = 0x17cc
USB_ID_PRODUCT: int = 0x2305
USB_STATE_FD: int = 0x84
USB_READ_BUFFER_SIZE: int = 24


class KontrolX1Mk1(multiprocessing.Process):
    serial_number: str
    # usb_device: Device
    midi_out: Output

    play_left_toggle: bool = False

    def __init__(self, serial_number: str):
        super().__init__()
        self.serial_number = serial_number
        # self.usb_device = usb.core.find(idVendor=USB_ID_VENDOR, idProduct=USB_ID_PRODUCT)
        # print(self.usb_device.serial_number)
        # self.midi_out = midi_out

    def run(self):
        usb_device = usb.core.find(idVendor=USB_ID_VENDOR, idProduct=USB_ID_PRODUCT,
                                   custom_match=lambda dev: dev.serial_number == self.serial_number)
        self.midi_out = mido.open_output('Traktor Virtual Input')
        print(f"Running: {usb_device.serial_number}")
        fd = 0x1
        while True:
            try:
                state = usb_device.read(USB_STATE_FD, USB_READ_BUFFER_SIZE)
                # Sometimes the read bytearray is smaller than expected
                # We need information about all the buttons and knobs to identify them based on array index.
                # if len(state) == USB_READ_BUFFER_SIZE:
                #     self.handle_state(state)
                try:
                    usb_device.write(0x1, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
                except Exception as e:
                    pass
                usb_device.read(0x81, 1)
            except (ValueError, USBError,) as e:
                print(f"Exiting {fd} {self.serial_number} {e}")
                continue

    def handle_state(self, state: bytearray):
        self.handle_start_pause(state[1])

    def handle_start_pause(self, value: int):
        if value == 1:
            if not self.play_left_toggle:
                self.midi_out.send(mido.Message('note_on', 60))
            self.play_left_toggle = True
        else:
            if self.play_left_toggle:
                self.play_left_toggle = False


class KontrolX1Mk1HotPlugUsbHandler(object):
    controllers: dict[str, KontrolX1Mk1]
    midi_out: Output

    def __init__(self, midi_virtual_port_name: str):
        self.midi_out = mido.open_output(midi_virtual_port_name)
        self.controllers = dict()

    def loop(self):
        while True:
            try:
                devices = list(usb.core.find(idVendor=USB_ID_VENDOR, idProduct=USB_ID_PRODUCT, find_all=True))
                for serial_number in list(self.controllers):
                    if serial_number not in [dev.serial_number for dev in devices]:
                        print(f"Unregister {serial_number}")
                        self.controllers[serial_number].close()
                        self.controllers.pop(serial_number)
                for dev in devices:
                    dev.set_configuration()
                    if dev.serial_number not in self.controllers.keys():
                        print(f"Registering {dev.serial_number}")
                        self.controllers[dev.serial_number] = KontrolX1Mk1(dev.serial_number)
                        self.controllers[dev.serial_number].start()
            except (ValueError, USBError,):
                pass
