import string
import random
import re
import time
import json


def is_valid_word(word):
    if set(word) - set(string.ascii_lowercase):
        return False
    return len(word) == 5


fw = set()

file = open("./words")
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


# Creates a wrapper so we can keep data between iterations
def cracker_wrapper(word, results):
    include = set()
    badPos = set()
    exclude = set()
    wordBuilder = ["-"] * 5
    filtered_Words = filteredWords.copy()

    def enclosure(word, results):

        filtered_Words.remove(word)

        # Track results and inserts correct chars into wordBuilder array
        for index, char in enumerate(results):
            inc = "".join(include)
            badP = "".join(badPos)
            if char == "exact":
                wordBuilder[index] = word[index]
                include.add(word[index])
            elif char == "out-of-place":
                wordBuilder[index] = "."
                badPos.add(word[index])
            # Ensures char isn't needed. Counting the char is important
            # as we can guess words with repeated letter out-of-place
            elif char == "no-way" and word[index] not in inc and word[index] not in badP and not word.count(char) > 1:
                wordBuilder[index] = "."
                exclude.add(word[index])
            else:
                wordBuilder[index] = "."

        # put correct regex into wordBuilder
        if len(exclude) > 0:
            for index, char in enumerate(wordBuilder):
                if char == "." and results[index] == "out-of-place":
                    # if char is out-of-place we can exclude it from this position
                    wordBuilder[index] = "[^" + "".join(exclude) + word[index] + "]"
                elif char == ".":
                    wordBuilder[index] = "[^" + "".join(exclude) + "]"
        # in case all char are -out-of-place we can include some of them in the regex
        # elif len(badPos) > 0 and len(exclude) == 0:
        #     for index, char in enumerate(wordBuilder):
        #         if char == "." and results[index] == "out-of-place":
        #             wordBuilder[index] = "^[" + ("".join(badPos)).replace(wordBuilder[index], "") + "]"

        for w in list(filtered_Words):
            if re.match("".join(wordBuilder), w):
                # if w doesn't include all chars from badPos, we remove w from filtered_Words
                if len(badPos) > 0 and not all(k in w for k in "".join(badPos)):
                    filtered_Words.remove(w)
                else:
                    pass
            else:
                # remove w from filtered_Words if it doesn't match regex
                filtered_Words.remove(w)

        return random.choice(filtered_Words)

    return enclosure


# pass True to run cracker
def run_game(is_test, answer = random.choice(filteredWords)):
    guessed = None
    guesses = 6

    if is_test:
        cracker = cracker_wrapper("", [])

    results = []

    while guesses:
        if is_test:
            print("Picking a word...")
            if guesses == 6:
                # pick any word to start with in the first guess
                word = random.choice(filteredWords)
            else:
                # if not first guess, pass in the guessed word and results to cracker,
                # so it can filter words based on results and return a new word
                word = cracker(guessed, results)
            print("The word picked was: " + word)
        else:
            word = input("Please guess a word: ")

        if is_valid_word(word):
            if is_test:
                guesses = 5
            else:
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

    print("\033[41mYOU ARE A LOSER THE ANSWER WAS " + answer + "\033[m")
    return False


def run_test(all_words = False):
    count = 0
    win = 0
    loose = 0
    if all_words:
        filteredWordsCopy = filteredWords.copy()
        for i in range(len(filteredWordsCopy)):
            print("Cracking...")
            print(str(i) + " " + filteredWordsCopy[i])
            try:
                w = run_game(True, filteredWordsCopy[i])
                if w:
                    win += 1
                else:
                    loose += 1
            except:
                count += 1
                loose += 1
    else:
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


def run_all_test(ts):
    errors = []
    count = 0
    win = 0
    loose = 0
    filteredWordsCopy = filteredWords.copy()
    n = len(filteredWords)

    for idx, word in enumerate(list(filteredWordsCopy)):
        try:
            filteredWordsCopy.remove(word)
            guessed = None
            answer = word
            guesses = 6
            results = []

            cracker = cracker_wrapper("", [])

            while guesses:
                if guesses == 6:
                    word = random.choice(filteredWords)
                else:
                    word = cracker(guessed, results)

                if is_valid_word(word):
                    guesses -= 1
                    if word == answer:
                        win += 1
                    else:
                        results = compute_hint(word, answer)
                        guessed = word

            loose += 1
            print(f'\rTotal: {n} - Done: {idx + 1} [{round((100*idx + 1)/n,2)}%] - Wins: {win} - Losses: {loose} - Errors: {count} - Time '
                  f'lapsed: {round(time.time() - ts, 2)}', end = ' ')
        except:
            count += 1
            errors.append(word)

    with open('errors_output.txt', 'w') as filehandle:
        json.dump(errors, filehandle)
    with open('output.txt', 'w') as filehandle:
        filehandle.write("Total: " + str(n) + " - Done: " + str(idx) + " - Wins: " + str(win) +
                  " - Losses: " + str(loose) + " - Errors: " + str(count) + " - Time lapsed: " + str(round(time.time() - ts, 2)))

    print("\n\n")
    print("-" * 30)
    print("Total:  " + str(n) + " games")
    print("Wins:   " + str(win) + " - " + str((100 * win)/n) + "%")
    print("Losses: " + str(loose - count) + " - " + str((100 * (loose - count))/n) + "%")
    print("Errors: " + str(count) + " - " + str((100 * count)/n) + "%")
    print("-" * 30)


def run_specific_word(answer):
    guessed = None
    guesses = 6

    cracker = cracker_wrapper("", [])

    results = []

    while guesses:

        if guesses == 6:
            # pick any word to start with in the first guess
            word = random.choice(filteredWords)
        else:
            # if not first guess, pass in the guessed word and results to cracker,
            # so it can filter words based on results and return a new word
            word = cracker(guessed, results)
        print("The word picked was: " + word)

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

    print("\033[41mYOU ARE A LOSER THE ANSWER WAS " + answer + "\033[m")
    return False


def main():
    print("")
    print("🎉 🎉 Welcome to wordle 🎉 🎉\n")
    print("")
    print("Press 1 to play")
    print("Press 2 to run game/cracker")
    print("Press 3 to run game/cracker for specific word")
    answer1 = int(input("Press 4 to run all tests: "))
    # answer1 = int(input("Press 1 to play, 2 to run game/cracker, or 9 to run all tests: "))
    print("")
    # test = True if answer1 != 1 and answer1 != 9 else False

    ts = time.time()
    if answer1 == 1:
        run_game(False)
    elif answer1 == 2:
        run_test()
    elif answer1 == 3:
        word = input("Enter the word to be used as answer: ")
        run_specific_word(word)
    elif answer1 == 4:
        run_test(True)
    else:
        run_test()

    print("Time elapsed: " + str(round(time.time() - ts, 2)) + "s")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
