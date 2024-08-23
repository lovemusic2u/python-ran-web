from flask import Blueprint,Flask, render_template, request, redirect, url_for
import pyodbc

point = Blueprint('point',__name__)

# Connection string to your ODBC data source
# Replace 'DSN_name' with the name of your ODBC data source
# If you have username and password, add them as well

class Database:
    def __init__(self, connection_string):
        self.connection_string = connection_string

    def connect(self):
        return pyodbc.connect(self.connection_string)

    def fetch_data(self, query):
        connection = self.connect()
        cursor = connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        connection.close()
        return rows

    def execute_query(self, query):
        connection = self.connect()
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        connection.close()
        return True

class UserDatabase(Database):
    def __init__(self):
        super().__init__('DSN=RanUser')
    def fetch_data(self, query):
        connection = self.connect()
        cursor = connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        connection.close() # Close the connection here
        return rows

    def execute_query(self, query, params=None):
        connection = self.connect()
        cursor = connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        connection.commit()
        cursor.close()
        connection.close()
        return True

class GameDatabase(Database):
    def __init__(self):
        super().__init__('DSN=RanGame1')

@point.route('/point')
def index():
    try:
        # Establish connection
        user_db = UserDatabase()

        sort_param = request.args.get('sort', 'tab1.ChaOnline')
        sort_order = request.args.get('order', 'DESC') # Default to descending

        query = f"""
        SELECT TOP 100 tab1.ChaNum, tab1.UserNum, tab2.UserName, tab1.ChaName, tab1.ChaLevel, tab1.ChaGuName, tab1.ChaMoney, tab2.UserPoint, tab2.UserPoint2, tab1.ChaOnline,tab2.UserLoginState, tab2.PlayTime
        FROM [RanGame1].[dbo].[ChaInfo] tab1
        LEFT JOIN [RanUser].[dbo].[UserInfo] tab2 ON tab1.UserNum = tab2.UserNum
        ORDER BY {sort_param} {sort_order}
        """
        user_data = user_db.fetch_data(query)

        # Format ChaMoney with commas as thousand separators using f-string
        formatted_data = []
        for row in user_data:
            formatted_row = list(row)
            formatted_row[6] = f"{int(formatted_row[6]):,}" # Format ChaMoney
            formatted_data.append(tuple(formatted_row))
        

        # Pass the fetched data to the template
        return render_template('point_index.html', data=formatted_data)

    except pyodbc.Error as e:
        return "Error: {}".format(e)

@point.route('/point_search', methods=['POST'])
def search():

    search_term = request.form.get('querys')
    try:
        # Establish connection
        user_db = UserDatabase()

        # Retrieve the search term from the request form data
        search_term = request.form.get('querys')

        query = """
        SELECT TOP 100 tab1.ChaNum, tab1.UserNum, tab2.UserName, tab1.ChaName, tab1.ChaLevel, tab1.ChaGuName, tab1.ChaMoney, tab2.UserPoint, tab2.UserPoint2, tab1.ChaOnline,tab2.UserLoginState, tab2.PlayTime
        FROM [RanGame1].[dbo].[ChaInfo] tab1
        LEFT JOIN [RanUser].[dbo].[UserInfo] tab2 ON tab1.UserNum = tab2.UserNum
        WHERE tab1.ChaName LIKE '%{}%'
        ORDER BY tab2.UserPoint DESC
        """.format(search_term)

        user_data = user_db.fetch_data(query)

        # Format ChaMoney with commas as thousand separators using f-string
        formatted_data = []
        for row in user_data:
            formatted_row = list(row)
            formatted_row[6] = f"{int(formatted_row[6]):,}" # Format ChaMoney
            formatted_data.append(tuple(formatted_row))

        # Pass the fetched data to the template
        return render_template('point_search.html', query=query, results=formatted_data,search_term=search_term)


    except pyodbc.Error as e:
        return "Error: {}".format(e)
    
@point.route('/update_data/<int:chanum>', methods=['POST'])
def update_data(chanum):
    # Retrieve data from the form
    cha_name = request.form.get('ChaName')
    user_point = request.form.get('UserPoint')
    user_point2 = request.form.get('UserPoint2')
    play_time = request.form.get('PlayTime')

    try:
        user_db = UserDatabase()
        # Construct the UPDATE query
        query1 = """
        UPDATE [RanGame1].[dbo].[ChaInfo]
        SET ChaName = ?
        WHERE ChaNum = ?
        """
        query2 = """
        UPDATE [RanUser].[dbo].[UserInfo]
        SET UserPoint = ?, UserPoint2 = ?, PlayTime = ?
        WHERE UserNum IN (
            SELECT UserNum FROM [RanGame1].[dbo].[ChaInfo] WHERE ChaNum = ?
        )
        """
        # Execute the queries
        user_db.execute_query(query1, (cha_name, chanum))
        user_db.execute_query(query2, (user_point, user_point2, play_time, chanum))

        # Redirect to the search page or display a success message
        return redirect(url_for('point.index'))
    except pyodbc.Error as e:
        return "Error: {}".format(e)
    
@point.route('/point_add', methods=['GET', 'POST'])
def point_add():
    if request.method == 'POST':
        # Retrieve data from the form
        user_name = request.form.get('UserName')
        user_point = request.form.get('UserPoint')
        user_point2 = request.form.get('UserPoint2')

        # Construct the UPDATE query
        query = """
        UPDATE [RanUser].[dbo].[UserInfo]
        SET UserPoint = UserPoint + ?, UserPoint2 = UserPoint2 + ?
        WHERE UserName = ?
        """
        # Execute the query
        user_db = UserDatabase()
        user_db.execute_query(query, (user_point, user_point2, user_name))

        # Redirect to the search page or display a success message
        return redirect(url_for('point.index'))
    else:
        # Render the form for adding points
        return render_template('point_add.html')

    


