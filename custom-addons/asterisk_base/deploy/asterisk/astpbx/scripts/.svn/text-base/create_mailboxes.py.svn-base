#!/bin/env python

"""
This script is used to create mailboxes from CSV file or generate default
"""

import sys

try:
    input_file = sys.argv[1]
except IndexError:
    input_file = None

output = open('mailboxes.out', 'w')
if not input_file:
    for box in xrange(700,999):
	output.write('%s => 1234\n' % box)
	
