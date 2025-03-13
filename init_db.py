import sqlite3
from datetime import datetime
import os

def init_db():
    # Delete existing database if it exists
    if os.path.exists('store.db'):
        os.remove('store.db')

    # Create database connection
    conn = sqlite3.connect('store.db')
    conn.row_factory = sqlite3.Row  # Позволяет обращаться к столбцам по имени
    cursor = conn.cursor()

    # Create tables
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS ProductCategory (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Product (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            model TEXT NOT NULL,
            category_P_id INTEGER,
            brand_name TEXT,
            FOREIGN KEY (category_P_id) REFERENCES ProductCategory(category_id)
        );

        CREATE TABLE IF NOT EXISTS ProductOption (
            product_PO_id INTEGER,
            barcode_id TEXT PRIMARY KEY,
            quantity INTEGER NOT NULL,
            wholesale_price INTEGER NOT NULL, 
            sale_price INTEGER NOT NULL,        
            FOREIGN KEY (product_PO_id) REFERENCES Product(product_id)
        );

        CREATE TABLE IF NOT EXISTS ProductAttribute (
            barcode_PA_id TEXT,
            attribute_id INTEGER,
            attribute_name TEXT NOT NULL,
            attribute_value TEXT NOT NULL,
            PRIMARY KEY (barcode_PA_id, attribute_id),
            FOREIGN KEY (barcode_PA_id) REFERENCES ProductOption(barcode_id)
        );

        CREATE TABLE IF NOT EXISTS PriceHistory (
            barcode_PH_id TEXT,
            price_id INTEGER PRIMARY KEY AUTOINCREMENT,
            old_price INTEGER NOT NULL,  
            new_price INTEGER NOT NULL,  
            change_date DATETIME NOT NULL,
            FOREIGN KEY (barcode_PH_id) REFERENCES ProductOption(barcode_id)
        );

        CREATE TABLE IF NOT EXISTS Supplier (
            supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_name TEXT NOT NULL,
            phone_number TEXT,
            address TEXT
        );

        CREATE TABLE IF NOT EXISTS ProductSupplier (
            product_PS_id INTEGER,
            supplier_PS_id INTEGER,
            PRIMARY KEY (product_PS_id, supplier_PS_id),
            FOREIGN KEY (product_PS_id) REFERENCES Product(product_id),
            FOREIGN KEY (supplier_PS_id) REFERENCES Supplier(supplier_id)
        );

        CREATE TABLE IF NOT EXISTS PromoCode (
            code_id TEXT PRIMARY KEY,
            discount_percentage INTEGER NOT NULL,  
            valid_from DATE NOT NULL,
            valid_to DATE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Sale (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_date DATETIME NOT NULL,
            source_name INTEGER,
            code_S_id TEXT,
            tax_rate INTEGER, 
            total_price_without_vat INTEGER NOT NULL, 
            vat_paid INTEGER NOT NULL,                 
            total_price_with_vat INTEGER NOT NULL,     
            FOREIGN KEY (code_S_id) REFERENCES PromoCode(code_id)
        );

        CREATE TABLE IF NOT EXISTS SaleItem (
            sale_SI_id INTEGER,
            sale_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode_SI_id TEXT NOT NULL,
            quantity_sold INTEGER NOT NULL,
            price_sold_without_vat INTEGER NOT NULL, 
            FOREIGN KEY (sale_SI_id) REFERENCES Sale(sale_id),
            FOREIGN KEY (barcode_SI_id) REFERENCES ProductOption(barcode_id)
        );
    ''')

    # Insert categories
    categories = [
        ('Smartphones',),
        ('Laptops',),
        ('Tablets',),
        ('Smartwatches',),
        ('Accessories',)
    ]
    cursor.executemany('INSERT INTO ProductCategory (category_name) VALUES (?)', categories)

    # Insert suppliers
    suppliers = [
        ('TechGlobal Inc.', '+1-555-0123', '123 Tech Street, Silicon Valley, CA'),
        ('Global Electronics', '+1-555-0124', '456 Electronics Ave, New York, NY'),
        ('Digital Solutions', '+1-555-0125', '789 Digital Road, Seattle, WA'),
        ('Smart Devices Co.', '+1-555-0126', '321 Smart Blvd, Austin, TX'),
        ('Future Tech Ltd.', '+1-555-0127', '654 Future Lane, Boston, MA')
    ]
    cursor.executemany('INSERT INTO Supplier (supplier_name, phone_number, address) VALUES (?, ?, ?)', suppliers)

    # Insert promo codes
    promo_codes = [
        ('SUMMER2024', 15, '2024-06-01', '2024-08-31'),
        ('WELCOME10', 10, '2024-01-01', '2024-12-31'),
        ('BLACKFRIDAY', 20, '2024-11-29', '2024-11-30')
    ]
    cursor.executemany('INSERT INTO PromoCode (code_id, discount_percentage, valid_from, valid_to) VALUES (?, ?, ?, ?)', promo_codes)

    # Insert products and their options
    products_data = [
        # Apple products
        ('iPhone 15 Pro', 1, 'Apple', 'APP15P-256', 50, 80000, 99900),
        ('iPhone 15', 1, 'Apple', 'APP15-128', 75, 60000, 79900),
        ('MacBook Pro 16', 2, 'Apple', 'APP-MBP16', 30, 150000, 199900),
        ('iPad Pro 12.9', 3, 'Apple', 'APP-IPAD12', 40, 80000, 99900),
        ('Apple Watch Series 9', 4, 'Apple', 'APP-WATCH9', 60, 30000, 39900),
        
        # Samsung products
        ('Galaxy S24 Ultra', 1, 'Samsung', 'SAM-S24U', 45, 70000, 89900),
        ('Galaxy Book 4', 2, 'Samsung', 'SAM-BOOK4', 35, 120000, 149900),
        ('Galaxy Tab S9', 3, 'Samsung', 'SAM-TABS9', 50, 60000, 79900),
        ('Galaxy Watch 6', 4, 'Samsung', 'SAM-WATCH6', 55, 25000, 29900),
        ('Galaxy Buds Pro', 5, 'Samsung', 'SAM-BUDSP', 80, 15000, 19900),
        
        # Sony products
        ('Xperia 1 V', 1, 'Sony', 'SON-XP1V', 40, 75000, 94900),
        ('VAIO SX14', 2, 'Sony', 'SON-VAIO14', 25, 130000, 169900),
        ('Xperia Tablet Z4', 3, 'Sony', 'SON-TABZ4', 30, 70000, 89900),
        ('WH-1000XM5', 5, 'Sony', 'SON-WH1000', 65, 20000, 29900),
        ('WF-1000XM5', 5, 'Sony', 'SON-WF1000', 70, 15000, 19900),
        
        # Dell products
        ('XPS 15', 2, 'Dell', 'DEL-XPS15', 40, 140000, 179900),
        ('Alienware m18', 2, 'Dell', 'DEL-ALIEN18', 25, 180000, 229900),
        ('Latitude 7440', 2, 'Dell', 'DEL-LAT7440', 35, 110000, 139900),
        ('Dell XPS 13', 2, 'Dell', 'DEL-XPS13', 45, 90000, 119900),
        ('Dell Inspiron 16', 2, 'Dell', 'DEL-INS16', 50, 70000, 89900),
        
        # Lenovo products
        ('ThinkPad X1 Carbon', 2, 'Lenovo', 'LEN-X1C', 40, 120000, 149900),
        ('Yoga 9i', 2, 'Lenovo', 'LEN-YOGA9', 35, 100000, 129900),
        ('Tab P12 Pro', 3, 'Lenovo', 'LEN-TABP12', 45, 65000, 84900),
        ('ThinkPad X13', 2, 'Lenovo', 'LEN-X13', 55, 85000, 109900),
        ('IdeaPad 5', 2, 'Lenovo', 'LEN-IDEA5', 60, 60000, 79900)
    ]

    # Insert products and their options
    for product in products_data:
        cursor.execute('''
            INSERT INTO Product (model, category_P_id, brand_name)
            VALUES (?, ?, ?)
        ''', (product[0], product[1], product[2]))
        
        product_id = cursor.lastrowid
        
        cursor.execute('''
            INSERT INTO ProductOption (product_PO_id, barcode_id, quantity, wholesale_price, sale_price)
            VALUES (?, ?, ?, ?, ?)
        ''', (product_id, product[3], product[4], product[5], product[6]))

        # Add some attributes for each product
        cursor.execute('''
            INSERT INTO ProductAttribute (barcode_PA_id, attribute_id, attribute_name, attribute_value)
            VALUES (?, ?, ?, ?)
        ''', (product[3], 1, 'Color', 'Black'))

        # Add price history
        cursor.execute('''
            INSERT INTO PriceHistory (barcode_PH_id, old_price, new_price, change_date)
            VALUES (?, ?, ?, datetime('now'))
        ''', (product[3], product[5], product[6]))

        # Link product to supplier
        cursor.execute('''
            INSERT INTO ProductSupplier (product_PS_id, supplier_PS_id)
            VALUES (?, ?)
        ''', (product_id, (product_id % 5) + 1))

    # Insert some sales
    sales = [
        (datetime.now(), 1, 'SUMMER2024', 20, 100000, 20000, 120000),
        (datetime.now(), 2, 'WELCOME10', 20, 150000, 30000, 180000),
        (datetime.now(), 3, None, 20, 80000, 16000, 96000)
    ]
    
    # Sample products to add sales for
    sale_items_data = [
        ('APP15P-256', 3, 99900),    # iPhone 15 Pro
        ('SAM-S24U', 2, 89900),      # Galaxy S24 Ultra
        ('APP-MBP16', 1, 199900),    # MacBook Pro 16
        ('DEL-XPS15', 2, 179900),    # Dell XPS 15
        ('LEN-X1C', 1, 149900),      # ThinkPad X1 Carbon
        ('SON-XP1V', 2, 94900),      # Sony Xperia 1 V
        ('APP-IPAD12', 2, 99900),    # iPad Pro 12.9
        ('SAM-TABS9', 3, 79900),     # Galaxy Tab S9
        ('APP-WATCH9', 4, 39900),    # Apple Watch Series 9
        ('SAM-WATCH6', 3, 29900),    # Galaxy Watch 6
        ('SAM-BUDSP', 4, 19900),     # Galaxy Buds Pro
        ('SON-WH1000', 5, 29900),    # Sony WH-1000XM5
        ('SON-WF1000', 5, 19900)     # Sony WF-1000XM5
    ]
    
    for sale in sales:
        cursor.execute('''
            INSERT INTO Sale (sale_date, source_name, code_S_id, tax_rate, 
                            total_price_without_vat, vat_paid, total_price_with_vat)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', sale)
        
        sale_id = cursor.lastrowid
        
        # Add multiple sale items for each sale
        for barcode, quantity, price in sale_items_data:
            cursor.execute('''
                INSERT INTO SaleItem (sale_SI_id, barcode_SI_id, quantity_sold, price_sold_without_vat)
                VALUES (?, ?, ?, ?)
            ''', (sale_id, barcode, quantity, price))

    # Commit all changes
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully!")
