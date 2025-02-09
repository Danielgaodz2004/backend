from django.contrib.auth.models import User
from django.db import connection
from django.shortcuts import render, redirect
from django.utils import timezone

from app.models import Code, Calculation, CodeCalculation


def index(request):
    code_name = request.GET.get("code_name", "")
    codes = Code.objects.filter(status=1)

    if code_name:
        codes = codes.filter(name__icontains=code_name)

    draft_calculation = get_draft_calculation()

    context = {
        "code_name": code_name,
        "codes": codes
    }

    if draft_calculation:
        context["codes_count"] = len(draft_calculation.get_codes())
        context["draft_calculation"] = draft_calculation

    return render(request, "codes_page.html", context)


def add_code_to_draft_calculation(request, code_id):
    code_name = request.POST.get("code_name")
    redirect_url = f"/?code_name={code_name}" if code_name else "/"

    code = Code.objects.get(pk=code_id)

    draft_calculation = get_draft_calculation()

    if draft_calculation is None:
        draft_calculation = Calculation.objects.create()
        draft_calculation.owner = get_current_user()
        draft_calculation.date_created = timezone.now()
        draft_calculation.save()

    if CodeCalculation.objects.filter(calculation=draft_calculation, code=code).exists():
        return redirect(redirect_url)

    item = CodeCalculation(
        calculation=draft_calculation,
        code=code
    )
    item.save()

    return redirect(redirect_url)


def code_details(request, code_id):
    context = {
        "code": Code.objects.get(id=code_id)
    }

    return render(request, "code_page.html", context)


def delete_calculation(request, calculation_id):
    if not Calculation.objects.filter(pk=calculation_id).exists():
        return redirect("/")

    with connection.cursor() as cursor:
        cursor.execute("UPDATE calculations SET status=5 WHERE id = %s", [calculation_id])

    return redirect("/")


def calculation(request, calculation_id):
    if not Calculation.objects.filter(pk=calculation_id).exists():
        return render(request, "404.html")

    calculation = Calculation.objects.get(id=calculation_id)
    if calculation.status == 5:
        return render(request, "404.html")

    context = {
        "calculation": calculation,
    }

    return render(request, "calculation_page.html", context)


def get_draft_calculation():
    return Calculation.objects.filter(status=1).first()


def get_current_user():
    return User.objects.filter(is_superuser=False).first()