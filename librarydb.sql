DROP TABLE IF EXISTS loaned_in;
DROP TABLE IF EXISTS borrows;
DROP TABLE IF EXISTS triggers;
DROP TABLE IF EXISTS owes;
DROP TABLE IF EXISTS pays_for;
DROP TABLE IF EXISTS pays;
DROP TABLE IF EXISTS reserves;
DROP TABLE IF EXISTS reserved_in;
DROP TABLE IF EXISTS payment;
DROP TABLE IF EXISTS fine;
DROP TABLE IF EXISTS loan;
DROP TABLE IF EXISTS reservation;
DROP TABLE IF EXISTS member;
DROP TABLE IF EXISTS staff;
DROP TABLE IF EXISTS admin;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS book;
DROP TABLE IF EXISTS digitalMedia;
DROP TABLE IF EXISTS magazine;
DROP TABLE IF EXISTS media;

CREATE TABLE user (
    userID INT PRIMARY KEY CHECK (userID >= 0),
    name VARCHAR(100),
    phoneNumber VARCHAR(100),
    emailAddress VARCHAR(100),
    physicalAddress VARCHAR(100),
    userType ENUM("admin", "staff", "member"),
    accountStatus ENUM("active", "inactive")
);

CREATE TABLE member (
	userID INT PRIMARY KEY,
	typeNAME ENUM("regular", "student", "senior"),
	borrowingLimit INT CHECK (borrowingLimit > 0),
	lateFeeRate DECIMAL CHECK (lateFeeRate > 0),
	FOREIGN KEY (userID) REFERENCES user(userID) ON DELETE CASCADE
);

CREATE TABLE staff (
    userID INT PRIMARY KEY,
    FOREIGN KEY (userID) REFERENCES user(userID) ON DELETE CASCADE
);

CREATE TABLE admin (
    userID INT PRIMARY KEY,
    FOREIGN KEY (userID) REFERENCES user(userID) ON DELETE CASCADE
);

CREATE TABLE media (
    itemID INT PRIMARY KEY CHECK (itemID >= 0),
    title VARCHAR(100),
    itemType ENUM("book", "digital", "magazine"),
    publicationYear INT CHECK (publicationYear > 0),
    availabilityStatus ENUM("available", "unavailable"),
    specialPremium DECIMAL CHECK (specialPremium >= 0),
    specialRestriction ENUM("common", "rare")
);

CREATE TABLE book (
    itemID INT PRIMARY KEY,
    FOREIGN KEY (itemID) REFERENCES media(itemID) ON DELETE CASCADE,
    ISBN INT CHECK (ISBN > 0),
    author VARCHAR(100),
    genre VARCHAR(100)
);

CREATE TABLE digitalMedia (
    itemID INT PRIMARY KEY,
    FOREIGN KEY (itemID) REFERENCES media(itemID) ON DELETE CASCADE,
    digitalMediaID INT CHECK (digitalMediaID > 0),
    creator VARCHAR(100),
    genre VARCHAR(100)
);

CREATE TABLE magazine (
    magazineID INT PRIMARY KEY,
    FOREIGN KEY (magazineID) REFERENCES media(itemID) ON DELETE CASCADE,
    issn INT CHECK (issn > 0),
    publicationDate DATE
);

CREATE TABLE loan (
    loanID INT PRIMARY KEY CHECK (loanID >= 0),
    memberID INT,
    FOREIGN KEY (memberID) REFERENCES member(userID) ON DELETE CASCADE,
    itemID INT,
    FOREIGN KEY (itemID) REFERENCES media(itemID),
    checkoutDate DATE,
    dueDate DATE CHECK (duedate > checkoutDate),
    returnDate DATE CHECK (returnDate > checkoutDate),
    lateFeeCharge DECIMAL CHECK (lateFeeCharge >= 0)
);

CREATE TABLE fine (
    fineID INT PRIMARY KEY CHECK (fineID >= 0),
    memberID INT,
    FOREIGN KEY (memberID) REFERENCES member(userID) ON DELETE CASCADE,
    loanID INT,
    FOREIGN KEY (loanID) REFERENCES loan(loanID),
    amount DECIMAL CHECK (amount >= 0),
    issueDate DATE,
    status ENUM("unpaid", "paid")
);

CREATE TABLE payment (
    paymentID INT PRIMARY KEY CHECK (paymentID >= 0),
    fineID INT,
    FOREIGN KEY (fineID) REFERENCES fine(fineID),
    memberID INT,
    FOREIGN KEY (memberID) REFERENCES member(userID),
    paymentDate DATE,
    amount DECIMAL CHECK (amount >= 0)
);

CREATE TABLE reservation (
    reservationID INT PRIMARY KEY CHECK (reservationID >= 0),
    memberID INT,
    FOREIGN KEY (memberID) REFERENCES member(userID) ON DELETE CASCADE,
    itemID INT,
    FOREIGN KEY (itemID) REFERENCES media(itemID),
    reservationDate DATE,
    expirationDate DATE CHECK (expirationDate >= reservationDate),
    status ENUM("active", "inactive")
);

CREATE TABLE loaned_in (
    loanID INT PRIMARY KEY,
    FOREIGN KEY (loanID) REFERENCES loan(loanID) ON DELETE CASCADE,
    itemID INT,
    FOREIGN KEY (itemID) REFERENCES media(itemID) ON DELETE CASCADE
);

CREATE TABLE borrows (
    loanID INT PRIMARY KEY,
    FOREIGN KEY (loanID) REFERENCES loan(loanID) ON DELETE CASCADE,
    memberID INT,
    FOREIGN KEY (memberID) REFERENCES member(userID) ON DELETE CASCADE
);

CREATE TABLE triggers (
    loanID INT PRIMARY KEY,
    FOREIGN KEY (loanID) REFERENCES loan(loanID) ON DELETE CASCADE,
    fineID INT,
    FOREIGN KEY (fineID) REFERENCES fine(fineID) ON DELETE CASCADE
);

CREATE TABLE owes (
    fineID INT PRIMARY KEY,
    FOREIGN KEY (fineID) REFERENCES fine(fineID) ON DELETE CASCADE,
    memberID INT,
    FOREIGN KEY (memberID) REFERENCES member(userID) ON DELETE CASCADE
);

CREATE TABLE pays_for (
    paymentID INT PRIMARY KEY,
    FOREIGN KEY (paymentID) REFERENCES payment(paymentID) ON DELETE CASCADE,
    fineID INT,
    FOREIGN KEY (fineID) REFERENCES fine(fineID) ON DELETE CASCADE
);

CREATE TABLE pays (
    paymentID INT PRIMARY KEY,
    FOREIGN KEY (paymentID) REFERENCES payment(paymentID) ON DELETE CASCADE,
    memberID INT,
    FOREIGN KEY (memberID) REFERENCES member(userID) ON DELETE CASCADE
);

CREATE TABLE reserves (
    reservationID INT PRIMARY KEY,
    FOREIGN KEY (reservationID) REFERENCES reservation(reservationID) ON DELETE CASCADE,
    memberID INT,
    FOREIGN KEY (memberID) REFERENCES member(userID) ON DELETE CASCADE
);

CREATE TABLE reserved_in (
    reservationID INT PRIMARY KEY,
    FOREIGN KEY (reservationID) REFERENCES reservation(reservationID) ON DELETE CASCADE,
    itemID INT,
    FOREIGN KEY (itemID) REFERENCES media(itemID) ON DELETE CASCADE
);
