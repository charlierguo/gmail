import pyimap4utf7 as iutf7


def encode7(input_str):
    '''Encode the input text to IMAP4 style UTF-7 charset'''
    if not isinstance(input_str, unicode):
        input_str = input_str.decode('utf-8')
    return iutf7.encode(input_str)


def decode7(input_str):
    '''Dncode IMAP4 style UTF-7 charset to unicode'''
    return iutf7.decode(input_str)


def u(input_str):
    '''Decode the input text from UTF-8 to unicode'''
    if not isinstance(input_str, unicode):
        return input_str.decode('utf-8')
    return input_str
