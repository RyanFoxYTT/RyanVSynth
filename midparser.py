import mido

def parse_midi(midi_path):
    """parse midi file"""
    mid = mido.MidiFile(midi_path)
    notes = []
    current_time = 0  # absolute time in ticks
    active_notes = {}
    
    tempo = 500000  # default 120 BPM
    
    for track in mid.tracks:
        for msg in track:
            current_time += msg.time  # absolute time!
            
            if msg.type == 'set_tempo':
                tempo = msg.tempo
            
            if msg.type == 'note_on' and msg.velocity > 0:
                active_notes[msg.note] = current_time
                
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                if msg.note in active_notes:
                    start_ticks = active_notes[msg.note]
                    end_ticks = current_time
                    duration_ticks = end_ticks - start_ticks
                    
                    ticks_per_beat = mid.ticks_per_beat
                    seconds_per_beat = tempo / 1_000_000
                    
                    start_seconds = (start_ticks / ticks_per_beat) * seconds_per_beat
                    duration_seconds = (duration_ticks / ticks_per_beat) * seconds_per_beat
                    
                    notes.append({
                        'pitch': msg.note,
                        'start': start_seconds,  # absolute start in seconds!
                        'duration': duration_seconds,
                    })
                    del active_notes[msg.note]
    
    return notes