'''
First two lines only needed if not using the method Aiham came up with.
'''
#import sys
#sys.path.insert(0, '../library_project/mysql-connector-python/lib')
import mysql.connector
import datetime


class User:
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

    def update_contact_info(self):
        self.cur.execute("SELECT name, phoneNumber, emailAddress, physicalAddress FROM user WHERE userID=%s", (self.ID,))
        profile = self.cur.fetchone()
        name = profile[0]
        phone = profile[1]
        email = profile[2]
        addr = profile[3]
        contact_info = [phone, email, addr]
        contact_names = ["phoneNumber", "emailAddress", "physicalAddress"]
        print(f"\nCurrent Profile:\nUserID: {self.ID}\nName: {name}\nPhone Number: {phone}\nEmail Address: {email}\nMailing Address: {addr}\n")
        change = input("Do you want to make changes to your contact information?(yes/no): ")
        if change == "yes":
            filled_in = 0
            for info in contact_info:
                if info != None:
                    filled_in += 1
            delete = input(f"\nWould you like to delete contact information?(yes/no): ")
            if delete == "yes":
                if filled_in > 1:
                    choice = input("\nChoose info to delete.\n0:Phone Number\n1:Email\n2:Address\nEnter number: ")
                    if choice in ['0', '1', '2']:
                        choice = int(choice)
                        confirm = input(f"Are you sure you want to delete your {contact_names[choice]}?(yes/no): ")
                        if confirm == "yes":
                            self.cur.execute(f"UPDATE user SET {contact_names[choice]}=NULL WHERE userID=%s", (self.ID,))
                            print("Changes made.")
                        else:
                            print("Changes cancelled.")
                            return
                    else:
                        print("Invalid choice.")
                        return
                else:
                    print("You must have at least one form of contact information.")
                    return
            else:
                choice = input("\nChoose info to change\n0:Phone Number\n1:Email\n2:Address\nEnter number: ")
                if choice in ['0', '1', '2']:
                    choice = int(choice)
                    entry = input(f"Enter value for {contact_names[choice]}: ")
                    confirm = input(f"Are you sure you want to change {contact_names[choice]} to {entry}?(yes/no): ")
                    if confirm == "yes":
                        self.cur.execute(f"UPDATE user SET {contact_names[choice]}=%s WHERE userID=%s", (entry, self.ID))
                        print("Changes made.")
                    else:
                        print("Changes cancelled.")
                        return
                else:
                    print("Invalid choice.")
                    return
        else:
            print("No changes made.")
            return


    



