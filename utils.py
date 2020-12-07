# Filters
def is_music_file(filename):
    """Returns a True if the filename is a music file."""
    files_extensions = [
        ".pcm", ".wav", ".aiff", ".mp3", ".aac", ".ogg", ".wma",
        ".flac", ".alac", ".m4a"
    ]
    is_music = [filename.endswith(extension) for extension in files_extensions]
    return any(is_music)
