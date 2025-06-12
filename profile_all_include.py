# user serializerde elave edersen eger dogrudursa
# class ProfileSerializer(serializers.ModelSerializer):
#     cities = serializers.StringRelatedField(many=True)
#     languages = serializers.StringRelatedField(many=True)
#     work_images = WorkImageSerializer(many=True)

#     class Meta:
#         model = CustomUser
#         fields = [
#             'id',
#             'first_name', 'last_name',
#             'profile_image',
#             'mobile_number',
#             'birth_date',
#             'gender',
#             'profession_area',
#             'profession_speciality',
#             'experience_years',
#             'cities',
#             'education',
#             'education_speciality',
#             'languages',
#             'facebook', 'instagram', 'tiktok', 'linkedin',
#             'work_images',
#             'note',
#         ]
#         read_only_fields = fields



#----------------------------------------------------------------------#


#view ucun
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
#from users.serializers.user_serializers import ProfileSerializer

# class ProfileAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         serializer = ProfileSerializer(request.user)
#         return Response(serializer.data, status=status.HTTP_200_OK)




#------------------------------------------------------#
