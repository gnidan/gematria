import sqlite3


class WordDatabase:
  def __init__(self, db_file="words.db"):
    self.conn = sqlite3.connect(db_file)
    self.cursor = self.conn.cursor()

    self._make_table()

  def commit(self):
    self.conn.commit()

  def close(self):
    self.conn.close()

  def _make_table(self):
    self.cursor.execute('''CREATE TABLE IF NOT EXISTS words
        (word text unique, value integer)''')
    self.conn.commit()

  def add_word(self, word, value):
    self.cursor.execute("INSERT OR IGNORE INTO words VALUES (?, ?)",
        (word, value))

  def empty(self):
    self.cursor.execute("DELETE FROM words")

  def del_word(self, word):
    self.cursor.execute("DELETE FROM words WHERE word = ?", (word,))
    self.commit()

  def query_value(self, value):
    self.cursor.execute("SELECT word, value FROM words WHERE value = ? ORDER BY word ASC",
        (value,))

    return list(self.cursor.fetchall())

  def find_words(self, substr, whole_word=False):
    if whole_word:
      sql = "SELECT * FROM words WHERE word = ?"
      self.cursor.execute(sql, (substr,))
    else:
      sql = "SELECT * FROM words WHERE word LIKE ? ORDER BY word ASC"
      self.cursor.execute(sql, ('%' + substr + '%',))
    return list(self.cursor.fetchall())
  
  def num_words(self):
    self.cursor.execute("SELECT COUNT(*) FROM words")
    return self.cursor.fetchone()[0]
  
  def get_words(self):
    self.cursor.execute("SELECT * FROM words ORDER BY word ASC")
    return list(self.cursor.fetchall())
