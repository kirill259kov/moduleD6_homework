
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Author, Category, Post, PostCategory, Comment
from .filters import PostFilter
from .forms import PostForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.shortcuts import HttpResponseRedirect, redirect
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timezone, timedelta
from django.core.exceptions import PermissionDenied
import logging

logger = logging.getLogger("django")

class PostsList(ListView):
    model = Post
    template_name = 'posts.html'
    context_object_name = 'posts'
    queryset = Post.objects.order_by('-dateCreation')
    paginate_by = 4


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'


class CategoryDetail(DetailView):
    model = Category
    template_name = 'category.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = Category.objects.get(id=self.kwargs['pk'])
        context['subscribers'] = category.subscribers.all()
        return context


class PostSearch(ListView):
    model = Post
    template_name = 'news_search.html'
    context_object_name = 'posts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        return context


class AddList(CreateView, PermissionRequiredMixin, UserPassesTestMixin):
    permission_required = 'news.add_post'
    queryset = Post.objects.all()
    template_name = 'add.html'
    form_class = PostForm
    success_url = '/news/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        context['form'] = PostForm()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
        return super().get(request, *args, **kwargs)

    def test_func(self):
        author = Author.objects.get(authorUser_id=self.request.user.id)
        yesterday = timezone.now() - timedelta(days=1)
        post_day = Post.objects.filter(author=author, dateCreation__gt=yesterday).count()
        print(post_day)
        if post_day > 2:
            logger.error(f"{author} превысил лимит по количеству публикаций в сутки ")
            raise PermissionDenied('Допускается публиковать до 3 постов в день')
        else:
            return redirect('/news')

    def post(self, request, *args, **kwargs):
            form = self.form_class(request.POST)
            self.object = form.save()
            self.postCategory_list = self.object.postCategory.all()
            for category in self.postCategory_list:
                for subscriber in category.subscribers.all():
                    html_content = render_to_string(
                        'new_post_email.html',
                        {
                            'user': subscriber,
                            'post': self.object,
                        }
                    )
                    message = EmailMultiAlternatives(
                        subject=f'{self.object.title}',
                        body=self.object.text,
                        from_email='Kirill2.5.9@yandex.ru',
                        to=[f'{subscriber.email}'],
                    )
                    message.attach_alternative(html_content, "text/html")
                    message.send()
                    print(html_content)
            return HttpResponseRedirect(self.get_success_url())


class PostEdit(LoginRequiredMixin, UpdateView, PermissionRequiredMixin):
    permission_required = 'news.change_post'
    template_name = 'edit.html'
    form_class = PostForm

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


class PostDelete(DeleteView):
    template_name = 'delete.html'
    queryset = Post.objects.all()
    success_url = '/news/'


def subscribe(request, pk):
    category = Category.objects.get(pk=pk)
    category.subscribers.add(request.user.id)
    html_content = render_to_string(
        'sub_email.html',
        {
            'category': category,
            'user': request.user,
        }
    )
    message = EmailMultiAlternatives(
        'Вы подписались на новую категорию новостей',
        '',
        'Kirill2.5.9@yandex.ru',
        [request.user.email],
    )
    message.attach_alternative(html_content, 'text/html')
    try:
        message.send()
    except Exception as e:
        print(f"Error sending email: {e}")
    return HttpResponseRedirect(reverse('category', args=[pk]))


def unsubscribe(request, pk):
    category = Category.objects.get(pk=pk)
    category.subscribers.remove(request.user.id)
    return HttpResponseRedirect(reverse('category', args=[pk]))
