# Goal: develop an Iot device that procides control over the brightness of 3 different LEDs (PWM),
# with an HTML interface that will allow the user to do the following:
# 1. Select a single LED to control from a set of radio buttons (multiple choice)
# 2. Choose a brightness level for the selected LED using a single range element from 0 - 100%
# 3. Display the current brightness lebel of all 3 LEDs
# 4. CHange the brightness as requested, with continous and independent control for each LED

import wifi
import machine
from machine import SoftI2C as I2C
from machine import Pin, PWM
from ssd1306 import SSD1306_I2C  # OLED display
import socket

led1 = PWM(Pin(2))
led1_duty = 0

led2 = PWM(Pin(0))
led2_duty = 0

led3 = PWM(Pin(4))
led3_duty = 0


### NOTE: OLED STOP WORKING SO I COMMENTED IT OUT

'''
# Set up I2C (neded for the OLED display). 
sda_pin, scl_pin = 5, 4    # original (black) HiLetgo board
#sda_pin, scl_pin = 4, 15  # alternate (white) HiLetgo board
sda = Pin(sda_pin)
scl = Pin(scl_pin)
i2c = I2C(sda=sda, scl=scl) 

# Reset I2C (not needed for many ESP32 boards):
rst = Pin(16, Pin.OUT)   # I2C reset pin
rst.off()    # set GPIO16 low to reset OLED
rst.on()     # while using I2C GPIO16 must be high

# Set up the OLED display:
w = const(128) # screen width
h = const(64)  # screen height
ch = const(8)  # character width/height
display = SSD1306_I2C(w, h, i2c)
    
# Function to center text on display
def display_center(s,row):
    display.text(s, w//2-len(s)//2*ch, row*ch)  #FrameBuffer.text(s, x, y)
'''    
    
def web_page(led1, led2, led3):
    print(f'\nLed1: {led1_duty}, Led2: {led2_duty}, Led3: {led3_duty}\n')
    
    html = """
    <html><head><title>Web Server Test</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="icon" href="data:,">
        <style>
        html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
        h1{color: #0F3376; padding: 2vh;}
        p{font-size: 1.5rem;}
        .button{display: inline-block; background-color: #e7bd3b; border: none; border-radius: 4px; color: white;
                         padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
        .button2{background-color: #4286f4;}
        </style>
        </head>
        <body>
        <p>Brightness level:</p>
        <form action="/" method="POST">
          <p><input type="range" name="brightness" min="0" max="100" value="100"></p><br>
          <p>Select LED:</p>
          <p><input type="radio" name="led1"> LED 1 (""" + str(led1) + """%)</p>
          <p><input type="radio" name="led2"> LED 2 (""" + str(led2) + """%)</p>
          <p><input type="radio" name="led3"> LED 3 (""" + str(led3) + """%)</p>
          <p><button type="submit" name="submit" value="submit_button">Submit</button></p>
        </form>
        </body>
    </html>
    """
    return bytes(html, 'utf-16')
    
    
def getPOSTdata(client_message):
    #print(client_message, '\n')
    data_dict = {}
    data = str(client_message)   # convert from bytes
    data = data[data.find('\\r\\n\\r\\n')+8 : -1]
    #print(data, '\n')
    data_pairs = data.split('&')
    #print(data_pairs, '\n')
    for pair in data_pairs:
        key_val = pair.split('=')
        if len(key_val) == 2:
            data_dict[key_val[0]] = key_val[1]
           
    return data_dict


def update_values(data):
    global led1_duty
    global led2_duty
    global led3_duty
    
    # 'data' is an empty dictionary in first POST
    try:
        brightness = int(data['brightness'])
        brightness = int((brightness/100) * 1023)
    except:
        brightness = 50
        brightness = int((brightness/100) * 1023)
        
        
    if 'led1' in data.keys():
        led1_duty = int(data['brightness']) # sent to web_page()
        led1.duty(brightness)
        
        
    if 'led2' in data.keys():
        led2_duty = int(data['brightness']) # sent to web_page()
        led2.duty(brightness)

        
    if 'led3' in data.keys():
        led3_duty = int(data['brightness']) # sent to web_page()
        led3.duty(brightness)
    
    

def main():
    
    # Set up WiFi:
    ssid = "ssid"               # Replace with router ssid
    password = "password"       # Replace with router password
    '''
    display.fill(0)
    display_center('connecting',2)  
    display_center('to',3)  
    display_center(ssid, 4) 
    display.show()
    '''
    ip = wifi.connect(ssid, password)
    print(ip)
    '''
    display.fill_rect(0,0,w,h,0)   # clear the screen
    display_center(ip, 4)
    display.show()
    '''
    
    # Set up Socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # pass IP addr & socket type
    # AF_INET -> IPv4 socket
    # SOCK_STREAM -> use TCP
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 80))     #  # Bind HOST IP address through the given PORT 
    # HOST can be a specific IP address, the loopback address (127.0.0.1), 
    # or an empty string (meaning any connection will be allowed). 
    # PORT can be a privileged port such as 80 for HTTP, or a custom port > 1023
    s.listen(5)          # up to 5 queued connections
    
    
    print('Waiting for connection...')
    conn, addr = s.accept()        # blocking call -- code pauses until connection
    print(f'Connection from {addr}')
    data = getPOSTdata(conn.recv(1024))    # specify buffer size (max data to be received)
    conn.sendall(b'HTTP/1.1 200 OK\r\n')             # status line
    conn.sendall(b'Content-Type: text/html\r\n')     # headers
    conn.sendall(b'Connection: close\r\n\r\n')   
    conn.sendall(web_page(100, 100, 100))                   # body
    conn.close()
        
    
    while True:
        print('Waiting for connection...')
        conn, addr = s.accept()        # blocking call -- code pauses until connection
        print(f'Connection from {addr}')
        data = getPOSTdata(conn.recv(1024))    # specify buffer size (max data to be received)
        conn.sendall(b'HTTP/1.1 200 OK\r\n')             # status line
        conn.sendall(b'Content-Type: text/html\r\n')     # headers
        conn.sendall(b'Connection: close\r\n\r\n')
        update_values(data)
        conn.sendall(web_page(led1_duty, led2_duty, led3_duty))   # update web_page() with new values
        conn.close()

    
    
    
    
    
if __name__ == "__main__":
    main()
