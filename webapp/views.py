from django.shortcuts import render, redirect, render_to_response, get_object_or_404
from .forms import UserForm
from django.contrib.auth import authenticate, login
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login as auth_login
from django.conf import settings
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.template import RequestContext
from django.contrib.auth.decorators import user_passes_test
from .models import Post, Comment, SearchTerm
from .forms import PostForm, CommentForm, SearchForm
from django.core.urlresolvers import reverse
from django.utils import timezone
from hitcount.models import HitCount
from hitcount.views import HitCountMixin
import operator
import math

posts = Post.objects.all().filter().order_by('-created_on')
searchPosts = Post.objects.all().filter().order_by('-created_on')

def post_info(posts, context):
    '''
        Generates the number of comments and the report link for each post.

        Parameters:
            posts (QuerySet) -> The posts / threads for Devhaven.io 
            context (dict) -> The context provided to this function, so that the posts can be updated
            with the new information
    '''
    for post in posts:
        post.commentCount = len(post.comment_set.all())
        # Generate mailto link (html href doesn't allow concatenation of strings)
        post.reportLink = "mailto:henry.david.zhu@gmail.com?Subject=Flagged%20-%20" + post.title + "%20(Reason%20below)"

    context['posts'] = posts

def chunk_posts(posts, space):
    '''
        Divids a list of posts into evenly spaced sublists to use for page indexing.

        Parameters:
            posts (QuerySet) -> The posts / threads for Devhaven.io
            space (int) -> The number of posts / threads for each page / sublist

        Returns:
            chunk_threads (2-dimensional list) -> The list of posts for each page

        Example (given space = 3):
            posts = [post0, post1, post2, post3, post4, post5, post6, post7]
            return: chunk_threads = [[post0, post1, post2], [post3, post4, post5], [post6, post7]]
            page indexing:
                    page | post(s)
                    --------------
                    1    | 0, 1, 2
                    --------------
                    2    | 3, 4, 5
                    --------------
                    3    | 6, 7
    '''
    chunk_threads = []

    for i in range(0, len(posts), space):
        chunk_threads.append(posts[i : i + space]) # Add the list of posts on page (i) to chunk_threads

    return chunk_threads

def index(request):
    '''
        The main function for Devhaven.io's main page. Processes / analyzes data and loads the main
        page for the user

        Parameters:
            request -> A request to home.html (main page)

        Returns:
            render -> Loads the main page for the user
    '''
    global posts, searchPosts # Retrieve all of Devhaven.io's posts (posts), and the specific posts
    # from searching for a specific category (searchPosts)

    posts = Post.objects.all().filter().order_by('-created_on') # Use filter on the QuerySet to sort by time
    context = {'posts' : posts, 'authenticated': request.user.is_authenticated(), 'search': False}

    # Calculates the first post to display to the user
    if (len(posts) > 0): 
        context['post'] = posts[0]
    else:
        context['post'] = None

    if request.method == "POST":
        searchForm = SearchForm(request.POST or None)

        if searchForm.is_valid(): # If the user has searched for a specific category
            category = searchForm.cleaned_data.get('category')

            if category == 'all': # Redirect the user back to the main page with all of the posts
                return redirect("../")
                context['search'] = False
            else: # Filter the posts specific to the category searched by the user
                searchPosts = Post.objects.all().filter(field=category).order_by('-created_on')
                context['posts'] = searchPosts
                posts = searchPosts
                context['search'] = True

                if (len(posts) > 0):
                    context['post'] = posts[0]
                else:
                    context['post'] = None

                post_info(searchPosts, context)
                
                return render(request, 'webapp/home.html', context)
        else:
            pass

        post = context['post'] # Set the first post of the webpage
        form = CommentForm(request.POST or None) # The form in which the user writes a comment / response

        # Retrieve user hits on the page -> analyze behavior of view counts
        hit_count = HitCount.objects.get_for_object(post)
        hit_count_response = HitCountMixin.hit_count(request, hit_count)
        print(hit_count_response)
        
        if form.is_valid(): # Check if the comment form is properly filled out
            comment = form.save(commit=False)
            comment.post = post

            try:
                comment.name = request.user
            except Exception as e:
                print("Exception when trying to set a comment's name: {0}".format(str(e)))
                
            comment.save()
            return redirect(request.path)
        else:
            print(form.is_valid())
            print(form.errors)

    post_info(posts, context) # Set the information of the posts
    print(chunk_posts(posts, 10)) # Test the chunk_posts function
    return render(request, 'webapp/home.html', context)

