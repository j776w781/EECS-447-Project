'''
First two lines only needed if not using the method Aiham came up with.
'''
#import sys
#sys.path.insert(0, '../library_project/mysql-connector-python/lib')
import mysql.connector

class Staff:
    def __init__(self, id, cur):
        self.ID = id
        self.cur = cur

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
                print("No existing item found.\n")
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
            print("\nMedia added.\n")
            query = "SELECT * FROM media WHERE itemID=%s"
            self.cur.execute(query, (itemID,))
            for row in self.cur.fetchall():
                print(row)
        else:
            print("\nEntry halted.\n")
        return



    #Will add more functions for other options (checkout, user management, etc).
    def front_end(self):
        print("Choose you option:\n1:Add Media\n2:Checkout Media\n3:Process Return\n4:Process Payment\n5:Exit")
        choice = int(input("Enter choice(number): "))
        if choice == 1:
            self.insert_media()
        else:
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
        self.cur = conn.cursor()

    #Login feature. User must input a valid ID that appears in the user table. 
    #Returns an integer representing the user's type.
    def log_on(self):
        id = int(input("Enter your userID: "))
        query = "SELECT userType from user WHERE userID='%s'"
        self.cur.execute(query, (id,))
        results = self.cur.fetchall()
        if len(results) == 1:
            print("Login Successful")
            userType = None
            for (type,) in results:
                userType = type

            if type == "staff":
                return 0
                staff = Staff(id, self.cur)
                staff.front_end()
        else:
            print("Login Unsuccessful")

    
    def run(self):
        try:
            print("Connection successful")
            usertype = self.log_on()
            #Will implement functionality for member as well.
            if usertype == 0:
                staff = Staff(id, self.cur)
                stay_on = 1
                while stay_on == 1:
                    stay_on = staff.front_end()
                    self.conn.commit()
            self.conn.close()
        except Exception as e:
            print(f"Error: {e}")
            self.conn.close()







def main():
    interface = Interface()
    interface.run()
main()
