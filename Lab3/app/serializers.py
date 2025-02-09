from rest_framework import serializers

from .models import *

视图（views.py）通过模型（models.py）从数据库获取数据，
并使用序列化器（serializers.py）将模型转换为 json 格式，以便发送给客户端
class CodesSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, code):
        if code.image:
            return code.image.url.replace("minio", "localhost", 1)

        return "http://localhost:9000/images/default.png"

    class Meta:
        model = Code
        fields = ("id", "name", "status", "weight", "image")


class CodeSerializer(CodesSerializer):
    class Meta:
        model = Code
        fields = "__all__"


class CalculationsSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    moderator = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Calculation
        fields = "__all__"


class CalculationSerializer(CalculationsSerializer):
    codes = serializers.SerializerMethodField()
            
    def get_codes(self, calculation):
        items = CodeCalculation.objects.filter(calculation=calculation)
        return [CodeItemSerializer(item.code, context={"order": item.order}).data for item in items]


class CodeItemSerializer(CodeSerializer):
    order = serializers.SerializerMethodField()

    def get_order(self, _):
        return self.context.get("order")

    class Meta:
        model = Code
        fields = ("id", "name", "weight", "image", "order")


class CodeCalculationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeCalculation
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username')


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'username')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
