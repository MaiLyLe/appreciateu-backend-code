from datetime import timedelta
import datetime 
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from core.models import Message


class MessageStatisticsView(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Message.objects.all()

    @action(detail=False, url_path='total-numbers-statistics-pie-chart')
    def get_total_numbers_statistics_pie_chart(self, request):
        time_threshold_seven = timezone.now() - timedelta(days=7)
        user = request.user
        seven_days_sent_student_total = Message.objects.filter(
            timestamp__gt=time_threshold_seven,
            sender=user,
            receiver__is_student=True).count()
        seven_days_sent_professor_total = Message.objects.filter(
            timestamp__gt=time_threshold_seven,
            sender=user,
            receiver__is_professor=True).count()
        seven_days_received_student_total = Message.objects.filter(
            timestamp__gt=time_threshold_seven,
            receiver=user,
            sender__is_student=True).count()
        seven_days_received_professor_total = Message.objects.filter(
            timestamp__gt=time_threshold_seven,
            receiver=user,
            sender__is_professor=True).count()

        time_threshold_months = timezone.now() - relativedelta(months=+6)

        six_months_sent_student_total = Message.objects.filter(
            timestamp__gt=time_threshold_months,
            sender=user,
            receiver__is_student=True).count()
        six_months_sent_professor_total = Message.objects.filter(
            timestamp__gt=time_threshold_months,
            sender=user,
            receiver__is_professor=True).count()
        six_months_received_student_total = Message.objects.filter(
            timestamp__gt=time_threshold_months,
            receiver=user,
            sender__is_student=True).count()
        six_months_received_professor_total = Message.objects.filter(
            timestamp__gt=time_threshold_months,
            receiver=user,
            sender__is_professor=True).count()

        return Response({"seven_days_sent_student_total": seven_days_sent_student_total,
                         "seven_days_sent_professor_total": seven_days_sent_professor_total,
                         "seven_days_received_student_total": seven_days_received_student_total,
                         "seven_days_received_professor_total": seven_days_received_professor_total,
                         "six_months_sent_student_total": six_months_sent_student_total,
                         "six_months_sent_professor_total": six_months_sent_professor_total,
                         "six_months_received_student_total": six_months_received_student_total,
                         "six_months_received_professor_total": six_months_received_professor_total
                        },
                        status=status.HTTP_200_OK)

    @action(detail=False, url_path='total-amount-array-bar-chart')
    def get_total_amount_array_bar_charts(self, request):
        user = request.user
        messages_sent_7_days = []
        messages_received_7_days = []
        messages_sent_6_months = []
        messages_received_6_months = []

        now = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        days_in_current_month = datetime.datetime.today().day
        current_month = (timezone.now() - timedelta(days=days_in_current_month)).replace(hour=0, minute=0, second=0, microsecond=0)
        today_messages_sent = Message.objects.filter(
                timestamp__gt=now,
                sender=user).count()
        today_messages_received = Message.objects.filter(
                timestamp__gt=now,
                receiver=user).count()
        this_month_messages_sent = Message.objects.filter(
                timestamp__gt=current_month,
                sender=user).count()
        this_month_messages_received = Message.objects.filter(
                timestamp__gt=current_month,
                receiver=user).count()
        messages_sent_7_days.append({"time": now, "count": today_messages_sent})
        messages_received_7_days.append({"time": now, "count": today_messages_received})
        messages_sent_6_months.append({"time": current_month, "count": this_month_messages_sent})
        messages_received_6_months.append({"time": current_month, "count": this_month_messages_received})

        for x in range(0, 6):

            if x == 0:
                day_threshold_max = now
            else:
                day_threshold_max = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=x)
            day_threshold_min = day_threshold_max - timedelta(days=1)
            count_sent_per_day = Message.objects.filter(
                timestamp__gt=day_threshold_min,
                timestamp__lt=day_threshold_max,
                sender=user).count(),
            count_received_per_day = Message.objects.filter(
                timestamp__gt=day_threshold_min,
                timestamp__lt=day_threshold_max,
                receiver=user).count()
            messages_sent_7_days.append({"time": day_threshold_min, "count": count_sent_per_day})
            messages_received_7_days.append({"time": day_threshold_min, "count": count_received_per_day})

            month_threshold_max = current_month - relativedelta(months=x) - timedelta(minutes=1)
            month_threshold_min = current_month - relativedelta(months=x+1)
            count_sent_per_month = Message.objects.filter(
                timestamp__gt=month_threshold_min,
                timestamp__lt=month_threshold_max,
                sender=user).count(),
                
            count_received_per_month = Message.objects.filter(
                timestamp__gt=month_threshold_min,
                timestamp__lt=month_threshold_max,
                receiver=user).count()
            messages_sent_6_months.append({"time": month_threshold_min, "count": count_sent_per_month})
            messages_received_6_months.append({"time": month_threshold_min, "count": count_received_per_month})

        messages_sent_6_months.pop()
        messages_received_6_months.pop()
        return Response({"messages_sent_7_days": messages_sent_7_days,
                         "messages_received_7_days": messages_received_7_days,
                         "messages_sent_6_months": messages_sent_6_months,
                         "messages_received_6_months": messages_received_6_months},
                        status=status.HTTP_200_OK)
