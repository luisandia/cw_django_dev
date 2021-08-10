from django.test import TestCase
from .models import Question
from django.urls import reverse
from django.contrib.auth import get_user_model
from freezegun import freeze_time


@freeze_time("2012-01-14")
class QuestionModelTest(TestCase):
    def setUp(self):
        self.users = []
        for i in range(6):
            user = get_user_model().objects.create_user(username='testuser{}'.format(i),
                                                        email='test{}@email.com'.format(i),
                                                        password='secret')
            self.users.append(user)

        self.question = Question.objects.create(
            title='Te gustaria trabajar aqui?',
            description='Tu ambiente de trabajo',
            author=self.users[0],
        )

    def verify_ranking_today(self, value):
        response = self.client.get('/')
        question = response.context['questions'][0]
        self.assertEqual(question['ranking'], value)

    def test_rank_question_today(self):
        response = self.client.get('/')
        question = response.context['questions'][0]
        self.assertEqual(question['ranking'], 10)

    @freeze_time("2012-01-15")
    def test_rank_question_not_today(self):
        response = self.client.get('/')
        question = response.context['questions'][0]
        self.assertEqual(question['ranking'], 0)

    def test_rank_question(self):
        for user in self.users:
            self.client.force_login(user)
            response = self.client.post(reverse('survey:question-answer'), {
                'question_pk': 1,
                'value': 1,
            })
            self.assertEqual(response.status_code, 200)
            self.client.logout()
        self.verify_ranking_today(6 * 10 + 10)
        for i in range(2):
            self.client.force_login(self.users[i])
            response = self.client.post(reverse('survey:question-like'), {
                'question_pk': 1,
                'value': 1,
            })
            self.assertEqual(response.status_code, 200)
            self.client.logout()
        self.verify_ranking_today(6 * 10 + 2 * 5 + 10)
        self.client.force_login(self.users[3])
        response = self.client.post(reverse('survey:question-like'), {
            'question_pk': 1,
            'value': 0,
        })
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        self.verify_ranking_today(6 * 10 + 2 * 5 - 1 * 3 + 10)
