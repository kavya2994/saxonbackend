import threading
from datetime import datetime, timedelta
import time
from ..models.member_view import MemberView
from ..models.employer_view import EmployerView
from ..models.users import Users


def scheduler(app):
    with app.app_context():
        i = 1
        x = datetime.today()
        y = x.replace(day=x.day, hour=19, minute=29, second=00, microsecond=0)
        while True:
            z = datetime.today()
            if i == 1:
                t = threading.Thread(target=create_users, args=(app, 0))
                t.start()
                t.join()
            if not i == 1:
                y = y + timedelta(days=1)
            delta_t = y - z
            secs = delta_t.total_seconds()
            print(secs)
            if not secs < 0:
                t = threading.Thread(target=create_users, args=(app, secs,))
                t.start()
                t.join()
                print(datetime.today())
            i += 1


def create_users(app, secs):
    print(secs)
    time.sleep(secs)
    with app.app_context():
        print("hello")
        # I need to get the data from MemberView and EmployerView and create all the member and employer accounts
        # into users table, i want to know whether this threading works
        # and first time when we run the flask
        # application ,it should create users and wait until 11pm everyday and execute this create_users() function
        # again the logic here would be as same as DevelopmentSeeder in /seeds/development.py i need to get data from views and
        # merge in Users table and any other information about conditional merge would be helpful example if account
        # exists i should not merge password, temppass and other things like displayname, phonenumber can be merged



