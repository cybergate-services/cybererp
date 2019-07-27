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
$SOX -t wav "$LEFT" -c 2 -t wav "$LEFT-tmp.wav" pan -1
# right channel 
$SOX "$RIGHT" -c 2 -t wav "$RIGHT-tmp.wav" pan 1

# mix 
$SOX -m -v 1 -t wav "$LEFT-tmp.wav" -v 1 -t wav "$RIGHT-tmp.wav" -t wav "$OUT.wav"

#remove temporary files 
test -w "$LEFT-tmp.wav" && rm $LEFT-tmp.wav
test -w "$RIGHT-tmp.wav" && rm $RIGHT-tmp.wav

#remove input files if successfull 
#test -r $OUT.wav && rm $LEFT $RIGHT
# eof

# now move it to mailbox folder. We take mailbox from filename
MAILBOX=`basename $OUT | awk 'BEGIN {FS="-"}; {print $1}'` 
mv "$OUT.wav" "/var/spool/asterisk/voicemail/default/$MAILBOX/INBOX"