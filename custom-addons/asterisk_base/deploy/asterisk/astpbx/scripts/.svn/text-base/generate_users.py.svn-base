#!/bin/env python

import sys
from random import Random

protocol = sys.argv[1]
start = int(sys.argv[2])
end = int(sys.argv[3])

    
def generate_password(passwordLength=8):
    rng = Random()
    righthand = '23456qwertasdfgzxcvbQWERTASDFGZXCVB'
    lefthand = '789yuiophjknmYUIPHJKLNM'
    allchars = righthand + lefthand
    new_password = ''
    for i in range(passwordLength):
	new_password += ''.join( rng.choice(allchars) )
    return new_password
    
if __name__ == '__main__':
    numbers = xrange(start,end+1)
    output = open('/etc/asterisk/users.conf', 'w')
    output_csv = open('/etc/asterisk/users.csv', 'w')
    for num in numbers:
	secret= generate_password()
	section='[%s](user)\naccountcode=%s\nmailbox=%s\nsecret=%s\ncallerid="" <%s>\n\n' % (num, num,num, secret,num)
	print section
	output.write(section)
	output_csv.write('%s : %s\n' % (num, secret))
    output.close()
