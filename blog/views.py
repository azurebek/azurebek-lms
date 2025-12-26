from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count
from .models import Post, Category
from .forms import CommentForm
from django.shortcuts import redirect

def blog_list(request):
    # 1. Barcha chop etilgan postlar
    posts = Post.objects.filter(status='published')

    # 2. Agar Kategoriya tanlangan bo'lsa, filtrlash (?category=slug)
    cat_slug = request.GET.get('category')
    if cat_slug:
        posts = posts.filter(category__slug=cat_slug)

    # 3. Qidiruv (?q=so'z)
    query = request.GET.get('q')
    if query:
        posts = posts.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )

    # 4. Sidebar uchun ma'lumotlar
    recent_posts = Post.objects.filter(status='published').order_by('-created_at')[:5]

    # Kategoriyalar ro'yxati (ichidagi postlar soni bilan)
    categories = Category.objects.annotate(post_count=Count('posts')).filter(post_count__gt=0)

    context = {
        'posts': posts,
        'recent_posts': recent_posts,
        'categories': categories,
        'query': query
    }
    return render(request, 'blog/blog.html', context)


def blog_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')

    # Sidebar uchun
    recent_posts = Post.objects.filter(status='published').order_by('-created_at')[:5]
    categories = Category.objects.annotate(post_count=Count('posts')).filter(post_count__gt=0)

    # KOMMENTARIYA MANTIG'I
    comments = post.comments.filter(active=True)  # Faqat aktiv izohlar
    new_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Hozircha saqlamay turamiz, chunki muallif va postni qo'shish kerak
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.author = request.user
            new_comment.save()
            # Sahifani yangilaymiz (qayta yuklaymiz)
            return redirect('blog_detail', slug=post.slug)
    else:
        comment_form = CommentForm()

    context = {
        'post': post,
        'recent_posts': recent_posts,
        'categories': categories,
        'comments': comments,
        'comment_form': comment_form
    }
    return render(request, 'blog/blog_details.html', context)