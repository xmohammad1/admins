from enum import Enum

# for next line     : \n
# for bold text     : **text**
# for mono text     : `text`
# for use ' in text : \'

class KeyboardTexts(str, Enum):
    base = 'base'

class MessageTexts(str, Enum):
    base = 'base'
    UserOnHoldResponse = 'Username: {username}'
    UserActiveResponse = 'Username: {username}'