def userprofile(request, author):
    '''
        Creates the user profile for a user

        Parameters:
            request -> request to the user profile page (userprofile.html)
            author (str) -> the name of the author / user

        Returns:
            render -> Loads the user profile page to the user
    '''
    userPosts = Post.objects.all().filter(author__username=author).order_by('created_on').reverse()

    for post in userPosts:
        post.commentCount = len(post.comment_set.all())

    for post in userPosts: # Generate mailto link (html href doesn't allow concatenation of strings)
        post.reportLink = "mailto:henry.david.zhu@gmail.com?Subject=Flagged%20-%20" + post.title + "%20(Reason%20below)"

    context = {'posts': userPosts, 'authenticated': request.user.is_authenticated(), 'username': author}

    if len(userPosts) > 0:
        context['post'] = userPosts[0]
    else:
        context['post'] = None

    if request.method == "POST":
        post = context['post']
        form = CommentForm(request.POST or None)
        hit_count = HitCount.objects.get_for_object(post)
        hit_count_response = HitCountMixin.hit_count(request, hit_count)
            
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post

            try:
                comment.name = request.user
            except Exception as e:
                print("Exception when trying to set a comment's name: {0}".format(str(e)))
                    
            comment.save()
            return redirect(request.path)
        else:
            print(form.is_valid())
            print(form.errors)

    post_info(userPosts, context)

    return render(request, 'webapp/userprofile.html', context)

def register(request):
    '''
        Registers the user to Devhaven.io

        Parameters:
            request -> request to the registration page (register.html)

        Returns:
            render -> Loads the registration page to the user
    '''
    form = UserForm(request.POST or None) # Create a registration form
    title = "Register." # Title of the registration form
    instruction = "The <b>email*</b> is required but only the username is displayed." #Instruction towards user
    displaySignUp = True # Only display the sign up if the user hasn't finished registering yet

    context = {
        "title": title,
        "form": form,
        "instruction": instruction,
        "displaySignUp": displaySignUp,
        "authenticated": request.user.is_authenticated() # Whether the user is authenticated or not
    }

    if form.is_valid():
        instruction = """We're excited to have you as a new user.""" # Welcome message when user has finished up the registration process

        context = {
            "title" : "Welcome to the community!",
            "form": form,
            "instruction": instruction,
            "displaySignUp" : False,
            "authenticated": request.user.is_authenticated()
        }

        try:
            user = User.objects.create_user(form.cleaned_data.get('username'), form.cleaned_data.get('email'), form.cleaned_data.get('password')) # If the user is valid, save the user into the database
            user.save()
            return HttpResponseRedirect("../login")
        except IntegrityError as e:
            context = {
                "title" : title,
                "form": form,
                "instruction": "We're sorry, but that user is already registered.", # When the username is already taken
                "displaySignUp" : True,
                "authenticated": request.user.is_authenticated()
            }            

    return render(request, 'webapp/register.html', context)

def login(request):
    next = request.GET.get('next', '/') # Direct the user to the home page after he / she logs in.
    instruction = "Login validation is <b>case-sensitive</b>."

    if request.method == "POST":
        username = request.POST['username'] # Get the username entered
        password = request.POST['password'] # Get the password entered 
        user = authenticate(username=username, password=password) # Get the user

        if user is not None: # If user exists
            if user.is_active: # If user is active
                auth_login(request, user) # Log the user in
                return HttpResponseRedirect(next) # REdirect the user to the main page
            else:
                instruction = "This user is currently inactive." # Display that the user is inactive
        else:
            instruction = "Incorrect user and/or password combination." # Displayt hat the user has entered incorrect data

    context = {
        'redirect_to': next,
        'instruction': instruction,
        'authenticated': request.user.is_authenticated()
    }
    
    return render(request, "webapp/login.html", context)

