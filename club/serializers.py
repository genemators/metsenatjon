from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from club import models


class SponsorSerializer(ModelSerializer):
    class Meta:
        model = models.Sponsor
        fields = (
            'id', 'first_name', 'last_name', 'phone', 'type', 'payment_amount', 'spent_amount', 'organization_name',
            'status')


class StudentSerializer(ModelSerializer):
    class Meta:
        model = models.Student
        fields = ('id', 'first_name', 'last_name', 'phone', 'type', 'university', 'allocated_amount', 'needed_amount')


class DonationSerializer(ModelSerializer):
    class Meta:
        model = models.Donation
        fields = ('id', 'sponsor', 'student', 'amount')

    def create(self, validated_data):
        sponsor_id = validated_data['sponsor'].id
        student_id = validated_data['student'].id

        amount = validated_data['amount']
        if models.Sponsor.objects.get(id=sponsor_id).status == 'Tasdiqlangan':
            if models.Sponsor.objects.filter(id=sponsor_id).exists() and models.Student.objects.filter(
                    id=student_id).exists():
                sponsor = models.Sponsor.objects.get(id=sponsor_id)

                student = models.Student.objects.get(id=student_id)
                if sponsor.payment_amount - sponsor.spent_amount >= amount:
                    if amount <= student.needed_amount - student.allocated_amount:
                        sponsor.spent_amount += amount
                        student.allocated_amount += amount
                        sponsor.save()
                        student.save()
                        return super().create(validated_data)
                    else:
                        raise ValidationError({"message": "Sponsor gave too much money"})
                else:
                    raise ValidationError({"message": "Sponsor doesn't have enough money"})

            else:
                raise ValidationError({"message": "Sponsor or Student with these id don't exist"})
        else:
            raise ValidationError({"message": "Sponsor isn't verified"})
