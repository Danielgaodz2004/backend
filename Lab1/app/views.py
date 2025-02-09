from django.shortcuts import render

codes = [
    {
        "id": 1,
        "name": "01001001000100",
        "description": "01001001000100010010010001000100100100010001001001000100010010010001000100100100010001001001000100010010010001000100100100010001001001000100",
        "weight": "128",
        "image": "http://localhost:9000/images/1.png"
    },
    {
        "id": 2,
        "name": "101000101101101",
        "description": "101000101101101101000101101101101000101101101101000101101101101000101101101101000101101101101000101101101101000101101101101000101101101101000101101101101000101101101",
        "weight": "64",
        "image": "http://localhost:9000/images/2.png"
    },
    {
        "id": 3,
        "name": "0101011110101010",
        "description": "01010111101010100101011110101010010101111010101001010111101010100101011110101010010101111010101001010111101010100101011110101010010101111010101001010111101010100101011110101010",
        "weight": "32",
        "image": "http://localhost:9000/images/3.png"
    },
    {
        "id": 4,
        "name": "10110111101101001",
        "description": "10110111101101001101101111011010011011011110110100110110111101101001101101111011010011011011110110100110110111101101001101101111011010011011011110110100110110111101101001",
        "weight": "256",
        "image": "http://localhost:9000/images/4.png"
    },
    {
        "id": 5,
        "name": "10101101011001010",
        "description": "10101101011001010101011010110010101010110101100101010101101011001010101011010110010101010110101100101010101101011001010101011010110010101010110101100101010101101011001010101011010110010101010110101100",
        "weight": "128",
        "image": "http://localhost:9000/images/5.png"
    },
    {
        "id": 6,
        "name": "010101001001010010",
        "description": "0101010010010100100101010010010100100101010010010100100101010010010100100101010010010100100101010010010100100101010010010100100101010010010100100101010010010100100101010010010100100101010010010100100101010",
        "weight": "16",
        "image": "http://localhost:9000/images/6.png"
    }
]

draft_calculation = {
    "id": 123,
    "status": "Черновик",
    "date_created": "12 сентября 2024г",
    "type": "Шифрование",
    "codes": [
        {
            "id": 1,
            "value": 1
        },
        {
            "id": 2,
            "value": 2
        },
        {
            "id": 3,
            "value": 3
        }
    ]
}


def getCodeById(code_id):
    for code in codes:
        if code["id"] == code_id:
            return code


def getCodes():
    return codes


def searchCodes(code_name):
    res = []

    for code in codes:
        if code_name.lower() in code["name"].lower():
            res.append(code)

    return res


def getDraftCalculation():
    return draft_calculation


def getCalculationById(calculation_id):
    return draft_calculation


def index(request):
    code_name = request.GET.get("code_name", "")
    codes = searchCodes(code_name) if code_name else getCodes()
    draft_calculation = getDraftCalculation()

    context = {
        "codes": codes,
        "code_name": code_name,
        "codes_count": len(draft_calculation["codes"]),
        "draft_calculation": draft_calculation
    }

    return render(request, "codes_page.html", context)


def code(request, code_id):
    context = {
        "id": code_id,
        "code": getCodeById(code_id),
    }

    return render(request, "code_page.html", context)


def calculation(request, calculation_id):
    calculation = getCalculationById(calculation_id)
    codes = [
        {**getCodeById(code["id"]), "value": code["value"]}
        for code in calculation["codes"]
    ]

    context = {
        "calculation": calculation,
        "codes": codes
    }

    return render(request, "calculation_page.html", context)
