DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS members;
DROP TABLE IF EXISTS membershipType;
DROP TABLE IF EXISTS media;
DROP TABLE IF EXISTS book;
DROP TABLE IF EXISTS digitalMedia;
DROP TABLE IF EXISTS magazine;
DROP TABLE IF EXISTS loan;
DROP TABLE IF EXISTS reservation;
DROP TABLE IF EXISTS fine;
DROP TABLE IF EXISTS payment;


CREATE TABLE users (
    userID INT PRIMARY KEY CHECK (userID >= 0),
    name VARCHAR(100),
    phoneNumber VARCHAR(100),
    emailAddress VARCHAR(100),
    physicalAddress VARCHAR(100),
    userType ENUM("admin", "staff", "member"),
    accountStatus ENUM("active", "inactive")
);

CREATE TABLE members (
    memberID INT PRIMARY KEY AUTO_INCREMENT,
);

CREATE TABLE membershipType (
    id INT PRIMARY KEY,
    FOREIGN KEY (id) REFERENCES members(memberID) ON DELETE CASCADE,
    typeName ENUM("regular", "student", "senior") NOT NULL,
    borrowingLimit INT CHECK (borrowingLimit > 0),
    lateFeeRate DECIMAL CHECK (lateFeeRate > 0)
);

CREATE TABLE media (
    itemID INT PRIMARY KEY AUTO_INCREMENT CHECK (itemID >= 0),
    title VARCHAR(100),
    itemType ENUM("book", "digital", "magazine"),
    publicationYear INT CHECK (publicationYear > 0),
    availabilityStatus ENUM("available", "unavailable"),
    specialPremium DECIMAL CHECK (specialPremium >= 0),
    specialRestriction ENUM("common", "rare")
);

CREATE TABLE book (
    bookID INT PRIMARY KEY,
    FOREIGN KEY (bookID) REFERENCES media(itemID) ON DELETE CASCADE,
    isbn INT CHECK (isbn > 0),
    author VARCHAR(100),
    genre VARCHAR(100)
);

CREATE TABLE digitalMedia (
    digitalMediaID INT PRIMARY KEY,
    FOREIGN KEY (digitalMediaID) REFERENCES media(itemID) ON DELETE CASCADE,
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
    loadID INT PRIMARY KEY CHECK (loanID >= 0),
    memberID INT,
    FOREIGN KEY (memberID) REFERENCES users(userID) ON DELETE CASCADE,
    itemID INT,
    FOREIGN KEY (itemID) REFERENCES media(itemID),
    checkoutDate DATE,
    dueDate DATE CHECK (duedate > checkoutDate),
    returnDate DATE CHECK (returnDate > checkoutDate),
    lateFeeCharge DECIMAL CHECK (lateFeeCharge >= 0)
);

CREATE TABLE reservation (
    reservationID INT PRIMARY KEY CHECK (reservationID >= 0),
    memberID INT,
    FOREIGN KEY (memberID) REFERENCES users(userID) ON DELETE CASCADE,
    itemID INT,
    FOREIGN KEY (itemID) REFERENCES media(itemID),
    reservationDate DATE,
    expirationDate DATE CHECK (expirationDate >= reservationDate),
    status ENUM("active", "inactive")
);

CREATE TABLE fine (
    fineID INT PRIMARY KEY CHECK (fineID >= 0),
    memberID INT,
    FOREIGN KEY (memberID) REFERENCES users(userID) ON DELETE CASCADE,
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
    FOREIGN KEY (memberID) REFERENCES users(userID),
    paymentDate DATE,
    amountPaid DECIMAL CHECK (amountPaid >= 0)
);