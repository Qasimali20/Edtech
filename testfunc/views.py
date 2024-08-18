from django.shortcuts import render,redirect,get_object_or_404
from .models import Test, Question, UserTest, UserAnswer, UserPerformance
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
from django.db.models import Avg
import json
from django.urls import reverse

# Create your views here.
@login_required
def list_tests(request):
    """
    View to list all available tests.
    """
    tests = Test.objects.all()
    return render(request, 'tests/list_tests.html', {'tests': tests})

@login_required
def test_details(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    questions = Question.objects.filter(test=test)

    # Ensure the start time is set when the test is opened
    user_test, created = UserTest.objects.get_or_create(
        user=request.user,
        test=test,
        defaults={'start_time': timezone.now(), 'created_at': timezone.now()}
    )

    # If the user already started the test but start_time is not set, set it now
    if not created and user_test.start_time is None:
        user_test.start_time = timezone.now()
        user_test.save()

    # Fetch user's answers for this test
    user_answers = UserAnswer.objects.filter(user_test=user_test)

    return render(request, 'tests/test_details.html', {
        'test': test,
        'questions': questions,
        'user_answers': user_answers
    })

@login_required
def submit_answers(request, test_id):
    user = request.user
    test = get_object_or_404(Test, id=test_id)

    # Get or create the UserTest entry
    user_test, created = UserTest.objects.get_or_create(
        user=user,
        test=test,
        defaults={'start_time': timezone.now(), 'created_at': timezone.now()}
    )

    if request.method == 'POST':
        end_time = timezone.now()

        # Ensure start_time is set
        if user_test.start_time is None:
            user_test.start_time = timezone.now()
        
        # Calculate time taken from hidden input
        timer_value = request.POST.get('timer_value', '0:0')
        minutes, seconds = map(int, timer_value.split(':'))
        time_taken = minutes * 60 + seconds  # Convert to total seconds

        # Check if all questions have been answered
        all_questions_answered = True
        score = 0

        with transaction.atomic():
            # Remove previous answers for this test
            UserAnswer.objects.filter(user_test=user_test).delete()

            for question in test.question_set.all():
                selected_option = request.POST.get(f'question_{question.id}')
                if not selected_option:
                    all_questions_answered = False
                    break
                
                selected_option = selected_option.strip().lower()
                correct_option = question.correct_option.strip().lower()
                is_correct = (selected_option == correct_option)
                score += 1 if is_correct else 0

                # Create UserAnswer for the current user and question
                UserAnswer.objects.create(
                    user_test=user_test,
                    question=question,
                    selected_option=selected_option.upper(),  # Keep as 'A', 'B', 'C', or 'D'
                    is_correct=is_correct,
                    created_at=end_time  # Use created_at as the timestamp
                )

            if not all_questions_answered:
                # Return to test details with error message if not all questions are answered
                return render(request, 'tests/test_details.html', {
                    'test': test,
                    'questions': test.question_set.all(),
                    'error_message': 'Please answer all questions before submitting.',
                    'timer_value': timer_value  # Pass timer value to preserve it
                })

            # Update the UserTest entry with end_time, time_taken, and score
            user_test.end_time = end_time
            user_test.time_taken = time_taken  # Set time_taken as calculated
            user_test.score = score
            user_test.save()

            # Compute the average difficulty level from the questions
            average_difficulty = test.question_set.aggregate(
                average_difficulty_level=Avg('difficulty_level')
            )['average_difficulty_level'] or 0

            # Create or update UserPerformance
            UserPerformance.objects.update_or_create(
                user=user,
                subject=test.subject,
                defaults={
                    'difficulty_level': average_difficulty,
                    'correct_answers': score,
                    'incorrect_answers': test.question_set.count() - score,
                    'adaptive_score': score * average_difficulty,  # Adjust this calculation as needed
                }
            )

        # Redirect to the test results page with the calculated time_taken as a query parameter
        return redirect(reverse('user_test_results', args=[test.id]) + f'?time_taken={time_taken}')

    return render(request, 'tests/test_details.html', {'test': test})

@login_required
def user_test_results(request, test_id):
    user_test = get_object_or_404(UserTest, user=request.user, test_id=test_id)
    user_answers = user_test.useranswer_set.all()

    # Get time_taken from query parameter if available
    time_taken = request.GET.get('time_taken', None)
    if time_taken:
        minutes, seconds = divmod(int(time_taken), 60)
        time_taken_display = f"{minutes}m {seconds}s"
    else:
        time_taken_display = "N/A"

    return render(request, 'tests/user_test_results.html', {
        'user_test': user_test,
        'user_answers': user_answers,
        'time_taken_display': time_taken_display
    })

@login_required
def user_performance(request):
    performances = UserPerformance.objects.filter(user=request.user)
    subjects = [performance.subject.name for performance in performances]
    correct_answers = [performance.correct_answers for performance in performances]
    incorrect_answers = [performance.incorrect_answers for performance in performances]
    scores = [performance.adaptive_score for performance in performances]

    return render(request, 'tests/user_performance.html', {
        'subjects_json': json.dumps(subjects),
        'correct_answers_json': json.dumps(correct_answers),
        'incorrect_answers_json': json.dumps(incorrect_answers),
        'scores_json': json.dumps(scores)
    })