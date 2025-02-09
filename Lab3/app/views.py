import random
from datetime import datetime, timedelta

from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import *


def get_draft_calculation():
    return Calculation.objects.filter(status=1).first()


def get_user():
    return User.objects.filter(is_superuser=False).first()


def get_moderator():
    return User.objects.filter(is_superuser=True).first()


@api_view(["GET"])
def search_codes(request):
    code_name = request.GET.get("code_name", "")

    codes = Code.objects.filter(status=1)

    if code_name:
        codes = codes.filter(name__icontains=code_name)

    serializer = CodesSerializer(codes, many=True)
    
    draft_calculation = get_draft_calculation()

    resp = {
        "codes": serializer.data,
        "codes_count": CodeCalculation.objects.filter(calculation=draft_calculation).count() if draft_calculation else None,
        "draft_calculation": draft_calculation.pk if draft_calculation else None
    }

    return Response(resp)


@api_view(["GET"])
def get_code_by_id(request, code_id):
    if not Code.objects.filter(pk=code_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    code = Code.objects.get(pk=code_id)
    serializer = CodeSerializer(code)

    return Response(serializer.data)


@api_view(["PUT"])
def update_code(request, code_id):
    if not Code.objects.filter(pk=code_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    code = Code.objects.get(pk=code_id)

    serializer = CodeSerializer(code, data=request.data, partial=True)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def create_code(request):
    serializer = CodeSerializer(data=request.data, partial=False)

    serializer.is_valid(raise_exception=True)

    Code.objects.create(**serializer.validated_data)

    codes = Code.objects.filter(status=1)
    serializer = CodeSerializer(codes, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_code(request, code_id):
    if not Code.objects.filter(pk=code_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    code = Code.objects.get(pk=code_id)
    code.status = 2
    code.save()

    codes = Code.objects.filter(status=1)
    serializer = CodeSerializer(codes, many=True)

    return Response(serializer.data)


@api_view(["POST"])
def add_code_to_calculation(request, code_id):
    if not Code.objects.filter(pk=code_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    code = Code.objects.get(pk=code_id)
# 14
    draft_calculation = get_draft_calculation()

    if draft_calculation is None:
        draft_calculation = Calculation.objects.create()
        draft_calculation.owner = get_user()
        draft_calculation.date_created = timezone.now()
        draft_calculation.save()

    if CodeCalculation.objects.filter(calculation=draft_calculation, code=code).exists():
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
    item = CodeCalculation.objects.create()
    item.calculation = draft_calculation
    item.code = code
    item.save()

    serializer = CalculationSerializer(draft_calculation)
    return Response(serializer.data["codes"])


@api_view(["POST"])
def update_code_image(request, code_id):
    if not Code.objects.filter(pk=code_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    code = Code.objects.get(pk=code_id)

    image = request.data.get("image")
    if image is not None:
        code.image = image
        code.save()

    serializer = CodeSerializer(code)

    return Response(serializer.data)


@api_view(["GET"])
def search_calculations(request):
    status = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    calculations = Calculation.objects.exclude(status__in=[1, 5])

    if status > 0:
        calculations = calculations.filter(status=status)

    if date_formation_start and parse_datetime(date_formation_start):
        calculations = calculations.filter(date_formation__gte=parse_datetime(date_formation_start))

    if date_formation_end and parse_datetime(date_formation_end):
        calculations = calculations.filter(date_formation__lt=parse_datetime(date_formation_end))

    serializer = CalculationsSerializer(calculations, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def get_calculation_by_id(request, calculation_id):
    if not Calculation.objects.filter(pk=calculation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    calculation = Calculation.objects.get(pk=calculation_id)
    serializer = CalculationSerializer(calculation, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_calculation(request, calculation_id):
    if not Calculation.objects.filter(pk=calculation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    calculation = Calculation.objects.get(pk=calculation_id)
    serializer = CalculationSerializer(calculation, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_user(request, calculation_id):
    if not Calculation.objects.filter(pk=calculation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    calculation = Calculation.objects.get(pk=calculation_id)

    if calculation.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    calculation.status = 2
    calculation.date_formation = timezone.now()
    calculation.save()

    serializer = CalculationSerializer(calculation, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_admin(request, calculation_id):
    if not Calculation.objects.filter(pk=calculation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])

    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    calculation = Calculation.objects.get(pk=calculation_id)

    if calculation.status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request_status == 3:
        calculation.result = random.randint(1, 10)

    calculation.date_complete = timezone.now()
    calculation.status = request_status
    calculation.moderator = get_moderator()
    calculation.save()

    return Response(status=status.HTTP_200_OK)


@api_view(["DELETE"])
def delete_calculation(request, calculation_id):
    if not Calculation.objects.filter(pk=calculation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    calculation = Calculation.objects.get(pk=calculation_id)

    if calculation.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    calculation.status = 5
    calculation.save()

    serializer = CalculationSerializer(calculation, many=False)

    return Response(serializer.data)

# м-м
@api_view(["DELETE"])
def delete_code_from_calculation(request, calculation_id, code_id):
    if not CodeCalculation.objects.filter(calculation_id=calculation_id, code_id=code_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = CodeCalculation.objects.get(calculation_id=calculation_id, code_id=code_id)
    item.delete()

    items = CodeCalculation.objects.filter(calculation_id=calculation_id)
    data = [CodeItemSerializer(item.code, context={"order": item.order}).data for item in items]

    return Response(data, status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_code_in_calculation(request, calculation_id, code_id):
    if not CodeCalculation.objects.filter(code_id=code_id, calculation_id=calculation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = CodeCalculation.objects.get(code_id=code_id, calculation_id=calculation_id)

    serializer = CodeCalculationSerializer(item, data=request.data,  partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def logout(request):
    return Response(status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = User.objects.get(pk=user_id)
    serializer = UserSerializer(user, data=request.data, partial=True)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    return Response(serializer.data)