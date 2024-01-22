from kontrol_x1_mk1 import KontrolX1Mk1HotPlugUsbHandler

if __name__ == '__main__':
    kontrol_x1_mk1 = KontrolX1Mk1HotPlugUsbHandler('Traktor Virtual Input')
    kontrol_x1_mk1.loop()
