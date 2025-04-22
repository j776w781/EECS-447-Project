import mysql.connector
import argparse

parser = argparse.ArgumentParser(prog="data_insert.py")
parser.add_argument('--demo', action=argparse.BooleanOptionalAction, help='If you are not on cycle servers, use this flag to run in demo mode.')
parser.add_argument('--verbose', action=argparse.BooleanOptionalAction, help='If you want to see the output of the script, use this flag.')
args = parser.parse_args()

def printv(msg):
    # Print the message if verbose mode is enabled.
    if args.verbose:
        print(msg)

conn = None
class CursorLogger:
    def __init__(self, cursor=None):
        self.cursor = cursor
    def execute(self, query, values=None):
        printv(f"Executing query: {query} with values: {values}")
        if self.cursor:
            self.cursor.execute(query, values)
class ConnectionLogger:
    def __init__(self, conn=None):
        self.conn = conn
    def cursor(self):
        return CursorLogger(None if self.conn is None else self.conn.cursor())
    def commit(self):
        printv("Committing changes.")
        if self.conn:
            self.conn.commit()
    def close(self):
        printv("Closing connection.")
        if self.conn:
            self.conn.close()
    def is_connected(self):
        return False if self.conn is None else self.conn.is_connected()

if args.demo:
    printv("Running in demo mode. No database connection will be established.")
    conn = ConnectionLogger()
    cur = conn.cursor()
else:
    printv("Connecting to the database...")
    conn = ConnectionLogger(mysql.connector.connect(
        user="447s25_j776w781",
        password="ohN7iewa",
        host="mysql.eecs.ku.edu",
        port=3306,
        database="447s25_j776w781"
    ))
    cur = CursorLogger(conn.cursor())

# Define the columns for each table
user_columns = [("user_id", int), ("name", str), ("phoneNumber", str), ("emailAddress", str), \
                ("physicalAddress", str), ("userType", str), ("accountStatus", str)]

media_columns = [("itemID", int), ("title", str), ("itemType", str), ("publicationYear", int), \
                 ("availabilityStatus", str), ("specialPremium", float), ("specialRestriction", str)]
books_columns = [("itemID", int), ("ISBN", int), ("author", str), ("genre", str)]
digital_media_columns = [("itemID", int), ("digitalMediaID", int), ("creator", str), ("genre", str)]
magazine_columns = [("magazineID", int), ("issn", str), ("publicationDate", str)]

# TODO For media types, we need to check the itemID and make sure it is not taken in the media table.
def insert_book(book):
    # Check if there is an extra type indicator at the beginning.
    # Expected total tokens: media (7) + child (len(child_columns))
    expected = len(media_columns) + len(books_columns)
    if len(book) == expected + 1:
        # Remove the type indicator (first token)
        book.pop(0)
    
    if len(book) != expected:
        raise ValueError(f"Row does not have the expected number of tokens: {book}")

    # Prepare data for media insert.
    insert_media(book[:len(media_columns)])

    # Prepare data for the child table. We enforce that the first column (itemID or magazineID)
    # must match the media itemID. If the CSV provided a child itemID that differs, we override it.
    child_tokens = book[len(media_columns):]
    child_values = []
    # Set first column from media's itemID.
    child_values.append(book[0])
    # Process remaining child columns.
    for i, (col, col_type) in enumerate(books_columns[1:], start=1):
        val = child_tokens[i]
        if col_type == int:
            child_values.append(int(val))
        elif col_type == float:
            child_values.append(float(val))
        else:
            child_values.append(val)
    
    child_query = f"INSERT INTO book VALUES (" + ", ".join(["%s"] * len(books_columns)) + ")"
    cur.execute(child_query, child_values)

