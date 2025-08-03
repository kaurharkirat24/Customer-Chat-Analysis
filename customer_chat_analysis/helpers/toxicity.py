TOXIC_WORDS = ['stupid', 'idiot', 'hate', 'dumb', 'terrible', 'awful', 'worst', 'sucks', 'useless']

def flag_toxic(message):
    return any(tw in message.lower() for tw in TOXIC_WORDS)