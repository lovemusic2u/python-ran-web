from flask import Blueprint, Flask, render_template, request, redirect, url_for
import pyodbc

time_point = Blueprint('time_point',__name__)

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

@time_point.route('/point_time', methods=['GET', 'POST'])
def index():
    message = None # Initialize message with a default value
    if request.method == 'POST':
        # Assuming you have a form or similar method to get user_id and playtime_to_exchange
        UserID = request.form.get('UserID')
        playtime_to_exchange = int(request.form.get('playtime_to_exchange'))

        with pyodbc.connect('DSN=' + 'RanUser') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT UserName, UserPoint, UserPoint2, PlayTime, UserSA FROM UserInfo WHERE UserID = ? and UserLoginState = 0', (UserID))
            rows = cursor.fetchall()

        if not rows:
            # Assuming you want to send a message back to the user, you might redirect to a page or return a message
            message = "User หรือ รหัสเข้าถึงตัวละคร ไม่ถูกต้อง หรือ User กำลัง Online อยู่ โปรดตรวจสอบให้แน่ใจ ก่อนนะเมี๊ยว"
        else:

            user_db = UserDatabase()
            row = user_db.fetch_data(f"SELECT PlayTime FROM UserInfo WHERE UserID = '{UserID}'")[0]

            if row[0] >= playtime_to_exchange:
                points_to_add = 5
                if playtime_to_exchange >= 600:
                    points_to_add = 10
                if playtime_to_exchange >= 900:
                    points_to_add = 15
                if playtime_to_exchange >= 1200:
                    points_to_add = 20
                if playtime_to_exchange >= 1500:
                    points_to_add = 25
                if playtime_to_exchange >= 1800:
                    points_to_add = 30
                if playtime_to_exchange >= 2100:
                    points_to_add = 35

                # Update the database to redeem PlayTime for UserPoints
                user_db.execute_query('UPDATE UserInfo SET UserPoint = UserPoint + ?, PlayTime = PlayTime - ? WHERE UserID = ?', (points_to_add, playtime_to_exchange, UserID,))

                # Assuming you want to send a message back to the user, you might redirect to a page or return a message
                message ="คุณท่านได้รับ {} Point จากการแลกเวลา Online คงเหลือ {} ชั่วโมง".format(points_to_add, row[0] - playtime_to_exchange)
                return render_template('point_time.html', message=message)
            else:
                message = "คุณท่านไม่มีเวลา Online ไม่พอสำหรับการแลก Point กิจกรรม ไปเล่นเกมให้เวลาเพียงพอก่อนนะเมี๊ยว"
                return render_template('point_time.html', message=message)
    else:
        # Render the form or initial page
        return render_template('point_time.html', message=message)
    
