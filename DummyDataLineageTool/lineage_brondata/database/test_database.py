import sqlite3

conn = sqlite3.connect(
    "brondata.sqlite"
)

 # get all the tables in the database
tables = conn.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
""").fetchall()

# print all the tables in the database
print("Tables:", tables)

# get all the columns in the Customers table
customers = conn.execute(
    "SELECT * FROM Customers"
).fetchall()

for customer in customers:
    print(customer)

conn.close()