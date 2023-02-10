"""
Command-line application that does a custom search using Google API.
"""

import pprint
import sys

from googleapiclient.discovery import build

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

    # Keep track of number of relevant results as we iterate through response 
    relevance_count = 0

    # Printing title, url, and description of the first 10 responses returned
    for i in range(10):
        # Res (dict) —> res[“items”] (list) —> res[“items”][0] (dict)
        
        # Output individual result information
        print("Result ", i + 1)
        print("[")
        print("    Title: ", res["items"][i]["title"])
        print("    URL: ", res["items"][i]["formattedUrl"])
        print("    Summary: ", res["items"][i]["snippet"])
        print("]")
        print('\n')

        # Determining relevance
        relevance = input("Relevant (Y/N)?: ")
        if relevance.lower() == 'y': relevance_count += 1

    # Calculate precision based on API results and user feedback
    result_precision = relevance_count/10

    print("======================")
    print("FEEDBACK SUMMARY")
    print("Query: ", query)
    print("Result precision: ", result_precision)
    
    # less than 10 results returned overall
    if(len(res["items"]) < 10): 
        return
    # precision target achieveed
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