from django.shortcuts import render
import pymysql
from datetime import datetime

from django.template import RequestContext
from django.contrib import messages
import pymysql
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from Homomorphic import encryptData
from datetime import datetime

global username, doctor
dataset = pd.read_csv("Dataset/heart.csv")
columns = dataset.columns
data = dataset.values
X = data[:,0:data.shape[1] - 1]
Y = data[:,data.shape[1] - 1]
homo_X = encryptData(X)#calling PerturnData function from Homomorphic class to encrypt dataset
X_train, X_test, y_train, y_test = train_test_split(homo_X, Y, test_size = 0.2)
rf = RandomForestClassifier()
rf.fit(X_train, y_train)

def UploadCloudAction(request):
    if request.method == 'POST':
        global username, rf
        age = int(request.POST.get('t1', False))
        gender = int(request.POST.get('t2', False))
        cp = int(request.POST.get('t3', False))
        blood = int(request.POST.get('t4', False))
        chol = int(request.POST.get('t5', False))
        fbs = int(request.POST.get('t6', False))
        ecg = int(request.POST.get('t7', False))
        thalac = int(request.POST.get('t8', False))
        exang = int(request.POST.get('t9', False))
        peak = float(request.POST.get('t10', False))
        slope = int(request.POST.get('t11', False))
        ca = int(request.POST.get('t12', False))
        thal = int(request.POST.get('t13', False))

        data = []
        data.append([age, gender, cp, blood, chol, fbs, ecg, thalac, exang, peak, slope, ca, thal])
        data = np.asarray(data)
        data = encryptData(data)
        predict = rf.predict(data)
        output = "Normal"
        if predict == 1:
            output = "Abnormal"
        enc = ""
        for i in range(len(data)):
            for j in range(len(data[i])):
                enc += str(data[i,j])+" "
        enc = enc.strip()
        enc += ","
        enc += str(age)+" "+str(gender)+" "+str(cp)+" "+str(blood)+" "+str(chol)+" "+str(fbs)+" "+str(ecg)+" "+str(thalac)+" "+str(exang)+" "+str(peak)+" "+str(slope)+" "+str(ca)+" "+str(thal)
        today = str(datetime.now())
        dbconnection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'CloudHealth',charset='utf8')
        dbcursor = dbconnection.cursor()
        qry = "INSERT INTO patientdata(username,patient_data,predict,predict_date) VALUES('"+str(username)+"','"+enc+"','"+output+"','"+today+"')"
        dbcursor.execute(qry)
        dbconnection.commit()
        encrypted = enc.split(",")
        result = "Encrypted Data = "+encrypted[0]+"<br/>Predicted Patient Health : "+output
        context= {'data':result}
        return render(request,'PatientScreen.html', context)

def ViewPrediction(request):
    if request.method == 'GET':
        global username
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=black>Patient Name</font></th>'
        output+='<th><font size=3 color=black>Encrypted Symptoms</font></th>'
        output+='<th><font size=3 color=black>Decrypted Symptoms</font></th>'
        output+='<th><font size=3 color=black>Predicted Health</font></th>'
        output+='<th><font size=3 color=black>Date</font></th></tr>'
        mysqlConnect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'CloudHealth',charset='utf8')
        with mysqlConnect:
            result = mysqlConnect.cursor()
            result.execute("select * from patientdata where username='"+username+"'")
            lists = result.fetchall()
            for ls in lists:
                enc = ls[1].split(",")
                output+='<tr><td><font size=3 color=black>'+str(ls[0])+'</font></td>'
                output+='<td><font size=3 color=black>'+enc[0]+'</font></td>'
                output+='<td><font size=3 color=black>'+enc[1]+'</font></td>'
                output+='<td><font size=3 color=black>'+ls[2]+'</font></td>'
                output+='<td><font size=3 color=black>'+ls[3]+'</font></td></tr>'
        context= {'data':output}        
        return render(request,'PatientScreen.html', context)

