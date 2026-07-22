def midi_to_hz(midi_note):
    """Конвертирует MIDI-номер (0-127) в частоту в Гц."""
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))