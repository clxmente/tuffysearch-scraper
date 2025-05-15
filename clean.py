# Clean up unicode escape sequences in our data, any new values will be printed
import os
import json
import unicodedata

TARGET_FILE = "2025-2026_catalog.json"
with open(os.path.join("data", TARGET_FILE), "r", encoding="utf-8") as f:
    data = json.load(f)
print(f"Loaded {len(data)} courses")

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
TRANSLATION_TABLE = str.maketrans(REPLACE_CHAR_MAP)

# Track unknown characters
unknown_chars = set()

# First pass: find unknown characters
for obj in data.values():
    if "description" in obj:
        for char in obj["description"]:
            if (
                ord(char) > 127 and char not in REPLACE_CHAR_MAP
            ):  # non-ASCII and not in our map
                unknown_chars.add(char)

# Output unknown characters
print("\nCharacters not in REPLACE_CHAR_MAP:") if unknown_chars else None
for char in sorted(unknown_chars, key=ord):
    codepoint = f"\\u{ord(char):04x}"
    name = unicodedata.name(char, "<unknown>")
    print(f"{codepoint} => {char} ({name})")

print("Replacing values using translation table")
# Process and translate the data
for obj in data.values():
    if "description" in obj:
        obj["description"] = obj["description"].translate(TRANSLATION_TABLE)

# Write the translated data back to file
output_file = os.path.join("data", f"cleaned_{TARGET_FILE}")
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Wrote {len(data)} courses to {output_file}")
