from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import re


# ------------------- Validator-lar -------------------
# Yalnız Azərbaycan əlifbasına uyğun hərflərə icazə verir
azerbaijani_letters_validator = RegexValidator(
    regex=r'^[A-Za-zƏəÖöĞğÜüÇçŞşİı]+$',
    message='Yalnız Azərbaycan əlifbasındakı hərflərə icazə verilir.'
)

# Mobil nömrə: 9 rəqəm (məs: 501234567)
mobile_number_validator = RegexValidator(
    regex=r'^\d{9}$',
    message='Mobil nömrə düzgün daxil edilməyib. 50 123 45 67 formatında daxil edin.'
)

# Şifrə gücü üçün yoxlama (8–15 simvol, böyük hərf, rəqəm və simvol)
def validate_password_strength(password):
    if not (8 <= len(password) <= 15):
        raise ValidationError('Şifrə 8-15 simvol arasında olmalıdır.')
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Şifrədə ən azı bir böyük hərf olmalıdır.')
    if not re.search(r'[0-9]', password):
        raise ValidationError('Şifrədə ən azı bir rəqəm olmalıdır.')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError('Şifrədə ən azı bir simvol (!@#$... və s.) olmalıdır.')

# ------------------- İstifadəçi Meneceri -------------------
# Özəl istifadəçi yaratma və superuser yaratmaq üçün CustomUserManager
class CustomUserManager(BaseUserManager):
    def create_user(self, mobile_number, password=None, **extra_fields):
        if not mobile_number:
            raise ValueError('Mobil nömrə daxil edilməlidir.')
        if password:
            validate_password_strength(password)  # Şifrə gücü yoxlanılır
        user = self.model(mobile_number=mobile_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(mobile_number, password, **extra_fields)

# ------------------- Page 2 Üçün Əlavə Modellər -------------------
# Peşə sahələri üçün model (məs: Həkim, Müəllim və s.)
class ProfessionalField(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Peşə Sahəsi")

    def __str__(self):
        return self.name

# Peşə kvalifikasiyaları üçün model (məs: Bakalavr, Magistr və s.)
class ProfessionalQualification(models.Model):
    title = models.CharField(max_length=100, unique=True, verbose_name="Peşə Kvalifikasiyası")

    def __str__(self):
        return self.title

# Region/Bölgə məlumatları üçün model (məs: Bakı, Gəncə və s.)
class Region(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Fəaliyyət bölgəsi")

    def __str__(self):
        return self.name

# ------------------- Əsas İstifadəçi Modeli -------------------
class CustomUser(AbstractBaseUser, PermissionsMixin):
    # Şəxsi məlumatlar (Page 1)
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
        ('K', 'Kişi'),
        ('Q', 'Qadın')
    ]
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        verbose_name="Cins"
    )

    # Peşə məlumatları (Page 2)
    professional_field = models.ForeignKey(
        ProfessionalField,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Peşə Sahəsi"
    )
    professional_qualification = models.ForeignKey(
        ProfessionalQualification,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Peşə Kvalifikasiyası"
    )
    work_experience = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        verbose_name="İş təcrübəsi (il olaraq)"
    )
    areas_of_operation = models.ManyToManyField(
        Region,
        verbose_name="Fəaliyyət bölgələri",
        blank=False  # boş qoymaq olmaz, mütləq seçilməlidir
    )

    # Texniki sahələr
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    # Sistemdə login üçün istifadə ediləcək əsas sahə
    USERNAME_FIELD = 'mobile_number'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'birth_date', 'gender',
                       'professional_field', 'professional_qualification', 'work_experience']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.mobile_number}"

    class Meta:
        verbose_name = "İstifadəçi"
        verbose_name_plural = "İstifadəçilər"
