#coding=utf-8
import pyotp

if __name__ == '__main__':
    totp = pyotp.TOTP('base32secret3232')
    print(totp.now()) # => 492039
    
    # OTP verified for current time
    print(totp.verify(492039)) # => True
    
    hotp = pyotp.HOTP('base32secret3232')
    print(hotp.at(0)) # => 260182
    print(hotp.at(1)) # => 55283
    print(hotp.at(1401)) # => 316439
     
    # OTP verified with a counter
    print(hotp.verify(316439, 1401)) # => True
    print(hotp.verify(316439, 1402)) # => False