def insert_digital_media(digital_media):
    expected = len(media_columns) + len(digital_media_columns)
    if len(digital_media) == expected + 1:
        digital_media.pop(0)
    
    if len(digital_media) != expected:
        raise ValueError(f"Row does not have the expected number of tokens: {digital_media}")

    insert_media(digital_media[:len(media_columns)])

    child_tokens = digital_media[len(media_columns):]
    child_values = []
    child_values.append(digital_media[0])
    for i, (col, col_type) in enumerate(digital_media_columns[1:], start=1):
        val = child_tokens[i]
        if col_type == int:
            child_values.append(int(val))
        elif col_type == float:
            child_values.append(float(val))
        else:
            child_values.append(val)
    
    child_query = f"INSERT INTO digitalMedia VALUES (" + ", ".join(["%s"] * len(digital_media_columns)) + ")"
    cur.execute(child_query, child_values)

def insert_magazine(magazine):
    expected = len(media_columns) + len(magazine_columns)
    if len(magazine) == expected + 1:
        magazine.pop(0)
    
    if len(magazine) != expected:
        raise ValueError(f"Row does not have the expected number of tokens: {magazine}")

    insert_media(magazine[:len(media_columns)])

    child_tokens = magazine[len(media_columns):]
    child_values = []
    child_values.append(magazine[0])
    for i, (col, col_type) in enumerate(magazine_columns[1:], start=1):
        val = child_tokens[i]
        if col_type == int:
            child_values.append(int(val))
        elif col_type == float:
            child_values.append(float(val))
        else:
            child_values.append(val)
    
    child_query = f"INSERT INTO magazine VALUES (" + ", ".join(["%s"] * len(magazine_columns)) + ")"
    cur.execute(child_query, child_values)

def insert_user(user):
    if len(user) != len(user_columns):
        raise ValueError(f"Row does not have the expected number of tokens: {user}")

    # TODO check type of user and insert into the correct table.

    values = []
    for i, (col, col_type) in enumerate(user_columns):
        val = user[i]
        if col_type == int:
            values.append(int(val))
        elif col_type == float:
            values.append(float(val))
        else:
            values.append(val)
    
    query = f"INSERT INTO user VALUES (" + ", ".join(["%s"] * len(user_columns)) + ")"
    cur.execute(query, values)

def insert_media(media):
    if len(media) != len(media_columns):
        raise ValueError(f"Row does not have the expected number of tokens: {media}")

    values = []
    for i, (col, col_type) in enumerate(media_columns):
        val = media[i]
        if col_type == int:
            values.append(int(val))
        elif col_type == float:
            values.append(float(val))
        else:
            values.append(val)
    
    query = f"INSERT INTO media VALUES (" + ", ".join(["%s"] * len(media_columns)) + ")"
    cur.execute(query, values)

def insert_table(table_name, input_file):
    """
    Inserts rows into a table. For subtables (book, digitalMedia, magazine),
    the CSV line is expected to contain first the media columns (7 values)
    and then the subtable specific values. If there is an extra token at the beginning,
    it is removed (e.g. a type indicator).
    """
    # Determine if this table is a child table.
    with open(input_file, 'r') as f:
        for line in f:
            tokens = line.strip().split(",")
            
            if table_name == "book":
                insert_book(tokens)
            elif table_name == "digitalMedia":
                insert_digital_media(tokens)
            elif table_name == "magazine":
                insert_magazine(tokens)
            elif table_name == "user":
                insert_user(tokens)
            elif table_name == "media":
                insert_media(tokens)
            else:
                raise ValueError(f"Unknown table name: {table_name}")

        conn.commit()

try:
    # Insert data into the tables
    printv("Inserting data into the database...")
    insert_table("user", "data/users.csv")
    insert_table("book", "data/books.csv")
    insert_table("magazine", "data/magazine.csv")
    insert_table("digitalMedia", "data/digitalmedia.csv")

    # Close the connection
    printv("Data inserted successfully.")
    conn.close()
except Exception as e:
    printv(f"Error: {e}")
    if conn.is_connected():
        conn.close()
