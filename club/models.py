from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver

from club import managers

STATUS_CHOICES = (
    ('Yangi', 'Yangi'),
    ('Moderatsiya', 'Moderatsiya'),
    ('Tasdiqlangan', 'Tasdiqlangan'),
    ('Bekor qilingan', 'Bekor qilingan')
)


class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    username = None
    phone_regex = RegexValidator(regex=r'^\d{9}$',
                                 message="901234567 Formatida kiriting")
    phone = models.CharField(validators=[phone_regex], max_length=9, unique=True)
    USERNAME_FIELD = 'phone'
    objects = managers.UserManager()


class Sponsor(CustomUser):
    SPONSOR_TYPE_CHOICES = (
        ('Jismoniy', 'Jismoniy'),
        ('Yuridik', 'Yuridik')
    )
    type = models.CharField(choices=SPONSOR_TYPE_CHOICES, max_length=255)
    payment_amount = models.PositiveIntegerField()
    spent_amount = models.PositiveIntegerField(default=0)
    organization_name = models.CharField(null=True, max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    status = models.CharField(choices=STATUS_CHOICES, max_length=255)

    class Meta:
        verbose_name = 'Homiy'
        verbose_name_plural = 'Homiylar'

    def __str__(self):
        return f"{self.id}"

    def save(self, *args, **kwargs):
        if self.type == 'Jismoniy':
            self.organization_name = None
            super(Sponsor, self).save(*args, **kwargs)
        elif self.type == 'Yuridik' and self.organization_name is not None:
            super(Sponsor, self).save(*args, **kwargs)


class Student(CustomUser):
    STUDENT_TYPE_CHOICES = (
        ('Bakalavr', 'Bakalavr'),
        ('Magistr', 'Magistr'),
    )
    type = models.CharField(choices=STUDENT_TYPE_CHOICES, max_length=255)
    university = models.CharField(max_length=255)
    allocated_amount = models.PositiveIntegerField()
    needed_amount = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Talaba'
        verbose_name_plural = 'Talabalar'

    def __str__(self):
        return self.first_name + " " + self.last_name


class Donation(models.Model):
    sponsor = models.ForeignKey(Sponsor, on_delete=models.CASCADE, related_name='donations', null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='donations', null=True)
    amount = models.PositiveIntegerField()
    status = models.CharField(choices=STATUS_CHOICES, max_length=255, default='Yangi')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Homiylik'
        verbose_name_plural = 'Homiyliklar'

    def __str__(self):
        return str(self.amount)


@receiver(pre_save, sender=Donation)
def save_donation(sender, instance, **kwargs):
    student = Student.objects.get(id=instance.student.id)
    sponsor = Sponsor.objects.get(id=instance.sponsor.id)
    amount = instance.amount
    if not instance.pk:
        if sponsor.status == 'Tasdiqlangan':
            student.allocated_amount += amount
            sponsor.spent_amount += amount
            student.save()
            sponsor.save()
        else:
            raise ValueError({"message": "Sponsor isn't verified"})
    else:
        prev_instance = Donation.objects.get(id=instance.id)
        prev_amount = prev_instance.amount
        if prev_instance.sponsor is instance.sponsor and \
                prev_instance.student is instance.student:
            if amount - prev_amount < sponsor.payment_amount - sponsor.spent_amount:
                if student.allocated_amount - prev_amount + amount <= student.needed_amount:
                    student.allocated_amount -= prev_amount + amount
                    sponsor.spent_amount -= prev_amount + amount
                    student.save()
                    sponsor.save()
                else:
                    raise ValueError({"message": "Student is being given too much money"})
            else:
                raise ValueError({"message": "Sponsor doesn't have enough money"})
        else:
            raise ValueError({"message": "You've changed users"})


@receiver(pre_delete, sender=Donation)
def delete_donation(sender, instance, **kwargs):
    student = Student.objects.get(id=instance.student.id)
    sponsor = Sponsor.objects.get(id=instance.sponsor.id)
    amount = instance.amount
    sponsor.spent_amount -= amount
    student.allocated_amount -= amount
    student.save()
    sponsor.save()
