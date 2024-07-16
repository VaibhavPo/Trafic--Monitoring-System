import firebase_admin
from firebase_admin import credentials,db

#Use the path to your .json file got from firebase
cred =credentials.Certificate('')


firebase_admin.initialize_app(
    cred,{
        'databaseURL':'https://trafficcngestion-default-rtdb.firebaseio.com/'
    }
)

ref = db.reference('/')
def update_data(data):
  # data = {'users':{'user1':{'name' :'Vai', 'age':'12'}}}
  ref.set(data)
  print('Updated database')