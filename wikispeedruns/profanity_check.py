from profanity_check import predict


def profanity_check_func(word):
    '''
    Profanity check for a word
    '''
    profanity = predict([word])
    if profanity[0]:
        return 1
    else:
        return 0
