from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.timezone import now
from django.views import View
from django.views.generic.edit import CreateView, UpdateView

from survey.models import Answer, LikeOrDislike, Question


class QuestionListView(View):
    def get_like_or_dislike(self, record):
        if self.request.user.is_authenticated:
            user_record = record.filter(user=self.request.user).first()
            if user_record:
                return {
                    'user_likes': user_record.like_or_dislike == 1,
                    'user_dislikes': user_record.like_or_dislike == 0,
                }
        return False

    def get_user_value(self, record):
        if self.request.user.is_authenticated:
            user_record = record.filter(author=self.request.user).first()
            if user_record:
                return user_record.value
        return False

    @staticmethod
    def add_ranking_to_today(ranking, created):
        today = now().date()
        return ranking + 10 if created == today else ranking

    @staticmethod
    def get_ranking(record):
        likes = 0
        dislikes = 0
        likes_records = record.likeordislike_set.all()
        answers = record.answers.all().count()

        if likes_records:
            likes = likes_records.filter(like_or_dislike=1).count()
            dislikes = likes_records.filter(like_or_dislike=0).count()

        ranking = answers * 10 + likes * 5 - dislikes * 3
        return ranking

    def get(self, request):
        queryset = Question.objects.all().order_by('-ranking')[:20]
        questions = []

        for question in queryset:
            ranking = self.add_ranking_to_today(question.ranking, question.created)
            data = {
                'title': question.title,
                'author': question.author,
                'description': question.description,
                'pk': question.pk,
                'user_value': self.get_user_value(question.answers),
                'ranking': ranking
            }
            like_or_dislike = self.get_like_or_dislike(question.likeordislike_set)
            question = {**data}
            if like_or_dislike:
                question = {**question, **like_or_dislike}
            questions.append(question)

        questions.sort(key=lambda x: x['ranking'], reverse=True)
        return render(request, 'survey/question_list.html', {'questions': questions})


class QuestionCreateView(CreateView):
    model = Question
    fields = ['title', 'description']
    redirect_url = ''

    def form_valid(self, form):
        form.instance.author = self.request.user

        return super().form_valid(form)


class QuestionUpdateView(UpdateView):
    model = Question
    fields = ['title', 'description']
    template_name = 'survey/question_form.html'


@transaction.atomic
def answer_question(request):
    question_pk = request.POST.get('question_pk')
    value = request.POST.get('value')

    if not request.POST.get('question_pk') and (value and (int(value) > 5 or int(value) < 1)):
        return JsonResponse({'ok': False})
    try:
        question = Question.objects.get(pk=question_pk)
        Answer.objects.update_or_create(question=question,
                                        author=request.user,
                                        defaults={'value': value})
        question.ranking = QuestionListView.get_ranking(question)
        question.save()
        ranking = QuestionListView.add_ranking_to_today(question.ranking, question.created)
        return JsonResponse({'ok': True, 'ranking': ranking})
    except Question.DoesNotExist:
        return JsonResponse({'ok': False})


@transaction.atomic
def like_dislike_question(request):
    question_pk = request.POST.get('question_pk')
    value = request.POST.get('value')

    if not question_pk and (value and int(value) < 2):
        return JsonResponse({'ok': False})
    try:
        question = Question.objects.get(pk=question_pk)
        LikeOrDislike.objects.update_or_create(user=request.user,
                                               question=question,
                                               defaults={
                                                   'like_or_dislike': value,
                                               })
        question.ranking = QuestionListView.get_ranking(question)
        question.save()
        ranking = QuestionListView.add_ranking_to_today(question.ranking, question.created)
        return JsonResponse({'ok': True, 'ranking': ranking})
    except Question.DoesNotExist:
        return JsonResponse({'ok': False})
