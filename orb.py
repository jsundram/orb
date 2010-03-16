#!/usr/bin/env python
# encoding: utf-8
"""
orb.py

Created by Jason Sundram and Tyler Williams on 2010-03-16.
"""

import serial 


class Orb:
    def __init__(self, port='/dev/ttyS0'):
        self.serial = serial.Serial(port, 19200, timeout=1)
    
    def __del__(self):
        self.serial.close()
    
    def set(self, color, animation):
        """ Color is: 0-36 (ROYGBIV, fading back to red)
            Animation is: in range 0 (None) - 9 (Heartbeat)
        """
        self.ignore_pager()
        
        self.serial.write('~A')
        self.serial.write(chr((color + (37 * animation)) / 94 + 32))
        self.serial.write(chr((color + (37 * animation)) % 94 + 32))
        return self.serial.read(2)
        
    def set_color(self, r,g,b):
        """r, g, b each in the range 0, 177"""
        self.ignore_pager()
        
        self.serial.write('~D')
        for i in map(chr, (r,g,b)):
            if 0 <= ord(i) <= 176: 
                self.serial.write(i)
            else:
                raise ValueError("Values must be in range [0, 176]")
        self.serial.read(2)
    
    def set_brightness(self, value):
        """value must be in range 0-2 (dim, medium, bright)"""
        if value < 0 or 2 < value:
            raise ValueError("Values must be in the range [0,2]")
        
        self.ignore_pager()
        self.serial.write('~R')
        self.serial.write(str(value))
        return self.serial.read(2)
    
    def ignore_pager(self, ignore=True):
        if ignore:
            self.serial.write('~GT')
        else:
            self.serial.write('~GF')
        return self.serial.read(2)
    
    def serial_number(self):
        self.serial.write('~I')
        data = self.serial.readline()
        # See info() for the response format.
        return data[6:15]
        
    def info(self):
        """returns a tuple: (Serial #, Brightness, IgnorePager, Copyright)"""
        self.serial.write('~I')
        data = self.serial.readline()
        """
        0       !  (exclamation point -- ASCII 33) 
        1       I  (uppercase 'I' -- ASCII 73) 
        2,3     product ID Currently 4266 
        4,5     version ID Currently 4116 
        6-15    serial number 9 digit serial number. 
        16-21   internal data internal 
        23      Current brightness 0 - dim, 1 - medium, 2 - bright 
        24      num pages received (zero) not implemented 
        25      ignore pager data 'T' for true, 'F' for false 
        26      premium capcode, private 'T' for true, 'F' for false 
        27 - 28 internal data internal data 
        29 ...  Copywrite string (c)2003 Amb Dev, Orb 2.0b
                (null-terminated)
        """
        return (data[6:15], ord(data[23]), data[25] == 'T', data[29:-1])
        
    def allow_local_control(self, allow=True):
        # TODO: start/stop polling here
        if allow:
            self.serial.write('~LI')
        else:
            self.serial.write('~LE')
        return self.serial.read(2)
        
    def ping(self):
        self.serial.write('~P')
        return self.serial.read(2)

if __name__ == '__main__':
    o = Orb()
    print o.info()