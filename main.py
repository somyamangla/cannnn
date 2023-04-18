from flask import Flask, request, render_template,redirect, url_for,session,redirect,session
import mysql.connector
import os
import pickle 
import numpy as np
# Create flask app
flask_app = Flask(__name__)
#breastcancer
bmodel = pickle.load(open("breastmodel.pkl", "rb"))
#livercancer
livmodel = pickle.load(open("livermodel.pkl", "rb"))
#lungcancer
lungmodel = pickle.load(open("lungmodel.pkl", "rb"))
#cervicalcancer
cervmodel = pickle.load(open("cervicalmodel.pkl","rb"))


flask_app.secret_key=os.urandom(24)

conn=mysql.connector.connect( host='localhost',user='root',password='',database='user',port='3307')

#main website
@flask_app.route("/")
def index():
    return render_template('index.html')


@flask_app.route('/login')
def login():
    return render_template("login.html")


@flask_app.route("/signup")
def signup():
    return render_template("signup.html")

@flask_app.route("/login_validation",methods=['POST','GET'])
def login_validation():
    name=request.form.get('name')
    password = request.form.get('pass')
    cursor=conn.cursor()
    cursor.execute("""SELECT * FROM `patients` WHERE `NAME` LIKE '{}' AND `PASSWORD` LIKE '{}' """.format(name,password))
    users=cursor.fetchall()
    if len(users)>0:
        session['user_id']=users[0][0]
        return redirect('/getstarted')
    else:
        return redirect('/login')

#main website done
            #######################################################################
#after login
@flask_app.route("/getstarted")
def getstarted():
    if 'user_id' in session:
        return render_template("getstarted.html")
    else:
        return redirect("/login")
    
@flask_app.route("/profile" , methods = ['POST','GET'])
def profile():
    cursor=conn.cursor()
    if request.method =='POST':
        adduser = request.form 
        name = adduser['rname']
        email = adduser['remail']
        password = adduser['rpass']
        cursor.execute("INSERT INTO `patients` (EMAIL,NAME,PASSWORD) VALUES (%s,%s,%s)",(email,name,password))
        conn.commit()

        cursor.execute("""SELECT * FROM `patients` WHERE `EMAIL` LIKE '{}'""".format(email))
        user = cursor.fetchall()
        session['user_id'] = user[0][0]
        cursor.close()
        return redirect('/getstarted')


        
@flask_app.route('/breastcancer')
def breastcancer():
    return render_template("breastcancer.html")

@flask_app.route('/lungcancer')
def lungcancer():
    return render_template("lungcancer.html")

@flask_app.route('/livercancer')
def livercancer():
    return render_template("livercancer.html")

@flask_app.route('/cervicalcancer')
def cervicalcancer():
    return render_template("cervicalcancer.html")

                              ##breast model prediction##
@flask_app.route('/pred' , methods=['POST'])
def pred():
    float_features = [float(x) for x in request.form.values()]
    features = [np.array(float_features)]
    prediction = bmodel.predict(features)

    if prediction==1:
        return render_template("breastcancer.html", prediction_text = "There is chance of cancer")
    else:
        return render_template("breastcancer.html", prediction_text = "There is no chance of cancer")

                              #liver cancer prediction#

@flask_app.route ("/livpred", methods = ["POST"])
def predict():
    float_features = [float(x) for x in request.form.values()]
    features = [np.array(float_features)]
    prediction = livmodel.predict(features)

    if prediction==1:
        return render_template("livercancer.html", prediction_text = "Chance of cancer")
    else:
        return render_template("livercancer.html", prediction_text = "No chance of cancer")

                                  ###lungcancer##
@flask_app.route("/lungpredict", methods = ["POST"])
def lungpredict():
    float_features = [float(x) for x in request.form.values()]
    features = [np.array(float_features)]
    prediction = lungmodel.predict(features)
    if prediction==1:
       return render_template("lungcancer.html", prediction_text = "The Chances of Cancer is Medium")
    if prediction==0:
        return render_template("lungcancer.html", prediction_text = "The Chances of Cancer is Low")
    else:
        return render_template("lungcancer.html", prediction_text = "The Chances of Cancer is High")

                                     ##cervical cancer ###

@flask_app.route ("/cervpred", methods = ["POST"])
def cervpred():
    float_features = [float(x) for x in request.form.values()]
    features = [np.array(float_features)]
    prediction = cervmodel.predict(features)

    if prediction==1:
        return render_template("cervicalcancer.html", prediction_text = "there is chance of cancer")
    else:
        return render_template("cervicalcancer.html", prediction_text = "there is no chance of cancer")

@flask_app.route('/choice')
def choice():
    return render_template('choice.html')

@flask_app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect('/')

if __name__ == "__main__":
    flask_app.run(debug=True)