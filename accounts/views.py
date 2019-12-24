from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from accounts.models import Favorite
from django.shortcuts import render, redirect, reverse
from urllib.parse import urlencode
from django.core.paginator import Paginator
from stocks.models import Company

 
class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


@login_required
def favorite(request):
    code = request.POST.get('code', 1400)
    before = request.GET.get('before')
    user = request.user
    prime = str(user) + ':' + str(code)
    try:
        favorite = Favorite.objects.create(
            prime=prime,
            user=user,
            code=code,
        )
    except:
        Favorite.objects.get(user=user, code=code).delete()
    return redirect(before)


@login_required
def my_page(request):
    page = request.GET.get('page')
    query = Favorite.objects.filter(user=request.user).order_by('code')
    codes = [row.code for row in query]
    names = [Company.objects.get(code=c).name for c in codes]
    result = [[c,n] for c, n in zip(codes, names)]
    paginator = Paginator(result, 20)
    content = paginator.get_page(page)
    return render(request, 'my_page.html', {'content':content})