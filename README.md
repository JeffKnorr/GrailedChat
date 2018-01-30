# GrailedChat
/chat/v1/inbox/
Creates a very basic RESTful chat server instance.

ToDo:
Add Unit Tests
Add more documentation
Enhance functionality: Add message threads, other REST Methods, Modify for WSGi server use, Switch to PostgreSQL database backend, rewrite using a framework such as Flask to minimize code, Sterilize data input
Performance improvements: Optimizing Queries/Indexes, Logic improvements

Features:
-Versioning/Ease of adding new backend/Rest Methods
-SQLite database backend
-SQLAlchemy ORM
-Minimal depencies

Example Usage:
POST - http://127.0.0.1:8080/chat/v1/inbox/
JSON Body:
{
"fromUser": "John",
"toUser": "Jeff",
"messageBody": "I'll pick you up."
}

GET - http://127.0.0.1:8080/chat/v1/inbox/{userInbox}
Sample Result:
[{
"id": 7,
"timestamp": "2018-01-30 20:26:21.096307",
"fromUser": "John",
"toUser": "Jeff",
"messageBody": "This is a test."
}]

DELETE - ttp://127.0.0.1:8080/chat/v1/inbox/{messageID}
