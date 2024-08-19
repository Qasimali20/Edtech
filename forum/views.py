from django.shortcuts import render, get_object_or_404, redirect
from .models import Thread, Post, Comment
from .forms import ThreadForm, PostForm, CommentForm
from .utils import detect_sentiment
from django.contrib.auth.decorators import login_required

@login_required
def thread_list(request):
    threads = Thread.objects.all()
    return render(request, 'thread_list.html', {'threads': threads})

@login_required
def thread_detail(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    posts = thread.posts.all()

    if request.method == 'POST':
        # Handle post submission
        form = PostForm(request.POST)
        if form.is_valid():
            post_content = form.cleaned_data['content']
            sentiment_score, sentiment_label = detect_sentiment(post_content)
            
            if isinstance(sentiment_score, str):
                try:
                    sentiment_score = float(sentiment_score)
                except ValueError:
                    sentiment_score = 0.0

            if sentiment_label == "NEGATIVE" or sentiment_score < 0.95:
                return render(request, 'thread_detail.html', {
                    'thread': thread,
                    'posts': posts,
                    'form': form,
                    'error_message': "Your post contains inappropriate content."
                })
            
            post = form.save(commit=False)
            post.thread = thread
            post.author = request.user
            post.sentiment_score = sentiment_score
            post.sentiment_label = sentiment_label
            post.save()
            return redirect('thread_detail', thread_id=thread.id)

        # Handle comment submission
        post_id = request.POST.get('post_id')
        if post_id:
            post = get_object_or_404(Post, id=post_id)
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment_content = comment_form.cleaned_data['content']
                sentiment_score, sentiment_label = detect_sentiment(comment_content)
                
                if isinstance(sentiment_score, str):
                    try:
                        sentiment_score = float(sentiment_score)
                    except ValueError:
                        sentiment_score = 0.0

                if sentiment_label == "NEGATIVE" or sentiment_score < 0.95:
                    return render(request, 'thread_detail.html', {
                        'thread': thread,
                        'posts': posts,
                        'form': form,
                        'error_message': "Your comment contains inappropriate content."
                    })
                
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.sentiment_score = sentiment_score
                comment.sentiment_label = sentiment_label
                comment.save()
                return redirect('thread_detail', thread_id=thread.id)

    else:
        form = PostForm()

    return render(request, 'thread_detail.html', {
        'thread': thread,
        'posts': posts,
        'form': form
    })

@login_required
def create_thread(request):
    if request.method == 'POST':
        form = ThreadForm(request.POST)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.creator = request.user
            sentiment_score,sentiment_label = detect_sentiment(thread.title)
            
            # Debugging output
            print(f"Sentiment Label: {sentiment_label}, Sentiment Score: {sentiment_score}")

            # Ensure sentiment_score is a float
            try:
                sentiment_score = float(sentiment_score)
            except (ValueError, TypeError):
                sentiment_score = 0.0  # Default value if conversion fails

            # Debugging output
            print(f"Converted Sentiment Score: {sentiment_score}")

            # Block threads with negative sentiment or positive sentiment below 0.95 score
            if sentiment_label == "NEGATIVE" or sentiment_score < 0.93:
                print("Blocking thread due to inappropriate content.")
                return render(request, 'create_thread.html', {
                    'form': form,
                    'error_message': "Your thread title contains inappropriate content."
                })
            
            thread.sentiment_score = sentiment_score
            thread.sentiment_label = sentiment_label
            thread.save()
            return redirect('thread_list')
        else:
            error_message = "There was an error with your submission."
    else:
        form = ThreadForm()
        error_message = None

    return render(request, 'create_thread.html', {'form': form, 'error_message': error_message})

@login_required
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment_content = form.cleaned_data['content']
            sentiment_score, sentiment_label = detect_sentiment(comment_content)
            
            if isinstance(sentiment_score, str):
                try:
                    sentiment_score = float(sentiment_score)
                except ValueError:
                    sentiment_score = 0.0

            if sentiment_label == "NEGATIVE" or sentiment_score < 0.95:
                return render(request, 'post_comment.html', {
                    'post': post,
                    'form': form,
                    'error_message': "Your comment contains inappropriate content."
                })
            
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.sentiment_score = sentiment_score
            comment.sentiment_label = sentiment_label
            comment.save()
            return redirect('thread_detail', thread_id=post.thread.id)
    else:
        form = CommentForm()

    return render(request, 'post_comment.html', {'post': post, 'form': form})
