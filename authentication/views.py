from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.views.generic import ListView
from django.contrib.auth import logout, login, authenticate
from django.template import RequestContext
from django.views.generic import FormView
from django.contrib.auth.forms import AuthenticationForm

from .forms import RegistrationForm
from books.models import Book
from people.models import Beneficiary, Donor

class RegistrationView(FormView):

    template_name = "authentication/registration.html"
    form_class = RegistrationForm
    def get_success_url(self):
        return reverse('books:listofbooks')


class DonorRegistrationView(RegistrationView):

    def get_context_data(self, **kwargs):
        kwargs = super(DonorRegistrationView, self).get_context_data(**kwargs)
        kwargs['formname'] = 'Donor'
        kwargs['post_url'] = reverse('accounts:donor')
        return kwargs

    def form_valid(self, form):
        user = form.save(commit=False)
        user.email = form.cleaned_data['email']
        user.save()
        user.profile.is_donor = True
        user.profile.save()
        Donor.objects.create(
            user=user, address=form.cleaned_data['address'],
            website=form.cleaned_data['website'])
        user = authenticate(username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'])
        if user is not None and user.is_active:
            login(self.request, user)
        return super(DonorRegistrationView, self).form_valid(form)


class BeneficiaryRegistrationView(RegistrationView):

    def get_context_data(self, **kwargs):
        kwargs = super(BeneficiaryRegistrationView, self).get_context_data(**kwargs)
        kwargs['formname'] = 'Beneficiary'
        kwargs['post_url'] = reverse('accounts:beneficiary')
        return kwargs

    def form_valid(self, form):
        user = form.save(commit=False)
        user.email = form.cleaned_data['email']
        user.save()
        user.profile.is_beneficiary = True
        user.profile.save()
        Beneficiary.objects.create(
            user=user, address=form.cleaned_data['address'],
            website=form.cleaned_data['website'])
        user = authenticate(username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'])
        if user is not None and user.is_active:
            login(self.request, user)
        return super(BeneficiaryRegistrationView, self).form_valid(form)


def user_login(request):
    login_form = AuthenticationForm()
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('books:listofbooks'))
    if request.method == 'POST':
        login_form = AuthenticationForm(data=request.POST)
        if login_form.is_valid():
            user = login_form.get_user()
            login(request, user)
            return HttpResponseRedirect(reverse('books:listofbooks'))
    return render_to_response("authentication/login.html", {'form': login_form},
                              context_instance=RequestContext(request))


def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('accounts:login'))


def approve(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if user:
        user.beneficiary.is_approved = True
        user.beneficiary.save()
        return HttpResponseRedirect(reverse('customadmin:unapproved'))
    return render_to_response('unapproved_users.html')


class UnapprovedUsers(ListView):
    template_name = 'authentication/unapproved_users.html'
    context_object_name = 'unapproved_users'

    def get_queryset(self):
        """
        Returns the unapproved users related to beneficiary in
        the database

        """

        return User.objects.filter(beneficiary__is_approved=False)


class CustomAdminIndex(ListView):
    template_name = 'authentication/customadmin_index.html'
    context_object_name = 'books'

    def get_queryset(self):
        return Book.objects.all()