class Member(User):
    def __init__(self, id, cur):
        super().__init__(id,cur)

    def notifications(self):
        self.cur.execute("SELECT itemID, expirationDate FROM reservation WHERE memberID=%s AND status='active' AND expirationDate IS NOT NULL", (self.ID,))
        for (itemID,expDate) in self.cur.fetchall():
            print(f"Your reserved item {itemID} is available! Your reservation will expire on {expDate}.")

        today = datetime.date.today()

        self.cur.execute("SELECT itemID, dueDate FROM loan WHERE returnDate IS NULL AND dueDate >= DATE(%s) AND dueDate <= DATE(%s) AND memberID=%s", (str(today), str(today + datetime.timedelta(days=7)), self.ID))
        for (itemID, dueDate) in self.cur.fetchall():
            print(f"Your loaned item {itemID} is due soon on {dueDate}.")

        self.cur.execute("SELECT itemID, dueDate FROM loan WHERE returnDate IS NULL AND dueDate < DATE(%s) AND memberID=%s", (str(today),self.ID))
        for (itemID, dueDate) in self.cur.fetchall():
            print(f"Your loaned item {itemID} was due on {dueDate}. Turn it in TODAY!!!")
        
        self.cur.execute("SELECT SUM(amount) FROM fine WHERE memberID=%s AND status='unpaid'", (self.ID,))
        tot = self.cur.fetchone()
        if tot != (None,):
            print(f"You owe ${tot[0]} in unpaid fines! Pay them TODAY!!!!")


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

    def view_reservations(self):
        self.cur.execute("SELECT * FROM reservation WHERE memberID=%s AND status='active'", (self.ID,))
        results = self.cur.fetchall()
        if len(results) != 0:
            for (rID, mID, iID, rDate, expDate, stat) in results:
                print(f"\nReservation ID: {rID}\nItem Reserved: {iID}\nDate Reserved: {rDate}\nExpiration Date: {expDate}")
        else:
            print("\nNo active reservations.")

    def view_loans(self):
        today = datetime.date.today()

        print("Loans Due Soon:")
        self.cur.execute("SELECT * FROM loan WHERE returnDate IS NULL AND dueDate >= DATE(%s) AND dueDate <= DATE(%s) AND memberID=%s", (str(today), str(today + datetime.timedelta(days=7)), self.ID))
        for (lID, mID, iID, cDate, dDate, rDate, l) in self.cur.fetchall():
            print(f"\nLoan ID: {lID}\nItem Loaned: {iID}\nCheckout Date: {cDate}\nDue Date: {dDate}")

        print("\nLoans OVERDUE:")
        self.cur.execute("SELECT * FROM loan WHERE returnDate IS NULL AND dueDate < DATE(%s) AND memberID=%s", (str(today),self.ID))
        for (lID, mID, iID, cDate, dDate, rDate, l) in self.cur.fetchall():
            print(f"\nLoan ID: {lID}\nItem Loaned: {iID}\nCheckout Date: {cDate}\nDue Date: {dDate}")


    def view_fines(self):
        self.cur.execute("SELECT * FROM fine WHERE memberID=%s AND status='unpaid'", (self.ID,))
        results = self.cur.fetchall()
        if len(results) != 0:
            for (fID, mID, lID, amount, isDate, stat) in results:
                print(f"\nFine ID: {fID}\nCorresponding Loan: {lID}\nDate Issued: {isDate}\nAmount: ${amount}")
        else:
            print("\nNo unpaid fines.")



    def front_end(self):
        print("\nChoose your option:\n1:Search Catalog\n2:Reserve Media\n3:View Loans\n4:View Fines\n5:View Reservations\n6:Update Account Information\n7:Exit")
        choice = input("Enter choice(number): ")
        if choice == '1':
            self.search_interface()
        elif choice == '2':
            self.reserve()
        elif choice == '3':
            self.view_loans()
        elif choice == '4':
            self.view_fines()
        elif choice == '5':
            self.view_reservations()
        elif choice == '6':
            self.update_contact_info()
        elif choice == '7':
            print("Have a nice day!")
            return 0
        else:
            print("Choice not recognized. Try again!")
        return 1





















