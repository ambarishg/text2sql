-- Create Tables for Northwind Database

CREATE TABLE Categories (
    CategoryID int PRIMARY KEY,
    CategoryName nvarchar(15) NOT NULL,
    Description ntext,
    Picture image
);

CREATE TABLE Customers (
    CustomerID nchar(5) PRIMARY KEY,
    CompanyName nvarchar(40) NOT NULL,
    ContactName nvarchar(30),
    ContactTitle nvarchar(30),
    Address nvarchar(60),
    City nvarchar(15),
    Region nvarchar(15),
    PostalCode nvarchar(10),
    Country nvarchar(15),
    Phone nvarchar(24),
    Fax nvarchar(24)
);

CREATE TABLE Employees (
    EmployeeID int PRIMARY KEY,
    LastName nvarchar(20) NOT NULL,
    FirstName nvarchar(10) NOT NULL,
    Title nvarchar(30),
    TitleOfCourtesy nvarchar(25),
    BirthDate datetime,
    HireDate datetime,
    Address nvarchar(60),
    City nvarchar(15),
    Region nvarchar(15),
    PostalCode nvarchar(10),
    Country nvarchar(15),
    HomePhone nvarchar(24),
    Extension nvarchar(4),
    Photo image,
    Notes ntext,
    ReportsTo int,
    PhotoPath nvarchar(255)
);

CREATE TABLE Shippers (
    ShipperID int PRIMARY KEY,
    CompanyName nvarchar(40) NOT NULL,
    Phone nvarchar(24)
);

CREATE TABLE Suppliers (
    SupplierID int PRIMARY KEY,
    CompanyName nvarchar(40) NOT NULL,
    ContactName nvarchar(30),
    ContactTitle nvarchar(30),
    Address nvarchar(60),
    City nvarchar(15),
    Region nvarchar(15),
    PostalCode nvarchar(10),
    Country nvarchar(15),
    Phone nvarchar(24),
    Fax nvarchar(24),
    HomePage ntext
);

CREATE TABLE Orders (
    OrderID int PRIMARY KEY,
    CustomerID nchar(5) FOREIGN KEY REFERENCES Customers(CustomerID),
    EmployeeID int FOREIGN KEY REFERENCES Employees(EmployeeID),
    OrderDate datetime,
    RequiredDate datetime,
    ShippedDate datetime,
    ShipVia int FOREIGN KEY REFERENCES Shippers(ShipperID),
    Freight money,
    ShipName nvarchar(40),
    ShipAddress nvarchar(60),
    ShipCity nvarchar(15),
    ShipRegion nvarchar(15),
    ShipPostalCode nvarchar(10),
    ShipCountry nvarchar(15)
);

CREATE TABLE Products (
    ProductID int PRIMARY KEY,
    ProductName nvarchar(40) NOT NULL,
    SupplierID int FOREIGN KEY REFERENCES Suppliers(SupplierID),
    CategoryID int FOREIGN KEY REFERENCES Categories(CategoryID),
    QuantityPerUnit nvarchar(20),
    UnitPrice money,
    UnitsInStock smallint,
    UnitsOnOrder smallint,
    ReorderLevel smallint,
    Discontinued bit
);

CREATE TABLE OrderDetails (
    OrderID int FOREIGN KEY REFERENCES Orders(OrderID),
    ProductID int FOREIGN KEY REFERENCES Products(ProductID),
    UnitPrice money NOT NULL,
    Quantity smallint NOT NULL,
    Discount real NOT NULL,
    PRIMARY KEY (OrderID, ProductID)
);
