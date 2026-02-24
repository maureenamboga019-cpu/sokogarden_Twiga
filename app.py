# import flask
from flask import * 
import pymysql
import pymysql.cursors
from flask_cors import CORS
import os #allows the python code to communicate with the os
# create flask application
app= Flask(__name__)
CORS(app)
# configure the upload folder
app.config ['UPLOAD_FOLDER'] = 'static/images'

# route for signup 
@app.route('/api/signup' ,methods=['POST']) #the route/endpoint
def signup(): #the function
# extract values posted by the user and store in variables.
# names in brackets should be same to those in the database.
   username = request.form['username']
   email = request.form['email']
   password = request.form['password']
   phone = request.form['phone']
# Connection to database to connect the info to data base use pymysql so it is also imported
   connection = pymysql.connect(host='localhost',user='root',password='',database='dailyyoughurts_twiga')
#    create a cursor to initialise the connection
   cursor = connection.cursor()
#    write a sql query
   sql ='insert into users(username,email,password,phone) values(%s,%s,%s,%s)'
#    prepare data to replace the placeholders
   data = (username,email,password,phone)
#    execute the sql and the data using the cursor
   cursor.execute(sql,data)
#    commit/save changes to the database
   connection.commit()
   return jsonify ({'success':'thanks for joining'}) #the dictionary 

# new route for sign in
@app.route ('/api/signin',methods =['POST'])
def signin():
   username = request.form ['username']
   password = request.form ['password']
   # create a connection to the database
   connection = pymysql.connect (host ='localhost',user ='root',password = '',database='dailyyoughurts_twiga')
   # create a cursor(go)
   cursor = connection.cursor(pymysql.cursors.DictCursor)
   # create a sql query(select bcoz you are signing in and it is a confirmation)
   sql= 'select* from users where username = %s and password= %s' #because of and both conditions should be true
   # create data to replace the placeholders
   data = (username,password)
   # create a cursor to execute the sql query and the data
   cursor.execute(sql,data)
   # dont commit changes to the data base
   # have the variable count to check if the cursor has returned any count /row
   count = cursor.rowcount
   # have the if ..else statement
   if count == 0:    #0 rows == invalid credentials
      return jsonify({'message':'login failed'})
   else : #cursor has retrned at least a row
      user = cursor.fetchone ()
      user.pop('password',None)
      return jsonify({'message':'login successful','user':user})
   
   # route for adding a product
@app.route('/api/add_product')
def add_product():
      # extract values from the database
      product_name = request.form ['product_name']
      product_description = request.form ['product_description']
      product_cost = request.form ['product_cost']
      photo = request.files ['product_photo']  #we use a diff variable for clarity
      # keys in square brackets should be same to those in the database
      # get the image filename
      filename = photo.filename
      # specify where the image will be saved (path) (import os first then configure the upload folder)
      photo_path = os.path.join(app.config['UPLOAD_FOLDER'],filename)
      # save your images in the path specified above
      photo.save(photo_path)
      # connect to the database
      connection = pymysql.connect (host='localhost',user='root',password='',database='dailyyoughurts_twiga')
      # create a cursor to execute the command
      cursor = connection.cursor()
      # create a sql query
      sql='insert into product_details(product_name,product_description,product_cost,product_photo) values(%s,%s,%s,%s)'
      # prepare data to replace the placeholders
      data = (product_name,product_description,product_cost,filename)
     # create a cursor to execute changes
      cursor.execute(sql,data)
     # commit changes
      connection.commit()
      return jsonify({'message': 'product added'})
# route for getting products-dont extract data from database besause the user is no inputing any data
@app.route('/api/get_product_details')
def get_product_details ():
   # connect to database
   connection = pymysql.connect(user='root',host='localhost',password='',database='dailyyoughurts_twiga')
   cursor=connection.cursor(pymysql.cursors.DictCursor)
   # sql query
   sql='select* from product_details'
   # execute sql alone
   cursor.execute (sql)
   # get products in dictionary format fetchall-to get all
   product_details = cursor.fetchall()
   return jsonify(product_details)
# route for mpesa payment
 # Mpesa Payment Route 
import requests
import datetime
import base64  #encrypts text
from requests.auth import HTTPBasicAuth  #used for importing authentication

@app.route('/api/mpesa_payment', methods=['POST'])
def mpesa_payment():
        if request.method == 'POST':
            # Extract POST Values sent
            amount = request.form['amount']
            phone = request.form['phone']

            # Provide consumer_key and consumer_secret provided by safaricom
            consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
            consumer_secret = "amFbAoUByPV2rM5A"

            # Authenticate Yourself using above credentials to Safaricom Services, and Bearer Token this is used by safaricom for security identification purposes -
            #  Your are given Access
            api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"  # AUTH URL
            # Provide your consumer_key and consumer_secret 
            response = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
            # Get response as Dictionary
            data = response.json()
            # Retrieve the Provide Token
            # Token allows you to proceed with the transaction
            access_token = "Bearer" + ' ' + data['access_token']

            #  GETTING THE PASSWORD
            timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')  # Current Time
            passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'  # Passkey(Safaricom Provided)
            business_short_code = "174379"  # Test Paybile (Safaricom Provided)
            # Combine above 3 Strings to get data variable
            data = business_short_code + passkey + timestamp
            # Encode to Base64 for security
            encoded = base64.b64encode(data.encode())
            #you decode for you to be able to see the password
            password = encoded.decode()

            # BODY OR PAYLOAD
            payload = {
                "BusinessShortCode": "174379",
                "Password":password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": "1",  # use 1 when testing .when not testing use the amount variable
                "PartyA": phone,  # change to your number
                "PartyB": "174379",
                "PhoneNumber": phone,
                "CallBackURL": "https://coding.co.ke/api/confirm.php", #to know who has paid
                "AccountReference": "SokoGarden Online", #what you are paying for
                "TransactionDesc": "Payments for Products" #description of what you are paying fpr
            }

            # POPULAING THE HTTP HEADER, PROVIDE THE TOKEN ISSUED EARLIER
            headers = {
                "Authorization": access_token,
                "Content-Type": "application/json"
            }

            # Specify STK Push  Trigger URL
            url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"  
            # Create a POST Request to above url, providing headers, payload 
            # Below triggers an STK Push to the phone number indicated in the payload and the amount.
            response = requests.post(url, json=payload, headers=headers)
            print(response.text) # 
            # Give a Response
            return jsonify({"message": "An MPESA Prompt has been sent to Your Phone, Please Check & Complete Payment"})

if __name__ == '__main__':
   app.run(debug=True)
#    nothing is written here-
