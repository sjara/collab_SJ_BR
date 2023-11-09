"""
Generate and save an example sound.
"""

import os
import sound_generation as soundgen
from importlib import reload
reload(soundgen)


sound = soundgen.Sound(duration=0.1, srate=44100)  # Create sound object

sound.add_tone(freq=500, amp=0.1)
sound.add_noise(amp=0.02)
#sound.add_tone(freq=12000, amp=0.1)
#sound.add_chord(midfreq=15000, factor=1.2, ntones=11, amp=0.1)
sound.apply_rise_fall()  # Smooth out the begining and end of the sound

#soundfile = '/tmp/test.wav'  # You can specify the filename or...
soundfile = sound.suggest_filename()  # Let the sound object suggest a filename

outdir = '/tmp/'
sound.save(soundfile, outdir=outdir)  # Save wav file and sound info file

soundgen.play_file(os.path.join(outdir,soundfile))  # Play sound


'''
# -- Plot the sound --
import matplotlib.pyplot as plt
plt.plot(sound.tvec, sound.wave)
plt.show()
'''


