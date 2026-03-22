from django.db.models import F, Count, Q
import json
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.utils import timezone
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from .forms import PollForm

class RegisterView(generic.CreateView):
    form_class = UserCreationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("polls:index")
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)

from .models import Choice, Question


class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future, and only those that are public).
        """
        return Question.objects.filter(
            start_date__lte=timezone.now(),
            is_public=True
        ).annotate(total_votes_count=Count('vote')).order_by("-start_date")[:5]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        
        # Calculate statistics efficiently using Q objects
        stats = Question.objects.aggregate(
            total_active_polls=Count('id', filter=Q(is_public=True) & (Q(end_date__isnull=True) | Q(end_date__gt=now))),
            total_finished_polls=Count('id', filter=Q(end_date__lt=now))
        )
        
        context.update(stats)
        context['total_users'] = User.objects.count()
        context['total_polls'] = Question.objects.count()
        return context


class DetailView(LoginRequiredMixin, generic.DetailView):
    model = Question
    template_name = "polls/detail.html"
    
    def get_queryset(self):
        """Excludes any questions that aren't published yet."""
        return Question.objects.filter(start_date__lte=timezone.now())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = self.get_object()
        user_voted = Vote.objects.filter(user=self.request.user, question=question).exists()
        context['user_voted'] = user_voted
        
        if user_voted or question.is_finished:
            choices = question.choice_set.all()
            total_votes = sum(choice.votes for choice in choices)
            context['choices'] = choices
            context['total_votes'] = total_votes
            context['chart_labels_json'] = json.dumps([c.choice_text for c in choices])
            context['chart_data_json'] = json.dumps([c.votes for c in choices])
            for choice in choices:
                choice.percentage = int((choice.votes / total_votes) * 100) if total_votes > 0 else 0
        return context


class ResultsView(LoginRequiredMixin, generic.DetailView):
    model = Question
    template_name = "polls/results.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = context['question']
        choices = question.choice_set.all()
        
        # Calculate total votes
        total_votes = sum(choice.votes for choice in choices)
        context['total_votes'] = total_votes
        
        # Data for Chart.js
        chart_labels = [choice.choice_text for choice in choices]
        chart_data = [choice.votes for choice in choices]
        context['chart_labels_json'] = json.dumps(chart_labels)
        context['chart_data_json'] = json.dumps(chart_data)
        
        # Calculate percentages for standard display
        if total_votes > 0:
            for choice in choices:
                choice.percentage = int((choice.votes / total_votes) * 100)
        else:
            for choice in choices:
                choice.percentage = 0
                
        context['choices'] = choices
        return context


@login_required
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    
    # 1. Protection: Check if already voted
    if Vote.objects.filter(user=request.user, question=question).exists():
        from django.contrib import messages
        messages.warning(request, "Bu ankete daha önce oy verdiniz.")
        if request.headers.get('HX-Request'):
             return render(request, "polls/partials/vote_notification.html", {"message": "Daha önce oy verdiniz!", "type": "warning"})
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))

    # 2. Protection: Expiration check
    if question.is_finished:
        if request.headers.get('HX-Request'):
             return render(request, "polls/partials/vote_notification.html", {"message": "Anket süresi doldu.", "type": "error"})
        return render(request, "polls/detail.html", {"question": question, "error_message": "Anket süresi doldu."})
        
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(request, "polls/detail.html", {"question": question, "error_message": "Geçerli bir seçenek belirlemediniz."})
    else:
        # Create Vote
        Vote.objects.create(user=request.user, question=question, choice=selected_choice)
        # Update choice votes count
        selected_choice.votes = F("votes") + 1
        selected_choice.save()

        if request.headers.get('HX-Request'):
            # Manual context data prep for partial to match ResultsView
            choices = question.choice_set.all()
            total_votes_agg = sum(choice.votes for choice in choices)
            chart_labels = [choice.choice_text for choice in choices]
            chart_data = [choice.votes for choice in choices]
            context = {
                "question": question,
                "choices": choices,
                "total_votes": total_votes_agg,
                "chart_labels_json": json.dumps(chart_labels),
                "chart_data_json": json.dumps(chart_data),
            }
            return render(request, "polls/partials/vote_results_partial.html", context)

        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))

# --- USER POLL MANAGEMENT VIEWS ---

class MyPollsView(LoginRequiredMixin, generic.ListView):
    template_name = "polls/my_polls.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return polls authored by the logged in user."""
        return Question.objects.filter(author=self.request.user).order_by("-start_date")

class PollCreateView(LoginRequiredMixin, generic.CreateView):
    model = Question
    form_class = PollForm
    template_name = "polls/poll_form.html"
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        # Start date handling if not provided
        if not form.cleaned_data.get('start_date'):
            form.instance.start_date = timezone.now()
        return super().form_valid(form)
        
    def get_success_url(self):
        return reverse("polls:manage", kwargs={"pk": self.object.pk})

class PollManageView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Question
    form_class = PollForm
    template_name = "polls/poll_manage.html"

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user

    def get_success_url(self):
        return reverse("polls:manage", kwargs={"pk": self.object.pk})

class PollDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = Question
    template_name = "polls/poll_confirm_delete.html"
    success_url = reverse_lazy("polls:my_polls")

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user

class ChoiceCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = Choice
    fields = ['choice_text']
    template_name = "polls/choice_form.html"

    def test_func(self):
        question = get_object_or_404(Question, pk=self.kwargs['question_id'])
        return question.author == self.request.user

    def form_valid(self, form):
        form.instance.question = get_object_or_404(Question, pk=self.kwargs['question_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("polls:manage", kwargs={"pk": self.kwargs['question_id']})

class ChoiceUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Choice
    fields = ['choice_text']
    template_name = "polls/choice_form.html"

    def test_func(self):
        obj = self.get_object()
        return obj.question.author == self.request.user

    def get_success_url(self):
        return reverse("polls:manage", kwargs={"pk": self.object.question.pk})

class ChoiceDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = Choice
    template_name = "polls/choice_confirm_delete.html"

    def test_func(self):
        obj = self.get_object()
        return obj.question.author == self.request.user

    def get_success_url(self):
        return reverse("polls:manage", kwargs={"pk": self.object.question.pk})
