# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import string
import random

expected = "GUESS"


def is_valid_word(word):
    if set(word) - set(string.ascii_lowercase):
        return False
    return len(word) == 5


filteredWords = []

file = open("/usr/share/dict/words")
for line in file:
    line = line.strip()
    line = line.lower()
    if is_valid_word(line):
        filteredWords.append(line)


def display_hint(results, guess):
    for r, l in zip(results, guess):
        if r == 'exact':
            print('\033[42;30m' + l, end='')
        elif r == 'out-of-place':

            print('\033[43;30m' + l, end='')
        else:
            print('\033[47;30m' + l, end='')
    print('\033[m')


def compute_hint(word, answer):
    results = []
    exact = []
    left = list(answer)
    for i, (w, a) in enumerate(zip(word, answer)):
        if w == a:
            results.append('exact')
            left.remove(w)
        else:
            results.append('no-way')

    for i, (w, a, r) in enumerate(zip(word, answer, results)):
        if r == 'exact':
            continue
        else:
            if w in left:
                results[i] = 'out-of-place'
                left.remove(w)
    return results


def main():

    answer = random.choice(filteredWords)
    guesses = 6
    while guesses:
        word = input("Please guess a word: ")
        if is_valid_word(word) and word in filteredWords:
            guesses -= 1
            if word == answer:
                print("WELL DONE," + word + "  IS THE RIGHT ANSWER!")
                return
            else:
                results = compute_hint(word, answer)
                display_hint(results, word)
        else:
            print('That is not a valid 5 letter word')

    print("YOU ARE A LOSER THE ANSWER WAS", answer)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
