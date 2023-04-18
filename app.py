from flask import Flask, request, render_template,redirect, url_for,session,redirect,session,g
import mysql.connector
import os
import pickle 
import numpy as np
import mysql.connector.errors
# Create flask app
flask_app = Flask(__name__)
            ###############################MODELS######################################
#breastcancer
bmodel = pickle.load(open("breastmodel.pkl", "rb"))
#livercancer
livmodel = pickle.load(open("livermodel.pkl", "rb"))
#lungcancer
lungmodel = pickle.load(open("lungmodel.pkl", "rb"))
#cervicalcancer
cervmodel = pickle.load(open("cervicalmodel.pkl","rb"))


flask_app.secret_key=os.urandom(24)

conn=mysql.connector.connect( host='localhost',user='root',password='',database='user',port='3307',consume_results=True)

                ####################MAIN WEBSITE###########################
@flask_app.route("/")
def index():
    return render_template('index.html')


@flask_app.route("/signup")
def signup():
    return render_template("signup.html")

@flask_app.route('/login')
def login():
    return render_template("login.html")

#################################################################################################


def get_user_info(user_id):
    c = conn.cursor(buffered=True)
    c.execute('SELECT EMAIL, NAME,DISEASE,`BREAST CANCER`,`LUNG CANCER`,`LIVER CANCER`,`CERVICAL CANCER` FROM `patients` WHERE id = %s', (user_id,))
    row = c.fetchone()
    c.fetchall()
    print(row)
    c.close()

    if row is None:
        return None

    # Convert the database row to a dictionary for easier access
    user_info = {
        'EMAIL': row[0],
        'NAME': row[1],
        'DISEASE': row[2],
        'BREAST':row[3],
        'LUNG':row[4],
        'LIVER':row[5],
        'CERVICAL':row[6]
                }
    return user_info


@flask_app.route("/login_validation", methods=['POST', 'GET'])
def login_validation():
    try:
        name = request.form.get('name')
        password = request.form.get('pass')
        cursor = conn.cursor()

        cursor.execute("""SELECT * FROM `patients` WHERE `NAME` LIKE %s AND `PASSWORD` LIKE %s""", (name, password))
        user = cursor.fetchone()
        cursor.fetchall()
        cursor.close()

        if user is not None:
            # If the user is found, retrieve their information using get_user_info
            user_id = user[0]
            user_info = get_user_info(user_id)

            # Store the user information in the session
            session['user_id'] = user_id
            session['EMAIL'] = user_info['EMAIL']
            session['NAME'] = user_info['NAME']
            session['DISEASE'] = user_info['DISEASE']
            session['BREAST'] = user_info['BREAST']
            session['LUNG'] = user_info['LUNG']
            session['LIVER'] = user_info['LIVER']
            session['CERVICAL'] = user_info['CERVICAL']
            g.name=user_info['NAME']

            return redirect('/getstarted')
        else:
            error = 'Invalid username or password. Please try again.'
            return render_template("login.html", error=error)


    except mysql.connector.errors.OperationalError as e:
        # If a MySQL connection error occurs, attempt to reconnect to the database
        if e.errno == mysql.connector.errorcode.CR_SERVER_LOST or e.errno == mysql.connector.errorcode.CR_CONN_HOST_ERROR:
            conn.reconnect(attempts=3, delay=0)
            return login_validation()

        # If the connection cannot be re-established, raise an error
        raise e


@flask_app.route("/register", methods=['POST', 'GET'])
def profile():
    cursor = conn.cursor(buffered=True)
    if request.method == 'POST':
        session['name'] = request.form.get('rname')
        adduser = request.form
        name = adduser['rname']
        session['NAME'] = request.form.get('rname')
        session['EMAIL'] = request.form.get('remail')
        session['DISEASE'] = 'NONE'
        email = adduser['remail']
        password = adduser['rpass']
        g.name=request.form.get('rname')

        # Check if the email or name already exists in the database
        cursor.execute("""SELECT * FROM `patients` WHERE `EMAIL` LIKE %s OR `NAME` LIKE %s""", (email, name))
        existing_user = cursor.fetchone()
        cursor.fetchall()

        # If email or name already exists, show an error message
        if existing_user is not None:
            error = 'An account with this email or name already exists. Please try again with a different email or name.'
            return render_template('signup.html', error=error)

        # If email and name do not exist, add the new user to the database
        cursor.execute("INSERT INTO `patients` (EMAIL,NAME,PASSWORD) VALUES (%s,%s,%s)", (email, name, password))
        conn.commit()

        cursor.execute("""SELECT * FROM `patients` WHERE `EMAIL` LIKE '{}'""".format(email))
        user = cursor.fetchall()
        session['user_id'] = user[0][0]
        cursor.close()
        return redirect('/getstarted')
    return render_template("signup.html")


                                    #main website done#
            #######################################################################

#after login
@flask_app.route("/getstarted")
def getstarted():
    if 'user_id' in session:
        return render_template("getstarted.html")
    else:
        return redirect("/login")

        ###############################prediction pages###########################
        
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

@flask_app.route('/doctor')
def doctor():
    cur=conn.cursor()
    cur.execute("""SELECT * FROM `doctor_2`""")
    doctors=cur.fetchall()
    cur.execute("""SELECT DISTINCT `PLACE` FROM `doctor_2`""")
    places = [row[0] for row in cur.fetchall()]
    cur.close()
    return render_template('doctor.html', places=places, doctors=doctors)

