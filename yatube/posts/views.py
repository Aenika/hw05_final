from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from core.constants import POSTS_PER_PAGE
from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User


def paginising(post_list, posts_per_page, request):
    paginator = Paginator(post_list, posts_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    post_list = Post.objects.select_related("author")
    page_obj = paginising(post_list, POSTS_PER_PAGE, request)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.select_related('group').filter(group=group)
    page_obj = paginising(posts, POSTS_PER_PAGE, request)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def all_groups(request):
    groups = Group.objects.order_by('title')
    context = {'groups': groups, }
    return render(request, 'posts/all_groups.html', context)


def profile(request, username):
    author = User.objects.get(username=username)
    posts_by_author = Post.objects.select_related('author').filter(
        author=author
    )
    page_obj = paginising(posts_by_author, POSTS_PER_PAGE, request)
    following = (
        request.user.is_authenticated
        and request.user != author
        and Follow.objects.filter(user=request.user, author=author).exists()
    )
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = Post.objects.get(id=post_id)
    author = post.author
    comments = Comment.objects.select_related('post').filter(post=post)
    context = {
        'post': post,
        'author': author,
        'form': CommentForm(),
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            user = request.user
            form.instance.author = user
            form.save()
            return redirect('posts:profile', username=user.username)
        return render(request, 'posts/create_post.html', {'form': form})
    form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    return render(request,
                  'posts/create_post.html',
                  {
                      'form': form,
                      'is_edit': True
                  })


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.select_related('author').filter(
        author__following__user=request.user
    )
    page_obj = paginising(posts, POSTS_PER_PAGE, request)
    context = {'page_obj': page_obj}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    follower = request.user
    already_following = Follow.objects.filter(user=follower, author=author)
    if author != follower and not already_following.exists():
        Follow.objects.create(user=follower, author=author)
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follower = request.user
    already_following = Follow.objects.filter(user=follower, author=author)
    if already_following.exists():
        already_following.delete()
    return redirect('posts:follow_index')
