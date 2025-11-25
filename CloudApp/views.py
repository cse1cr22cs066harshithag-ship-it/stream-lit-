from django.shortcuts import render, redirect
from django.db import connection
from .models import PatientData, UserSignup
from datetime import datetime
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
import os

# Defer heavy ML and data imports until they're actually needed. This avoids
# import-time failures when running management commands (check/migrate) on
# systems that don't have optional ML dependencies installed.
_ml_initialized = False
_ml_model = None

def _load_ml_model():
    """Lazily import ML libs, train the model, and cache it.

    Returns a callable `predict(data)`-like object (here a fitted estimator).
    If imports fail, returns None and leaves an informative message in logs.
    """
    global _ml_initialized, _ml_model
    if _ml_initialized:
        return _ml_model
    _ml_initialized = True
    try:
        import pandas as pd
        import numpy as np
        from sklearn.model_selection import train_test_split
        from sklearn.ensemble import RandomForestClassifier
        from Homomorphic import encryptData
    except Exception:
        # Optional ML dependencies not available; don't block Django management commands.
        _ml_model = None
        return None

    # Dataset path: repo root / Dataset/heart.csv
    dataset_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Dataset", "heart.csv")
    try:
        dataset = pd.read_csv(dataset_path)
    except Exception:
        _ml_model = None
        return None

    data = dataset.values
    X = data[:, 0 : data.shape[1] - 1]
    Y = data[:, data.shape[1] - 1]
    homo_X = encryptData(X)
    X_train, X_test, y_train, y_test = train_test_split(homo_X, Y, test_size=0.2)
    rf = RandomForestClassifier()
    rf.fit(X_train, y_train)
    _ml_model = (rf, encryptData)
    return _ml_model

def UploadCloudAction(request):
    # If someone visits this URL with GET, redirect them to the upload form.
    if request.method != 'POST':
        return redirect('UploadCloud')

    # POST handling
    try:
        # Check if user is logged in using session
        if 'username' not in request.session:
            messages.error(request, 'You must be logged in to submit patient data.')
            return redirect('PatientLogin')
            
        username = request.session['username']
        # Read form inputs (keep as plain Python types)
        age = request.POST.get('t1', False)
        gender = request.POST.get('t2', False)
        cp = request.POST.get('t3', False)
        blood = request.POST.get('t4', False)
        chol = request.POST.get('t5', False)
        fbs = request.POST.get('t6', False)
        ecg = request.POST.get('t7', False)
        thalac = request.POST.get('t8', False)
        exang = request.POST.get('t9', False)
        peak = request.POST.get('t10', False)
        slope = request.POST.get('t11', False)
        ca = request.POST.get('t12', False)
        thal = request.POST.get('t13', False)

        # Keep a canonical plaintext representation to store alongside any encrypted data
        plaintext_vals = [age, gender, cp, blood, chol, fbs, ecg, thalac, exang, peak, slope, ca, thal]
        plaintext_str = " ".join(str(x) for x in plaintext_vals)

        # Try to load the ML model and perform encryption/prediction. If unavailable,
        # fall back to storing plaintext and a helpful prediction message.
        model = _load_ml_model()
        output = "Prediction unavailable"
        encrypted_str = ""
        if model is not None:
            try:
                import numpy as np
                rf, encrypt_func = model
                data = np.asarray([ [int(age), int(gender), int(cp), int(blood), int(chol), int(fbs), int(ecg), int(thalac), int(exang), float(peak), int(slope), int(ca), int(thal)] ])
                enc_data = encrypt_func(data)
                predict = rf.predict(enc_data)
                output = "Normal"
                # original logic treated predict==1 as Abnormal
                try:
                    if int(predict[0]) == 1:
                        output = "Abnormal"
                except Exception:
                    # non-integer/shape issues — keep generic output
                    pass

                # Build encrypted string (space-separated values) and append plaintext part
                enc_parts = []
                for i in range(len(enc_data)):
                    enc_parts.append(" ".join(str(x) for x in enc_data[i]))
                encrypted_str = ",".join(enc_parts) + "," + plaintext_str
            except Exception:
                # If prediction/encryption fails, fall back to plaintext storage
                encrypted_str = ",".join(["", plaintext_str])
                output = "Prediction failed"
        else:
            # ML not available; store empty encrypted part and plaintext after comma
            encrypted_str = ",".join(["", plaintext_str])

        today = str(datetime.now())
        try:
            # ORM: Find user object
            user_obj = UserSignup.objects.filter(username=username).first()
            if not user_obj:
                messages.error(request, 'User not found. Please log in again.')
                return redirect('PatientLogin')
            PatientData.objects.create(
                user=user_obj,
                patient_data=encrypted_str,
                predict=output,
                predict_date=today
            )
        except Exception as db_exc:
            print('DB error in UploadCloudAction:', db_exc)
            messages.error(request, 'Unable to save patient data right now. Please try again later.')
            return redirect('UploadCloud')

        encrypted = encrypted_str.split(",")
        # Ensure we always have at least the encrypted (maybe empty) and plaintext parts
        enc_display = encrypted[0] if len(encrypted) > 0 else ""
        result = "Encrypted Data = "+enc_display+"<br/>Predicted Patient Health : "+output
        context= {'data':result}
        return render(request,'PatientScreen.html', context)
    except Exception as exc:
        # Generic catch-all to avoid 500 pages and give user-friendly feedback
        print('UploadCloudAction unexpected error:', exc)
        messages.error(request, 'An internal error occurred. Please try again.')
        return redirect('UploadCloud')