@flask_app.route('/doctor', methods=['POST'])
def filter_doctors():
    place = request.form['place']
    cur = conn.cursor()
    if place == 'All':
        cur.execute("""SELECT * FROM `doctor_2`""")
    else:
        cur.execute('SELECT * FROM `doctor_2` WHERE place = %s', (place,))
    doctors = cur.fetchall()
    cur.execute('SELECT DISTINCT `PLACE` FROM `doctor_2`')
    places = [row[0] for row in cur.fetchall()]
    cur.close()
    return render_template('doctor.html', places=places, doctors=doctors)




             ################breast cancer prediction##########################

@flask_app.route('/pred' , methods=['POST'])
def pred():
    float_features = [float(x) for x in request.form.values()]
    features = [np.array(float_features)]
    prediction = bmodel.predict(features)

    if prediction==1:
       cursor = conn.cursor()
       name = session.get('NAME')
       print(name)
       cursor.execute("UPDATE `patients` SET `BREAST CANCER`='YES' WHERE `NAME`=%s", (name,))
       conn.commit()
       cursor.close()
       prediction_text="Chances of cancer is there<a href='/doctor'> Click on this link to show nearby doctos</a>"
       return render_template("breastcancer.html", prediction_text = prediction_text)
    else:
        cursor = conn.cursor()
        name = session.get('NAME')
        print(name)
        cursor.execute("UPDATE `patients` SET `BREAST CANCER`='NO' WHERE `NAME`=%s", (name,))
        conn.commit()
        cursor.close()
        return render_template("breastcancer.html", prediction_text = "There is no chance of cancer")


           ###################liver cancer prediction#####################

@flask_app.route ("/livpred", methods = ["POST"])
def predict():
    float_features = [float(x) for x in request.form.values()]
    features = [np.array(float_features)]
    prediction = livmodel.predict(features)

    if prediction==1:
        cursor = conn.cursor()
        name = session.get('NAME')
        print(name)
        cursor.execute("UPDATE `patients` SET `LIVER CANCER`='YES' WHERE `NAME`=%s", (name,))
        conn.commit()
        cursor.close()
        prediction_text = "Chances of cancer is there<a href='/doctor'> Click on this link to show nearby doctos</a>"
        return render_template("livercancer.html", prediction_text=prediction_text)
    else:
        cursor = conn.cursor()
        name = session.get('NAME')
        print(name)
        cursor.execute("UPDATE `patients` SET `LIVER CANCER`='NO' WHERE `NAME`=%s", (name,))
        conn.commit()
        cursor.close()
        return render_template("livercancer.html", prediction_text = "No chance of cancer")

                                  
                ###############lung cancer prediction####################

@flask_app.route("/lungpredict", methods = ["POST"])
def lungpredict():
    float_features = [float(x) for x in request.form.values()]
    features = [np.array(float_features)]
    prediction = lungmodel.predict(features)
    if prediction==1:
       cursor = conn.cursor()
       name = session.get('NAME')
       print(name)
       cursor.execute("UPDATE `patients` SET `LUNG CANCER`='MED' WHERE `NAME`=%s", (name,))
       conn.commit()
       cursor.close()
       prediction_text = "Chances of cancer is medium<a href='/doctor'> Click on this link to show nearby doctos</a>"
       return render_template("lungcancer.html", prediction_text = prediction_text)
    if prediction==0:
        cursor = conn.cursor()
        name = session.get('NAME')
        print(name)
        cursor.execute("UPDATE `patients` SET `LUNG CANCER`='LOW' WHERE `NAME`=%s", (name,))
        conn.commit()
        cursor.close()
        return render_template("lungcancer.html", prediction_text = "The Chances of Cancer is Low")
    else:
        cursor = conn.cursor()
        name = session.get('NAME')
        print(name)
        cursor.execute("UPDATE `patients` SET `LUNG CANCER`='HIGH' WHERE `NAME`=%s", (name,))
        conn.commit()
        cursor.close()
        prediction_text = "Chances of cancer is high<a href='/doctor'> Click on this link to show nearby doctos</a>"
        return render_template("lungcancer.html", prediction_text = prediction_text)

             ######################cervical cancer prediction####################

@flask_app.route ("/cervpred", methods = ["POST"])
def cervpred():
    float_features = [float(x) for x in request.form.values()]
    features = [np.array(float_features)]
    prediction = cervmodel.predict(features)

    if prediction==1:
        cursor = conn.cursor()
        name = session.get('NAME')
        print(name)
        cursor.execute("UPDATE `patients` SET `CERVICAL CANCER`='YES' WHERE `NAME`=%s", (name,))
        conn.commit()
        cursor.close()
        prediction_text = "Chances of cancer is there<a href='/doctor'> Click on this link to show nearby doctos</a>"
        return render_template("cervicalcancer.html", prediction_text =prediction_text)
    else:
        cursor = conn.cursor()
        name = session.get('NAME')
        print(name)
        cursor.execute("UPDATE `patients` SET `CERVICAL CANCER`='NO' WHERE `NAME`=%s", (name,))
        conn.commit()
        cursor.close()
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