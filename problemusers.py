"""This report will comprehensively identify all 
“problem members” in the database. This report will analyze information on 
active members’ borrowing trends and late fee payments, searching for repeated 
and sustained instances of overdue returns and late-fee repayment tardiness. This 
report will provide staff with a comprehensive list of all members who may 
require intervention or even deactivation of their accounts. It will also highlight 
potential conflicts that may arise from any actions taken against these members. 
For instance, a problem member who is currently borrowing a book may not be 
recommended for deactivation until that book has been returned."""

import mysql.connector

conn = mysql.connector.connect(
    user="447s25_j776w781",
    password="ohN7iewa",
    host="mysql.eecs.ku.edu",
    port=3306,
    database="447s25_j776w781"
)

cursor = conn.cursor()

#query all overdue loans
overdue_query = """ 
SELECT memberID, COUNT(*) AS overdueCount
FROM loan
WHERE returnDate > dueDate
GROUP BY memberID;
"""

cursor.execute(overdue_query)
overdue_results = cursor.fetchall()
overdue_dict = {member_id: count for member_id, count in overdue_results}
print("DEBUG: Overdue Loans", overdue_dict)  # Debugging line to check overdue_dict

#query all unpaid/late fines
fines_query = """
SELECT f.memberID, COUNT(*) AS unpaidFines
FROM fine f
LEFT JOIN payment p on f.fineID = p.fineID
WHERE f.status = 'unpaid'
GROUP BY f.memberID;
"""

cursor.execute(fines_query)
fines_results = cursor.fetchall()
fines_dict = {member_id: count for member_id, count in fines_results}
print("DEBUG: Unpaid Fines", fines_dict)  # Debugging line to check fines_dict


#members who are currently borrowing items
cur_borrow_query = """
SELECT memberID
FROM loan
WHERE returnDate IS NULL
"""

cursor.execute(cur_borrow_query)
cur_borrow_results = cursor.fetchall()  
cur_borrow_set = {row[0] for row in cur_borrow_results}  #this ones a set for faster lookup
print("DEBUG: Currently Borrowing", cur_borrow_set)  # Debugging line to check cur_borrow_set

all_members = set(overdue_dict) | set(fines_dict) | cur_borrow_set
print("DEBUG: All Members", all_members)  # Debugging line to check all_members

print("\n------PROBLEM MEMBER REPORT------\n")
for member_id in all_members:
    overdue_count = overdue_dict.get(member_id, 0)
    unpaid_fines_count = fines_dict.get(member_id, 0)
    currently_borrowing = member_id in cur_borrow_set

    #flag as problem member if they have 3 or more overdue loans or 2 or more unpaid fines
    #is_problem_member = overdue_count >= 3 or unpaid_fines_count >= 2
    is_problem_member = overdue_count >= 1 or unpaid_fines_count >= 1
    #recommend deactivation if they are a problem member and not currently borrowing
    recommendation = is_problem_member and not currently_borrowing #recommend d

    if is_problem_member:
        print(f"Member ID: {member_id}")
        print(f"Overdue Loans: {overdue_count}")
        print(f"Unpaid Fines: {unpaid_fines_count}")
        print(f"Currently Borrowing: {'Yes' if currently_borrowing else 'No'}")
        if recommendation:
            print("Recommendation: Deactivation")
        else:
            print("Recommendation: Monitor")
        print("-------------------------------")


cursor.close()
conn.close()
