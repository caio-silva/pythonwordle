import string
import random
import re
import time
import json
import copy


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
    print('\033[m\n')


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
    filtered_Words = copy.deepcopy(filteredWords)

    def enclosure(word, results):

        # for some reason word is not present in filtered_Words ??
        # not sure why. try will avoid this type of error
        try:
            filtered_Words.remove(word)
        except ValueError:
            pass

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
        #             wordBuilder[index] = "[" + ("".join(badPos)).replace(word[index], "") + "]"

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
def run_game(is_test):
    guessed = None
    answer = random.choice(filteredWords)
    guesses = 6

    if is_test:
        cracker = cracker_wrapper("", [])

    results = []

    while guesses:
        if is_test:
            print("Thinking of a word... 🤔🤔🤔")
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
            guesses -= 1
            if word == answer:
                print("\n👍 👍 \033[42;30m WELL DONE, \x1B[3m" + word + "\x1B[0m\033[42;30m IS THE RIGHT ANSWER!, YOU GUESSED ON YOUR " + str(
                    6 - guesses) + " guess." + " \033[m 👍 👍")
                return True
            else:
                results = compute_hint(word, answer)
                display_hint(results, word)
                guessed = word
        else:
            print('That is not a valid 5 letter word')

    print("\n👎 👎 \033[41m YOU ARE A LOSER THE ANSWER WAS \x1B[3m" + answer + " \x1B[0m\033[m 👎 👎")
    print("")
    return False


def run_test():
    errors = 0
    win = 0
    loose = 0
    n = int(input("How many games? "))
    print("")
    for i in range(n):
        try:
            w = run_game(True)
            if w:
                win += 1
            else:
                loose += 1
        except:
            errors += 1
        finally:
            input("\nPress \x1B[3mEnter\x1B[0m to continue..")
            print("")

    print("\n\n")
    print("-" * 30)
    print("Total:  " + str(n) + " games")
    print("Wins:   " + str(win) + " - " + str((100 * win)/n) + "%")
    print("Losses: " + str(loose) + " - " + str((100 * loose)/n) + "%")
    print("Errors: " + str(errors) + " - " + str((100 * errors)/n) + "%")
    print("-" * 30)


def bar(win, loose, errors, idx, n, ts):
    return f'\rTotal: {n} - Done: {idx + 1} [{round((100*(idx + 1))/n,2)}%] - Wins: {win} [{round((100*win)/(idx + 1),2)}%] - Losses: {loose} [{round((100*loose)/(idx + 1), 2)}%] - Errors: {errors} [{round((100*errors)/(idx + 1), 2)}%] - Time lapsed: {round(time.time() - ts, 2)}s'


def run_all_test(ts):
    lostList = []
    errors = 0
    win = 0
    loose = 0
    filteredWordsCopy = copy.deepcopy(filteredWords)
    n = len(filteredWords)
    p = ""

    for idx, word in enumerate(list(filteredWordsCopy)):
        try:
            guessed = None
            answer = word
            guesses = 6
            results = []

            cracker = cracker_wrapper("", [])

            while guesses:
                if guesses == 6:
                    w = random.choice(filteredWords)
                else:
                    w = cracker(guessed, results)

                if is_valid_word(w):
                    guesses -= 1
                    if w == answer:
                        win += 1
                        break
                    else:
                        results = compute_hint(w, answer)
                        guessed = w
                if guesses == 0 and w != answer:
                    loose += 1
                    lostList.append(answer)

            p = bar(win, loose, errors, idx, n, ts)
            print(f'{p}', end= ' ')
        except KeyboardInterrupt:
            print("\n\nThe application is shutting down.")
            print("Saving files to disk")
            p = bar(win, loose, errors, idx, n, ts)
            break
        except:
            errors += 1

    with open('lost_output2.txt', 'w') as filehandle:
        json.dump(lostList, filehandle)
    with open('output2.txt', 'w') as filehandle:
        filehandle.write(p)

    print("Files saved.")
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
    print("")

    ts = time.time()
    if answer1 == 1:
        run_game(False)
    elif answer1 == 2:
        run_test()
    elif answer1 == 3:
        word = input("Enter the word to be used as answer: ").lower().strip()
        run_specific_word(word)
    elif answer1 == 4:
        run_all_test(ts)
    else:
        run_test()

    print("\n\nTime elapsed: " + str(round(time.time() - ts, 2)) + "s")
    print("\n💔 Good bye 💔")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
