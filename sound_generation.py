"""
Module for generating sounds for perceptual decision tasks.
"""

import os
import numpy as np
import scipy.io.wavfile


randomGen = np.random.default_rng()

class Sound():
    """
    Represents a synthetic sound waveform generator.

    Attributes:
        duration (float): Duration of the sound in seconds.
        srate (int): Sampling rate of the sound.
        tvec (numpy.ndarray): Time vector for the sound.
        wave (numpy.ndarray): The generated sound waveform.
        components (list): List to store information about added components.
    """
    def __init__(self, duration, srate):
        """
        Initializes a Sound object.

        Args:
            duration (float): Duration of the sound in seconds.
            srate (int): Sampling rate of the sound.
        """
        self.duration = duration
        self.srate = srate
        self.tvec = np.arange(0, self.duration, 1/self.srate)
        self.wave = np.zeros(len(self.tvec))
        self.components = []
    def add_tone(self, freq, amp=1):
        """
        Adds a sine wave tone to the sound waveform.

        Args:
            freq (float): Frequency of the tone in Hertz.
            amp (float): Amplitude of the tone (default is 1).

        Returns:
            tuple: Time vector and the updated sound waveform.
        """
        self.wave += amp * np.sin(2*np.pi*freq*self.tvec)
        self.components += [{'type':'tone', 'freq':freq, 'amp':amp}]
        return self.tvec, self.wave
    def add_noise(self, amp=1):
        """
        Adds random noise to the sound waveform.

        Args:
            amp (float): Amplitude of the noise (default is 1).

        Returns:
            tuple: Time vector and the updated sound waveform.
        """
        self.wave += amp * randomGen.uniform(-1, 1, len(self.tvec))
        self.components += [{'type':'noise', 'amp':amp}]
        return self.tvec, self.wave
    def add_chord(self, midfreq, factor, ntones, amp=1):
        """
        Adds a chord (multiple tones) to the sound waveform.

        Args:
            midfreq (float): Mid-frequency of the chord in Hertz.
            factor (float): Factor determining how far the highest tone is from the midfreq.
            ntones (int): Number of tones in the chord.
            amp (float): Amplitude of the chord (default is 1).

        Returns:
            tuple: Time vector and the updated sound waveform.
        """
        freqEachComp = np.logspace(np.log10(midfreq/factor),
                                   np.log10(midfreq*factor),
                                   ntones)
        phase = randomGen.uniform(-np.pi, np.pi, ntones)
        for indcomp, freqThisComp in enumerate(freqEachComp):
            self.wave += amp*np.sin(2*np.pi * freqThisComp * self.tvec + phase[indcomp])
        self.components += [{'type':'chord', 'midfreq':midfreq, 'factor':factor,
                             'ntones':ntones, 'amp':amp}]
        return self.tvec, self.wave
    def apply_rise_fall(self, riseTime=0.002, fallTime=0.002):
        """
        Applies rise and fall envelope to the sound waveform.

        Args:
            riseTime (float): Rise time of the envelope in seconds (default is 2ms).
            fallTime (float): Fall time of the envelope in seconds (default is 2ms).

        Returns:
            tuple: Time vector and the updated sound waveform.
        """
        nSamplesRise = round(self.srate * riseTime)
        nSamplesFall = round(self.srate * fallTime)
        riseVec = np.linspace(0, 1, nSamplesRise)
        fallVec = np.linspace(1, 0, nSamplesFall)
        self.wave[:nSamplesRise] *= riseVec
        self.wave[-nSamplesFall:] *= fallVec
        return self.tvec, self.wave
    def suggest_filename(self, suffix=''):
        """
        Generates a suggested filename based on added components.

        Args:
            suffix (str): Optional suffix to append to the filename (default is '').

        Returns:
            str: Suggested filename.
        """
        filename = ''
        for comp in self.components:
            compStr = comp['type']
            if comp['type'] == 'tone':
                compStr += f'{comp["freq"]}Hz'
            if comp['type'] == 'chord':
                compStr += f'{comp["midfreq"]}Hz'
            filename += compStr
            filename += '_'
        return filename.strip('_') + suffix + '.wav'
    def save(self, wavefile, infofile=None, outdir='./'):
        """
        Saves the sound waveform as a WAV file along with a text file containing sound information.

        Args:
            wavefile (str): Filename for the WAV file.
            infofile (str): Filename for the text file containing component information
                            (default is the same as wavefile but with .txt extension).
            outdir (str): Directory to save the files (default is './').
        """
        if wavefile[-4:] != '.wav':
            print('Nothing saved. Your filename needs to end the extension ".wav"')
            return
        wave16bit = (32767*self.wave).astype('int16')
        wavefileFull = os.path.join(outdir, wavefile)
        scipy.io.wavfile.write(wavefileFull, self.srate, wave16bit)
        if infofile is None:
            infofile = wavefile.replace('.wav','.txt')
        infofileFull = os.path.join(outdir, infofile)
        with open(infofileFull, 'w') as file:
            objStr = ''.join([str(cstr)+'\n' for cstr in self.components])
            file.write(objStr)
        print(f'Saved: {wavefileFull}\n       {infofileFull}')


def play_file_linux(soundfile):
    import os
    os.system('aplay {}'.format(soundfile))


def play_file(soundfile):
    try:
        import pygame
    except ModuleNotFoundError:
        print('You need the Python package "pygame" to use play_file().')
        return
    pygame.mixer.init()
    pygame.mixer.music.load(soundfile)
    pygame.mixer.music.play()
    #pygame.time.wait(5000)  # Keep the program running while the sound is playing

