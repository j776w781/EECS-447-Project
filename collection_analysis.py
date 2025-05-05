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

    # 1. All Items by Borrow Frequency (Descending)
    print("All Items by Borrow Frequency:")
    cursor.execute("""
        SELECT m.itemID, m.title, COUNT(l.itemID) AS loan_count
        FROM media m
        LEFT JOIN loan l ON m.itemID = l.itemID
        GROUP BY m.itemID, m.title
        ORDER BY loan_count DESC;
    """)
    for itemID, title, count in cursor.fetchall():
        print(f"Item ID: {itemID}, Title: {title}, Times Borrowed: {count}")
    print()

    # 2. Most Under-Utilized Genre (Books with no loans)
    print("Most Under-Utilized Book Genre (Never Loaned):")
    cursor.execute("""
        SELECT b.genre, COUNT(*) AS unloaned_count
        FROM media m
        JOIN book b ON m.itemID = b.itemID
        LEFT JOIN loan l ON m.itemID = l.itemID
        WHERE l.itemID IS NULL
        GROUP BY b.genre
        ORDER BY unloaned_count DESC
        LIMIT 1;
    """)
    result = cursor.fetchone()
    if result:
        print(f"Genre: {result[0]}, Unloaned Books: {result[1]}")
    else:
        print("No unloaned genres found.")
    print()

    # 3. Most Under-Utilized Media Type (Never Loaned)
    print("Most Under-Utilized Media Type (Never Loaned):")
    cursor.execute("""
        SELECT m.itemType, COUNT(*) AS unloaned_count
        FROM media m
        LEFT JOIN loan l ON m.itemID = l.itemID
        WHERE l.itemID IS NULL
        GROUP BY m.itemType
        ORDER BY unloaned_count DESC
        LIMIT 1;
    """)
    result = cursor.fetchone()
    if result:
        print(f"Media Type: {result[0]}, Unloaned Items: {result[1]}")
    else:
        print("No unloaned media types found.")
    print()

    cursor.close()
    conn.close()

# Run the report
collection_analysis()
