#!/bin/sh

set -e
SOX="/usr/bin/nice -n 10 /usr/bin/sox"

# command line variables 
set > /tmp/ss
LEFT="$1"
RIGHT="$2"
OUT=`echo $3|sed s/.wav//`

#echo $1 $2 $3 >>/tmp/2wav2ogg.log 

#test if input files exist 
test ! -r "$LEFT" && exit 1
test ! -r "$RIGHT" && exit 2

# convert mono to stereo, adjust balance to -1/1 
# left channel 
$SOX -t wav $LEFT -c 2 -t wav $LEFT-tmp.wav pan -1
# right channel 
$SOX $RIGHT -c 2 -t wav $RIGHT-tmp.wav pan 1

# mix and encode to ogg vorbis 
$SOX -m -v 1 -t wav $LEFT-tmp.wav -v 1 -t wav $RIGHT-tmp.wav -t vorbis $OUT.ogg

#remove temporary files 
test -w $LEFT-tmp.wav && rm $LEFT-tmp.wav
test -w $RIGHT-tmp.wav && rm $RIGHT-tmp.wav
test -w $OUT.wav && rm $OUT.wav

#remove input files if successfull 
test -r $OUT.ogg && rm $LEFT $RIGHT
# eof
