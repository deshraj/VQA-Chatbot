from django.shortcuts import render


def home(request, template_name="index.html"):
    return render(request, template_name, {})


