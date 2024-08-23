from flask import Blueprint,Flask, render_template, request, redirect, url_for
import pyodbc

shop = Blueprint('shop',__name__)

# Connection string to your ODBC data source
# Replace 'DSN_name' with the name of your ODBC data source
# If you have username and password, add them as well
connection_string = 'DSN=RanShop'

def fetch_data(query):
    try:
        # Establish connection
        connection = pyodbc.connect(connection_string)

        # Cursor object creation
        cursor = connection.cursor()

        # Execute the query
        cursor.execute(query)

        # Fetch results
        rows = cursor.fetchall()

        # Close cursor and connection
        cursor.close()
        connection.close()

        return rows

    except pyodbc.Error as e:
        return None

def execute_query(query):
    try:
        # Establish connection
        connection = pyodbc.connect(connection_string)

        # Cursor object creation
        cursor = connection.cursor()

        # Execute the query
        cursor.execute(query)

        # Commit changes
        connection.commit()

        # Close cursor and connection
        cursor.close()
        connection.close()

        return True

    except pyodbc.Error as e:
        return False
    
@shop.route('/')
def index():
    try:
        # Establish connection
        connection = pyodbc.connect(connection_string)

        # Cursor object creation
        cursor = connection.cursor()

        # Example: Execute a query to fetch data
        cursor.execute("SELECT * FROM ShopItemMap")

        # Fetch results
        rows = cursor.fetchall()

        # Close cursor and connection
        cursor.close()
        connection.close()

        # Pass the fetched data to the template
        return render_template('index.html', data=rows)

    except pyodbc.Error as e:
        return "Error: {}".format(e)
    
@shop.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    search_query = "SELECT * FROM ShopItemMap WHERE ItemName LIKE '%{}%'".format(query)
    search_results = fetch_data(search_query)
    return render_template('search_results.html', query=query, results=search_results)

@shop.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
    # Retrieve data from the form
        data = {
            'ItemMain': request.form.get('ItemMain'),
            'ItemSub': request.form.get('ItemSub'),
            'ItemName': request.form.get('ItemName'),
            'ItemSec': request.form.get('ItemSec'),
            'ItemPrice': request.form.get('ItemPrice'),
            'Itemstock': request.form.get('Itemstock'),
            'ItemCtg': request.form.get('ItemCtg'),
            'isHide': request.form.get('isHide')
        }

        # Construct the INSERT query
        insert_query = "INSERT INTO ShopItemMap (ItemMain, ItemSub, ItemName, ItemSec, ItemPrice, Itemstock, ItemCtg, isHide) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
            data['ItemMain'], data['ItemSub'], data['ItemName'], data['ItemSec'], data['ItemPrice'], data['Itemstock'], data['ItemCtg'], data['isHide'])

        # Execute the INSERT query
        success = execute_query(insert_query)

        if success:
            return redirect(url_for('shop.add'))  # Redirect to the index page
        else:
            return "Failed to add data"  # Display an error message
    else:
        select_query = "SELECT * FROM ShopItemMap ORDER BY ProductNum DESC"
        existing_data = fetch_data(select_query)

        if existing_data is not None:
            return render_template('add_item_shop.html', data=existing_data)
        else:
            return "Failed to fetch existing data"

@shop.route('/edit_index')
def edit_index():
    try:
        # Establish connection
        connection = pyodbc.connect(connection_string)

        # Cursor object creation
        cursor = connection.cursor()

        # Example: Execute a query to fetch data
        cursor.execute("SELECT * FROM ShopItemMap")

        # Fetch results
        rows = cursor.fetchall()

        # Close cursor and connection
        cursor.close()
        connection.close()

        # Pass the fetched data to the template
        return render_template('edit_index.html', data=rows)

    except pyodbc.Error as e:
        return "Error: {}".format(e)
    


@shop.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit(item_id):
    if request.method == 'POST':
        # Retrieve data from the form
        data = {
            'ItemMain': request.form.get('ItemMain'),
            'ItemSub': request.form.get('ItemSub'),
            'ItemName': request.form.get('ItemName'),
            'ItemSec': request.form.get('ItemSec'),
            'ItemPrice': request.form.get('ItemPrice'),
            'Itemstock': request.form.get('Itemstock'),
            'ItemCtg': request.form.get('ItemCtg'),
            'isHide': request.form.get('isHide')
        }

        # Construct the UPDATE query
        update_query = "UPDATE ShopItemMap SET ItemMain = '{}', ItemSub = '{}', ItemName = '{}', ItemSec = '{}', ItemPrice = '{}', Itemstock = '{}', ItemCtg = '{}', isHide = '{}' WHERE ProductNum = {}".format(
            data['ItemMain'], data['ItemSub'], data['ItemName'], data['ItemSec'], data['ItemPrice'], data['Itemstock'], data['ItemCtg'], data['isHide'], item_id)

        # Execute the UPDATE query
        success = execute_query(update_query)

        if success:
            return redirect(url_for('shop.edit_index')) # Redirect to the index page
        else:
            return "Failed to update data" # Display an error message
    else:
        # Fetch the item data for editing
        select_query = "SELECT * FROM ShopItemMap WHERE ProductNum = {}".format(item_id)
        item_data = fetch_data(select_query)

        if item_data:
            return render_template('edit_item.html', item=item_data[0])
        else:
            return "Item not found"



