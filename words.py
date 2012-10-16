import string
from unidecode import unidecode
from memoized import memoized

@memoized
def _letter_values():
  ''' Returns a map of letter values: { a=1, b=2, ... }
  '''
  letters = string.lowercase
  value = 0
  map = {}
  for letter in letters:
    if letter != 'j' and letter != 'v':
      value += 1
    map[letter] = value
  return map


@memoized
def _letter_value(letter):
  ''' Returns the value for a letter or zero.
      Assumes letter is ASCII between [a-z], otherwise returns 0
  '''
  map = _letter_values()
  if letter in map:
    return map[letter]
  else:
    return 0


class WordController:
  ''' Calculates word value, loads words into DB, finds all words with a 
  given value.
  '''
  def __init__(self, db):
    self.db = db

  def check_word(self, word):
    word = unidecode(word).lower().strip()
    return self._gematria(word)
  
  def add_word(self, word, commit=True):
    word = unidecode(word).lower().strip()

    if len(word) == 0:
      return 0

    value = self.check_word(word)
    self.db.add_word(word, value)
    if commit:
      self.db.commit()
    return value

  def finish_adding(self):
    self.db.commit()

  def empty(self):
    self.db.empty()

  def del_word(self, word):
    self.db.del_word(word)

  def query_value(self, value):
    return self.db.query_value(value)

  def num_words(self):
    return self.db.num_words()

  def get_words(self):
    return self.db.get_words()

  def find_words(self, substr, whole_word=False):
    return self.db.find_words(substr, whole_word)
  
  def _gematria(self, word):
    sum = 0
    for letter in word:
      sum += _letter_value(letter)
    return sum
