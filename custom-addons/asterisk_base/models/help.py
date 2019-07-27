#-*- encoding: utf-8 -*-

DIAL_OPTIONS = u"""The options parameter, which is optional, is a string containing zero or more of the following flags and parameters:

A(x): Play an announcement (x.gsm) to the called party.
C: Reset the CDR (Call Detail Record) for this call. This is like using the NoCDR command
c: Sets the channel driver flag that the “call is answered elsewhere” if Dial() cancels the call
D(digits): After the called party answers, send digits as a DTMF stream, then connect the call to the originating channel (you can also use ‘w’ to produce .5 second pauses). You can also provide digits after a colon – all digits before the colon are sent to the called channel, all digits after the colon are sent to the calling channel (all digits are sent to the called channel if there is no colon present).
d: This flag trumps the ‘H’ flag and intercepts any single DTMF tone while waiting for the call to be answered and jumps to that extension if it exists. This allows you to dial a 1-digit exit extension while waiting for the call to be answered – see also RetryDial. This uses the current context unless ${EXITCONTEXT} is defined.
e: Execute “h” as the peer when this call ends
 F(context^exten^pri): When the caller hangs up, transfer the called party to the specified context and extension and continue execution.
f: forces callerid to be set based on a dialplan “hint” for the current channel. For example, some PSTNs don’t allow callerids from other extensions than the ones that are assigned to you.
G(context^exten^pri): If the call is answered, transfer both parties to the specified context and extension. The calling party is transferred to priority x, and the called party to priority x+1. This allows the dialplan to distinguish between the calling and called legs of the call (new in v1.2). You cannot use any options that would affect the post-answer state if this option is used.
g: When the called party hangs up, continue to execute commands in the current context at the next priority.
H: Allow the caller to hang up by dialing * ( * is defined in features.conf -> featuremap -> disconnect )
h: Allow the callee to hang up by dialing * ( * is defined in features.conf -> featuremap -> disconnect )
i: Asterisk will ignore any forwarding requests it may receive on this dial attempt. (new in 1.4) Useful if you are ringing a group of people and one person has set their phone to forwarded direct to voicemail on their cell or something which normally prevents any of the other phones from ringing.
j: Asterisk 1.2 and later (1.6???): Jump to priority n+101 if all of the requested channels were busy (just like behaviour in Asterisk 1.0.x)
K: Allow the calling party to enable parking of the call by sending the DTMF sequence defined for call parking in features.conf (Asterisk v1.4.x)
k: Allow the called party to enable parking of the call by sending the DTMF sequence defined for call parking in features.conf (Asterisk v1.4.x)
L(x[:y][:z]): Limit the call to ‘x’ ms, warning when ‘y’ ms are left, repeated every ‘z’ ms) Only ‘x’ is required, ‘y’ and ‘z’ are optional. Numbers must be integers- beware of AGI scripts that may return long integers in scientific notation (esp PHP 5.2.5&6) The following special variables are optional for limit calls: (pasted from app_dial.c)
LIMIT_PLAYAUDIO_CALLER – yes|no (default yes) – Play sounds to the caller.
LIMIT_PLAYAUDIO_CALLEE – yes|no – Play sounds to the callee.
LIMIT_TIMEOUT_FILE – File to play when time is up.
LIMIT_CONNECT_FILE – File to play when call begins.
LIMIT_WARNING_FILE – File to play as warning if ‘y’ is defined. If LIMIT_WARNING_FILE is not defined, then the default behaviour is to announce (“You have [XX minutes] YY seconds”).
M(x): Executes the macro (x) upon connect of the call (i.e. when the called party answers). See also U. IMPORTANT – The CDR ‘billsecs’ field is set to zero if the callee answers the call, but hangs up whilst the macro is still running (if the callee answers and the macro finishes, ‘billsecs’ contains the correct value). The macro can set ${MACRO_RESULT} to the following:
ABORT: Hang up both legs
CONGESTION: Signal congestion to the caller
BUSY: Signal busy to the caller
CONTINUE: Hangup the called party but continue execution at the next priority in the dialplan for the caller
GOTO: Transfer the execution to context^exten^pri
m: Provide Music on Hold to the calling party until the called channel answers. This is mutually exclusive with option ‘r’, obviously. Use m(class) to specify a class for the music on hold.
N: Modifies the privacy manager – turns off call screening if caller ID information is present
n(delete): (Asterisk 1.6) If delete is 0 or not specified, delete the privacy manager introduction if the caller hangs up before the call is answered. If set to 1, delete the recording even if the call is answered.
O(mode): If mode is set to 1 or isn’t specified, ringback immediately if the originator hangs up. If mode is set to 2, ring back when the operator flashes the trunk. This is only valid when the caller and called channels are DAHDI channels. It is intended for calling an operator station.
o: Restore the Asterisk v1.0 CallerId behaviour (send the original caller’s ID) in Asterisk v1.2 (default: send this extension’s number)
P(x): Use the PrivacyManager, using x as the database (x is optional and will default to the current extension)
p: This option enables screening mode. This is basically Privacy mode without memory of how to handle the caller. It looks for the file sounds/priv-callerintros/${IF($[ “${CALLERID(num)}” != “” ]?${CALLERID(num)}:NOCALLERID_${EXTEN}${CUT(CHANNEL,/,1)}=${CUT(CHANNEL,/,2)})}.gsm and if it is not found, prompts the caller to say his name. It then rings the called party and plays sounds/priv-callpending, sounds/priv-callerintros/<see-above>, and sounds/screen-callee-options. If the called party enters 1, the call is accepted, 2, the DIAL command exits with ${DIALSTATUS} set to NOANSWER, 3, set to TORTURE and 4, set to DONTCALL. If no valid entry is made, the DIAL command exits with ${DIALSTATUS} set to ANSWER. The check for pre-existence of the name recording may not be what you want. For example, everyone from the same number is not necessarily the same person, especially if the number is OUTOFAREA, but if the file is there, no new name will be recorded. Since the files are never removed, you may wish to remove them with a System(rm /var/lib/asterisk/sounds/priv-callerintros/${IF($[ “${CALLERID(num)}” != “” ]?${CALLERID(num)}:NOCALLERID_${EXTEN}${CUT(CHANNEL,/,1)}=${CUT(CHANNEL,/,2)})}.*) right before the Dial command and clean up old ones with a cron job.
R: Indicate ringing to the calling party when the called party indicates ringing, pass no audio until answered. This is available only if you are using kapejod’s Bristuff.
r: Generate a ringing tone for the calling party, passing no audio from the called channel(s) until one answers. Without this option, Asterisk will generate ring tones automatically where it is appropriate to do so; however, “r” will force Asterisk to generate ring tones, even if it is not appropriate. For example, if you used this option to force ringing but the line was busy the user would hear “RING RIBEEP BEEP BEEP” (thank you tzanger), which is potentially confusing and/or unprofessional. However, the option is necessary in a couple of places. For example, when you’re dialing multiple channels, call progress information is not consistantly passed back. Look at Progress(), the progressinband setting in sip.conf or Ringing() if you would like to avoid the use of ‘r’ but have issues with the ringback behaviour of Dial().
S(n): Hangup the call n seconds AFTER called party picks up.
T: Allow the calling user to transfer the call by hitting the blind xfer keys (features.conf). Does not affect transfers initiated through other methods.
If you have set the variable GOTO_ON_BLINDXFR then the transferrer will be sent to the context|exten|pri (you can use ^ to represent | to avoid escapes), example: SetVar(GOTO_ON_BLINDXFR=woohoo^s^1); works with both t and T
t: Allow the called user to transfer the call by hitting the blind xfer keys (features.conf) Does not affect transfers initiated through other methods.
If you have set the variable GOTO_ON_BLINDXFR then the transferrer will be sent to the context|exten|pri (you can use ^ to represent | to avoid escapes), example: SetVar(GOTO_ON_BLINDXFR=woohoo^s^1); works with both t and T
U(x): Executes, via gosub, routine x on the called channel. This is similar to M above, but a gosub rather than a macro. The subroutine can set ${GOSUB_RESULT}__ to the following:
ABORT: Hang up both legs
CONGESTION: Signal congestion to the caller
BUSY: Signal busy to the caller
CONTINUE: Hangup the called party but continue execution at the next priority in the dialplan for the caller
GOTO: Transfer the execution to context^exten^pri
W: Allow the calling user to start recording after pressing *1 or what defined in features.conf (Asterisk v1.2.x); requires Set(DYNAMIC_FEATURES=automon)
w: Allow the called user to start recording after pressing *1 or what defined in features.conf (Asterisk v1.2.x); requires Set(DYNAMIC_FEATURES=automon)
X: Allow the calling user to start recording using automixer after pressing *1 or what defined in features.conf (Asterisk v1.6)
x: Allow the called user to start recording using automixer after pressing *1 or what defined in features.conf (Asterisk v1.6)"""


