from django.shortcuts import render
from django.views import View
from django.views.generic import ListView
from .forms import FormOutflow
from .models import ModelOutflow, ModelCreditOutflow, OutflowTypeChoice
from supplier.models import ModelSupplier
from projects.models import ModelProject
import datetime
from dateutil.relativedelta import relativedelta
import threading

# Create your views here.
class ListOutflow(ListView):
    model = ModelOutflow
    template_name = 'outflow.html'
    context_object_name = 'outflows'

    def get_queryset(self):
        outflows = super().get_queryset().order_by('paid', 'date', )
        search = self.request.GET.get('search')
        if search:
            outflows = outflows.filter(expense__icontains=search)
        return outflows

class CreateOutflow(View):
    def get(self, request):
        form = FormOutflow()
        return render(request, 'new_outflow.html', {'form': form})

    def post(self, request):
        form_posted = FormOutflow(request.POST)
        if form_posted.is_valid():
            if request.POST['payment_method'] == 'CRED':
                threading.Thread(
                    target=self.__credit_parcel_creation,
                    args=(request.POST.copy(),)
                ).start()
                
            else:
                outflow = ModelOutflow(
                    expense=request.POST['expense'],
                    favored=ModelSupplier.objects.get(pk=int(request.POST['favored'])) if request.POST['favored'] else None,
                    paid=bool(request.POST['paid']) if 'paid' in request.POST.keys() else False,
                    date=request.POST['date'],
                    payment_method=request.POST['payment_method'],
                    project=ModelProject.objects.get(pk=int(request.POST['project'])) if request.POST['project'] else None,
                    value=float(request.POST['value'])
                )
                outflow.save()
                if 'type' in request.POST.keys():
                    for type in request.POST['type']:
                        outflow.type.add(OutflowTypeChoice.objects.get(pk=int(type)))
        form = FormOutflow()
        return render(request, 'outflow.html', {'form': form})
    
    def __credit_parcel_creation(self, request_data):
        parcel_value = float(request_data['value'])/int(request_data['parcel'])
        for parcel in range(int(request_data['parcel'])):
            date = datetime.datetime.strptime(request_data['date'], '%Y-%m-%d')
            date = (date + relativedelta(months=parcel)).strftime('%Y-%m-%d')
            outflow = ModelCreditOutflow(
                expense=f"{request_data['expense']} - {parcel+1}/{int(request_data['parcel'])}" if int(request_data['parcel'])>1 else request_data['expense'],
                favored=ModelSupplier.objects.get(pk=int(request_data['favored'])) if request_data['favored'] else None,
                date=date,
                project=ModelProject.objects.get(pk=int(request_data['project'])) if request_data['project'] else None,
                value=parcel_value
            )
            outflow.save()
            if 'type' in request_data.keys():
                for type in request_data['type']:
                    outflow.type.add(OutflowTypeChoice.objects.get(pk=int(type)))