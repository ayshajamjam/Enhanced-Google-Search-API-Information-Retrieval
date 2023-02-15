"""
Command-line application that does a custom search using Google API.
"""

import pprint
import sys
import math
import re

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

    document_frequencies = defaultdict(int)
    inverse_df = defaultdict(int)

    # term_frequencies_query = []
    # log_frequencies_query = []

    document_frequencies_query = defaultdict(int)
    inverse_df_query = defaultdict(int)

    vocabulary = set()

    # Build the vocabulary dict using the page summary
    for page in range(number_of_search_results):
        summary = res["items"][page]["snippet"].lower()
        summary = re.sub('[^A-Za-z0-9]+', ' ', summary)
        summary = summary.split()

        for word in summary:
            vocabulary.add(word.lower())

    print('Vocabulary: ', vocabulary, '\n')

    # Printing title, url, and description of the first 10 responses returned
    for i in range(number_of_search_results):
        # Res (dict) —> res[“items”] (list) —> res[“items”][0] (dict)

        if(res["items"][i].get("fileFormat") != None):
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
        else:
            relevance_tracker.append(0)
        
        # Ignore's case and includes words followed by 's, -ed, etc
        dict_tf = {}
        dict_log_tf = {}

        summary = res["items"][i]["snippet"].lower()
        summary = re.sub('[^A-Za-z0-9]+', ' ', summary)
        summary = summary.split()

        for term in vocabulary:
            # For this document, calculate term frequencies
            tf = summary.count(term.lower())
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
        # TODO: confirm what N should be
        inverse_df = inverse_document_frequency(html_docs_returned, document_frequencies)
    
        # dict_tf_query = {}
        # dict_log_tf_query = {}

        # for term in query.split():
        #     tf_query = summary.count(term.lower())
        #     dict_tf_query[term] = tf_query

        #     log_tf_query = log_frequency(tf_query)
        #     dict_log_tf_query[term] = log_tf_query

        #     if(tf_query > 0):
        #         document_frequencies_query[term] += 1

        # term_frequencies_query.append(dict_tf_query)
        # log_frequencies_query.append(dict_log_tf_query)

        # inverse_df_query = inverse_document_frequency(html_docs_returned, document_frequencies_query)

    # print('Term frequencies: ' , term_frequencies, '\n')
    # print('Log frequencies: ' , log_frequencies, '\n')
    # print('Document frequencies: ', document_frequencies, '\n')
    # print('Inverse Document frequencies: ', inverse_df, '\n')

    tf_idf = log_frequencies.copy()
    for doc in range(html_docs_returned):
        for term in tf_idf[doc]:
            tf_idf[doc][term] = tf_idf[doc][term] * inverse_df[term]

    print('tf-idf: ', tf_idf, '\n')

    # print('Query Term frequencies: ' , term_frequencies_query, '\n')
    # print('Query Log frequencies: ' , log_frequencies_query, '\n')
    # print('Query Document frequencies: ', document_frequencies_query, '\n')
    # print('Query Inverse Document frequencies: ', inverse_df_query, '\n')

    # tf_idf_query = log_frequencies_query.copy()
    # for doc in range(number_of_search_results):
    #     for term in tf_idf_query[doc]:
    #         tf_idf_query[doc][term] = tf_idf_query[doc][term] * inverse_df_query[term]

    # print('tf-idf query: ', tf_idf_query, '\n')

    # Calculate precision based on API results and user feedback
    result_precision = relevance_count/html_docs_returned

    print("======================")
    print("FEEDBACK SUMMARY")
    print("Query: ", query)
    print("Result precision: ", result_precision)
    
    # less than 10 results returned overall (this includes html + non-html docs)
    if(len(res["items"]) < 10): 
        return
    # precision target achieved
    elif result_precision >= 0.9:
        print("Desired precision reached, done")
        return
    # need to improve results
    else:
        print("Still below the desired precision of ", input_precision)
        
        alpha, beta, gamma = 1, 0.5, 0.25

        # Calculate q_0 where q_i is the tf-idf weight of term i in query q

        q_0 = {}
        for term in vocabulary:
            tf_query = query.lower().split().count(term.lower())
            q_0[term] = tf_query

        # print('Term frequencies Query: ', q_0, '\n')

        # dict_tf_query = {}
        # dict_log_tf_query = {}

        # for term in vocabulary:
        #     tf_query = query.lower().split().count(term.lower())
        #     dict_tf_query[term] = tf_query

        #     log_tf_query = log_frequency(tf_query)
        #     dict_log_tf_query[term] = log_tf_query

        # print('Term frequencies Query: ', dict_tf_query, '\n')

        # tf_idf_query = dict_log_tf_query.copy()
        # for term in tf_idf_query:
        #     tf_idf_query[term] = tf_idf_query[term] * inverse_df[term]

        # print('tf-idf query: ', tf_idf_query, '\n')

        # calculate sum over relevant and nonrelevant doccuments
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
            # tf_idf_query[word] *= alpha
            q_0[word] *= alpha
            relevant_sum[word] *= beta/relevance_count
            nonrelevant_sum[word] *= gamma/nonrelevant_doc_count
        
        # print('relevant_sum: ', relevant_sum, '\n')
        # print('nonrelevant_sum: ', nonrelevant_sum, '\n')
        # print('relevant doc count: ', relevance_count, '\n')
        # print('nonrelevant doc count: ', nonrelevant_doc_count, '\n')

        q_tplus1 = {}
        for word in vocabulary:
            q_tplus1[word] = q_0[word] + relevant_sum[word] - nonrelevant_sum[word]

        # print('Difference: ', q_tplus1, '\n')

        sorted_words = dict(sorted(q_tplus1.items(), key=lambda x:x[1], reverse=True)[:10])
        # print(sorted_words)

        ## Indexing...
        ## Augmenting
        ## call on main function again
        query_new_size = len(query.split()) + 2
        res = dict(sorted(q_tplus1.items(), key = itemgetter(1), reverse = True)[:query_new_size])

        print(res, '\n')

        # Build new query
        new_query = ""
        for word in res:
            new_query += word + ' '
        new_query = new_query.strip()

        print('Augmenting by: ...')
        print(new_query, '\n')

        main(new_query)
        
if __name__ == "__main__":
    main()