from flask import Flask,render_template,redirect,request,session,url_for
from flask_session import Session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

# from flask import Flask, render_template, request



app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'heart_disease_system'

mysql = MySQL(app)

import pickle
#to load the developed model
filename = 'finalized_model_main.sav'
loaded_model = pickle.load(open(filename, 'rb'))


filename = 'normalized.sav'
normalized_model = pickle.load(open(filename,'rb'))
'''import mysql.connector
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    database="test"
)
mycursor = mydb.cursor()
'''



#home page method
@app.route("/")
def index():
    return render_template('signin.html');

@app.route("/signup")
def singup1():
    return render_template('signin.html');

#login method
@app.route("/login")
def login1():
    return render_template('login.html');
@app.route("/profile")
def profile():

    with app.app_context():
        cursor = mysql.connection.cursor()
        cursor.execute('''select * from registration where uemail = %s ''',(session['uemail'],))
        # if (cursor.fetchall()[0][0] >= 1):
        #     name = cursor.get("uname")
        #     email = request.form.get("uemail")
        #     phone = request.form.get("umobile_NO")
        #     session["uemail"] = request.form.get("ueamil")
        #     return render_template("profile.html", data)
        data = cursor.fetchall()
        uname=""
        uemail=""
        umobile_NO=""
        # print(uname)
        for row in data:
            uname = row[1]
            uemail = row[2]
            umobile_NO = row[4]


        if ((session["uemail"]) != False):
            return render_template('profile.html',data={'uname':uname,'uemail':uemail,'umobile_NO':umobile_NO});
        else:
            return redirect("/login")




@app.route("/info")
def info():
    if ((session["uemail"]) != False):
        return render_template('detail.html')
    else:
        return redirect("/login")
    # return render_template('detail.html')




#singup
@app.route("/home")
def home():
    # return render_template('home.html');
    if((session["uemail"])!=False):
        return render_template("home.html")
    else:
          return redirect("/login")



#about us
@app.route("/about_us")
def about_us1():
    if ((session["uemail"]) != False):
        return render_template('about_us.html');
    else:
        return redirect("/login")







#prediction login successfully
@app.route("/prediction")
def prediction():
    uemail = session["uemail"]
    if((session["uemail"])!=False):
        return render_template("prediction.html",data=uemail)
    else:
        return render_template("login.html")




#prediction logic
@app.route("/prediction_data", methods=["POST"])
def prediction_data():
#patient info
    name = request.form.get("pname")

    email = request.form.get("pmail")

    # uemail = request.form.get("u_id")

    uemail = session["uemail"]

    # print(uemail,email)

    with app.app_context():
        cursor = mysql.connection.cursor()
        cursor.execute(''' INSERT INTO prediction (u_id,p_id) VALUES (%s,%s)''',
                    (uemail,email,))
        mysql.connection.commit()
        cursor.close()




    # if request.method == "POST":
    #     with app.app_context():
    #         cursor = mysql.connection.cursor()
    #
    #         cursor.execute('''select p_id from patient_info2 where p_id= %s ''',
    #                    (request.form.get("p_id"),))
    #
    #         if (cursor.fetchall()[0][0] >= 1):
    #             print(cursor.fetchall())
    #             # session["uemail"] = request.form.get("uemail")
    #             # cursor.execute('''insert into prediction (u_id,p_id) values (%s,%s)''',('uemail',email,))
    #         # else:


    with app.app_context():
        cursor = mysql.connection.cursor()
        cursor.execute('''select count(*) from patient where p_email = %s ''', (email,))
        if (cursor.fetchall()[0][0] >= 1):
            with app.app_context():
                cursor.execute(
                    ''' INSERT INTO prediction_log2 (p_id) VALUES (%s)''', (email,))
                mysql.connection.commit()
                cursor.close()
            #   print()
        else:
        # with app.app_context():
            cursor.execute(
                        ''' INSERT INTO patient (p_name,p_email) VALUES (%s,%s)''', (name, email,))
            mysql.connection.commit()
            cursor.close()

    with app.app_context():
        cursor = mysql.connection.cursor()
        cursor.execute(
            ''' INSERT INTO patient_info2 (p_id,p_email) VALUES (%s,%s)''',
            (email, email,))


        mysql.connection.commit()
        cursor.close()
