# The contents of this file has been derived code from the Twisted project
# (http://twistedmatrix.com/). The original author is Jp Calderone.

# Twisted project license follows:

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

text_type = unicode
binary_type = str

PRINTABLE = set(range(0x20, 0x26)) | set(range(0x27, 0x7f))

def encode(s):
    """Encode a folder name using IMAP modified UTF-7 encoding.

    Despite the function's name, the output is still a unicode string.
    """
    if not isinstance(s, text_type):
        return s

    r = []
    _in = []

    def extend_result_if_chars_buffered():
        if _in:
            r.extend(['&', modified_utf7(''.join(_in)), '-'])
            del _in[:]

    for c in s:
        if ord(c) in PRINTABLE:
            extend_result_if_chars_buffered()
            r.append(c)
        elif c == '&':
            extend_result_if_chars_buffered()
            r.append('&-')
        else:
            _in.append(c)

    extend_result_if_chars_buffered()

    return ''.join(r)

def decode(s):
    """Decode a folder name from IMAP modified UTF-7 encoding to unicode.

    Despite the function's name, the input may still be a unicode
    string. If the input is bytes, it's first decoded to unicode.
    """
    if isinstance(s, binary_type):
        s = s.decode('latin-1')
    if not isinstance(s, text_type):
        return s

    r = []
    _in = []
    for c in s:
        if c == '&' and not _in:
            _in.append('&')
        elif c == '-' and _in:
            if len(_in) == 1:
                r.append('&')
            else:
                r.append(modified_deutf7(''.join(_in[1:])))
            _in = []
        elif _in:
            _in.append(c)
        else:
            r.append(c)
    if _in:
        r.append(modified_deutf7(''.join(_in[1:])))

    return ''.join(r)

def modified_utf7(s):
    # encode to utf-7: '\xff' => b'+AP8-', decode from latin-1 => '+AP8-'
    s_utf7 = s.encode('utf-7').decode('latin-1')
    return s_utf7[1:-1].replace('/', ',')

def modified_deutf7(s):
    s_utf7 = '+' + s.replace(',', '/') + '-'
    # encode to latin-1: '+AP8-' => b'+AP8-', decode from utf-7 => '\xff'
    return s_utf7.encode('latin-1').decode('utf-7')