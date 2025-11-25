from django.db import models

class UserSignup(models.Model):
    """Signup information for a user.

    - `id` is an implicit AutoField primary key provided by Django.
    - `username` is unique so it can be used to look up users.
    - `password` should be handled via Django auth in a real app; kept here
      for compatibility with the existing project structure.
    """
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    phone_no = models.CharField(max_length=20, blank=True)
    email = models.EmailField(max_length=254, blank=True)
    address = models.TextField(blank=True)
    description = models.TextField(blank=True)
    usertype = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'user_signup'


class PatientData(models.Model):
    """Medical or patient data recorded for a user.

    Uses a foreign key to `UserSignup` so relational integrity is enforced
    when using a Postgres backend.
    """
    user = models.ForeignKey(UserSignup, on_delete=models.CASCADE, related_name='patient_records')
    patient_data = models.TextField()
    predict = models.CharField(max_length=30, blank=True)
    # Store as a proper date; apps that need time can add DateTimeField.
    predict_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Data for {self.user.username} ({self.predict_date})"

    class Meta:
        db_table = 'patientdata'