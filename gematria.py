import argparse
import codecs
import os
import sys

from words import WordController
from db import WordDatabase

DEFAULT_DATABASE='words.db'

def load_words(file):
  f = codecs.open(file, encoding='utf-8')
  words = f.readlines()
  word_controller.load_words(words)

def check_word(word):
  value = word_controller.check_word(word)
  print "'%s' has Gematria value %d" % (word, value)

def check_value(value):
  for word in word_controller.query_value(value):
    sys.stdout.write("%s\n" % word)

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Search gematria values")
  parser.add_argument('--load', type=str, help="Load a database file")
  parser.add_argument('--word', type=str, help="Check a word's value")
  parser.add_argument('--value', type=int, help='''Get list of all words 
      with a value''')
  
  args = parser.parse_args()

  db_file = os.environ.get('GEMATRIA_DB', DEFAULT_DATABASE)
  db = WordDatabase(db_file)

  word_controller = WordController(db)

  if args.load is not None:
    load_words(args.load)

  if args.word is not None:
    check_word(args.word)
  elif args.value is not None:
    check_value(args.value)
