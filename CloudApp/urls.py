from django.urls import path

from . import views

urlpatterns = [path("index.html", views.index, name="index"),
	       path('DoctorLogin.html', views.DoctorLogin, name="DoctorLogin"), 
	       path('PatientLogin.html', views.PatientLogin, name="PatientLogin"), 
	       path('Register.html', views.Register, name="Register"),
	       path('RegisterAction', views.RegisterAction, name="RegisterAction"),	
	       path('UploadCloud', views.UploadCloud, name="UploadCloud"),
	       path('UploadCloudAction', views.UploadCloudAction, name="UploadCloudAction"),
	       path('ViewPrediction', views.ViewPrediction, name="ViewPrediction"),
	       path('PatientData', views.PatientData, name="PatientData"),	     
	       path('PatientLoginAction', views.PatientLoginAction, name="PatientLoginAction"),	
	       path('DoctorLoginAction', views.DoctorLoginAction, name="DoctorLoginAction"),	
]
