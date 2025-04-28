from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.http import HttpResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Complaint, Feedback
from .forms import FeedbackForm
from users.models import Employee
from django.core.mail import send_mail

FROM_EMAIL = "talktopujas@gmail.com"  # random
SUBJECT = "Complaint Number : {}"
BODY_NEW_COMPLAINT = "A new complaint with number : {} has been registered with our system. Status {}."
BODY_UPDATE_COMPLAINT = "Status of complaing number : {} changed to : {}."

def send_email(from_email, to_email, complaint_number, complaint_status, is_new = True):
    print(from_email, to_email)
    from_email = FROM_EMAIL
    subject = SUBJECT.format(complaint_number)
    recipient_list = [to_email]

    body_template =  BODY_NEW_COMPLAINT if is_new else BODY_UPDATE_COMPLAINT
    body = body_template.format(complaint_number, complaint_status)
    try:
        send_mail(subject, body, from_email, recipient_list)
        print("email sent")
    except:
        print("could not send email")

@login_required
def complaint_list(request):
    complaint_exists = True
    if request.user.profile.is_employee:
        employee_id = Employee.objects.get(employee=request.user)
        user_complaints = Complaint.objects.filter(
            assigned_employee=employee_id).order_by('-id')

    else:
        user_complaints = Complaint.objects.filter(
            user_id=request.user).order_by('-id')

    if len(user_complaints) == 0:
        complaint_exists = False

    paginator = Paginator(user_complaints, 3) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'complaints': page_obj, 
        'complaint_exists': complaint_exists,
        'page_obj': page_obj,
    }
    print(request.user.first_name is "")
    return render(request, 'index.html', context)


@login_required
def complaint_detail(request, pk):
    complaint = get_object_or_404(Complaint, id=pk)
    if request.user.profile.is_employee:
        employee_id = Employee.objects.get(employee=request.user)
        if employee_id != complaint.assigned_employee:
            return HttpResponse('<h1>HTTP 403: Access Denied</h1>', status=403)

    else:
        if request.user != complaint.user_id:
            return HttpResponse('<h1>HTTP 403: Access Denied</h1>', status=403)

    feedbacks = Feedback.objects.filter(complaint=complaint).order_by('id')

    if request.method == 'POST':
        feedback_form = FeedbackForm(request.POST or None)
        if feedback_form.is_valid():
            content = request.POST.get('content')
            feedback = Feedback.objects.create(
                complaint=complaint, user=request.user, content=content)
            feedback.save()
            return HttpResponseRedirect(complaint.get_absolute_url())

    else:
        feedback_form = FeedbackForm()

    context = {
        'complaint': complaint,
        'feedbacks': feedbacks,
        'feedback_form': feedback_form,
    }
    return render(request, 'complaint_detail.html', context)

@login_required
def status_change(request, pk):
    complaint = get_object_or_404(Complaint, id=pk)
    if request.user.profile.is_employee:
        employee_id = Employee.objects.get(employee=request.user)
        if employee_id != complaint.assigned_employee:
            return HttpResponse('<h1>HTTP 403: Access Denied</h1>', status=403)

    else:
        if request.user != complaint.user_id:
            return HttpResponse('<h1>HTTP 403: Access Denied</h1>', status=403)

    form = request.POST.dict()
    if 'Solved' in form:
        print('Solved')
        complaint.status = 2
        complaint.save()
    if 'Pending' in form:
        print('Pending')
        complaint.status = 1
        complaint.save()
    print()
    send_email(FROM_EMAIL, complaint.user.email, complaint.id, complaint.status, False)
    return HttpResponseRedirect(complaint.get_absolute_url())

class ComplaintCreateView(LoginRequiredMixin, CreateView):
    model = Complaint
    template_name = 'complaint_create.html'
    fields = ['title', 'details']

    def form_valid(self, form):
        form.instance.user_id = self.request.user
        to_email = self.request.user.email
        response = super().form_valid(form)
        complaint = form.instance
        send_email(FROM_EMAIL, to_email, complaint.id, complaint.status, True)
        return response


class ComplaintUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Complaint
    template_name = 'complaint_create.html'
    fields = ['title', 'details']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def test_func(self):
        complaint = self.get_object()
        if self.request.user == complaint.user_id:
            return True
        return False


class ComplaintDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Complaint
    template_name = 'complaint_confirm_delete.html'
    success_url = '/'

    def test_func(self):
        complaint = self.get_object()
        if self.request.user == complaint.user_id:
            return True
        return False
