'''
First two lines only needed if not using the method Aiham came up with.
'''
#import sys
#sys.path.insert(0, '../library_project/mysql-connector-python/lib')
import mysql.connector
import datetime


class Member:
    def __init__(self, id, cur):
        self.ID = id
        self.cur = cur

    def search_by(self, parameter, value, type, use_media_param=False):
        media_results = []
        type_results = []
        if type == "media" or use_media_param:
            self.cur.execute(f"SELECT * FROM media WHERE {parameter}=%s", (value,))
            for (id,a,itemtype,c,d,e,f) in self.cur.fetchall():
                media_results.append((id,a,itemtype,c,d,e,f))
                id_name = "itemID"

                if itemtype == "digital":
                    subtype = itemtype + "Media"
                else:
                    if itemtype == "magazine":
                        id_name = "magazineID"
                    subtype = itemtype
                
                if use_media_param and subtype != type:
                    continue

                self.cur.execute(f"SELECT * FROM {subtype} WHERE {id_name}=%s", (id,))
                for row in self.cur.fetchall():
                    type_results.append(row)
        else:
            self.cur.execute(f"SELECT * FROM {type} WHERE {parameter}=%s", (value,))
            for row in self.cur.fetchall():
                type_results.append(row)
                self.cur.execute(f"SELECT * FROM media WHERE itemID=%s", (row[0],))
                for r in self.cur.fetchall():
                    media_results.append(r)
        return media_results, type_results


    def search_interface(self):
        book_params = ["ISBN","author", "genre"]
        digi_params = ["digitalMediaID", "creator", "genre"]
        maga_params = ["issn","publicationDate"]
        media_params = ["itemID", "title", "itemType", "publicationYear", "availabilityStatus"]
        params = [media_params, book_params, digi_params, maga_params]
        types = ["media", "book", "digitalMedia", "magazine"]

        media_choice = input("\nChoose Media Type:\n0:All Media\n1:Book\n2:Digital Media\n3:Magazine\nEnter Number: ")
        if media_choice in ["0","1","2","3"]:
            media_choice = int(media_choice)
        else:
            print("Invalid choice. Try again!")
            return        
        
        print("\nSearch by: ")
        cntr = 0
        for p in media_params:
            print(f"{cntr}:{p}")
            cntr+=1
        if media_choice > 0:
            for p in params[media_choice]:
                print(f"{cntr}:{p}")
                cntr+=1
        param = input("Enter Number: ")
        try:
            param = int(param)
        except ValueError:
            print("Invalid choice. Try again!")
            return

        use_media_param = False
        new_media_choice = media_choice

        if param >= cntr:
            print("Invalid choice. Try again!")
            return            
        elif param >= len(media_params):
            param = param-len(media_params)
        elif media_choice > 0:
            use_media_param = True
            new_media_choice = 0
            
        value = input(f"What should the {params[new_media_choice][param]} be: ")
        try:
            value = int(value)
            print("INTED")
        except ValueError:
            value = value

        print(f"\nConfirm (yes/no):\nMedia Type: {types[media_choice]}\nSearch Parameter: {params[new_media_choice][param]}\nParameter Value: {value}")
        confirm = input("Enter yes/no: ")

        
        if confirm == "yes":
            media_results, type_results = self.search_by(params[new_media_choice][param],value,types[media_choice],use_media_param)
            if len(media_results) == 0 or len(type_results) == 0:
                print("\nNo results found.")
            else:
                print("\nResults:\n")
                for i in range(len(media_results)):
                    print(f"Item ID: {media_results[i][0]}\nTitle: {media_results[i][1]}\nMedia Type: {media_results[i][2]}\nPublication Year: {media_results[i][3]}")
                    if media_results[i][2] == "book":
                        print(f"ISBN: {type_results[i][1]}\nAuthor: {type_results[i][2]}\nGenre: {type_results[i][3]}")
                    elif media_results[i][2] == "digital":
                        print(f"Digital ID: {type_results[i][1]}\nCreator: {type_results[i][2]}\nGenre: {type_results[i][3]}")
                    else:
                        print(f"ISSN: {type_results[i][1]}\nPublication Date: {type_results[i][2]}")

                    print(f"Availability Status: {media_results[i][4]}\nSpecial Premium: {media_results[i][5]}\nRarity: {media_results[i][6]}\n")

        elif confirm == "no":
            print("Search cancelled.")
        else:
            print("Invalid choice. Try again!")



    def reserve(self):
        #Obtain item id from user.
        itemID = input("\nEnter the Item ID of your item.\nNeed help? Type a letter to return to the menu and search for an item!\nEnter itemID: ")
        try:
            itemID = int(itemID)
        except ValueError:
            print("Invalid Item ID. Please try again!")
            return
        
        #Check for item existence.
        media_results, type_results = self.search_by("itemID",itemID,"media")
        if len(media_results) == 0:
            print("No item exists with that ID. Please try again!")
            return
        
        #Confirm item with user.
        print("\nItem found:\n")
        print(f"Item ID: {media_results[0][0]}\nTitle: {media_results[0][1]}\nMedia Type: {media_results[0][2]}\nPublication Year: {media_results[0][3]}")
        if media_results[0][2] == "book":
            print(f"ISBN: {type_results[0][1]}\nAuthor: {type_results[0][2]}\nGenre: {type_results[0][3]}")
        elif media_results[0][2] == "digital":
            print(f"Digital ID: {type_results[0][1]}\nCreator: {type_results[0][2]}\nGenre: {type_results[0][3]}")
        else:
            print(f"ISSN: {type_results[0][1]}\nPublication Date: {type_results[0][2]}")
        print(f"Availability Status: {media_results[0][4]}\nSpecial Premium: {media_results[0][5]}\nRarity: {media_results[0][6]}\n")

        confirm = input("Is this item correct (yes/no): ")
        if confirm == "yes":
            itemID = media_results[0][0]
        else:
            print("Try again!")
            return
        
        #Check for existing reservation.
        self.cur.execute("SELECT * FROM reservation WHERE itemID=%s AND status='active'", (itemID,))
        res_results = self.cur.fetchall()
        if len(res_results) != 0:
            print("\nSorry, this item is already reserved.")
            return
        
        #Obtain reservationDate
        print("\nThis item is available for reservation!")
        today = datetime.date.today()
        
        #If the item is on hand, expirationDate should be three days from today. If not, it will start as NULL and be updated when the item is returned.
        if media_results[0][4] == "available":
            expirationDate = today + datetime.timedelta(days=3)
            print(f"This item is available right now! Your reservation will expire on {expirationDate}.")
        else:
            expirationDate = None
            print("This item is currently out on loan. We'll let you know when it's back. Your reservation will expire three days after it returns.")
        
        #Generate reservationID
        max = 0
        self.cur.execute("SELECT MAX(reservationID) FROM reservation")
        for row in self.cur.fetchall():
            max = row[0]
        resID = max+1

        #Update all relevant tables to create the reservation.
        print(self.ID)
        confirm = input(f"\nConfirm(yes/no):\nReservation ID: {resID}\nMember ID: {self.ID}\nItem ID: {itemID}\nReservation Date: {today}\nDue Date: {expirationDate}\nEnter choice: ")
        if confirm == 'yes':
            if expirationDate != None:
                self.cur.execute("INSERT INTO reservation VALUES (%s,%s,%s,%s,%s,%s)", (resID,self.ID,itemID,str(today),str(expirationDate),"active",))
            else:
                 self.cur.execute("INSERT INTO reservation VALUES (%s,%s,%s,%s,%s,%s)", (resID,self.ID,itemID,str(today),expirationDate,"active",))               
            self.cur.execute("INSERT INTO reserves VALUES (%s,%s)", (resID,self.ID))
            self.cur.execute("INSERT INTO reserved_in VALUES (%s,%s)", (resID,itemID))

            print("Reservation made. Thank you!")
        else:
            print("Reservation cancelled.")



        



        return


    def front_end(self):
        print("\nChoose your option:\n1:Search Catalog\n2:Reserve Media\n3:View Loans\n4:View Fines:\n5:View Reservations\n6:Update Account Information\n5:Exit")
        choice = input("Enter choice(number): ")
        if choice == '1':
            self.search_interface()
        elif choice == '2':
            self.reserve()
        elif choice == '5':
            print("Have a nice day!")
            return 0
        else:
            print("Choice not recognized. Try again!")
        return 1





















