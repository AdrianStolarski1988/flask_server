1. install requirements
2. to run server run command:

python apiSerwer.py

server is running on http://127.0.0.1:5000/

Methods:
GET /api/solwit/all - return all results
POST /api/solwit/add - add record to database
GET /api/solwit/records?id=1 - return one result filtered by id
GET /api/solwit/records?email=test@wp.pl - return one result filtered by email
GET /api/solwit/records?phone=555444333 - return one result filtered by phone
DELETE /api/solwit/delete/1 - delete record with id=1
