from django.shortcuts import redirect
def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('outflow_credit')
    else:
        return redirect('login')
