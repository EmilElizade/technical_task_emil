from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import re

# ---------------------------------------
#      Validators
# ---------------------------------------

# 1) Azərbaycan əlifbasındakı hərflər üçün validator
azerbaijani_letters_validator = RegexValidator(
    regex=r'^[A-Za-zƏəÖöĞğÜüÇçŞşİı]+$',
    message='Yalnız Azərbaycan əlifbasındakı hərflərə icazə verilir.'
)

# 2) Mobil nömrə validatoru: yalnız 9 rəqəm (məs: 501234567)
mobile_number_validator = RegexValidator(
    regex=r'^\d{9}$',
    message='Mobil nömrə düzgün daxil edilməyib. 50 123 45 67 formatında daxil edin.'
)

# 3) Şifrə gücü üçün validator (8–15 simvol, ən az 1 böyük hərf, 1 rəqəm, 1 xüsusi simvol)
def validate_password_strength(password):
    if not (8 <= len(password) <= 15):
        raise ValidationError('Şifrə 8-15 simvol arasında olmalıdır.')
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Şifrədə ən azı bir böyük hərf olmalıdır.')
    if not re.search(r'[0-9]', password):
        raise ValidationError('Şifrədə ən azı bir rəqəm olmalıdır.')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError('Şifrədə ən azı bir simvol (!@#$... və s.) olmalıdır.')

# ---------------------------------------
#      Custom User Manager
# ---------------------------------------
class CustomUserManager(BaseUserManager):
    """
    CustomUser üçün yaradan menecer.
    Şifrə gücünü yoxlayır və mobil nömrə mütləq olmalıdır.
    """
    def create_user(self, mobile_number, password=None, **extra_fields):
        if not mobile_number:
            raise ValueError('Mobil nömrə daxil edilməlidir.')
        if password:
            validate_password_strength(password)
        user = self.model(mobile_number=mobile_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(mobile_number, password, **extra_fields)

# ---------------------------------------
#      Page 1: CustomUser Model
# ---------------------------------------
class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Peşə sahibi qeydiyyatının 1-ci səhifəsində
    (Şəxsi Məlumatlar) toplanan əsas istifadəçi məlumatları:
      - Ad, Soyad, Doğum tarixi, Mobil nömrə, Şifrə, Cins
    Bunlar CustomUser modelində saxlanılır.
    """
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
        ('Q', 'Qadın'),
        ('K', 'Kişi'),
    ]
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        verbose_name="Cins"
    )

    # Texniki sahələr (login/permission üçün)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    # login üçün unikal sahə
    USERNAME_FIELD = 'mobile_number'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'birth_date', 'gender']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.mobile_number}"

    class Meta:
        verbose_name = "İstifadəçi"
        verbose_name_plural = "İstifadəçilər"

# ---------------------------------------
#      Page 2: Ayrılmış Modellər
# ---------------------------------------

class ProfessionalField(models.Model):
    """
    Peşə sahələrini saxlayan baza cədvəli.
    Məs: 'Mühəndis', 'Dərzi', 'Elektrik' və s.
    Page 2-də 'Peşə sahəsi' xanası üçün FK bu modelə istinad edəcək.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Peşə Sahəsi")

    def __str__(self):
        return self.name


class ProfessionalQualification(models.Model):
    """
    Peşəkar ixtisas/kvalifikasiyalar cədvəli.
    Məs: 'Bakalavr', 'Magistr', 'Sertifikatlı' və s.
    Page 2-də 'Peşə ixtisası' xanası üçün FK bu modelə istinad edəcək.
    """
    title = models.CharField(max_length=100, unique=True, verbose_name="Peşə Kvalifikasiyası")

    def __str__(self):
        return self.title


class Region(models.Model):
    """
    Şəhər/Rayon cədvəli. 
    Page 2-də 'Fəaliyyət göstərdiyi ərazi' xanası üçün M2M bu modelə bağlanacaq.
    Məsələn: 'Bakı', 'Gəncə', 'Sumqayıt' və s.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Fəaliyyət Bölgəsi")

    def __str__(self):
        return self.name


class ProfessionalProfile(models.Model):
    """
    Ayrılmış peşəkar profil modeli – Page 2-də daxil olunan məlumatlar burada saxlanır.
    1-to-1 olaraq CustomUser ilə əlaqələnir.
    """
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='professional_profile',
        verbose_name="İstifadəçi"
    )
    profession = models.ForeignKey(
        ProfessionalField,
        on_delete=models.PROTECT,
        verbose_name="Peşə Sahəsi"
    )
    qualification = models.ForeignKey(
        ProfessionalQualification,
        on_delete=models.PROTECT,
        verbose_name="Peşə Kvalifikasiyası"
    )
    work_experience = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        verbose_name="İş Təcrübəsi (il olaraq)"
    )
    areas = models.ManyToManyField(
        Region,
        verbose_name="Fəaliyyət Bölgələri"
    )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} – {self.profession.name}"

    class Meta:
        verbose_name = "Peşəkar Profil"
        verbose_name_plural = "Peşəkar Profillər"
