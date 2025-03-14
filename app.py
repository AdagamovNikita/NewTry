from flask import Flask, render_template, jsonify, request, redirect, url_for
import sqlite3

#write a big comment here that I used lectures as a reference for code style

app = Flask(__name__)
def get_db_connection():
    try:
        conn = sqlite3.connect('store.db')
        conn.row_factory = sqlite3.Row #write comment here
        return conn
    except Exception as e:
        print(f"Error: {e}")
        return None


#add a comment before each route that explains what it does on the website
@app.route('/')
def index():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Sorry, there is a server problem :("})
        brands = conn.execute('SELECT DISTINCT brand_name FROM Product ORDER BY brand_name').fetchall()  
        return render_template('index.html', brands=brands)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Sorry, there is a server problem :("})
    finally:
        if conn:
            conn.close()



@app.route('/search_brand', methods=['POST'])
def search_brand():
    try:
        brand = request.form.get('brand')
        if not brand:
            return redirect(url_for('index')) #write comment here
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Sorry, there is a server problem :("})
        results = conn.execute('''
            SELECT 
                p.brand_name AS Brand,
                p.model AS Model,
                pa.attribute_name AS AttributeName,
                pa.attribute_value AS AttributeValue,
                po.quantity AS Quantity,
                po.wholesale_price AS WholesalePrice,
                po.sale_price AS SalePrice,
                ph.new_price AS NewPrice,
                ph.change_date AS ChangeDate,
                pc.code_id AS PromoCode
            FROM 
                Product p
            JOIN 
                ProductOption po ON p.product_id = po.product_PO_id
            LEFT JOIN 
                ProductAttribute pa ON po.barcode_id = pa.barcode_PA_id
            LEFT JOIN 
                PriceHistory ph ON po.barcode_id = ph.barcode_PH_id
            LEFT JOIN
                SaleItem si ON po.barcode_id = si.barcode_SI_id
            LEFT JOIN 
                Sale s ON si.sale_SI_id = s.sale_id
            LEFT JOIN 
                PromoCode pc ON s.code_S_id = pc.code_id
            WHERE p.brand_name = ?
            ORDER BY 
                p.brand_name, p.model
        ''', (brand,)).fetchall()
        return render_template('search_results.html', results=results, brand=brand)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Sorry, there is a server problem :("})
    finally:
        if conn:
            conn.close()



@app.route('/api/top_products')
def top_products():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Sorry, there is a server problem :("})
        products = conn.execute('''
            SELECT 
                p.brand_name AS Brand,
                p.model AS Model,
                SUM(si.quantity_sold) AS TotalQuantitySold
            FROM 
                SaleItem si
            JOIN 
                ProductOption po ON si.barcode_SI_id = po.barcode_id
            JOIN 
                Product p ON po.product_PO_id = p.product_id
            GROUP BY 
                p.product_id, p.brand_name, p.model
            ORDER BY 
                TotalQuantitySold DESC
            LIMIT 5
        ''').fetchall()
        profit = conn.execute('''
            SELECT 
                SUM((po.sale_price - po.wholesale_price) * si.quantity_sold) AS profit
            FROM 
                SaleItem si
            JOIN 
                ProductOption po ON si.barcode_SI_id = po.barcode_id
        ''').fetchone()
        return jsonify({
            'products': [dict(row) for row in products],
            'profit': profit['profit'] / 100  # Convert cents to dollars
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Sorry, there is a server problem :("})
    finally:
        if conn:
            conn.close()



@app.route('/api/top_categories')
def top_categories():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Sorry, there is a server problem :("})
        categories = conn.execute('''
            SELECT 
                pc.category_name AS Category,
                COUNT(DISTINCT p.product_id) AS NumberOfProducts,
                SUM(si.quantity_sold) AS TotalQuantitySold
            FROM 
                ProductCategory pc
            JOIN 
                Product p ON pc.category_id = p.category_P_id
            JOIN 
                ProductOption po ON p.product_id = po.product_PO_id
            JOIN 
                SaleItem si ON po.barcode_id = si.barcode_SI_id
            GROUP BY 
                pc.category_id, pc.category_name
            ORDER BY 
                TotalQuantitySold DESC
            LIMIT 5
        ''').fetchall()
        revenue = conn.execute('''
            SELECT 
                SUM(po.sale_price * si.quantity_sold) AS revenue
            FROM 
                SaleItem si
            JOIN 
                ProductOption po ON si.barcode_SI_id = po.barcode_id
        ''').fetchone()
        return jsonify({
            'categories': [dict(row) for row in categories],
            'revenue': revenue['revenue'] / 100  # Convert cents to dollars
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Sorry, there is a server problem :("})
    finally:
        if conn:
            conn.close()



@app.route('/api/product_details')
def product_details():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Sorry, there is a server problem :("})
        products = conn.execute('''
            SELECT 
                p.brand_name AS Brand,
                p.model AS Model,
                po.sale_price AS SalePrice,
                SUM(si.quantity_sold) AS TotalQuantitySold,
                ((po.sale_price - po.wholesale_price) * 100.0 / po.sale_price) AS MarginPercentage,
                s.supplier_name AS SupplierName,
                s.phone_number AS Phone,
                s.address AS Address
            FROM 
                SaleItem si
            JOIN 
                ProductOption po ON si.barcode_SI_id = po.barcode_id
            JOIN 
                Product p ON po.product_PO_id = p.product_id
            JOIN 
                ProductSupplier ps ON p.product_id = ps.product_PS_id
            JOIN 
                Supplier s ON ps.supplier_PS_id = s.supplier_id
            GROUP BY 
                p.product_id
            ORDER BY 
                TotalQuantitySold DESC
        ''').fetchall()
        return jsonify([dict(row) for row in products]) #write comment here
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Sorry, there is a server problem :("})
    finally:
        if conn:
            conn.close()



@app.route('/api/category_details')
def category_details():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Sorry, there is a server problem :("})
        categories = conn.execute('''
            SELECT 
                pc.category_name AS Category,
                COUNT(DISTINCT p.product_id) AS NumberOfProducts,
                SUM(si.quantity_sold) AS TotalQuantitySold,
                AVG(po.sale_price) AS AverageProductPrice,
                MAX(po.sale_price) AS MaximumProductPrice,
                SUM(si.price_sold_without_vat) AS TotalRevenue
            FROM 
                ProductCategory pc
            JOIN 
                Product p ON pc.category_id = p.category_P_id
            JOIN 
                ProductOption po ON p.product_id = po.product_PO_id
            JOIN 
                SaleItem si ON po.barcode_id = si.barcode_SI_id
            GROUP BY 
                pc.category_id, pc.category_name
            ORDER BY 
                TotalRevenue DESC
        ''').fetchall()
        return jsonify([dict(row) for row in categories])
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Sorry, there is a server problem :("})
    finally:
        if conn:
            conn.close()



if __name__ == '__main__':
    app.run(debug=True) 