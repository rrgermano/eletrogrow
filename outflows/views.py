from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, CreateView
from .forms import FormOutflow, FormUpdateOutflow, FormOutflowTypeChoice
from .models import ModelOutflow, ModelCreditOutflow, OutflowTypeChoice
from dateutil.relativedelta import relativedelta
import threading
from time import sleep


class ListOutflow(LoginRequiredMixin, ListView):
    model = ModelOutflow
    template_name = 'outflow.html'
    context_object_name = 'outflows'

    def get_queryset(self):
        outflows = super().get_queryset().order_by('paid', 'date', )
        search = self.request.GET.get('search')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if search:
            outflows = outflows.filter(expense__icontains=search)
        if start_date:
            outflows = outflows.filter(date__gte=start_date)
        if end_date:
            outflows = outflows.filter(date__lte=end_date)
        return outflows

class CreateOutflow(LoginRequiredMixin, View):

    def get(self, request):
        form = FormOutflow()
        return render(request, 'new_outflow.html', {'form': form})

    def post(self, request):
        form_posted = FormOutflow(request.POST)
        if form_posted.is_valid():
            cleaned_data = form_posted.cleaned_data
            if cleaned_data['payment_method'] == 'CRED':
                threading.Thread(
                    target=self.__credit_parcel_creation,
                    args=(cleaned_data.copy(),)
                ).start()
                return redirect('outflow_credit')
                
            else:
                outflow = ModelOutflow(
                    expense=cleaned_data['expense'],
                    favored=cleaned_data['favored'],
                    paid=cleaned_data['paid'],
                    date=cleaned_data['date'].strftime('%Y-%m-%d'),
                    payment_method=cleaned_data['payment_method'],
                    project=cleaned_data['project'],
                    value=cleaned_data['value'],
                )
                outflow.save()
                outflow.type.set(cleaned_data['type'])
                return redirect('outflow')
    
    def __credit_parcel_creation(self, form):
        parcel_value = form['value']/form['parcel']
        sleep(2)
        for parcel in range(form['parcel']):
            date = form['date']
            date = (date + relativedelta(months=parcel)).strftime('%Y-%m-%d')
            outflow = ModelCreditOutflow(
                expense=f"{form['expense']} - {parcel+1}/{form['parcel']}" if form['parcel']>1 else form['expense'],
                favored=form['favored'],
                date=date,
                project=form['project'],
                value=round(parcel_value, 2)
            )
            outflow.save()
            outflow.type.set(form['type'])

class DetailOutflow(LoginRequiredMixin, DetailView):
    model = ModelOutflow
    template_name = "detail_outflow.html"

class DeleteOutflow(LoginRequiredMixin, DeleteView):
    model = ModelOutflow
    template_name = 'delete_outflow.html'
    success_url = '/outflow/'

class UpdateOutflow(LoginRequiredMixin, UpdateView):
    model = ModelOutflow
    form_class = FormUpdateOutflow
    template_name = 'update_outflow.html'
    success_url = '/outflow/'

    def get_form_class(self):
        # Criar uma classe temporária que herda do seu Form
        original_form = super().get_form_class()
        
        class TempModelForm(original_form):
            def save(self, commit=True):
                # Pegar o objeto da view
                obj = self.instance if hasattr(self, 'instance') else None
                if obj:
                    for field_name in self.cleaned_data:
                        if hasattr(obj, field_name) and field_name != 'type':
                            setattr(obj, field_name, self.cleaned_data[field_name])
                        elif hasattr(obj, field_name) and field_name == 'type':
                            getattr(obj, field_name).set(self.cleaned_data[field_name])
                    if commit:
                        obj.save()
                    return obj
                return None
        
        return TempModelForm
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()  # Passa o objeto para o form
        return kwargs

class ListCreditOutflow(LoginRequiredMixin, ListView):
    model = ModelCreditOutflow
    template_name = 'outflow.html'
    context_object_name = 'outflows'

    def get_queryset(self):
        outflows = super().get_queryset().order_by('date', )
        search = self.request.GET.get('search')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if search:
            outflows = outflows.filter(expense__icontains=search)
        if start_date:
            outflows = outflows.filter(date__gte=start_date)
        if end_date:
            outflows = outflows.filter(date__lte=end_date)
        return outflows

class DetailCreditOutflow(LoginRequiredMixin, DetailView):
    model = ModelCreditOutflow
    template_name = "detail_outflow.html"

class DeleteCreditOutflow(LoginRequiredMixin, DeleteView):
    model = ModelCreditOutflow
    template_name = 'delete_outflow.html'
    success_url = '/outflow/credit/'

class UpdateCreditOutflow(LoginRequiredMixin, UpdateView):
    model = ModelCreditOutflow
    form_class = FormUpdateOutflow
    template_name = 'update_outflow.html'
    success_url = '/outflow/credit/'

    def get_form_class(self):
        # Criar uma classe temporária que herda do seu Form
        original_form = super().get_form_class()
        
        class TempModelForm(original_form):
            def save(self, commit=True):
                # Pegar o objeto da view
                obj = self.instance if hasattr(self, 'instance') else None
                if obj:
                    for field_name in self.cleaned_data:
                        if hasattr(obj, field_name) and field_name != 'type':
                            setattr(obj, field_name, self.cleaned_data[field_name])
                        elif hasattr(obj, field_name) and field_name == 'type':
                            getattr(obj, field_name).set(self.cleaned_data[field_name])
                    if commit:
                        obj.save()
                    return obj
                return None
        
        return TempModelForm
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()  # Passa o objeto para o form
        return kwargs

class CreateOutflowTypeChoice(LoginRequiredMixin, CreateView):
    model = OutflowTypeChoice
    form_class = FormOutflowTypeChoice
    template_name = 'new_outflow.html'
    success_url = '/outflow/new/'

class UpdateOutflowTypeChoice(LoginRequiredMixin, UpdateView):
    model = OutflowTypeChoice
    form_class = FormOutflowTypeChoice
    template_name = 'update_outflow.html'
    success_url = '/outflow/new/'

class DeleteOutflowTypeChoice(LoginRequiredMixin, DeleteView):
    model = OutflowTypeChoice
    template_name = 'delete_outflow.html'
    success_url = '/outflow/new/'