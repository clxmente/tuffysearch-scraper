import unicodedata

# Character mapping for common Unicode escape sequences
REPLACE_CHAR_MAP = {
    "\u00a0": " ",  # NO-BREAK SPACE
    "\u00a9": "(c)",  # COPYRIGHT SIGN
    "\u00ae": "(r)",  # REGISTERED SIGN
    "\u00bf": "?",  # INVERTED QUESTION MARK
    "\u00c1": "A",  # Á
    "\u00cd": "I",  # Í
    "\u00e9": "e",  # é
    "\u00f1": "n",  # ñ
    "\u2013": "-",  # EN DASH
    "\u2019": "'",  # RIGHT SINGLE QUOTE
    "\u201c": '"',  # LEFT DOUBLE QUOTE
    "\u201d": '"',  # RIGHT DOUBLE QUOTE
}

# Create translation table once at module level for better performance
TRANSLATION_TABLE = str.maketrans(REPLACE_CHAR_MAP)


def clean_text(text: str) -> str:
    """Clean unicode escape sequences from text using a predefined mapping

    :param str text: The input text to clean
    :return str: The cleaned text
    """
    # log any unknown characters
    unknown_chars = set()
    for char in text:
        if ord(char) > 127 and char not in REPLACE_CHAR_MAP:
            unknown_chars.add(char)
    if unknown_chars:
        print("\nCharacters not in REPLACE_CHAR_MAP:")
        for char in sorted(unknown_chars, key=ord):
            codepoint = f"\\u{ord(char):04x}"
            name = unicodedata.name(char, "<unknown>")
            print(f"{codepoint} => {char} ({name})")
    return text.translate(TRANSLATION_TABLE)
