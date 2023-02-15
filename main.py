"""
Command-line application that does a custom search using Google API.
"""

import pprint
import sys
import math

from collections import defaultdict
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

def main():

    # query URL = python main.py <google api developer key> <google engine id> <precision> <query>
    if (len(sys.argv) != 5):
        print("Invalid arguments provided")
        print("Arguments should contain: main.py <google api developer key> <google engine id> <precision> <query>")
        return
    
    developer_key = sys.argv[1]
    engine_key = sys.argv[2]
    input_precision = (float)(sys.argv[3])
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

    # Don't include non-html documents returned by Google
    html_docs_returned = 0

    # Keep track of number of relevant results as we iterate through response 
    relevance_count = 0

    term_frequencies = []
    log_frequencies = []

    document_frequencies = defaultdict(int)
    inverse_df = defaultdict(int)

    # Printing title, url, and description of the first 10 responses returned
    for i in range(10):
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
        
        # Ignore's case and includes words followed by 's, -ed, etc
        dict_tf = {}
        dict_log_tf = {}
        for term in query.split():
            # For this document, calculate term frequencies
            tf = summary.lower().count(term.lower())
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
    
    print('Term frequencies: ' , term_frequencies)
    print('Log frequencies: ' , log_frequencies)
    print('Document frequencies: ', document_frequencies)
    print('Inverse Document frequencies: ', inverse_df)

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
        ## Indexing...
        ## Augmenting
        ## call on main function again

if __name__ == "__main__":
    main()