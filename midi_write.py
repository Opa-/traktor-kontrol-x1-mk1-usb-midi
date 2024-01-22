import rtmidi
from rtmidi import MidiMessage

midiout = rtmidi.RtMidiOut()


def main():
    ports = range(midiout.getPortCount())
    if ports:
        for i in ports:
            print(f"{i} -> {midiout.getPortName(i)}")
        print("Opening port 0!")
        midiout.openPort(0)
        msg = MidiMessage().noteOn(176, 6, 127)
        msg = MidiMessage().masterVolume(127.0)
        print(msg)
        midiout.sendMessage(msg)


if __name__ == '__main__':
    main()
