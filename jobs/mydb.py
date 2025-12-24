import pymysql

dataBase = pymysql.connect(
	host = 'localhost',
	user = 'Amir',
	passwd = 'Azerty.619'
	)

# prepare a cursor object
cursorObject = dataBase.cursor()

# Create a database
cursorObject.execute("CREATE DATABASE jobs")

print("All Done!")