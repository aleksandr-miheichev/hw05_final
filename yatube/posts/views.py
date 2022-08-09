from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .settings import POSTS_PER_PAGE


def paginator_page(request, posts):
    return Paginator(posts, POSTS_PER_PAGE).get_page(request.GET.get('page'))


def index(request):
    return render(request, 'posts/index.html', {
        'page_obj': paginator_page(request, Post.objects.all())
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    return render(request, 'posts/group_list.html', {
        'group': group,
        'page_obj': paginator_page(request, group.posts.all()),
    })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author and request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=author
        ).exists()
    else:
        following = False
    return render(request, 'posts/profile.html', {
        'page_obj': paginator_page(
            request,
            Post.objects.filter(author__username=username)
        ),
        'author': author,
        'following': following
    })


def post_detail(request, post_id):
    return render(request, 'posts/post_detail.html', {
        'post': get_object_or_404(Post, id=post_id),
        'form': CommentForm(),
        'comments': get_object_or_404(Post, id=post_id).comments.all(),
    })


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'posts/post_create.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post_new = form.save()
    return redirect('posts:profile', post_new.author.username)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if not form.is_valid():
        return render(request, 'posts/post_create.html', {
            'post': post,
            'form': form,
        })
    form.save()
    return redirect('posts:post_detail', post_id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id)


@login_required
def follow_index(request):
    return render(request, 'posts/follow.html', {
        'page_obj': paginator_page(
            request,
            Post.objects.filter(author__following__user=request.user)
        )})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    subscription = Follow.objects.filter(
        user=request.user,
        author=author
    ).exists()
    if request.user != author and (
            request.user.is_authenticated and not subscription
    ):
        Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    subscription = Follow.objects.filter(
        user=request.user,
        author=get_object_or_404(User, username=username)
    )
    if subscription.exists():
        subscription.delete()
    return redirect('posts:profile', username)
