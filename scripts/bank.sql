-- Create the database
CREATE DATABASE BankDB;
GO

-- Use the database
USE BankDB;
GO

-- Create the Customers table
CREATE TABLE Customers (
    CustomerID INT PRIMARY KEY IDENTITY(1,1),
    FirstName NVARCHAR(50) NOT NULL,
    LastName NVARCHAR(50) NOT NULL,
    Email NVARCHAR(100) UNIQUE NOT NULL,
    PhoneNumber NVARCHAR(15),
    Address NVARCHAR(255),
    City NVARCHAR(50),
    State NVARCHAR(50),
    ZipCode NVARCHAR(10),
    CreatedAt DATETIME DEFAULT GETDATE()
);
GO

-- Create the Accounts table
CREATE TABLE Accounts (
    AccountID INT PRIMARY KEY IDENTITY(1,1),
    CustomerID INT NOT NULL,
    AccountNumber NVARCHAR(20) UNIQUE NOT NULL,
    AccountType NVARCHAR(20) NOT NULL,
    Balance DECIMAL(18, 2) DEFAULT 0.00,
    CreatedAt DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_Customers_Accounts FOREIGN KEY (CustomerID)
        REFERENCES Customers(CustomerID)
);
GO

-- Create the BankTransactions table
CREATE TABLE BankTransactions (
    TransactionID INT PRIMARY KEY IDENTITY(1,1),
    AccountID INT NOT NULL,
    TransactionType NVARCHAR(20) NOT NULL,
    Amount DECIMAL(18, 2) NOT NULL,
    TransactionDate DATETIME DEFAULT GETDATE(),
    Description NVARCHAR(255),
    CONSTRAINT FK_Accounts_Transactions FOREIGN KEY (AccountID)
        REFERENCES Accounts(AccountID)
);
GO

-- Insert sample records into Customers table
INSERT INTO Customers (FirstName, LastName, Email, PhoneNumber, Address, City, State, ZipCode)
VALUES 
('John', 'Doe', 'john.doe@example.com', '555-1234', '123 Elm Street', 'Springfield', 'IL', '62701'),
('Jane', 'Smith', 'jane.smith@example.com', '555-5678', '456 Oak Avenue', 'Metropolis', 'NY', '10001'),
('Alice', 'Johnson', 'alice.johnson@example.com', '555-9101', '789 Pine Road', 'Gotham', 'NJ', '07001'),
-- Add more records here, following the same pattern
-- Repeat until you have at least 50 records
('Customer48', 'LastName48', 'customer48@example.com', '555-4848', '48th Address St', 'City48', 'State48', '48401'),
('Customer49', 'LastName49', 'customer49@example.com', '555-4949', '49th Address St', 'City49', 'State49', '49401'),
('Customer50', 'LastName50', 'customer50@example.com', '555-5050', '50th Address St', 'City50', 'State50', '50501');
GO

-- Insert sample records into Accounts table
-- Assuming each customer has one account, with some random account types and balances
INSERT INTO Accounts (CustomerID, AccountNumber, AccountType, Balance)
VALUES 
(1, 'ACC001', 'Savings', 1000.00),
(2, 'ACC002', 'Checking', 1500.50),
(3, 'ACC003', 'Savings', 2500.75),
-- Add more records here, following the same pattern
-- Repeat until you have at least 50 records
(48, 'ACC048', 'Savings', 3200.40),
(49, 'ACC049', 'Checking', 2100.60),
(50, 'ACC050', 'Savings', 1800.80);
GO

-- Insert sample records into BankTransactions table
-- Each account will have a few random transactions
INSERT INTO BankTransactions (AccountID, TransactionType, Amount, Description)
VALUES 
(1, 'Deposit', 500.00, 'Initial deposit'),
(1, 'Withdrawal', 200.00, 'ATM withdrawal'),
(1, 'Deposit', 300.00, 'Salary deposit'),
(2, 'Deposit', 700.00, 'Initial deposit'),
(2, 'Withdrawal', 100.00, 'ATM withdrawal'),
(2, 'Deposit', 400.00, 'Salary deposit'),
(3, 'Deposit', 800.00, 'Initial deposit'),
(3, 'Withdrawal', 300.00, 'ATM withdrawal'),
(3, 'Deposit', 500.00, 'Salary deposit'),
-- Add more records here, following the same pattern
-- Repeat until you have at least 50 records
(48, 'Deposit', 1200.00, 'Initial deposit'),
(48, 'Withdrawal', 400.00, 'ATM withdrawal'),
(48, 'Deposit', 600.00, 'Salary deposit'),
(49, 'Deposit', 1100.00, 'Initial deposit'),
(49, 'Withdrawal', 300.00, 'ATM withdrawal'),
(49, 'Deposit', 500.00, 'Salary deposit'),
(50, 'Deposit', 900.00, 'Initial deposit'),
(50, 'Withdrawal', 250.00, 'ATM withdrawal'),
(50, 'Deposit', 350.00, 'Salary deposit');
GO
