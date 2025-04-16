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

def insert_table(table_name, columns, input_file):
    """
    Inserts rows into a table. For subtables (book, digitalMedia, magazine),
    the CSV line is expected to contain first the media columns (7 values)
    and then the subtable specific values. If there is an extra token at the beginning,
    it is removed (e.g. a type indicator).
    """
    # For child tables, we need to do two inserts: one into media and one into the subtable.
    child_tables = {"book": books_columns,
                    "digitalMedia": digital_media_columns,
                    "magazine": magazine_columns}
    standalone_tables = {"user": user_columns,
                         "media": media_columns}

    # Determine if this table is a child table.
    if table_name in child_tables:
        with open(input_file, 'r') as f:
            for line in f:
                tokens = line.strip().split(",")
                
                # Check if there is an extra type indicator at the beginning.
                # Expected total tokens: media (7) + child (len(child_columns))
                expected = len(media_columns) + len(child_tables[table_name])
                if len(tokens) == expected + 1:
                    # Remove the type indicator (first token)
                    tokens.pop(0)
                
                if len(tokens) != expected:
                    raise ValueError(f"Row does not have the expected number of tokens: {tokens}")

                # Prepare data for media insert.
                media_values = []
                for i, (col, col_type) in enumerate(media_columns):
                    val = tokens[i]
                    if col_type == int:
                        media_values.append(int(val))
                    elif col_type == float:
                        media_values.append(float(val))
                    else:
                        media_values.append(val)
                
                media_query = "INSERT INTO media VALUES (" + ", ".join(["%s"] * len(media_columns)) + ")"
                cur.execute(media_query, media_values)
                
                # Prepare data for the child table. We enforce that the first column (itemID or magazineID)
                # must match the media itemID. If the CSV provided a child itemID that differs, we override it.
                child_tokens = tokens[len(media_columns):]
                child_values = []
                # Set first column from media's itemID.
                child_values.append(media_values[0])
                # Process remaining child columns.
                for i, (col, col_type) in enumerate(child_tables[table_name][1:], start=1):
                    val = child_tokens[i]
                    if col_type == int:
                        child_values.append(int(val))
                    elif col_type == float:
                        child_values.append(float(val))
                    else:
                        child_values.append(val)
                
                child_query = f"INSERT INTO {table_name} VALUES (" + ", ".join(["%s"] * len(child_tables[table_name])) + ")"
                cur.execute(child_query, child_values)
        conn.commit()
    elif table_name in standalone_tables:
        # For standalone tables (for example, the user table).
        with open(input_file, 'r') as f:
            for line in f:
                tokens = line.strip().split(", ")
                if len(tokens) != len(columns):
                    raise ValueError(f"Row does not have the expected number of tokens: {tokens}")
                values = []
                for i, (col, col_type) in enumerate(columns):
                    val = tokens[i]
                    if col_type == int:
                        values.append(int(val))
                    elif col_type == float:
                        values.append(float(val))
                    else:
                        values.append(val)
                query = f"INSERT INTO {table_name} VALUES (" + ", ".join(["%s"] * len(columns)) + ")"
                cur.execute(query, values)
        conn.commit()
    else:
        raise ValueError(f"Unknown table name: {table_name}")

try:
    # Insert data into the tables
    printv("Inserting data into the database...")
    insert_table("user", user_columns, "data/users.csv")
    insert_table("book", books_columns, "data/books.csv")
    insert_table("magazine", magazine_columns, "data/magazine.csv")
    insert_table("digitalMedia", digital_media_columns, "data/digitalmedia.csv")

    # Close the connection
    printv("Data inserted successfully.")
    conn.close()
except Exception as e:
    printv(f"Error: {e}")
    if conn.is_connected():
        conn.close()
