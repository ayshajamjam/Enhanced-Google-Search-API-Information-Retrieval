"""
Command-line application that does a custom search using Google API.
"""
# coding: utf-8

import sys
import math
import re


import nltk
import ssl
import itertools

# Run this and donwload the packages when you first run the program

# try:
#     _create_unverified_https_context = ssl._create_unverified_context
# except AttributeError:
#     pass
# else:
#     ssl._create_default_https_context = _create_unverified_https_context

# nltk.download()

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from collections import defaultdict
from operator import itemgetter
from googleapiclient.discovery import build

def log_frequency(tf):
    if (tf == 0):
        return 0
    else: 
        return (1 +  math.log10(tf))

def inverse_document_frequency(N, df):

    idf = df.copy()
    for key in df:
        idf[key] = math.log10(N/idf[key])
    
    return idf

def get_ngrams(sequence, n):
    ngrams = []

    start = []
    if n == 1:
        start = ['START']
    if n > 1:
        for i in range(0, n-1):
            start = start + ['START']
    elif n <= 0:
        return []

    sequence = start + sequence + ['STOP']
    
    for i in range(0, len(sequence) - n + 1):
        ngram = []
        for j in range(i, i+n):
            ngram.append(sequence[j])
        ngrams.append(tuple(ngram))

    return ngrams

def count_ngrams(corpus, unigramcounts, bigramcounts):
        for corp in corpus:
            for uni in get_ngrams(corp, 1):
                if uni == ('START',):
                    continue
                if uni in unigramcounts:
                    unigramcounts[uni] = unigramcounts[uni] + 1
                else:
                    unigramcounts[uni] = 1

            for bi in get_ngrams(corp, 2):
                if bi in bigramcounts:
                    bigramcounts[bi] = bigramcounts[bi] + 1
                else:
                    bigramcounts[bi] = 1
        return [unigramcounts, bigramcounts]

def raw_bigram_probability(bigram, unigramcounts, bigramcounts, sentence_count):
        """
        COMPLETE THIS METHOD (PART 3)
        Returns the raw (unsmoothed) bigram probability
        """
        uni = bigram[:1]
        uni = tuple(uni)

        try:
            if uni == ('START',):
                return float(bigramcounts[bigram])/sentence_count

            return float(bigramcounts[bigram])/unigramcounts[uni]
        except:
            return 0.0
    
def raw_unigram_probability(unigram, unigramcounts, word_count):
    return float(unigramcounts[unigram])/ word_count

def smoothed_bigram_probability(bigram, unigramcounts, bigramcounts, word_count, sentence_count):
    lambda1 = 1/3.0
    lambda2 = 1/3.0

    unigram = bigram[1:]
    unigram = tuple(unigram)
    # print(unigram)
    return lambda1*raw_bigram_probability(bigram, unigramcounts, bigramcounts, sentence_count) + lambda2*raw_unigram_probability(unigram, unigramcounts, word_count)
        
def sentence_logprob(sentence, unigramcounts, bigramcounts, word_count, sentence_count):
    sentence_prob = 0.0
    for bigram in get_ngrams(sentence, 2):
        sentence_prob = sentence_prob+math.log2(smoothed_bigram_probability(bigram, unigramcounts, bigramcounts, word_count, sentence_count))
    return sentence_prob

