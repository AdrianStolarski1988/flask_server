1. install requirements
2. to run server run command:

python FlaskApp.py

server is running on http://127.0.0.1:5000/

Methods:
GET flask/all - return all results
POST flask/add - add record to database
GET flask/records/?id=1 - return one result filtered by id
GET flask/records/?email=test@wp.pl - return one result filtered by email
GET flask/records?phone=555444333 - return one result filtered by phone
DELETE flask/delete/1 - delete record with id=1