class Staff(User):
    def __init__(self, id, cur):
        super().__init__(id,cur)


    def process_return(self):
        itemID = int(input("\nEnter Item ID: "))
        self.cur.execute("SELECT * FROM loan WHERE returnDate IS NULL AND itemID=%s", (itemID,))
        loan_result = self.cur.fetchone()
        if loan_result == (None,):
            print("No active loan for that member\n")
            return
        loanID = loan_result[0]
        memberID = loan_result[1]
        itemID = loan_result[2]
        checkoutDate = loan_result[3]
        dueDate = loan_result[4]
        lateFeeCharge = loan_result[6]

        today = datetime.date.today()

        print(f"\nProcessing return for loan {loanID}")
        if lateFeeCharge != 0:
            print("Overdue return detected.")

        choice = input("Confirm return?(yes/no): ")
        if choice == "yes":
            self.cur.execute("UPDATE loan SET returnDate=%s WHERE loanID=%s", (str(today), loanID,))
            self.cur.execute("UPDATE media SET availabilityStatus='available' WHERE itemID=%s", (itemID,))
            if lateFeeCharge != 0:
                query = "SELECT MAX(fineID) FROM fine"
                self.cur.execute(query)
                result = self.cur.fetchall()
                max = None
                for (num,) in result:
                    max = num
                fineID = max + 1

                self.cur.execute("INSERT INTO fine VALUES (%s,%s,%s,%s,%s,%s)", (fineID,memberID,loanID,lateFeeCharge,str(today),"unpaid"))
                print(f"Fine created with ID: {fineID}")
                self.cur.execute("INSERT INTO triggers VALUES (%s,%s)", (loanID,fineID))
                self.cur.execute("INSERT INTO owes VALUES (%s,%s)", (fineID,memberID))

            self.cur.execute("UPDATE reservation SET expirationDate=%s WHERE itemID=%s AND status='active'",(str(today + datetime.timedelta(days=3)),itemID))

            print("Return successful.")

        else:
            print("Return Cancelled.")

        return


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
        if result == (None,):
            print("No matching media item found.")
            return
        
        self.cur.execute("SELECT * FROM loan WHERE itemID=%s AND returnDate is NULL",(itemID,))
        if self.cur.fetchone() != (None,):
            print("Item is already on loan.")
            return
        
        self.cur.execute("SELECT memberID,reservationID FROM reservation WHERE itemID=%s AND status='active'", (itemID,))
        fulfill_res = False
        result = self.cur.fetchone()
        if result != (None,):
            if result[0] == memberID:
                fulfill_res = True
            else:
                print("Item is reserved by another member.")
                return
        
        
        datechoice = input("Manually enter Checkout and Due Dates? (yes/no): ")
        if datechoice == 'yes':
            today = input("Enter checkout date in Year-Month-Day Format: ")
            dueDate = input("Enter due date in Year-Month-Day Format: ")
        else:
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



    def process_payment(self):
        memberID = int(input("\nEnter Member ID: "))
        self.cur.execute("SELECT fineID, amount FROM fine WHERE memberID=%s", (memberID,))
        fines = self.cur.fetchall()
        if len(fines) == 0:
            print("No fines for this member")
            return
        else:
            print("\n")
            for (id, amount) in fines:
                print(f"Fine {id} for ${amount}")

        fineID = int(input("Enter desired fine ID: "))
        self.cur.execute("SELECT * FROM fine WHERE fineID=%s", (fineID,))
        result = self.cur.fetchone()
        if result == (None,):
            print("No fine found.")
            return

        amount = result[3]

        today = datetime.date.today()


        query = "SELECT MAX(paymentID) FROM payment"
        self.cur.execute(query)
        result = self.cur.fetchall()
        max = None
        for (num,) in result:
            max = num
        paymentID = max + 1

        choice = input(f"Confirm (yes/no):\nPayment {paymentID} towards fine {fineID} by member {memberID} for ${amount}\nEnter choice: ")
        if choice == "yes":
            self.cur.execute("INSERT INTO payment VALUES (%s,%s,%s,%s,%s)", (paymentID, fineID, memberID, str(today), amount))
            self.cur.execute("UPDATE fine SET status='paid' WHERE fineID=%s", (fineID,))
            self.cur.execute("INSERT INTO pays VALUES (%s,%s)", (paymentID, memberID))
            self.cur.execute("INSERT INTO pays_for VALUES (%s,%s)", (paymentID,fineID))
            print("\nPayment successful.")
        else:
            print("Payment cancelled.")

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


    def problem_user_report(self):
        #This function will generate a report of all problem users. A problem user is defined as one who has 3 or more overdue loans or 2 or more unpaid fines.
        #It will also check if the user is currently borrowing any items. If they are not, it will recommend deactivation of their account.
       
        cursor = self.cur
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

        #members who are currently borrowing items
        cur_borrow_query = """
        SELECT memberID
        FROM loan
        WHERE returnDate IS NULL
        """

        cursor.execute(cur_borrow_query)
        cur_borrow_results = cursor.fetchall()  
        cur_borrow_set = {row[0] for row in cur_borrow_results}  #this ones a set for faster lookup

        all_members = set(overdue_dict) | set(fines_dict) | cur_borrow_set

        print("\n------PROBLEM MEMBER REPORT------\n")
        for member_id in all_members:
            overdue_count = overdue_dict.get(member_id, 0)
            unpaid_fines_count = fines_dict.get(member_id, 0)
            currently_borrowing = member_id in cur_borrow_set

            #flag as problem member if they have 3 or more overdue loans or 2 or more unpaid fines
            is_problem_member = overdue_count >= 3 or unpaid_fines_count >= 2
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



    def collection_analysis(self):
        print("\n------ COLLECTION ANALYSIS REPORT ------\n")

        # 1. Most Frequently Borrowed Items
        print("Top 10 Most Frequently Borrowed Items:")
        self.cur.execute("""
            SELECT m.itemID, m.title, COUNT(l.loanID) AS borrowCount
            FROM media m
            JOIN loan l ON m.itemID = l.itemID
            GROUP BY m.itemID
            ORDER BY borrowCount DESC
            LIMIT 10;
        """)
        for itemID, title, count in self.cur.fetchall():
            print(f"Item ID: {itemID}, Title: {title}, Times Borrowed: {count}")
        print()

        # 2. Least Frequently Borrowed Items
        print("Top 10 Least Frequently Borrowed Items:")
        self.cur.execute("""
            SELECT m.itemID, m.title, COUNT(l.loanID) AS borrowCount
            FROM media m
            LEFT JOIN loan l ON m.itemID = l.itemID
            GROUP BY m.itemID
            HAVING borrowCount > 0
            ORDER BY borrowCount ASC
            LIMIT 10;
        """)
        for itemID, title, count in self.cur.fetchall():
            print(f"Item ID: {itemID}, Title: {title}, Times Borrowed: {count}")
        print()

        # 3. Items Most Often Returned Late
        print("Items Most Often Returned Late:")
        self.cur.execute("""
            SELECT m.itemID, m.title, COUNT(*) AS lateReturns
            FROM media m
            JOIN loan l ON m.itemID = l.itemID
            WHERE l.returnDate > l.dueDate
            GROUP BY m.itemID
            ORDER BY lateReturns DESC
            LIMIT 10;
        """)
        for itemID, title, count in self.cur.fetchall():
            print(f"Item ID: {itemID}, Title: {title}, Late Returns: {count}")
        print()

        # 4. Collection Circulation Summary
        print("Collection Circulation Summary:")
        self.cur.execute("SELECT COUNT(*) FROM media;")
        total_items = self.cur.fetchone()[0]

        self.cur.execute("SELECT COUNT(DISTINCT itemID) FROM loan;")
        items_borrowed = self.cur.fetchone()[0]

        if total_items > 0:
            circulation_rate = (items_borrowed / total_items) * 100
        else:
            circulation_rate = 0

        print(f"Total Items in Collection: {total_items}")
        print(f"Items Borrowed At Least Once: {items_borrowed}")
        print(f"Circulation Rate: {circulation_rate:.2f}%")
        print()

    

    def report_interface(self):
        choice = input("\nEnter report to generate:\n1:Problem Member Analysis\n2:Collection Analysis\n3:\nEnter number: ")
        if choice == '1':
            self.problem_user_report()
        elif choice == '2':
            self.collection_analysis()
        else:
            print("Choice not recognized.")

    #Will add more functions for other options (checkout, user management, etc).
    def front_end(self):
        print("\nChoose your option:\n1:Add Media\n2:Checkout Media\n3:Process Return\n4:Process Payment\n5:Search Media\n6:Generate Report\n7:Update Contact Info\n8:Exit")
        choice = input("Enter choice(number): ")
        if choice == '1':
            self.insert_media()
        elif choice == '2':
            self.checkout()
        elif choice == '3':
            self.process_return()
        elif choice == '5':
            self.search_interface()
        elif choice == '4':
            self.process_payment()
        elif choice == '6':
            self.report_interface()
        elif choice == '7':
            self.update_contact_info()
        elif choice == '8':
            print("Have a nice day!")
            return 0
        else:
            print("Choice not recognized. Try again!")
        return 1








