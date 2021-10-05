# from rest_framework import serializers
# from core.models import Message


# class MessageStatisticsSerializer(serializers.ModelSerializer):
#     """Serializer for Message Statistics based on Message Model"""
#     sender_professor = serializers.SerializerMethodField(read_only=True, method_name='get_sender_professor')
#     sender_student = serializers.SerializerMethodField(read_only=True, method_name='get_sender_student')
#     receiver_professor = serializers.SerializerMethodField(read_only=True, method_name='get_receiver_is_professor')
#     receiver_student = serializers.SerializerMethodField(read_only=True, method_name='get_receiver_student')

#     def get_sender_student(self, obj):
#         """Serializes boolean value for whether sender is student"""
#         return obj.sender.is_student

#     def get_sender_professor(self, obj):
#         """Serializes boolean value for whether sender is professor"""
#         return obj.sender.is_professor


#     def get_receiver_is_professor(self, obj):
#         """Serializes boolean value for whether receiver is professor"""
#         return obj.receiver.is_professor

#     def get_receiver_student(self, obj):
#         """Serializes boolean value for whether receiver is student"""
#         return obj.receiver.is_student

#     class Meta:
#         """Meta class of Message serializer"""
#         model = Message
#         fields = ('timestamp',
#                   'id',
#                   'sender_professor',
#                   'sender_student',
#                   'receiver_professor',
#                   'receiver_student', )
