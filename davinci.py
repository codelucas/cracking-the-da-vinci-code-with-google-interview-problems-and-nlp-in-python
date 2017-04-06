import string
import time


TRIE_END = '__end'

INPUT_COMMON_ENGLISH_WORDS = './google-10000-english-usa.txt'
INPUT_TRIGRAMS = './trigrams.txt'


def build_trie():
    with open (INPUT_COMMON_ENGLISH_WORDS, 'r') as english_words:
        data = [line.strip() for line in english_words.readlines()
                if line.strip()]
        root = {}
        for word in data:
            current_dict = root
            for letter in word:
                current_dict = current_dict.setdefault(letter, {})
            current_dict[TRIE_END] = True
        print('Trie contains %s words' % len(data))
        return root


def build_english_dict():
    with open (INPUT_COMMON_ENGLISH_WORDS, 'r') as english_words:
        return set(line.strip() for line in english_words.readlines()
                   if line.strip() and len(line.strip()) > 1)


def find_bigrams(input_list):
    return zip(input_list, input_list[1:])


def is_trie_prefix(trie, word):
    if not word or not word.strip():
        return False

    current_dict = trie
    for letter in word:
        if letter in current_dict:
            current_dict = current_dict[letter]
        else:
            return False
    return True


TRIE = build_trie()
ENGLISH_DICT = build_english_dict()

skipped_recursion = 0


def recurse(input_letters, current_permu, solution, final_len, word_end_index):
    global skipped_recursion
    # current permutation matches original anagram length, see if words
    # qualify as real sentence and dedupe, if valid, add to solution set
    if len(current_permu) == final_len:
        last_word = ''.join(current_permu[word_end_index:])
        candidate_word = ''.join(current_permu)
        if last_word in ENGLISH_DICT and \
                candidate_word not in solution:
            solution = solution.add(candidate_word)
            # print(candidate_word.upper())
        return

    seen_at_start = set()  # dedupe repeated characters in recursive depth
    for idx in range(len(input_letters)):
        cur = input_letters.pop(idx)
        if cur in seen_at_start:
            skipped_recursion += 1
            input_letters.insert(idx, cur)
            continue

        seen_at_start.add(cur)
        current_permu.append(cur)
        # spaces get special treatment since they distinguish words,
        # if a word is not valid english (via trie) we stop recursing
        if cur == ' ':
            # cut off extra space
            candidate_word = ''.join(current_permu[word_end_index:-1])
            if candidate_word not in ENGLISH_DICT: # not is_trie_word(TRIE, candidate_word):
                # don't recurse - recent word chunk not valid
                skipped_recursion += 1
                pass
            else:
                recurse(
                    input_letters,
                    current_permu,
                    solution,
                    final_len,
                    len(current_permu)
                )
        else:
            if is_trie_prefix(TRIE, ''.join(current_permu[word_end_index:])):
                recurse(
                    input_letters,
                    current_permu,
                    solution,
                    final_len,
                    word_end_index
                )
            else:
                # don't recurse - word isn't valid, skip onto next one
                skipped_recursion += 1
                pass

        input_letters.insert(idx, cur)
        current_permu.pop()


def transform(s):
    # remove punctution, make lowercase
    s = s.translate(None, string.punctuation)
    return s.lower()


start = time.time()

# orig_string = 'OH, LAME SAINT'
orig_string = 'O, DRACONIAN DEVIL'
xformed_string = transform(orig_string)
xformed_string = list(xformed_string)

# we sort the input characters so we can dedupe and skip recursive calls
# orig = sorted(xformed_string)
final_anagram_len = len(xformed_string)
solution = set()

recurse(xformed_string, [], solution, final_anagram_len, 0)
print('After permuting the anagram %s has %s combinations' %
    (orig_string, len(solution)))

end = time.time()
print('Time elapsed is %s' % (end - start))
print('We skipped recursive calls %s times' % skipped_recursion)


common_ngrams_dict = {}
# now we need to build a map of the english language's most common bigrams, common bigrams
# are referred to as collocations - two words that, together, are unusually common in
# english texts. we use this technique to filter out the nonsense anagram combinations
# to a sane number this file has just over 1M trigrams, about 17MB (that's fine)
with open(INPUT_TRIGRAMS, 'r') as ngrams_data:
    clean_lines = [s.strip() for s in ngrams_data.read().splitlines()]
    for line in clean_lines:
        freq, w1, w2, w3 = line.split()
        common_ngrams_dict[(w1, w2, w3)] = int(freq)


print('ngram dictionary contains %s words' % len(common_ngrams_dict))

filtered_solution = []
for anagram in solution:
    trigram = tuple(anagram.split())
    if trigram in common_ngrams_dict:
        filtered_solution.append(anagram)


print('After filtering anagrams without common trigrams, the anagram %s has %s combinations' %
    (orig_string, len(filtered_solution)))


for anagram in filtered_solution:
    print(anagram.upper())
