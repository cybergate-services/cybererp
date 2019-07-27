#!/bin/sh
# 2wav2mp3 - create stereo mp3 out of two mono wav-files
# source files will be deleted
#
# 2005 05 23 dietmar zlabinger http://www.zlabinger.at/asterisk
#
SOX="/usr/bin/nice -n 10 /usr/bin/sox"
# command line variables
LEFT="$1"
RIGHT="$2"
OUT=`echo $3 | sed s/.wav//`

#test if input files exist
test ! -r "$LEFT" && exit
test ! -r "$RIGHT" && exit

# convert mono to stereo, adjust balance to -1/1
# left channel
$SOX "$LEFT" -c 2 "$LEFT-tmp.wav" pan -1
# right cha     nnel
$SOX "$RIGHT" -c 2 "$RIGHT-tmp.wav" pan 1

# combine and compress
# this requires sox to be built with mp3-support.
$SOX "$LEFT-tmp.wav" "$RIGHT-tmp.wav" "$OUT.mp3"

#remove temporary files
test -w "$LEFT-tmp.wav" && rm "$LEFT-tmp.wav"
test -w "$RIGHT-tmp.wav" && rm "$RIGHT-tmp.wav"
test -w "$OUT.wav" && rm "$OUT.wav"

#remove input files if successfull
test -r "$OUT.mp3" && rm "$LEFT" "$RIGHT"
# eof 
