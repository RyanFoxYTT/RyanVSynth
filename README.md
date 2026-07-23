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




## ARPABET to RyanVSynth (RVSynth) Conversion Guide

RVSynth uses a compact single-character system. Use this cheat sheet to convert ARPABET lyrics:

**Vowels:**
*   `AA` → `a` (f**a**ther)
*   `AE` → `V` (c**a**t)
*   `AX` → `Q` (**a**bout)
*   `EH` → `e` (b**e**d)
*   `ER` → `3` (b**ir**d)
*   `IY` / `IH` → `i` (b**ee**t / b**i**t)
*   `OW` → `o w` (g**o**)
*   `UW` → `u w` (t**oo**)

**Consonants (Special single-char mappings):**
*   `CH` → `C`
*   `DH` → `D` (**th**is)
*   `JH` → `j`
*   `NG` → `N` (si**ng**)
*   `SH` → `S` (**sh**e)
*   `TH` → `T` (**th**ink)
*   `TS` → `c` (ca**ts**) 
*   `ZH` → `Z` (plea**s**ure)
*   `HH` → `h` (**h**ello)

**Other sounds:**
*   Glottal stop (`Q`) → `q`
*   All other ARPABET consonants (`B, D, F, G, H, K, L, M, N, P, R, S, T, V, W, Y, Z`) map directly to their lowercase equivalent.

License: MIT
