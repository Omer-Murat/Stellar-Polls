from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.utils import timezone
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

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
            pub_date__lte=timezone.now(),
            is_public=True
        ).order_by("-pub_date")[:5]


class DetailView(LoginRequiredMixin, generic.DetailView):
    model = Question
    template_name = "polls/detail.html"
    
    def get_queryset(self):
        """Excludes any questions that aren't published yet."""
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(LoginRequiredMixin, generic.DetailView):
    model = Question
    template_name = "polls/results.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = context['question']
        
        # Calculate total votes
        total_votes = sum(choice.votes for choice in question.choice_set.all())
        context['total_votes'] = total_votes
        
        # Calculate percentages and attach to choices, ensuring they sum to 100
        choices = list(question.choice_set.all())
        if total_votes > 0:
            # calculate exact float percentages
            for choice in choices:
                choice.exact_percentage = (choice.votes / total_votes) * 100
                choice.percentage = int(choice.exact_percentage) # floor to start
            
            # calculate how much percentage is missing from 100
            current_sum = sum(choice.percentage for choice in choices)
            remainder = 100 - current_sum
            
            # distribute remainder to choices with highest fractional part
            choices.sort(key=lambda c: c.exact_percentage - c.percentage, reverse=True)
            for i in range(remainder):
                choices[i].percentage += 1
                
            # restore original order (e.g., by id)
            choices.sort(key=lambda c: c.id)
        else:
            for choice in choices:
                choice.percentage = 0
                
        context['choices'] = choices
        return context


@login_required
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    
    if question.is_expired:
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "Bu anketin süresi dolmuştur, artık oy kullanamazsınız.",
            },
        )
        
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "Herhangi bir seçenek belirlemediniz.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))

# --- USER POLL MANAGEMENT VIEWS ---

class MyPollsView(LoginRequiredMixin, generic.ListView):
    template_name = "polls/my_polls.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return polls authored by the logged in user."""
        return Question.objects.filter(author=self.request.user).order_by("-pub_date")

class PollCreateView(LoginRequiredMixin, generic.CreateView):
    model = Question
    fields = ['question_text', 'is_public', 'end_date']
    template_name = "polls/poll_form.html"
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.pub_date = timezone.now()
        return super().form_valid(form)
        
    def get_success_url(self):
        return reverse("polls:manage", kwargs={"pk": self.object.pk})

class PollManageView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Question
    fields = ['question_text', 'is_public', 'end_date']
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