def PatientData(request):
    if request.method == 'GET':
        global username
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=black>Patient Name</font></th>'
        output+='<th><font size=3 color=black>Encrypted Symptoms</font></th>'
        output+='<th><font size=3 color=black>Decrypted Symptoms</font></th>'
        output+='<th><font size=3 color=black>Predicted Health</font></th>'
        output+='<th><font size=3 color=black>Date</font></th></tr>'
        mysqlConnect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'CloudHealth',charset='utf8')
        with mysqlConnect:
            result = mysqlConnect.cursor()
            result.execute("select * from patientdata")
            lists = result.fetchall()
            for ls in lists:
                enc = ls[1].split(",")
                output+='<tr><td><font size=3 color=black>'+str(ls[0])+'</font></td>'
                output+='<td><font size=3 color=black>'+enc[0]+'</font></td>'
                output+='<td><font size=3 color=black>'+enc[1]+'</font></td>'
                output+='<td><font size=3 color=black>'+ls[2]+'</font></td>'
                output+='<td><font size=3 color=black>'+ls[3]+'</font></td></tr>'
        context= {'data':output}        
        return render(request,'DoctorScreen.html', context)     

def UploadCloud(request):
    if request.method == 'GET':
        output = '<tr><td><font size="3" color="black">Age</td><td><select name="t1">'
        for i in range(10, 100):
            output += '<option value="'+str(i)+'">'+str(i)+'</option>'
        output += '</select></td></tr>'
        context= {'data1':output}
        return render(request,'UploadCloud.html', context)

def index(request):
    if request.method == 'GET':
        return render(request,'index.html', {})

def Register(request):
    if request.method == 'GET':
       return render(request, 'Register.html', {})
    
def DoctorLogin(request):
    if request.method == 'GET':
       return render(request, 'DoctorLogin.html', {})

def PatientLogin(request):
    if request.method == 'GET':
       return render(request, 'PatientLogin.html', {})

def isUserExists(username):
    is_user_exists = False
    global details
    mysqlConnect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'CloudHealth',charset='utf8')
    with mysqlConnect:
        result = mysqlConnect.cursor()
        result.execute("select * from user_signup where username='"+username+"'")
        lists = result.fetchall()
        for ls in lists:
            is_user_exists = True
    return is_user_exists    

def RegisterAction(request):
    if request.method == 'POST':
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        contact = request.POST.get('t3', False)
        email = request.POST.get('t4', False)
        address = request.POST.get('t5', False)
        desc = request.POST.get('t6', False)
        usertype = request.POST.get('t7', False)
        record = isUserExists(username)
        page = None
        if record == False:
            dbconnection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'CloudHealth',charset='utf8')
            dbcursor = dbconnection.cursor()
            qry = "INSERT INTO user_signup(username,password,phone_no,email,address,description,usertype) VALUES('"+str(username)+"','"+password+"','"+contact+"','"+email+"','"+address+"','"+desc+"','"+usertype+"')"
            dbcursor.execute(qry)
            dbconnection.commit()
            if dbcursor.rowcount == 1:
                data = "Signup Done! You can login now"
                context= {'data':data}
                return render(request,'Register.html', context)
            else:
                data = "Error in signup process"
                context= {'data':data}
                return render(request,'Register.html', context) 
        else:
            data = "Given "+username+" already exists"
            context= {'data':data}
            return render(request,'Register.html', context)


def checkUser(uname, password, utype):
    global username
    msg = "Invalid Login Details"
    mysqlConnect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'CloudHealth',charset='utf8')
    with mysqlConnect:
        result = mysqlConnect.cursor()
        result.execute("select * from user_signup where username='"+uname+"' and password='"+password+"' and usertype='"+utype+"'")
        lists = result.fetchall()
        for ls in lists:
            msg = "success"
            username = uname
            break
    return msg

def PatientLoginAction(request):
    if request.method == 'POST':
        global username
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        msg = checkUser(username, password, "Patient")
        if msg == "success":
            context= {'data':"Welcome "+username}
            return render(request,'PatientScreen.html', context)
        else:
            context= {'data':msg}
            return render(request,'PatientLogin.html', context)
        
def DoctorLoginAction(request):
    if request.method == 'POST':
        global username
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        msg = checkUser(username, password, "Doctor")
        if msg == "success":
            context= {'data':"Welcome "+username}
            return render(request,'DoctorScreen.html', context)
        else:
            context= {'data':msg}
            return render(request,'DoctorLogin.html', context)










        


        