class Admin(User):
    def __init__(self, id, cur):
        super().__init__(id,cur)

    def query(self):
        query = input("Enter SQL query(exclude semicolon): ")
        try:
            self.cur.execute(query)
            results = self.cur.fetchall()
            if len(results) != 0:
                for row in results:
                    print(row)
            else:
                print("No results returned.")
        except Exception as E:
            print(E)
            return
        
    def front_end(self):
        print("\nChoose your option:\n1:Enter Query\n2:Update Contact Info\n3:Search Media\n4:Exit")
        choice = input("Enter choice(number): ")      
        if choice == '1':
            self.query()
        elif choice == '2':
            self.update_contact_info()
        elif choice == '3':
            self.search_interface()
        elif choice == '4':
            print("Have a nice day!")
            return 0
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


    def update(self):
        today = datetime.date.today()
        self.cur.execute("UPDATE reservation SET status='inactive' WHERE status='active' AND expirationDate < DATE(%s)", (str(today),))
        self.cur.execute("SELECT loanID FROM loan WHERE dueDate < DATE(%s) AND returnDate IS NULL", (str(today),))
        overdue_loans = self.cur.fetchall()
        if len(overdue_loans) != 0:
            for (loanID,) in overdue_loans:
                self.cur.execute("select DATEDIFF(\"2025-05-04\", l.dueDate) * (m.lateFeeRate+i.specialPremium) from (loan l join member m on l.memberID = m.userID) join media i on i.itemID=l.itemID where loanID=%s", (loanID,))
                charge = self.cur.fetchone()[0]
                self.cur.execute("UPDATE loan SET lateFeeCharge=%s WHERE loanID=%s", (charge, loanID))
        self.conn.commit()

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
            self.update()
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
                member.notifications()
                stay_on = 1
                while stay_on == 1:
                    stay_on = member.front_end()
                    self.conn.commit()
            elif userType == 2:
                admin = Admin(id, self.cur)
                stay_on = 1
                while stay_on == 1:
                    stay_on = admin.front_end()
                    self.conn.commit()
            self.conn.close()
        except Exception as e:
            print(f"Error: {e}")
            self.conn.close()







def main():
    interface = Interface()
    interface.run()
main()
