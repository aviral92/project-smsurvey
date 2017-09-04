from django.shortcuts import render

# Create your views here.


def config(request):
    """
    View function of the config page
    :param request:
    :return:
    """

    return render(
        request,
        "config.html",
        context={}
    )
