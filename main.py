import numpy as np
import argparse
import midparser
import lyrparser
import pitcht
import os
import logging
import soundfile as sf
import time
import sys
from colorama import init, Style, Fore, Back
import tqdm

init()

def handle_exception(exc_type, exc_value, exc_traceback):
    """Ловит ВСЕ необработанные исключения и пишет в лог."""
    logger.critical("UNHANDLED EXCEPTION:", exc_info=(exc_type, exc_value, exc_traceback))


logger = logging.getLogger(__name__)
logging.basicConfig(
    filename='rv_synth_' + time.strftime('%Y-%m-%d_%H-%M-%S') + '.log',
    encoding='utf-8', 
    level=logging.DEBUG
)

sys.excepthook = handle_exception

logger.debug('start time: \n' + time.strftime('%Y-%m-%d_%H-%M-%S'))

def get_wav_path(voice_folder, phoneme):
    logger.debug('getting/finding wav paths')
    # if phoneme is UPPERCASE, try underscore first
    if phoneme != phoneme.lower():  # это заглавная буква
        logger.debug('finding uppercase phonemes/underscore wav files')
        path_underscore = os.path.join(voice_folder, f"_{phoneme}.wav")
        if os.path.exists(path_underscore):
            return path_underscore
    
    # normal path for everyone
    path_normal = os.path.join(voice_folder, f"{phoneme}.wav")
    if os.path.exists(path_normal):
        logger.debug('finding normal wav files')
        return path_normal

    logger.warning(f"wav file for phoneme '{phoneme}' not found")
    print(f"WARNING: wav file for phoneme '{phoneme}' not found")
    return None

parser = argparse.ArgumentParser()
parser.add_argument("-v", type=str, help="voicebank folder")
parser.add_argument("-m", type=str, help="midi path")
parser.add_argument("-l", type=str, help="lyrics")
parser.add_argument("-t", type=int, default=0, help="transpose (-24 to 24)")
parser.add_argument("-o", type=str, help="output file name")
args = parser.parse_args()

logger.debug("\n\n - - - PARSING SECTION - - - ")

logger.debug("-- parsing midi")
parsed_midi = midparser.parse_midi(args.m)
parsed_midi_str = "".join(map(str, parsed_midi)) 
logger.debug("-- parsed midi:\n" + parsed_midi_str)
logger.debug("-- parsing lyrics")
parsed_lyrics = lyrparser.parse_lyrics(args.l)
parsed_lyrics_str = "".join(map(str, parsed_lyrics)) 
logger.debug("-- parsed lyrics:\n" + parsed_lyrics_str)

output_audio = []

def synthesize():

    logger.debug("\n\n - - - SYNTHESIZING SECTION - - - ")

    sample_rate = 44100
    output_audio = []
    last_end_time = 0.0  # когда закончилась предыдущая нота

    print('\n')
    pbar = tqdm.tqdm(total=len(parsed_midi), desc="Synthesizing", unit="notes", colour="green")
    
    for midi_note, lyric in zip(parsed_midi, parsed_lyrics):
        note_pitch = midi_note['pitch']
        note_duration = midi_note['duration']
        note_start = midi_note['start']
        
        # ADD SILENCE IF GAP BEFORE NOTE
        if note_start > last_end_time:
            gap = note_start - last_end_time
            silence = np.zeros(int(gap * sample_rate))
            output_audio.append(silence)
        logger.debug("-- adding silence (if theres gaps before note)")
        
        # just collect all phonemes for this note
        note_audio = []
        note_samples = int(note_duration * sample_rate)
        logger.debug("-- collecting phones for current note")
        
        # find the vowel
        vowel_phonemes = []
        before_phonemes = []
        after_phonemes = []
        logger.debug("-- finding vowels")
        
        found_vowel = False
        for phoneme in lyric:
            ptype = pitcht.phone_dict.get(phoneme, "stop")
            if ptype != "stop":
                found_vowel = True
                vowel_phonemes.append(phoneme)
                logger.debug("-- found vowel")
            elif not found_vowel:
                before_phonemes.append(phoneme)
                logger.debug("-- not found vowel")
            else:
                after_phonemes.append(phoneme)
                logger.debug("-- idk blyat")
        
        # play everything in order
        for phoneme in before_phonemes:
            wav_path = get_wav_path(args.v, phoneme)
            if wav_path:
                audio, sr = pitcht.shift_sample(wav_path, note_pitch, "stop", note_duration)
                note_audio.append(audio)
            logger.debug("-- playing all in order")

        # calculate how much time after-vowel consonants need
        after_duration = 0
        for phoneme in after_phonemes:
            wav_path = get_wav_path(args.v, phoneme)
            if wav_path:
                audio, sr = pitcht.shift_sample(wav_path, note_pitch, "stop", note_duration)
                after_duration += len(audio) / sr
            logger.debug("-- calculating how much time after-vowel consonants need")

        # vowel gets remaining time MINUS after-consonants time
        vowel_time = note_duration - after_duration
        if vowel_time < 0:
            vowel_time = 0

        for phoneme in vowel_phonemes:
            wav_path = get_wav_path(args.v, phoneme)
            if wav_path:
                ptype = pitcht.phone_dict.get(phoneme, "vowel")
                audio, sr = pitcht.shift_sample(wav_path, note_pitch, ptype, vowel_time)
                # cut vowel if too long
                desired = int(vowel_time * sample_rate)
                if len(audio) > desired:
                    audio = audio[:desired]
                note_audio.append(audio)

        # now add after-vowel consonants (they will be cut if note ends)
        for phoneme in after_phonemes:
            wav_path = get_wav_path(args.v, phoneme)
            if wav_path:
                audio, sr = pitcht.shift_sample(wav_path, note_pitch, "stop", note_duration)
                note_audio.append(audio)
        
        # combine and cut to note duration
        if note_audio:
            combined = np.concatenate(note_audio)
            if len(combined) > note_samples:
                combined = combined[:note_samples]
            elif len(combined) < note_samples:
                combined = np.pad(combined, (0, note_samples - len(combined)))
            output_audio.append(combined)
        
        # update position
        last_end_time = note_start + note_duration

        pbar.set_postfix({
            'pitch': midi_note['pitch'],
            'phonemes': ''.join(lyric)
        })
        pbar.update(1)
    
    pbar.close()
    
    # save
    if not output_audio:
        logger.error("\n           ERROR: \n                 -- no audio generated... check midi and voicebank.. \n                 -- does midi contains notes? / does voicebank folder contains any wavs? \n\n anyways, program will crash/end. . .")
        tqdm.tqdm.write(f"\n           {Style.BRIGHT}{Fore.GREEN}ERROR:{Style.RESET_ALL}{Fore.RESET} \n                 {Fore.BLACK}{Back.GREEN}-- no audio generated... check midi and voicebank.. {Back.RESET}{Fore.RESET}\n                 {Fore.BLACK}{Back.GREEN}-- does midi contains notes? / does voicebank folder contains any wavs?{Back.RESET}{Fore.RESET} \n\n {Style.DIM}{Fore.LIGHTBLACK_EX}anyways, program will crash/end. . .{Style.RESET_ALL}")
        return

    final = np.concatenate(output_audio)
    sf.write(args.o if args.o.endswith('.wav') else args.o + '.wav', final, sample_rate)
    logger.info(f"total notes: {len(parsed_midi)}")
    logger.info(f"total duration: {last_end_time:.2f} seconds")
    print("done! rendered into " + (args.o if args.o.endswith('.wav') else args.o + '.wav'))

if __name__ == "__main__":
    synthesize()