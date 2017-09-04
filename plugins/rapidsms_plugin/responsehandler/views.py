import os

from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt


@xframe_options_exempt
def config(request):
    """
    View function of the config page
    :param request:
    :return:
    """

    return render(
        request,
        "config.html",
        context={"phone_number": os.environ.get("TWILIO_NUM")}
    )
