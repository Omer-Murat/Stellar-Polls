from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Question
import datetime

class PollStatsTests(TestCase):
    def test_active_poll_count(self):
        """
        Tests that IndexView correctly counts active polls.
        Active: end_date is null OR end_date > now.
        """
        now = timezone.now()
        # Active poll (no end date)
        Question.objects.create(question_text="Active 1", start_date=now - datetime.timedelta(days=1), is_approved=True)
        # Active poll (future end date)
        Question.objects.create(question_text="Active 2", start_date=now - datetime.timedelta(days=1), end_date=now + datetime.timedelta(days=1), is_approved=True)
        # Finished poll (past end date)
        Question.objects.create(question_text="Finished", start_date=now - datetime.timedelta(days=2), end_date=now - datetime.timedelta(days=1), is_approved=True)
        
        user = User.objects.create_user(username='index_user', password='password')
        self.client.login(username='index_user', password='password')
        
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_active_polls'], 2)
        self.assertEqual(response.context['total_finished_polls'], 1)

    def test_end_date_validation(self):
        """
        Tests that end_date cannot be before start_date.
        """
        now = timezone.now()
        start = now
        end = now - datetime.timedelta(days=1)
        q = Question(question_text="Invalid Dates", start_date=start, end_date=end)
        with self.assertRaises(ValidationError):
            q.clean()

    def test_start_date_ordering(self):
        """
        Tests that MyPollsView orders by start_date descending.
        """
        user = User.objects.create_user(username='testuser_stats', password='password')
        q1 = Question.objects.create(question_text="Old Poll", start_date=timezone.now() - datetime.timedelta(days=2), author=user)
        q2 = Question.objects.create(question_text="New Poll", start_date=timezone.now() - datetime.timedelta(days=1), author=user)
        
        self.client.login(username='testuser_stats', password='password')
        response = self.client.get(reverse('polls:my_polls'))
        self.assertEqual(list(response.context['latest_question_list']), [q2, q1])
