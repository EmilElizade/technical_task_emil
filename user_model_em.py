from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

from ..validators import az_letter_validator, phone_validator
from ..user_managers import CustomUserManager

from core.models import City
from .language_model import Language
from .work_image_model import WorkImage


# Yalnız Azərbaycan əlifbasındakı hərflərə icazə verilir (böyük və kiçik hərflər)
azerbaijani_letters_validator = RegexValidator(
    regex=r'^[A-Za-zƏəÖöĞğÜüÇçŞşİı]+$',
    message='Yalnız Azərbaycan əlifbasındakı hərflərə icazə verilir.'
)

# Mobil nömrə validatoru (9 rəqəm, məsələn: 501234567)
mobile_number_validator = RegexValidator(
    regex=r'^\d{9}$',
    message='Mobil nömrə düzgün daxil edilməyib. 50 123 45 67 formatında daxil edin.'
)



##########//  Custom User Manager  \\##########

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ##########//  Şəxsi məlumatlar  \\##########
    first_name = models.CharField(
        max_length=20,
        validators=[azerbaijani_letters_validator],
        verbose_name="Ad"
    )

    last_name = models.CharField(
        max_length=20,
        validators=[azerbaijani_letters_validator],
        verbose_name="Soyad"
    )

    birth_date = models.DateField(
        verbose_name="Doğum tarixi",
        help_text="Format: gün.ay.il (məsələn: 29.05.2025)"
    )

    mobile_number = models.CharField(
        max_length=9,
        unique=True,
        validators=[mobile_number_validator],
        verbose_name="Mobil nömrə"
    )

    GENDER_CHOICES = [
        ('MALE', 'Kişi'),
        ('FEMALE', 'Qadın')
    ]
    gender = models.CharField(
        max_length=6,
        choices=GENDER_CHOICES,
        verbose_name="Cins"
    )


    ##########//  Peşə məlumatları  \\##########
    profession_area = models.CharField(
        max_length=100,
        verbose_name="İxtisas sahəsi"
    )

    profession_speciality = models.CharField(
        max_length=100,
        verbose_name="İxtisas üzrə peşə"
    )

    experience_years = models.PositiveIntegerField(
        verbose_name="İş təcrübəsi (il ilə)"
    )

    cities = models.ManyToManyField(
        "core.City",
        verbose_name="Fəaliyyət göstərdiyi regionlar"
    )


    ##########//  Təhsil məlumatları  \\##########
    EDUCATION_CHOICES = [
        ('0', 'Yoxdur'),
        ('1', 'Tam ali'),
        ('2', 'Natamam ali'),
        ('3', 'Orta'),
        ('4', 'Peşə təhsili'),
        ('5', 'Orta ixtisas təhsili'),
    ]
    education = models.CharField(
        max_length=20,
        choices=EDUCATION_CHOICES,
        verbose_name="Təhsil səviyyəsi"
    )

    education_speciality = models.CharField(
        max_length=50,
        blank=True,
        validators=[azerbaijani_letters_validator],
        verbose_name="Təhsil üzrə ixtisas"
    )

    languages = models.ManyToManyField(
        "Language",
        verbose_name="Bildiyi dillər"
    )

    profile_image = models.ImageField(
        upload_to='profile_images/',
        blank=True,
        null=True,
        verbose_name="Profil şəkli"
    )

    facebook = models.URLField(blank=True, verbose_name="Facebook linki")
    instagram = models.URLField(blank=True, verbose_name="Instagram linki")
    tiktok = models.URLField(blank=True, verbose_name="TikTok linki")
    linkedin = models.URLField(blank=True, verbose_name="LinkedIn linki")

    work_images = models.ManyToManyField(
        "WorkImage",
        blank=True,
        verbose_name="İşlərinə aid şəkillər"
    )

    note = models.TextField(
        blank=True,
        max_length=1500,
        verbose_name="Əlavə qeyd"
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now, verbose_name="Yaradılma tarixi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Son yenilənmə tarixi")

    USERNAME_FIELD = 'mobile_number'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'birth_date', 'gender']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.mobile_number})"