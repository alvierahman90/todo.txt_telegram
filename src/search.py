from fuzzywuzzy import process

choices = open('tmp').read().split('\n')

search_term = input('Search term: ')

for result, matchness in process.extract(search_term, choices):
    print(str(matchness), result)