class Staff:
    def __init__(self, id, cur):
        self.ID = id
        self.cur = cur


    def checkout(self):
        query = "SELECT MAX(loanID) FROM loan"
        self.cur.execute(query)
        result = self.cur.fetchall()
        max = None
        for (num,) in result:
            max = num
        
        loanID = max + 1

        memberID = int(input("\nEnter Member ID: "))
        query = "SELECT userType FROM user WHERE userID=%s"
        self.cur.execute(query, (memberID,))
        result = self.cur.fetchall()
        if result != None and len(result) == 1:
            userType = None
            for (type,) in result:
                userType = type
            if userType != "member":
                print("No matching member found.")
                return
            
            self.cur.execute("SELECT borrowingLimit FROM member WHERE userID=%s", (memberID,))
            limit = None
            result = self.cur.fetchall()
            for (b_limit,) in result:
                limit = b_limit
            
            self.cur.execute("SELECT COUNT(*) FROM (select * from loan WHERE memberID=%s AND returnDate IS NULL) AS subquery", (memberID,))
            borrowed_media = None
            result = self.cur.fetchall()
            for (num,) in result:
                borrowed_media = num
            
            if borrowed_media + 1 > limit:
                print("Member has reached borrowing limit.")
                return
            else:
                print("Member can borrow an item.")
        else:
            print("No matching member found.")
            return
        


        itemID = int(input("Enter Item ID: "))
        query = "SELECT * FROM media WHERE itemID=%s"
        self.cur.execute(query, (itemID,))
        result = self.cur.fetchone()
        if result == None:
            print("No matching media item found.")
            return
        
        self.cur.execute("SELECT * FROM loan WHERE itemID=%s AND returnDate is NULL",(itemID,))
        if self.cur.fetchone() != None:
            print("Item is already on loan.")
            return
        
        self.cur.execute("SELECT memberID,reservationID FROM reservation WHERE itemID=%s AND status='active'", (itemID,))
        fulfill_res = False
        result = self.cur.fetchone()
        if result != None:
            if result[0] == memberID:
                fulfill_res = True
            else:
                print("Item is reserved by another member.")
                return
        
        
        today = datetime.date.today()
        dueDate = today + datetime.timedelta(days=14)
        
        choice = input(f"\nConfirm(yes/no):\nLoan ID: {loanID}\nMember ID: {memberID}\nItem ID: {itemID}\nCheckout Date: {today}\nDue Date: {dueDate}\nEnter choice: ")

        if choice == "yes":
            print("\n")
            if fulfill_res:
                self.cur.execute("UPDATE reservation SET status='inactive' WHERE reservationID=%s",(result[1],))
                print("Reservation Fulfilled.")
            self.cur.execute("INSERT INTO loan VALUES (%s,%s,%s,%s,%s,%s,%s)", (loanID,memberID,itemID,str(today),str(dueDate),None,0))
            self.cur.execute("INSERT INTO borrows VALUES (%s,%s)", (loanID,memberID))
            self.cur.execute("INSERT INTO loaned_in VALUES (%s,%s)", (loanID,itemID))
            self.cur.execute("UPDATE media SET availabilityStatus='unavailable' WHERE itemID=%s",(itemID,))
            print("Loan created.")
        else:
            print("Loan cancelled.")
        return
















    #Allows a staff member to insert a media item without needing to directly interact with database.
    #Includes functionality for adding a copy of an already existing media item (two copies of The Hobbit)
    def insert_media(self):
        query = "SELECT MAX(itemID) FROM media"
        self.cur.execute(query)
        result = self.cur.fetchall()
        max = None
        for (num,) in result:
            max = num

        itemID = max + 1

        copy = input("\nAdding copy?(yes/no): ")

        #Manual entry for a media item.
        if copy == "no":
            title = input("\nTitle: ")
            type = input("book, digital, or magazine: ")
            publicationYear = int(input("Publication Year: "))
            availabilityStatus = "available"
            specialPremium = int(input("Additional Fee Premium(for rarity): "))
            specialRestriction = input("common or rare: ")
            if type == "book":
                ISBN = int(input("Enter ISBN: "))
                author = input("Enter Author: ")
                genre = input("Enter Genre: ")
                approve = input(f"\nConfirm(yes/no):\nitemID: {itemID}\nTitle: {title}\nType: {type}\nPublication Year: {publicationYear}\nAvailability Status: {availabilityStatus}\nSpecial Premium: {specialPremium}\nSpecial Restriction: {specialRestriction}\nISBN: {ISBN}\nAuthor: {author}\nGenre: {genre}\nEnter yes/no: ")
            elif type == "digitalMedia":
                digitalMediaID = int(input("Enter Digital Media ID: "))
                creator = input("Enter Creator: ")
                genre = input("Enter Genre: ")
                approve = input(f"\nConfirm(yes/no):\nitemID: {itemID}\nTitle: {title}\nType: {type}\nPublication Year: {publicationYear}\nAvailability Status: {availabilityStatus}\nSpecial Premium: {specialPremium}\nSpecial Restriction: {specialRestriction}\nDigital Media ID: {digitalMediaID}\nCreator: {creator}\nGenre: {genre}\nEnter yes/no: ")
            elif type == "magazine":
                ISSN = int(input("Enter ISSN: "))
                publicationDate = input("Enter PublicationDate: ")
                approve = input(f"\nConfirm(yes/no):\nitemID: {itemID}\nTitle: {title}\nType: {type}\nPublication Year: {publicationYear}\nAvailability Status: {availabilityStatus}\nSpecial Premium: {specialPremium}\nSpecial Restriction: {specialRestriction}\nISSN: {ISSN}\nPublication Date: {publicationDate}\nEnter yes/no: ")                
            else:
                print("Invalid Type")
                return

        #When adding a copy, the user inputs the itemID of a valid item. It then looks up all the identical information.
        else:
            copy_id = int(input("Enter ID of existing media item: "))
            query = "SELECT title,itemType,publicationYear,availabilityStatus,specialPremium,specialRestriction FROM media WHERE itemID=%s"
            self.cur.execute(query, (copy_id,))
            result = self.cur.fetchall()
            if len(result) == 1:
                for (ttl, typ, yr, avs, sp, sr) in result:
                    title = ttl
                    type = typ
                    publicationYear = yr
                    availabilityStatus = avs
                    specialPremium = sp
                    specialRestriction = sr
                if type == "book":
                    query = "SELECT ISBN,author,genre FROM book WHERE itemID=%s"
                    self.cur.execute(query, (copy_id,))
                    result = self.cur.fetchall()
                    for (isbn,auth,gen) in result:
                        ISBN = isbn
                        author = auth
                        genre = gen
                    approve = input(f"\nConfirm(yes/no):\nitemID: {itemID}\nTitle: {title}\nType: {type}\nPublication Year: {publicationYear}\nAvailability Status: {availabilityStatus}\nSpecial Premium: {specialPremium}\nSpecial Restriction: {specialRestriction}\nISBN: {ISBN}\nAuthor: {author}\nGenre: {genre}\nEnter yes/no: ")
                elif type == "digital":
                    query = "SELECT digitalMediaID,creator,genre FROM digitalMedia WHERE itemID=%s"
                    self.cur.execute(query, (copy_id,))
                    result = self.cur.fetchall()
                    for (dgid,creat,gen) in result:
                        digitalMediaID = dgid
                        creator = creat
                        genre = gen
                    approve = input(f"\nConfirm(yes/no):\nitemID: {itemID}\nTitle: {title}\nType: {type}\nPublication Year: {publicationYear}\nAvailability Status: {availabilityStatus}\nSpecial Premium: {specialPremium}\nSpecial Restriction: {specialRestriction}\nDigital Media ID: {digitalMediaID}\nCreator: {creator}\nGenre: {genre}\nEnter yes/no: ")
                elif type == "magazine":
                    query = "SELECT issn,publicationDate FROM magazine WHERE magazineID=%s"
                    self.cur.execute(query, (copy_id,))
                    result = self.cur.fetchall()
                    for (issn,date) in result:
                        ISSN = issn
                        publicationDate = date
                    approve = input(f"\nConfirm(yes/no):\nitemID: {itemID}\nTitle: {title}\nType: {type}\nPublication Year: {publicationYear}\nAvailability Status: {availabilityStatus}\nSpecial Premium: {specialPremium}\nSpecial Restriction: {specialRestriction}\nISSN: {ISSN}\nPublication Date: {publicationDate}\nEnter yes/no: ")                
                else:
                    print("Invalid Type")
                    return
            else:
                print("No existing item found.")
                return

        if approve == "yes":
            query = "INSERT INTO media VALUES (%s,%s,%s,%s,%s,%s,%s)"
            self.cur.execute(query, (itemID, title, type, publicationYear, availabilityStatus, specialPremium, specialRestriction))
            if type == "book":
                query = "INSERT INTO book VALUES (%s,%s,%s,%s)"
                self.cur.execute(query, (itemID, ISBN, author, genre))
            elif type == "digital":
                query = "INSERT INTO digitalMedia VALUES (%s,%s,%s,%s)"
                self.cur.execute(query, (itemID, digitalMediaID, creator, genre))
            elif type == "magazine":
                query = "INSERT INTO magazine VALUES (%s,%s,%s)"
                self.cur.execute(query,(itemID, ISSN, publicationDate))
            print("\nMedia added.")
            query = "SELECT * FROM media WHERE itemID=%s"
            self.cur.execute(query, (itemID,))
            for row in self.cur.fetchall():
                print(row)
        else:
            print("\nEntry halted.")
        return




    #Will add more functions for other options (checkout, user management, etc).
    def front_end(self):
        print("\nChoose you option:\n1:Add Media\n2:Checkout Media\n3:Process Return\n4:Process Payment\n5:Exit")
        choice = input("Enter choice(number): ")
        if choice == '1':
            self.insert_media()
        elif choice == '2':
            self.checkout()
        elif choice == '5':
            print("Have a nice day!")
            return 0
        else:
            print("Choice not recognized. Try again!")
        return 1