def logout(request):
    auth.logout(request) # Log the user out
    return redirect('../login/')

@user_passes_test(lambda u: u.is_authenticated)
def add_post(request):
    form = PostForm(request.POST or None) # Form for posting threads
    error = ""

    context = { 'form': form, "authenticated": request.user.is_authenticated(), "error": error }

    if request.method == "POST":
        if form.is_valid() and request.user.is_authenticated(): # Check if the form is validated and the user has been authenticated
            comparePosts = Post.objects.all()

            duplicate = False

            for post in comparePosts:
                if post.title == form.cleaned_data.get("title"):
                    duplicate = True
                    break

            print("Duplicate: " + str(duplicate))

            if duplicate:
                print("Title has already been used before.")
                context["error"] = "Validation error: Title has already been used before."
            else:
                try:
                    post = Post.objects.create(author=request.user, title=form.cleaned_data.get("title"), text=form.cleaned_data.get("text"), 
                    field = form.cleaned_data.get("field"))
                    return redirect(post)
                except IntegrityError as e:
                    print(e)
        else:
            print("Invalid form")
            print(form.errors)
            context["error"] = "Validation error: The text field is blank."

    return render_to_response('webapp/startthread.html', context,
                              context_instance=RequestContext(request))

def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    postAuthor = post.author

    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.title = form.cleaned_data.get("title")
            post.author = postAuthor
            post.published_date = timezone.now()
            post.save()
            redirectLink = '../../' + str(post.slug)
            return redirect(redirectLink)
        else:
            print("Errors: " + str(form.errors))
    elif request.POST:
        form = PostForm(instance=post)

    return render(request, 'webapp/threadedit.html', {'post': post, 'authenticated': request.user.is_authenticated()})

def response_edit(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    name = comment.name

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.name = name
            comment.published_date = timezone.now()
            comment.save()
            return render(request, 'webapp/responseeditmessage.html', {'authenticated': request.user.is_authenticated()})
        else:
            print("Errors: " + str(formerrors))
    elif request.POST:
        form = CommentForm(instance=comment)

    return render(request, 'webapp/responseedit.html', {'comment': comment, 'authenticated': request.user.is_authenticated()})

def delete_new(request, pk):
    postToDelete = Post.objects.get(pk=pk).delete()
    global posts, searchPosts
    posts = Post.objects.all().filter().order_by('-created_on')
    return render(request, 'webapp/deletemessage.html', {'authenticated': request.user.is_authenticated()})

def delete_response(request, pk):
    responseToDelete = Comment.objects.get(pk=pk).delete()
    return render(request, 'webapp/deletemessage.html', {'authenticated': request.user.is_authenticated()})

def view_post(request, slug):
    context = {'posts': posts, 'authenticated': request.user.is_authenticated()}
    post_info(posts, context)
    context['post'] = Post.objects.all().get(slug=slug)
    return render(request, 'webapp/home.html', context)

def your_post(request):
    posts2 = Post.objects.all().filter(author__username=str(request.user)).order_by('-created_on') # Use filter on the QuerySet to sort by time
    numPosts = len(posts2)

    context = {'authenticated': request.user.is_authenticated(), 'posts':posts2, 'numPosts':numPosts, 'post':posts2[0]}
    
    if request.method == "POST":
        post = context['post']
        form = CommentForm(request.POST or None)
        hit_count = HitCount.objects.get_for_object(post)
        hit_count_response = HitCountMixin.hit_count(request, hit_count)
            
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post

            try:
                comment.name = request.user
            except:
                pass
                    
            comment.save()
            return redirect(request.path)
        else:
            print(form.is_valid())
            print(form.errors)

    post_info(posts2, context)

    return render(request, 'webapp/yourthreads.html', context)