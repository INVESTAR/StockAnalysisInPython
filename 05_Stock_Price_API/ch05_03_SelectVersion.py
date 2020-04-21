import pymysql

connection = pymysql.connect(host='localhost', port=3306, db='INVESTAR', 
    user='root', passwd='myPa$$word', autocommit=True)  

cursor = connection.cursor()
cursor.execute("SELECT VERSION();")
result = cursor.fetchone()

print ("MariaDB version : {}".format(result))

connection.close()