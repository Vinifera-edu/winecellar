from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.views import generic
from django.db.models import Sum
from wine.models import Wine
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from wine.forms import WineForm
import csv
import xlwt
import datetime
from datetime import datetime
from django.contrib.auth.models import User
import openai
import base64


def create_admin(request):
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin1234')
        return HttpResponse("Admin user created!")
    else:
        return HttpResponse("Admin user already exists.")


class WinesView(LoginRequiredMixin, generic.ListView):
    model = Wine
    template_name = 'wine/wine_list.html'

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class DeleteView(LoginRequiredMixin, DeleteView):
    model = Wine
    success_url = reverse_lazy('wine:wine_list')

def index(request):
    return render(request, 'wine/home.html')

def about(request):
    return render(request, 'wine/about.html')

@login_required
def info(request):
    return render(request, 'wine/info.html')

@login_required
def home(request):
    return render(request, 'wine/index.html')

@login_required
def createWine(request):
    ai_data = request.session.pop('ai_wine_data', None)

    if request.method == 'POST':
        form = WineForm(request.POST, request.FILES)
        if form.is_valid():
            wine = form.save(commit=False)
            wine.owner = request.user
            wine.save()
            return redirect('/wine')
    else:
        form = WineForm(initial=ai_data if ai_data else None)

    return render(request, 'wine/create_form.html', {'form': form})


@login_required
def updateWine(request, pk):
    wine_instance = Wine.objects.get(id=pk)
    if request.method == 'POST':
        form = WineForm(request.POST, request.FILES, instance=wine_instance)
        if form.is_valid():
            wine = form.save(commit=False)
            wine.owner = request.user
            wine.save()
            return redirect('/wine')
    else:
        form = WineForm(instance=wine_instance)
    return render(request, 'wine/create_form.html', {'form': form})


@login_required
def copyWine(request, pk):
    original_wine = Wine.objects.get(id=pk)
    if request.method == 'POST':
        form = WineForm(request.POST, request.FILES)
        if form.is_valid():
            wine = form.save(commit=False)
            wine.owner = request.user
            wine.save()
            return redirect('/wine')
    else:
        form = WineForm(instance=original_wine)
    return render(request, 'wine/create_form.html', {'form': form})


class FullView(LoginRequiredMixin, generic.ListView):
    model = Wine
    template_name = 'wine/wine_fullview.html'

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class WineLog(LoginRequiredMixin, generic.ListView):
    model = Wine
    template_name = 'wine/wine_log.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bottles_sum'] = Wine.objects.filter(owner=self.request.user).aggregate(Sum('nmbrbottles'))['nmbrbottles__sum']
        context['wines_sum'] = Wine.objects.filter(owner=self.request.user).count()
        return context

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user).order_by('-editdate')[:30]


@login_required
def WineLogDetail(request, pk):
    wine = Wine.objects.get(id=pk)
    return render(request, 'wine/wine_log_detail.html', {'wine': wine})

@login_required
def export_csv(request):
    wines = Wine.objects.filter(owner=request.user)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="wine_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['Wein', 'Produzent', 'Trauben', 'Jahrgang', 'Land', 'Region', 'Kaufdatum', 'Preis/Fl.', 'Dealer', 'von', 'bis', 'Lagerort', 'Anz.Fl'])
    for wine in wines.values_list('winename','producer', 'grapes', 'year', 'country', 'region', 'purchase', 'price', 'dealer', 'drinkfrom', 'drinkto', 'warehouse', 'nmbrbottles'):
        writer.writerow(wine)
    return response

@login_required
def export_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="wine_export.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('MyBottles', cell_overwrite_ok=True)
    columns = ['Wein', 'Produzent', 'Trauben', 'Jahrgang', 'Land', 'Region', 'Kaufdatum', 'Preis/Fl.', 'Dealer', 'von', 'bis', 'Lagerort', 'Anz.Fl']
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    for col_num, column_title in enumerate(columns):
        ws.write(0, col_num, column_title, font_style)
    font_style = xlwt.XFStyle()
    date_style = xlwt.XFStyle()
    date_style.num_format_str = "dd.mm.YYYY"
    for row_num, wine in enumerate(Wine.objects.filter(owner=request.user).values_list('winename','producer', 'grapes', 'year', 'country', 'region', 'purchase', 'price', 'dealer', 'drinkfrom', 'drinkto', 'warehouse', 'nmbrbottles'), start=1):
        for col_num, value in enumerate(wine):
            if col_num == 6 and isinstance(value, datetime):
                ws.write(row_num, col_num, value, date_style)
            else:
                ws.write(row_num, col_num, value, font_style)
    wb.save(response)
    return response

@login_required
def analyze_wine_image(request):
    if request.method == 'POST' and request.FILES.get('wine_image'):
        image_file = request.FILES['wine_image']
        image_b64 = base64.b64encode(image_file.read()).decode('utf-8')
        response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": "Describe this wine label and extract the wine name, producer, country, region, grape type, and year."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
                ]}
            ],
            max_tokens=1000
        )
        text = response.choices[0].message['content']
        request.session['ai_wine_data'] = text
        return redirect('wine:create_wine')
    return render(request, 'wine/analyze_image.html')