def main(query=None):

    # query URL = python main.py <google api developer key> <google engine id> <precision> <query>
    if (len(sys.argv) != 5):
        print("Invalid arguments provided")
        print("Arguments should contain: main.py <google api developer key> <google engine id> <precision> <query>")
        return
    
    developer_key = sys.argv[1]
    engine_key = sys.argv[2]
    input_precision = (float)(sys.argv[3])
    if query == None:
        query = sys.argv[4]

    query = query.lower()

    print("\n")
    print("Parameters:")
    print("Developer key = ", developer_key)
    print("Engine key    = ", engine_key)
    print("Query         = ", query)
    print("Precision     = ", input_precision)
    print("Google Search Results:")
    print("======================")

    service = build(
        "customsearch", "v1", developerKey=developer_key
    )

    res = (
        service.cse()
        .list(
            q=query,
            cx=engine_key,
        )
        .execute()
    )

    number_of_search_results = 10

    # Don't include non-html documents returned by Google
    html_docs_returned = 0

    # Keep track of number of relevant results as we iterate through response 
    relevance_count = 0
    relevance_tracker = []

    term_frequencies = []
    log_frequencies = []

    corpus = []
    unigramcounts = {} # might want to use defaultdict or Counter instead
    bigramcounts = {}
    sentence_count = 0
    word_count = 0
    
    document_frequencies = defaultdict(int)
    inverse_df = defaultdict(int)

    vocabulary = set()
    stop_words = set(stopwords.words('english'))

    # Build the vocabulary dict using the page summary + title
    for page in range(number_of_search_results):

        allKeys = res["items"][page].keys()

        # print("Page ", page, ' ', res["items"][page], '\n')

        if("fileFormat" in allKeys or "snippet" not in allKeys or "title" not in allKeys):
            continue
        
        # Parse through summary
        summary = res["items"][page]["snippet"].lower()
        summary = re.sub('[^A-Za-z0-9]+', ' ', summary)
        
        # removing stop words from summary
        summary_tokens = word_tokenize(summary)
        # print(summary_tokens)
        for word in summary_tokens:
            if word not in stop_words:
                vocabulary.add(word)

        # Parse through title
        title = res["items"][page]["title"].lower()
        title = re.sub('[^A-Za-z0-9]+', ' ', title)
        
        # removing stop words from title
        title_tokens = word_tokenize(title)
        for word in title_tokens:
            if word not in stop_words:
                vocabulary.add(word)

    # First 10 responses
    for i in range(number_of_search_results):
        # Res (dict) -> res['items'] (list) -> res['items'][0](dict)

        # Handle non-HTML files
        allKeys = res["items"][i].keys()
        if("fileFormat" in allKeys or "snippet" not in allKeys or "title" not in allKeys):
            continue
        html_docs_returned += 1

        title = res["items"][i]["title"]
        url = res["items"][i]["formattedUrl"]
        summary = res["items"][i]["snippet"]
        
        # Output individual result information
        print("Result ", i + 1)
        print("[")
        print("    Title: ", title)
        print("    URL: ", url)
        print("    Summary: ", summary)
        print("]")
        print('\n')

        # Determining relevance
        relevance = input("Relevant (Y/N)?: ")
        if relevance.lower() == 'y':
            relevance_count += 1
            relevance_tracker.append(1)

            corpus.append(word_tokenize(re.sub('[^A-Za-z0-9]+', ' ', summary.lower())))
            corpus.append(word_tokenize(re.sub('[^A-Za-z0-9]+', ' ', title.lower())))
            sentence_count = sentence_count + 2
            word_count = word_count + len(summary_tokens) + len(title_tokens) + 2
        else:
            relevance_tracker.append(0)
        
        # Ignore's case and includes words followed by 's, -ed, etc
        dict_tf = {}
        dict_log_tf = {}

        summary = res["items"][i]["snippet"].lower()
        summary = re.sub('[^A-Za-z0-9]+', ' ', summary)
        summary = summary.split()

        title = res["items"][i]["title"].lower()
        title = re.sub('[^A-Za-z0-9]+', ' ', title)
        title = title.split()

        for term in vocabulary:
            # For this document, calculate term frequencies
            tf_summary = summary.count(term)
            tf_title = title.count(term)
            tf = tf_summary + tf_title
            dict_tf[term] = tf

            # Calculate log frquencies
            log_tf = log_frequency(tf)
            dict_log_tf[term] = log_tf

            # Add to document frequency if term is seen
            if(tf > 0):
                document_frequencies[term] += 1
        
        term_frequencies.append(dict_tf)
        log_frequencies.append(dict_log_tf)

        # Inverse document frequency
        inverse_df = inverse_document_frequency(html_docs_returned, document_frequencies)

    # Calculate tf-idf using log_frequencies and inverse_df
    tf_idf = log_frequencies.copy()
    for doc in range(html_docs_returned):
        for term in tf_idf[doc]:
            tf_idf[doc][term] = tf_idf[doc][term] * inverse_df[term]

    # Calculate precision based on API results and user feedback
    result_precision = relevance_count/html_docs_returned

    print("======================")
    print("FEEDBACK SUMMARY")
    print("Query: ", query)
    print("Result precision: ", result_precision)

    # less than 10 results returned overall (this includes html + non-html docs)
    if(len(res["items"]) < 10): 
        return
    elif result_precision == 0.0:
        print("No results returned by the query were relevant")
        return
    # precision target achieved
    elif result_precision >= 0.9:
        print("Desired precision reached, done")
        return
    # need to improve results
    else:
        print("Still below the desired precision of ", input_precision, '\n')
        
        alpha, beta, gamma = 1, 0.5, 0.25

        # Calculate q_0 where q_i is the tf-idf weight of term i in query q
        q_0 = {}
        for term in vocabulary:
            tf_query = query.split().count(term.lower())
            q_0[term] = tf_query

        # calculate sum over relevant and nonrelevant documents
        relevant_sum = defaultdict(int)
        nonrelevant_sum = defaultdict(int)

        nonrelevant_doc_count = html_docs_returned - relevance_count
        
        for i in range(html_docs_returned):
            if(relevance_tracker[i] == 1):
                for word in tf_idf[i]:
                    relevant_sum[word] += tf_idf[i][word]
            else:
                for word in tf_idf[i]:
                    nonrelevant_sum[word] += tf_idf[i][word]
        
        for word in vocabulary:
            q_0[word] *= alpha
            relevant_sum[word] *= beta/relevance_count
            nonrelevant_sum[word] *= gamma/nonrelevant_doc_count

        q_tplus1 = {}
        for word in vocabulary:
            q_tplus1[word] = q_0[word] + relevant_sum[word] - nonrelevant_sum[word]

        # Build new query using previous query
        query_str = ""
        for term in query.split():
            query_str += term + ' '
            q_tplus1[term] = 0  # exclude current query terms from the ranking

        # Sort values in dict. Find top-10 highest idf-values
        sorted_words = dict(sorted(q_tplus1.items(), key=lambda x:x[1], reverse=True)[:10])
        # print(sorted_words)

        # Select 2 best
        top_2 = dict(sorted(q_tplus1.items(), key = itemgetter(1), reverse = True)[:2])
        # print("Top 2: ", top_2, '\n')

        unigramcounts, bigramcounts = count_ngrams(corpus, unigramcounts, bigramcounts)

        query_list = query.split()

        query_wordone = []
        query_wordone.extend(query_list)

        query_wordtwo = []
        query_wordtwo.extend(query_list)

        query_bothwords = []
        query_bothwords.extend(query_list)

        top_word = ""
        top_two_words = ""

        # Build new query using new terms
        i = 0
        for word in top_2:
            if i == 0:
                query_wordone.extend([word])
                top_word = word
                top_two_words = word
            elif i == 1:
                query_wordtwo.extend([word])
                top_two_words += ' ' + word
            i = i + 1
            query_bothwords.extend([word])

        new_query = query_bothwords

        permutations1 = list(itertools.permutations(query_wordone)) # permutations of old + first new query word
        permutations2 = list(itertools.permutations(query_wordtwo)) # permutations of old + second new query word
        permutations3 = list(itertools.permutations(query_bothwords)) # permutations of old + both new query words

        # permutation of first and second new query words combined
        permutations = []
        permutations.extend(permutations1)
        permutations.extend(permutations2)

        # one word expansion: check best ordering
        # priotritizing highest tf-idf value from top-2 query expansion terms (contained in permutations1)
        highest_prob = -float('inf')
        best_query = []
        augment = ""
        for perm in permutations1:
            perm_prob = sentence_logprob(list(perm), unigramcounts, bigramcounts, word_count, sentence_count)
            if perm_prob > highest_prob:
                highest_prob = perm_prob
                best_query = list(perm)
                augment = top_word
        
        # two word expansion: check best ordering
        new_highest_prob = -float('inf')
        for perm in permutations3:
            perm_prob = sentence_logprob(list(perm), unigramcounts, bigramcounts, word_count, sentence_count)
            if perm_prob + 5 > highest_prob and perm_prob > new_highest_prob:
                new_highest_prob = perm_prob
                best_query = list(perm)
                augment = top_two_words

        new_query = ' '.join(best_query)

        print('Augmenting by: ...', augment, '\n')

        ## call on main function again
        main(new_query)
        
if __name__ == "__main__":
    main()