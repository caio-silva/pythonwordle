import string
import random
import re
import time


def is_valid_word(word):
    if set(word) - set(string.ascii_lowercase):
        return False
    return len(word) == 5


fw = set()

file = open("/usr/share/dict/words")
for line in file:
    line = line.strip().lower()
    if is_valid_word(line):
        fw.add(line)

filteredWords = list(fw)


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


def cracker_wrapper(word, results):
    include = set()
    badPos = set()
    exclude = set()
    wordBuilder = ["-"] * 5
    filtered_Words = filteredWords.copy()

    def enclosure(word, results):

        filtered_Words.remove(word)

        for index, char in enumerate(results):
            inc = "".join(include)
            badP = "".join(badPos)
            if char == "exact":
                wordBuilder[index] = word[index]
                include.add(word[index])
            elif char == "out-of-place":
                wordBuilder[index] = "."
                badPos.add(word[index])
            elif char == "no-way" and char not in inc and char not in badP:
                wordBuilder[index] = "."
                exclude.add(word[index])

        if len(exclude) > 0:
            for index, char in enumerate(wordBuilder):
                if char == "." and results[index] == "out-of-place":
                    wordBuilder[index] = "[^" + "".join(exclude) + word[index] + "]"
                elif char == ".":
                    wordBuilder[index] = "[^" + "".join(exclude) + "]"

        for w in list(filtered_Words):
            if re.match("".join(wordBuilder), w):
                if len(badPos) > 0 and not all(k in w for k in "".join(badPos)):
                    filtered_Words.remove(w)
                else:
                    pass
            else:
                filtered_Words.remove(w)

        return random.choice(filtered_Words)

    return enclosure


def run_game(is_test):
    guessed = None
    answer = random.choice(filteredWords)
    guesses = 6

    if is_test:
        cracker = cracker_wrapper("", [])

    results = []

    while guesses:
        if is_test:
            print("Picking a word...")
            if guesses == 6:
                word = random.choice(filteredWords)
                filteredWords.remove(word)
            else:
                word = cracker(guessed, results)
            print("The word picked was: " + word)
        else:
            word = input("Please guess a word: ")

        # if is_valid_word(word) and word in filteredWords:
        if is_valid_word(word):
            guesses -= 1
            if word == answer:
                print("\033[42;30mWELL DONE, " + word + "  IS THE RIGHT ANSWER!, You guessed on your " + str(
                    6 - guesses) + " guess." + "\033[m")
                return True
            else:
                results = compute_hint(word, answer)
                display_hint(results, word)
                guessed = word
        else:
            print('That is not a valid 5 letter word')

    print("YOU ARE A LOSER THE ANSWER WAS", answer)
    return False


def run_test():
    count = 0
    win = 0
    loose = 0
    n = int(input("How many games? "))
    for i in range(n):
        try:
            w = run_game(True)
            if w:
                win += 1
            else:
                loose += 1
        except:
            count += 1
            loose += 1
    print("\n\n")
    print("-" * 30)
    print("Total:  " + str(n) + " games")
    print("Wins:   " + str(win) + " - " + str((100 * win)/n) + "%")
    print("Losses: " + str(loose - count) + " - " + str((100 * (loose - count))/n) + "%")
    print("Errors: " + str(count) + " - " + str((100 * count)/n) + "%")
    print("-" * 30)


def main():
    answer1 = int(input("Play? Press 1 and Enter or to use the cracker press 2 and Enter "))
    test = True if answer1 == 2 else False

    ts = time.time()
    if test:
        run_test()
    else:
        run_game(False)
    print("Time elapsed in secs: " + str(time.time() - ts))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