#prediction information
    age = request.form.get("age")
    anaemia  =request.form.get("anaemia")
    cr_ph = request.form.get("cr_ph")
    dia = request.form.get("dia")
    ej_fr = request.form.get("ej_fr")
    hbp  = request.form.get("hbp")
    platelets = request.form.get("platelets")
    se_cr = request.form.get("se_cr")
    se_so = request.form.get("se_so")

    if(request.form.get("sex")=='male'):
        sex = 0
    else:
        sex = 1
    # sex = request.form.get("sex")
    smoking = request.form.get("smoking")
    time = request.form.get("time")
    l=[age,anaemia,cr_ph,dia,ej_fr,hbp,platelets,se_cr,se_so,sex,smoking,time]
    n=[]



    for i in l:
        n.append(float(i))

    import numpy as np



    from datetime import datetime

    date = datetime.now()
    import numpy as np

    temp = normalized_model.transform(np.array(l).reshape(1, -1))
    r = int(loaded_model.predict(temp.reshape(1, -1))[0])

    with app.app_context():
        cursor = mysql.connection.cursor()
        cursor.execute(
            ''' INSERT INTO prediction_log2 (p_id,age,anaemia,creatinine_phosphokinase,diabetes,ejection_fraction,high_blood_pressure,platelets,serum_creatinine,serum_sodium,sex,smoking,time,timestamp,prediction_result) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
            (
                email,age, anaemia, cr_ph, dia, ej_fr, hbp, platelets, se_cr, se_so, sex, smoking, time, date, r))
        mysql.connection.commit()
        cursor.close()

    if(int(loaded_model.predict(temp.reshape(1,-1))[0])==0):
         return render_template("prediction.html",data1="PATIENT WILL SAFE")
    else:
        return render_template("prediction.html",data2="patient situation is very critical")



#login logic
@app.route("/login_data", methods=["POST"])
def login():
    if request.method == "POST":
        if (request.form.get("uemail")  and request.form.get("upassword")):

            with app.app_context():
                cursor = mysql.connection.cursor()
                cursor.execute('''select count(*) from registration where uemail= %s and u_password = %s''',(request.form.get("uemail"),request.form.get("upassword")))
                if(cursor.fetchall()[0][0]>=1):
                    session["uemail"] = request.form.get("uemail")

                    return render_template("home.html",data="login successfully   "+request.form.get("uemail"))
                else:
                    return render_template('login.html',data="login fail")
                    #return redirect("/signup")
                # cursor.execute(''' INSERT INTO registration (uname,uemail,u_password,umobile_NO) VALUES(%s,%s,%s,%s)''', (request.form.get("uname"),request.form.get("uemail"),request.form.get("upassword"),request.form.get("umobile")))
                mysql.connection.commit()
                cursor.close()
            # sql = "INSERT INTO example(name,password) VALUES (%s,%s) "
            # val = (request.form.get("name"), request.form.get("password"))

            # mycursor.execute(sql,val)
            # mydb.commit()
            # print(mycursor.rowcount, "record inserted.")


        else:
            return render_template('login.html',data="login fail")
            #render_template('login', data=[{'v':"login failed"}])
    return render_template('login.html',data="login fail")





#singup logic
@app.route("/singup_data", methods=["POST"])
def signup():
    if request.method == "POST":
        if (request.form.get("uname") and request.form.get("upassword")):
            with app.app_context():
                cursor = mysql.connection.cursor()
                cursor.execute('''select count(*) from registration where uemail= %s ''',(request.form.get("uemail"),))
                if(cursor.fetchall()[0][0]>=1):
                    return render_template("signin.html", data="Already have Account")
                cursor.execute(''' INSERT INTO registration (uname,uemail,u_password,umobile_NO) VALUES(%s,%s,%s,%s)''', (request.form.get("uname"),request.form.get("uemail"),request.form.get("upassword"),request.form.get("umobile")))
                mysql.connection.commit()
                cursor.close()
            #sql = "INSERT INTO example(name,password) VALUES (%s,%s) "
            #val = (request.form.get("name"), request.form.get("password"))

            #mycursor.execute(sql, val)
            #mydb.commit()
            #print(mycursor.rowcount, "record inserted.")

            session["name"] = request.form.get("uname")
            return render_template("login.html", data="signup successfully")
        else:
            return render_template("signin.html", data="Already have Account")
    return render_template("signin.html", data="Already have Account")
#session
@app.route("/home1")
def index1():
    if not session.get("name"):
        return redirect("/")
    return render_template('home.html')



#logout method
@app.route("/logout")
def logout():
    session["uemail"] = False
    return redirect("/login")


#app run
if __name__ == "__main__":
    app.run(debug=True)




