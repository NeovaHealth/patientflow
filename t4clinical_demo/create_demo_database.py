import erppeek

new_db = "demo_test2"
new_demo = False
rollback = True

user = "admin"
pwd = "admin"
#current_db = "test11"

 

client = erppeek.Client("http://localhost:8069", verbose=True)
client.create_database(pwd, new_db, new_demo, 'en_GB', pwd)
client.install('t4clinical_demo')
#client.execute('demo', 'scenario1', rollback)