import random
from datetime import datetime, timedelta
import uuid

from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .permissions import *
from .redis import session_storage
from .serializers import *
from .utils import identity_user, get_session


def get_draft_calculation(request):
    user = identity_user(request)

    if user is None:
        return None

    calculation = Calculation.objects.filter(owner=user).filter(status=1).first()

    return calculation


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'query',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        )
    ]
)
@api_view(["GET"])
def search_codes(request):
    code_name = request.GET.get("code_name", "")

    codes = Code.objects.filter(status=1)

    if code_name:
        codes = codes.filter(name__icontains=code_name)

    serializer = CodesSerializer(codes, many=True)

    draft_calculation = get_draft_calculation(request)

    resp = {
        "codes": serializer.data,
        "codes_count": CodeCalculation.objects.filter(calculation=draft_calculation).count() if draft_calculation else None,
        "draft_calculation_id": draft_calculation.pk if draft_calculation else None
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
@permission_classes([IsModerator])
def update_code(request, code_id):
    if not Code.objects.filter(pk=code_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    code = Code.objects.get(pk=code_id)

    serializer = CodeSerializer(code, data=request.data)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsModerator])
def create_code(request):
    serializer = CodeSerializer(data=request.data, partial=False)

    serializer.is_valid(raise_exception=True)

    Code.objects.create(**serializer.validated_data)

    codes = Code.objects.filter(status=1)
    serializer = CodeSerializer(codes, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsModerator])
def delete_code(request, code_id):
    if not Code.objects.filter(pk=code_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    code = Code.objects.get(pk=code_id)
    code.status = 2
    code.save()

    code = Code.objects.filter(status=1)
    serializer = CodeSerializer(code, many=True)

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_code_to_calculation(request, code_id):
    if not Code.objects.filter(pk=code_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    code = Code.objects.get(pk=code_id)

    draft_calculation = get_draft_calculation(request)

    if draft_calculation is None:
        draft_calculation = Calculation.objects.create()
        draft_calculation.date_created = timezone.now()
        draft_calculation.owner = identity_user(request)
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
@permission_classes([IsModerator])
def update_code_image(request, code_id):
    if not Code.objects.filter(pk=code_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    code = Code.objects.get(pk=code_id)

    image = request.data.get("image")

    if image is None:
        return Response(status.HTTP_400_BAD_REQUEST)

    code.image = image
    code.save()

    serializer = CodeSerializer(code)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_calculations(request):
    status_id = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    calculations = Calculation.objects.exclude(status__in=[1, 5])

    user = identity_user(request)
    if not user.is_superuser:
        calculations = calculations.filter(owner=user)

    if status_id > 0:
        calculations = calculations.filter(status=status_id)

    if date_formation_start and parse_datetime(date_formation_start):
        calculations = calculations.filter(date_formation__gte=parse_datetime(date_formation_start))

    if date_formation_end and parse_datetime(date_formation_end):
        calculations = calculations.filter(date_formation__lt=parse_datetime(date_formation_end))

    serializer = CalculationsSerializer(calculations, many=True)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_calculation_by_id(request, calculation_id):
    user = identity_user(request)

    if not Calculation.objects.filter(pk=calculation_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    calculation = Calculation.objects.get(pk=calculation_id)
    serializer = CalculationSerializer(calculation)

    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=CalculationSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_calculation(request, calculation_id):
    user = identity_user(request)

    if not Calculation.objects.filter(pk=calculation_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    calculation = Calculation.objects.get(pk=calculation_id)
    serializer = CalculationSerializer(calculation, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_status_user(request, calculation_id):
    user = identity_user(request)

    if not Calculation.objects.filter(pk=calculation_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    calculation = Calculation.objects.get(pk=calculation_id)

    if calculation.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    calculation.status = 2
    calculation.date_formation = timezone.now()
    calculation.save()

    serializer = CalculationSerializer(calculation)

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsModerator])
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

    calculation.status = request_status
    calculation.date_complete = timezone.now()
    calculation.moderator = identity_user(request)
    calculation.save()

    serializer = CalculationSerializer(calculation)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_calculation(request, calculation_id):
    user = identity_user(request)

    if not Calculation.objects.filter(pk=calculation_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    calculation = Calculation.objects.get(pk=calculation_id)

    if calculation.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    calculation.status = 5
    calculation.save()

    return Response(status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_code_from_calculation(request, calculation_id, code_id):
    user = identity_user(request)

    if not Calculation.objects.filter(pk=calculation_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not CodeCalculation.objects.filter(calculation_id=calculation_id, code_id=code_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = CodeCalculation.objects.get(calculation_id=calculation_id, code_id=code_id)
    item.delete()

    calculation = Calculation.objects.get(pk=calculation_id)

    serializer = CalculationSerializer(calculation)
    codes = serializer.data["codes"]

    return Response(codes)


@swagger_auto_schema(method='PUT', request_body=CodeCalculationSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_code_in_calculation(request, calculation_id, code_id):
    user = identity_user(request)

    if not Calculation.objects.filter(pk=calculation_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not CodeCalculation.objects.filter(code_id=code_id, calculation_id=calculation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = CodeCalculation.objects.get(code_id=code_id, calculation_id=calculation_id)

    serializer = CodeCalculationSerializer(item, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@swagger_auto_schema(method='post', request_body=UserLoginSerializer)
@api_view(["POST"])
def login(request):
    user = identity_user(request)

    if user is not None:
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    session_id = str(uuid.uuid4())
    session_storage.set(session_id, user.id)

    serializer = UserSerializer(user)
    response = Response(serializer.data, status=status.HTTP_200_OK)
    response.set_cookie("session_id", session_id, samesite="lax")

    return response


@swagger_auto_schema(method='post', request_body=UserRegisterSerializer)
@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    session_id = str(uuid.uuid4())
    session_storage.set(session_id, user.id)

    serializer = UserSerializer(user)
    response = Response(serializer.data, status=status.HTTP_201_CREATED)
    response.set_cookie("session_id", session_id, samesite="lax")

    return response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    session = get_session(request)
    session_storage.delete(session)

    response = Response(status=status.HTTP_200_OK)
    response.delete_cookie('session_id')

    return response


@swagger_auto_schema(method='PUT', request_body=UserProfileSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = identity_user(request)

    if user.pk != user_id:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(user, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    password = request.data.get("password", None)
    if password is not None and not user.check_password(password):
        user.set_password(password)
        user.save()

    return Response(serializer.data, status=status.HTTP_200_OK)
