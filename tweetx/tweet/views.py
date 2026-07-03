from django.shortcuts import render,redirect,get_object_or_404
from .models import Tweet, Like, Comment
from django.http import JsonResponse
from .forms import TweetForm,UserRegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse



# Create your views here.

def home(request):
    tweets = Tweet.objects.all().order_by('-created_at')
    comments = {}
    for tweet in tweets:
        comments[tweet.id] = tweet.comments.all().order_by('-created_at')
    liked_tweet_ids = []
    if request.user.is_authenticated:
        liked_tweet_ids = Like.objects.filter(user = request.user).values_list('tweet_id', flat=True)
    return render(request, 'index.html', {'tweets':tweets,'liked_tweet_ids':liked_tweet_ids, 'comments': comments})


@login_required
def create_tweet(request):
    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid:
            tweet = form.save(commit=False)
            tweet.user = request.user
            try:
                tweet.save()
                print("tweet save in database")
                return redirect('home')
            except Exception as e:
                import traceback
                error_msg = f"AZURE STORAGE UPLOAD FAILED:\\n\\n{str(e)}\\n\\n{traceback.format_exc()}"
                from django.http import HttpResponse
                return HttpResponse(error_msg, content_type="text/plain", status=500)
    else:
        form = TweetForm()
    return render(request, 'tweet_form.html', {'form':form})


@login_required
def edit_tweet(request,tweet_id):
    tweet = get_object_or_404(Tweet,pk = tweet_id, user = request.user)
    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES, instance=tweet)
        if form.is_valid:
            tweet_temp = form.save(commit=False)
            tweet_temp.user = request.user
            tweet_temp.save()
            return redirect('home')
    else:
        form = TweetForm(instance=tweet)
    return render(request, 'tweet_form.html', {'form':form})


@login_required
def delete_tweet(request,tweet_id):
    tweet = get_object_or_404(Tweet, pk = tweet_id, user = request.user)
    if request.method == 'POST':
        tweet.delete()
        return redirect('home')
    return render(request, 'confirm_delete.html',{'tweet':tweet})


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password1'])
                user.save()
                login(request, user)
                messages.success(request, "Registration successful!")
                return redirect('home')
            except Exception as e:
                messages.error(request, "Registration failed")
        else:
            # Handle non-field errors (like password mismatch)
            if form.non_field_errors():
                for error in form.non_field_errors():
                    messages.error(request, error)
            # Handle field-specific errors
            for field, errors in form.errors.items():
                if field != '__all__':  # Skip non-field errors as we handled them above
                    field_label = form.fields[field].label or field
                    messages.error(request, f"{field_label}: {'. '.join(errors)}")
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def my_tweets(request):
    my_tweets = Tweet.objects.filter(user = request.user ).order_by('-created_at')
    return render(request, 'my_tweets.html', {'tweets':my_tweets})


def like_tweet(request, tweet_id):
    if not request.user.is_authenticated:
            login_url = reverse('login') 
            response = HttpResponse(status=204)
            response['HX-Redirect'] = login_url
            return response

    tweet = get_object_or_404(Tweet, pk=tweet_id)
    like = Like.objects.filter(user=request.user, tweet=tweet).first()
    
    if like:
        like.delete()
    else:
        Like.objects.create(user=request.user, tweet=tweet)
    
    liked_tweet_ids = Like.objects.filter(user=request.user).values_list('tweet_id', flat=True)
    
    context = {
        'tweet': tweet,
        'liked_tweet_ids': liked_tweet_ids
    }

    return render(request, 'partials/like_button.html', context)


def add_comment(request, tweet_id):
    if request.user.is_anonymous:
        login_url = reverse('login')
        response = HttpResponse(status=204)
        response['HX-Redirect'] = login_url
        return response
    tweet = get_object_or_404(Tweet, pk=tweet_id)
    if request.method == 'POST':
        comment_text = request.POST.get('comment', '').strip()

        if comment_text:
            if len(comment_text)<=280:
                Comment.objects.create(user = request.user, tweet = tweet, comment = comment_text)
        
    comments = tweet.comments.all().order_by('-created_at')
    context = {
        'comments': comments,
        'tweet': tweet
    }
    response = render(request, 'partials/comments_list.html', context)
    # Add trigger to update comments count
    response['HX-Trigger'] = f'updateCommentsCount-{tweet_id}'
    return response


def get_comments_count(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id)
    context = {'tweet': tweet}
    return render(request, 'partials/comments_count.html', context)


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, user=request.user)
    tweet = comment.tweet
    
    if request.method == 'POST':
        comment.delete()
        
    comments = tweet.comments.all().order_by('-created_at')
    context = {
        'comments': comments,
        'tweet': tweet
    }
    response = render(request, 'partials/comments_list.html', context)
    # Add trigger to update comments count
    response['HX-Trigger'] = f'updateCommentsCount-{tweet.id}'
    return response