class Interface:
    def __init__(self):
        self.conn = mysql.connector.connect(
                    user="447s25_j776w781",
                    password="ohN7iewa",
                    host="mysql.eecs.ku.edu",
                    port=3306,
                    database="447s25_j776w781"
                )
        self.cur = self.conn.cursor()

    #Login feature. User must input a valid ID that appears in the user table. 
    #Returns an integer representing the user's type.
    def log_on(self):
        id = int(input("Enter your userID: "))
        query = "SELECT userType,name from user WHERE userID='%s'"
        self.cur.execute(query, (id,))
        results = self.cur.fetchall()
        if len(results) == 1:
            print("Login Successful")
            userType = None
            uname = None
            for (type,name) in results:
                userType = type
                uname = name


            if userType == "staff":
                return 0,id,uname
            elif userType == "member":
                return 1,id,uname
            elif userType == "admin":
                return 2,id,uname
        else:
            print("Login Unsuccessful")

    
    def run(self):
        try:
            print("Welcome!")
            userType,id,name = self.log_on()
            print(f"Hello {name}!")
            if userType == 0:
                staff = Staff(id, self.cur)
                stay_on = 1
                while stay_on == 1:
                    stay_on = staff.front_end()
                    self.conn.commit()
            elif userType == 1:
                member = Member(id, self.cur)
                stay_on = 1
                while stay_on == 1:
                    stay_on = member.front_end()
                    self.conn.commit()
            elif userType == 2:
                print("Hello admin!")
            self.conn.close()
        except Exception as e:
            print(f"Error: {e}")
            self.conn.close()







def main():
    interface = Interface()
    interface.run()
main()
