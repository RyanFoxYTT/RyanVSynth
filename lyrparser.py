def parse_lyrics(lyrics):
    """Разбивает лирику на ноты (по пробелам) и фонемы (посимвольно)."""
    notes = lyrics.split()
    result = []
    for note in notes:
        phonemes = list(note)
        result.append(phonemes)
    print(result)
    return result