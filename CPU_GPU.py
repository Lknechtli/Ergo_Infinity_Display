#!/usr/bin/env python

# Author: Ilia Baranov
# Very simple demo of showing system stats on the Keyboard LCD

import os
import psutil
from time import strftime, time
import urllib
import socket

from Ergo_Infinity_Display import *
lcd = [[0 for x in range(32)] for x in range(128)]

hostname = socket.gethostname()

if __name__ == '__main__':

    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.5
                        )  #Change to (Serial port - 1) on Windows.
    ser.close()
    ser.open()

    # Keeping track of Incoming + outgoing net traffic
    l_net = psutil.net_io_counters().bytes_recv + psutil.net_io_counters(
    ).bytes_sent
    l_time = time()

    try:
        while True:
            try:
                with open('/sys/class/thermal/thermal_zone0/temp') as t:
                    temp = float(t.readline().strip())/1000.0
            except:
                temp = 0
            cpu = psutil.cpu_percent(interval=None)  #CPU Usage
            mem = psutil.virtual_memory().percent  #Memory Usage
            disk = psutil.disk_usage('/').percent
            net = ((psutil.net_io_counters().bytes_recv +
                    psutil.net_io_counters().bytes_sent) - l_net) / (
                        time() - l_time)  # Messy, lousy net estimate
            l_time = time()
            l_net = psutil.net_io_counters(
            ).bytes_recv + psutil.net_io_counters().bytes_sent

            if (mem >= 60):
                lcd_color(16300, 16300, 0, ser
                          )  #RGB colors with max value of 65535 (16 bit) each
            elif (mem >= 80):
                lcd_color(16300, 0, 0, ser)
            else:
                lcd_color(16300, 16300, 16300, ser
                          )  #RGB colors with max value of 65535 (16 bit) each

            for x in range(len(lcd)):  #Clean old LCD
                for y in range(len(lcd[0])):
                    lcd[x][y] = 0

            #Show CPU, MEM, etc loading in bar graphs
            y_t = 24
            send_string(lcd, "CPU [", 0, y_t)
            send_string(lcd, "]", 76, y_t)
            send_string(lcd, "" * int(round(cpu / 10)), 26, y_t
                        )  # Represent bar graph for CPU usage (total)
            send_string(lcd, "{0:.0f}".format(temp) + "*C", 82, y_t)
            y_t -= 8
            send_string(lcd, strftime("%m-%d"), 103, y_t)  #Print date and time
            send_string(lcd, "MEM [", 0, y_t)
            send_string(lcd, "]", 76, y_t)
            send_string(lcd, "" * int(round(mem / 10)), 26, y_t
                        )  # Represent bar graph for Mem
            y_t -= 8
            send_string(lcd, strftime("%H:%M"), 103, y_t)  #Print date and time
            send_string(lcd, "DSK [", 0, y_t)
            send_string(lcd, "]", 76, y_t)
            send_string(lcd, "" * int(round(disk / 10)), 26, y_t
                        )  # Represent bar graph for Disk usage
            y_t -= 8
            send_string(lcd, "NET ", 0, y_t)
            send_string(lcd, "{0:.1f}".format(net / 1048576) + "M", 24, y_t)
            ip = socket.gethostbyname(
                hostname
            )  # Use Local IP instead of global one source above, not reliable
            send_string(lcd, ip.rjust(15), 53, y_t)

            send(lcd, ser)  #Update LCD all at once

    except KeyboardInterrupt:  # Press Ctrl + C to exit
        print('Exit')

    ser.close()
