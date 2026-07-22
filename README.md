# RyanVSynth
A singing synthesizer like utau but on python and easier

RVSynth don't have gui, only console use.

RVSynth voicebanks do not require configurations like oto.ini in utau. wav only. the synthesizer itself does the rest. it also doesn’t yet have time stretching, so the notes will be cut off before the end of the notes (this synthesizer originally started just for fun, but.. 

Example command:

python main.py -v E:\voicebank -m song.mid -l "hVl low may neym iz ra yVn FQx" -o 'mysong'

Arguments:

-v = voicebank folder path
-m = midi file path
-l = lyrics/phonemes (like: hVl low may neym iz ra yQn FQx)
-o = output wav name

Dependencies:

pip install numpy soundfile colorama tqdm pyworld mido

License: MIT
