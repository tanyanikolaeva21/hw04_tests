from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from utils.pagin import get_page_context

POSTS_PER_PAGE = 10


def index(request):
    text = 'Последние обновления на сайте'
    post_list = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'title': text,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    text = 'Группа сообщества: '
    group = get_object_or_404(Group, slug=slug)
    post_list_group = Post.objects.filter(group=group).order_by('-pub_date')
    context = {
        'group': group,
        'posts': post_list_group,
        'title': text,
    }
    context.update(get_page_context(post_list_group, request))
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user = User.objects.get(username=username)
    posts_user = Post.objects.filter(author=user)
    posts_count = posts_user.count()
    context = {
        'author': user,
        'posts_count': posts_count,
    }
    context.update(get_page_context(user.posts.all(), request))
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post_info = get_object_or_404(Post, pk=post_id)
    authors_post = post_info.author.posts.count()
    context = {
        'post_info': post_info,
        'authors_post': authors_post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if request.method == 'POST':
        if not form.is_valid():
            return render(request, 'posts/create_post.html', {'form': form})
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id, author=request.user)
    user = request.user.get_username()
    is_edit = True
    form = PostForm(request.POST or None, instance=post)

    if request.method == 'GET':
        if user != post.author.username:
            return redirect('posts:post_detail', post.id)

    elif request.method == 'POST':
        if form.is_valid():
            form.save()
        return redirect('posts:post_detail', post.id)

    context = {
        'form': form,
        'post': post,
        'is_edit': is_edit,
    }
    return render(request, template, context)
