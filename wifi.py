# wifi.py
# Establish WiFi connection

import network
import time

def connect(ssid, password):
    # Pass the ssid and password for the desired network
    # Return the IP address assigned to the ESP32 by the router
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    print('Available networks:')
    for (scan_ssid, bssid, channel, RSSI, security, hidden) in wlan.scan():
        if len(scan_ssid) > 0:
            print(f'    {scan_ssid.decode('utf-8')}')
    
    print(f'\nConnecting to {ssid}')

    wlan.connect(ssid, password)
    while not wlan.isconnected():
        timestamp = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), timestamp) < 1000: pass
        print(wlan.ifconfig())
    
    ip = wlan.ifconfig()[0]
    
    return ip