
import string
import random

expected = "GUESS"
filteredWords = []

file = open("/usr/share/dict/words")

def is_valid_word(word):
    if set(word) - set(string.ascii_lowercase):
        return False
    return len(word) == 5

for line in file:
    line = line.strip()
    line = line.lower()
    if is_valid_word(line):
        filteredWords.append(line)

matches = []
known = input("Known positions: ")
import re
exacts=[]
for word in filteredWords:
    if re.match(known, word):
        exacts.append(word)

possibles = []

known_bad = input("Bad letters: ")
for exact in exacts:
    if any(k in known_bad for k in exact):
        pass
    else:
        possibles.append(exact)

print(possibles)
