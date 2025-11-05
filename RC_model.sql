-- SQL DDL generated from RC_model ER diagram
-- Tables: Manufacturer, Product, Inventory, Customer, Invoice, Line, Shipment

CREATE TABLE Manufacturer (
  manufacturer_id INTEGER PRIMARY KEY,
  manufacturer_name VARCHAR(150) NOT NULL,
  manufacturer_website VARCHAR(255)
);

CREATE TABLE Product (
  product_id VARCHAR(20) PRIMARY KEY,
  product_name VARCHAR(200) NOT NULL,
  model_type VARCHAR(100),
  model_price DECIMAL(10,2),
  decal VARCHAR(100),
  category VARCHAR(100),
  scale VARCHAR(50),
  manufacturer_id INTEGER,
  CONSTRAINT fk_product_manufacturer FOREIGN KEY (manufacturer_id) REFERENCES Manufacturer(manufacturer_id)
);

CREATE TABLE Inventory (
  product_id VARCHAR(20) PRIMARY KEY,
  qoh INTEGER,
  reorder_level INTEGER,
  CONSTRAINT fk_inventory_product FOREIGN KEY (product_id) REFERENCES Product(product_id)
);

CREATE TABLE Customer (
  customer_id INTEGER PRIMARY KEY,
  customer_name VARCHAR(200) NOT NULL,
  cust_address VARCHAR(300),
  cust_email VARCHAR(150),
  cust_phone VARCHAR(30)
);

CREATE TABLE Invoice (
  invoice_number VARCHAR(30) PRIMARY KEY,
  invoice_date DATE,
  customer_id INTEGER,
  order_id VARCHAR(50),
  total_amount DECIMAL(12,2),
  shipping_charge DECIMAL(10,2),
  invoice_status VARCHAR(50),
  CONSTRAINT fk_invoice_customer FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);

-- Line uses a composite primary key: (invoice_number, line_number)
CREATE TABLE Line (
  invoice_number VARCHAR(30) NOT NULL,
  line_number INTEGER NOT NULL,
  product_id VARCHAR(20),
  line_units INTEGER,
  unit_price DECIMAL(10,2),
  line_status VARCHAR(50),
  ship_date DATE,
  PRIMARY KEY (invoice_number, line_number),
  CONSTRAINT fk_line_invoice FOREIGN KEY (invoice_number) REFERENCES Invoice(invoice_number),
  CONSTRAINT fk_line_product FOREIGN KEY (product_id) REFERENCES Product(product_id)
);

CREATE TABLE Shipment (
  shipment_id INTEGER PRIMARY KEY,
  invoice_number VARCHAR(30),
  line_number INTEGER,
  ship_date DATE,
  tracking_no VARCHAR(100),
  shipment_status VARCHAR(50),
  qty_shipped INTEGER,
  CONSTRAINT fk_shipment_invoice FOREIGN KEY (invoice_number) REFERENCES Invoice(invoice_number),
  CONSTRAINT fk_shipment_line FOREIGN KEY (invoice_number, line_number) REFERENCES Line(invoice_number, line_number)
);

-- Indexes for faster lookups (optional)
CREATE INDEX idx_product_manufacturer ON Product(manufacturer_id);
CREATE INDEX idx_inventory_product ON Inventory(product_id);
CREATE INDEX idx_invoice_customer ON Invoice(customer_id);
CREATE INDEX idx_line_product ON Line(product_id);
CREATE INDEX idx_shipment_invoice ON Shipment(invoice_number);
