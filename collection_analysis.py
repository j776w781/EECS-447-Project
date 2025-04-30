import mysql.connector

def collection_analysis():
    conn = mysql.connector.connect(
        user="447s25_j776w781",
        password="ohN7iewa",
        host="mysql.eecs.ku.edu",
        port=3306,
        database="447s25_j776w781"
    )

    cursor = conn.cursor()

    print("\n------ COLLECTION ANALYSIS REPORT ------\n")

    # 1. Most Frequently Borrowed Items
    print("Top 10 Most Frequently Borrowed Items:")
    cursor.execute("""
        SELECT m.itemID, m.title, COUNT(l.loanID) AS borrowCount
        FROM media m
        JOIN loan l ON m.itemID = l.itemID
        GROUP BY m.itemID
        ORDER BY borrowCount DESC
        LIMIT 10;
    """)
    for itemID, title, count in cursor.fetchall():
        print(f"Item ID: {itemID}, Title: {title}, Times Borrowed: {count}")
    print()

    # 2. Least Frequently Borrowed Items
    print("Top 10 Least Frequently Borrowed Items:")
    cursor.execute("""
        SELECT m.itemID, m.title, COUNT(l.loanID) AS borrowCount
        FROM media m
        LEFT JOIN loan l ON m.itemID = l.itemID
        GROUP BY m.itemID
        HAVING borrowCount > 0
        ORDER BY borrowCount ASC
        LIMIT 10;
    """)
    for itemID, title, count in cursor.fetchall():
        print(f"Item ID: {itemID}, Title: {title}, Times Borrowed: {count}")
    print()

    # 3. Items Most Often Returned Late
    print("Items Most Often Returned Late:")
    cursor.execute("""
        SELECT m.itemID, m.title, COUNT(*) AS lateReturns
        FROM media m
        JOIN loan l ON m.itemID = l.itemID
        WHERE l.returnDate > l.dueDate
        GROUP BY m.itemID
        ORDER BY lateReturns DESC
        LIMIT 10;
    """)
    for itemID, title, count in cursor.fetchall():
        print(f"Item ID: {itemID}, Title: {title}, Late Returns: {count}")
    print()

    # 4. Collection Circulation Summary
    print("Collection Circulation Summary:")
    cursor.execute("SELECT COUNT(*) FROM media;")
    total_items = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT itemID) FROM loan;")
    items_borrowed = cursor.fetchone()[0]

    if total_items > 0:
        circulation_rate = (items_borrowed / total_items) * 100
    else:
        circulation_rate = 0

    print(f"Total Items in Collection: {total_items}")
    print(f"Items Borrowed At Least Once: {items_borrowed}")
    print(f"Circulation Rate: {circulation_rate:.2f}%")
    print()

    cursor.close()
    conn.close()

# Run the report
collection_analysis()
