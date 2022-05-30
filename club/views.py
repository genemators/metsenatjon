from django.db.models import Q
from django.utils.dateformat import DateFormat
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from club import models, serializers


class StudentViewSet(viewsets.ModelViewSet):
    queryset = models.Student.objects.all()
    serializer_class = serializers.StudentSerializer
    lookup_field = 'id'
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        query = models.Student.objects.all()
        sortKey = request.GET.get('sort')
        searchKey = request.GET.get('search')
        print(sortKey)
        if sortKey is not None and (sortKey[0] != '-' and sortKey in [f.name for f in models.Student._meta.fields]
                                    or sortKey[1:] in [f.name for f in models.Student._meta.fields]):
            query = query.order_by(sortKey)
        if searchKey is not None:
            query = query.filter(
                Q(first_name__icontains=searchKey) | Q(last_name__icontains=searchKey) |
                Q(phone__icontains=searchKey) | Q(type__icontains=searchKey) |
                Q(university__icontains=searchKey)
            )
        serializer = serializers.StudentSerializer(query, many=True)
        return Response(serializer.data)


class SponsorViewSet(viewsets.ModelViewSet):
    queryset = models.Sponsor.objects.all()
    serializer_class = serializers.SponsorSerializer
    lookup_field = 'id'

    def get_permissions(self):
        if self.action != 'create':
            return [IsAdminUser()]
        else:
            return super().get_permissions()

    def list(self, request, *args, **kwargs):
        query = models.Sponsor.objects.all()
        sortKey = request.GET.get('sort')
        searchKey = request.GET.get('search')
        if sortKey is not None and (sortKey[0] != '-' and sortKey in [f.name for f in models.Sponsor._meta.fields]
                                    or sortKey[1:] in [f.name for f in models.Sponsor._meta.fields]):
            query = query.order_by(sortKey)

        if searchKey is not None:
            query = query.filter(
                Q(first_name__icontains=searchKey) | Q(last_name__icontains=searchKey) |
                Q(phone__icontains=searchKey) | Q(organization_name__icontains=searchKey)
            )
        serializer = serializers.SponsorSerializer(query, many=True)
        return Response(serializer.data)


class DonateViewSet(viewsets.ModelViewSet):
    queryset = models.Donation.objects.all()
    serializer_class = serializers.DonationSerializer
    permission_classes = [IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        donation = models.Donation.objects.get(id=int(kwargs['pk']))
        sponsor = models.Sponsor.objects.get(id=donation.sponsor.id)
        student = models.Student.objects.get(id=donation.student.id)
        amount = donation.amount
        sponsor.spent_amount -= amount
        student.allocated_amount -= amount
        sponsor.save()
        student.save()
        return super(DonateViewSet, self).destroy(request, *args, **kwargs)


class StatView(APIView):
    def get(self, request, format=None):
        donations = models.Donation.objects.all()
        donation_stats = dict()
        given_money = needed_money = 0
        for i in donations:
            date = DateFormat(i.created_at).format('Y-m')
            donation_stats[date] = donation_stats.get(date, 0) + i.amount
            given_money += i.amount
        for i in models.Student.objects.all():
            needed_money += i.needed_amount

        return Response({"total donated money": given_money, "total requested money": needed_money,
                         "required money": given_money - needed_money, "stats": donation_stats})