def ViewPrediction(request):
    if request.method == 'GET':
        # Check if user is logged in
        if 'username' not in request.session:
            messages.error(request, 'Please log in to view predictions.')
            return redirect('PatientLogin')
            
        username = request.session['username']
        output = '<table border=1 align=center width="100%">'
        output += '<tr><th><font size=3 color=black>Patient Name</font></th>'
        output += '<th><font size=3 color=black>Encrypted Symptoms</font></th>'
        output += '<th><font size=3 color=black>Decrypted Symptoms</font></th>'
        output += '<th><font size=3 color=black>Predicted Health</font></th>'
        output += '<th><font size=3 color=black>Date</font></th></tr>'
        
        try:
            # Use ORM to get predictions for the logged-in user
            user_obj = UserSignup.objects.filter(username=username).first()
            if user_obj:
                records = PatientData.objects.filter(user=user_obj).order_by('-created_at')
                if not records.exists():
                    output += '<tr><td colspan="5" align="center">No prediction records found.</td></tr>'
                else:
                    for rec in records:
                        enc = rec.patient_data.split(",")
                        output += f'<tr><td><font size=3 color=black>{rec.user.username}</font></td>'
                        output += f'<td><font size=3 color=black>{enc[0][:50] + "..." if len(enc[0]) > 50 else enc[0] if len(enc)>0 else ""}</font></td>'
                        output += f'<td><font size=3 color=black>{enc[1] if len(enc)>1 else ""}</font></td>'
                        output += f'<td><font size=3 color=black>{rec.predict}</font></td>'
                        output += f'<td><font size=3 color=black>{rec.predict_date}</font></td></tr>'
            else:
                output += '<tr><td colspan="5" align="center">User not found.</td></tr>'
        except Exception as e:
            print(f"Error in ViewPrediction: {e}")
            output += '<tr><td colspan="5" align="center">Error loading prediction data. Please try again.</td></tr>'
            
        output += '</table>'
        context = {'data': output}
        return render(request, 'PatientScreen.html', context)

def patient_data_view(request):
    if request.method == 'GET':
        output = '<table border=1 align=center>'
        output += '<tr><th><font size=3 color=black>Patient Name</font></th>'
        output += '<th><font size=3 color=black>Encrypted Symptoms</font></th>'
        output += '<th><font size=3 color=black>Decrypted Symptoms</font></th>'
        output += '<th><font size=3 color=black>Predicted Health</font></th>'
        output += '<th><font size=3 color=black>Date</font></th></tr>'
        # Use ORM to get all patient records
        records = PatientData.objects.select_related('user').all()
        for rec in records:
            enc = rec.patient_data.split(",")
            output += f'<tr><td><font size=3 color=black>{rec.user.username}</font></td>'
            output += f'<td><font size=3 color=black>{enc[0] if len(enc)>0 else ""}</font></td>'
            output += f'<td><font size=3 color=black>{enc[1] if len(enc)>1 else ""}</font></td>'
            output += f'<td><font size=3 color=black>{rec.predict}</font></td>'
            output += f'<td><font size=3 color=black>{rec.predict_date}</font></td></tr>'
        context = {'data': output}
        return render(request, 'DoctorScreen.html', context)

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
    return UserSignup.objects.filter(username=username).exists()

def RegisterAction(request):
    if request.method == 'POST':
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        contact = request.POST.get('t3', False)
        email = request.POST.get('t4', False)
        address = request.POST.get('t5', False)
        desc = request.POST.get('t6', False)
        usertype = request.POST.get('t7', False)
        if not isUserExists(username):
            UserSignup.objects.create(
                username=username,
                password=password,
                phone_no=contact,
                email=email,
                address=address,
                description=desc,
                usertype=usertype
            )
            data = "Signup Done! You can login now"
            context = {"data": data}
            return render(request, "Register.html", context)
        else:
            data = "Given "+username+" already exists"
            context= {'data':data}
            return render(request,'Register.html', context)


def checkUser(uname, password, utype):
    try:
        user = UserSignup.objects.filter(username=uname, password=password, usertype=utype).first()
        if user is not None:
            return 'Login Success'
        return 'Login Failed'
    except Exception as e:
        print(f"Error in checkUser: {e}")
        return 'Login Failed'

def PatientLoginAction(request):
    if request.method == 'POST':
        username = request.POST.get('t1', '').strip()
        password = request.POST.get('t2', '').strip()
        status = checkUser(username, password, 'Patient')
        if status == 'Login Success':
            # Store username in session
            request.session['username'] = username
            request.session.set_expiry(3600)  # Session expires in 1 hour
            return redirect('ViewPrediction')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('PatientLogin')
    return redirect('PatientLogin')
        
def DoctorLoginAction(request):
    if request.method == 'POST':
        username = request.POST.get('t1', '').strip()
        password = request.POST.get('t2', '').strip()
        status = checkUser(username, password, 'Doctor')
        if status == 'Login Success':
            # Store username in session
            request.session['username'] = username
            request.session.set_expiry(3600)  # Session expires in 1 hour
            return redirect('patient_data_view')
        msg = checkUser(username, password, "Doctor")
        if msg == "success":
            context= {'data':"Welcome "+username}
            return render(request,'DoctorScreen.html', context)
        else:
            context= {'data':msg}
            return render(request,'DoctorLogin.html', context)










        


        
