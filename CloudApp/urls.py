# from django.urls import path

# from . import views

# urlpatterns = [path("index.html", views.index, name="index"),
# 	       path('DoctorLogin.html', views.DoctorLogin, name="DoctorLogin"), 
# 	       path('PatientLogin.html', views.PatientLogin, name="PatientLogin"), 
# 	       path('Register.html', views.Register, name="Register"),
# 	       path('RegisterAction', views.RegisterAction, name="RegisterAction"),	
# 	       path('UploadCloud', views.UploadCloud, name="UploadCloud"),
# 	       path('UploadCloudAction', views.UploadCloudAction, name="UploadCloudAction"),
# 	       path('ViewPrediction', views.ViewPrediction, name="ViewPrediction"),
# 	       path('PatientData', views.PatientData, name="PatientData"),	     
# 	       path('PatientLoginAction', views.PatientLoginAction, name="PatientLoginAction"),	
# 	       path('DoctorLoginAction', views.DoctorLoginAction, name="DoctorLoginAction"),	
# ]


# CloudApp/urls.py

from django.urls import path
from . import views

# Define the app's name space (good practice)

urlpatterns = [
    # 🌟 NEW: This maps the root URL (/) to your index view
    path("", views.index, name="home"), 

    # Application Paths (Must match the names used in the redirect/links)
    path("index.html", views.index, name="index"), # This one can stay if you want both / and /index.html to work
    path('DoctorLogin.html', views.DoctorLogin, name="DoctorLogin"), 
    # ... (rest of your paths)
    path('PatientLogin.html', views.PatientLogin, name="PatientLogin"), 
    path('Register.html', views.Register, name="Register"),
    path('RegisterAction', views.RegisterAction, name="RegisterAction"), 
    path('UploadCloud', views.UploadCloud, name="UploadCloud"),
    path('UploadCloudAction', views.UploadCloudAction, name="UploadCloudAction"),
    path('ViewPrediction', views.ViewPrediction, name="ViewPrediction"),
    path('PatientData', views.patient_data_view, name="PatientData"), 
    path('PatientLoginAction', views.PatientLoginAction, name="PatientLoginAction"), 
    path('DoctorLoginAction', views.DoctorLoginAction, name="DoctorLoginAction"), 
]