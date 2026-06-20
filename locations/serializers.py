from rest_framework import serializers
from .models import *
   
class divisionSerializers(serializers.ModelSerializer):
    class Meta:
        model = Division
        fields = ["name"]
        read_only_fields = ["id"]

class districtSerializers(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ["name", "division"]
        read_only_fields = ["id"]

class upazilaSerializers(serializers.ModelSerializer):
    class Meta:
        model = Upazila
        fields = ["name", "district"]
        read_only_fields = ["id"]
