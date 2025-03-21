"""
dice.py

    Dice Rolling Simulator

"""
# Imports
import utime
import random

from machine import Pin, SPI
import cst816
import gc9a01

from bitmap import vga1_8x8 as font
from bitmap import vga2_bold_16x32 as font_bold

import d2_large
import d4_large
import d6_large
import d8_large
import d10_large
import d12_large
import d20_large


# Global Variables and Consts
DEBUG = False

text_selected = gc9a01.WHITE
text_deselected = 0x6a6a6a
background = gc9a01.BLACK
foreground = gc9a01.WHITE
labels = ['d4 ','d6 ','d8 ','d20','d10','d12','d2 ']
values = [[1,4],[1,6],[1,8],[1,20],[1,10],[1,12],[1,2]]

# Initialize I2C
touch = cst816.CST816()

# Check if the touch controller is detected
if touch.who_am_i():
    print("CST816 detected.")
else:
    print("CST816 not detected.")


# Draw Dice UI
def selectDice(tft, index):
    
    # D4
    tft.jpg("d4.jpg", 7, 70, gc9a01.SLOW)
    tft.text(font,'D4', 12, 97, text_selected if index == 0 else text_deselected, background)
    if index == 0:
        tft.pbitmap(d4_large, 58, 58)
      
    # D6
    tft.jpg("d6.jpg", 37, 40, gc9a01.SLOW)
    tft.text(font,'D6', 42, 67, text_selected if index == 1 else text_deselected, background)
    if index == 1:
        tft.pbitmap(d6_large, 58, 58)
       
    # D8
    tft.jpg("d8.jpg", 67, 20, gc9a01.SLOW)
    tft.text(font,'D8', 72, 47, text_selected if index == 2 else text_deselected, background)
    if index == 2:
        tft.pbitmap(d8_large, 58, 58)
       
    # Emblem
    tft.jpg("emblem.jpg", 101, 0, gc9a01.SLOW)
    tft.text(font,'D20', 110, 40, text_selected if index == 3 else text_deselected, background)
    if index == 3:
        tft.pbitmap(d20_large, 58, 58)

    # D10
    tft.jpg("d10.jpg", 148, 20, gc9a01.SLOW)
    tft.text(font,'D10', 150, 47, text_selected if index == 4 else text_deselected, background)
    if index == 4:
        tft.pbitmap(d10_large, 58, 58)

    # D12
    tft.jpg("d12.jpg", 178, 40, gc9a01.SLOW)
    tft.text(font,'D12', 183, 67, text_selected if index == 5 else text_deselected, background)
    if index == 5:
        tft.pbitmap(d12_large, 58, 58)

    # D2
    tft.jpg("d2.jpg", 210, 70, gc9a01.SLOW)
    tft.text(font,'D2', 213, 97, text_selected if index == 6 else text_deselected, background)
    if index == 6:
        tft.pbitmap(d2_large, 58, 58)



def main():
    tft = gc9a01.GC9A01(
        SPI(2, baudrate=80000000, polarity=0, sck=Pin(10), mosi=Pin(11)),
        240,
        240,
        reset=Pin(14, Pin.OUT),
        cs=Pin(9, Pin.OUT),
        dc=Pin(8, Pin.OUT),
        backlight=Pin(2, Pin.OUT),
        rotation=0,
        buffer_size=16*32*2)


    tft.init()
    tft.fill(background)
    utime.sleep(1)

    height = tft.height()
    width = tft.width()
    
    # Data tracking 
    press = False
    point = None
    
    # Set D20 as default
    index = 3
    selectDice(tft, index)

    while True:
        # Process Touch Input
        point = touch.get_point()
        gesture = touch.get_gesture()
        press = touch.get_touch()
        
        # Process dice selection
        if press and gesture == 0 and point:
            x,y = point.x_point, point.y_point
            
            if x >= 0 and x < 35 and y <= 180: # D4
                index = 0
            elif x >= 35 and x < 65 and y <= 90: # D6
                index = 1
            elif x >= 65 and x < 95 and y <= 70: # D8
                index = 2
            elif x >= 95 and x < 145 and y <= 65: # D20
                index = 3
            elif x >= 145 and x < 175 and y <= 70: # D10
                index = 4
            elif x >= 175 and x < 205 and y <= 90: # D12
                index = 5
            elif x >= 205 and x < 240 and y <= 180: # D2
                index = 6
            
            selectDice(tft, index)
            
            press = False
            
        # Process dice roll
        if press and gesture == 1 and point:
            x,y = point.x_point, point.y_point
            print("Position: {0},{1} - Gesture: {2} - Pressed? {3}".format(point.x_point, point.y_point, gesture, press))
            

            if x >= 30 and x < 210 and y > 90 and y <= 240:
                # Clean screen
                tft.fill_rect(0,180,240,60, background)
                selectDice(tft, index)
                
                # Get Low and High vals for selected dice
                low = values[index][0]
                high = values[index][1]
                
                
                # String buffers
                next = ''
                curr = ''
                prev = ''
                
                i = 0
                while i < 50:
                    prev = curr
                    curr = next
                    next = str(random.randint(low, high))
                    
                    tft.text(font_bold, f'{"":>8}', 56, 104, foreground, background)
                    tft.text(font_bold, f'{prev:>2}', 56, 104, text_deselected, background)
                    tft.text(font_bold, f'{curr:>2}', 104, 104, text_selected, background)
                    tft.text(font_bold, f'{next:>2}', 152, 104, text_deselected, background)

                    if i < 30:
                        utime.sleep(0.1)
                    elif i < 45:
                        utime.sleep(0.2)
                    else:
                        utime.sleep(0.4)
                        
                    i += 1
                
                # Color text based on success or failure
                color = foreground
                if int(curr) == high:
                    color = gc9a01.color565(0,128,0)
                if int(curr) == low:
                    color = gc9a01.color565(128,0,0)
                
                # draw final number
                for i in range(7):
                    tft.text(font_bold, f'{"":>8}', 56, 104, foreground, background)
                    if (i%2)==0:
                        tft.text(font_bold, f'{curr:>2}', 104, 104, color, background)
            
                    utime.sleep(0.5)
                    
            
            utime.sleep(2)
            press = False
        
        
        # Draw Roll Text
        text = 'Roll ' + labels[index]
        tft.text(font_bold, text, 56, 180, foreground, background)
        
        
        # Debug Printing
        if DEBUG:
            print("Position: {0},{1} - Gesture: {2} - Pressed? {3}".format(point.x_point, point.y_point, gesture, press))

            tft.fill_rect(30,90,180,150, foreground)
            
            tft.vline(20,0,240, foreground)
            tft.vline(50,0,240, foreground)
            tft.vline(80,0,240, foreground)
            tft.vline(120,0,240, foreground)
            tft.vline(160,0,240, foreground)
            tft.vline(190,0,240, foreground)
            tft.vline(220,0,240, foreground)
            
            tft.fill_rect(0,70,35,110, 0x0000ff)
            tft.fill_rect(35,40,30,50, 0x00ff00)
            tft.fill_rect(65,20,30,50, 0x0000ff)
            tft.fill_rect(95,0,50,65, 0x00ff00)
            tft.fill_rect(145,20,30,50, 0x0000ff)
            tft.fill_rect(175,40,30,50, 0x00ff00)
            tft.fill_rect(205,70,35,110, 0x0000ff)
        
    
        utime.sleep(0.1)


main()


