import nltk
for resource in ['punkt','punkt_tab','averaged_perceptron_tagger','averaged_perceptron_tagger_eng','wordnet','omw-1.4']:
    print('Downloading',resource)
    nltk.download(resource)