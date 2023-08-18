from datetime import timedelta
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from ...models import Post, Category
from django.conf import settings


def compose_obj(post):
    _post = {}
    _post['id'] = post.id
    _post['title'] = post.title
    return _post


def send_notification(subscriber, cat_obj):
    template = 'weekly_article_list_email.html.html'
    subject = f'Еженедельная рассылка новых публикаций'

    posts_info = {}
    posts_info["category"] = ''
    posts_info["posts"] = []

    for category, posts in cat_obj.items():
        posts_info["category"] = category
        posts_info["posts"] = [compose_obj(post) for post in posts]

    html = render_to_string(
        template_name=template,
        context={
            'user_name': subscriber,
            'posts_info': posts_info,
        },
    )

    message = EmailMultiAlternatives(
        subject=subject,
        body='',
        from_email='Kirill2.5.9@yandex.ru',
        to=[f'{subscriber.email}'],
    )
    message.attach_alternative(html, "text/html")
    message.send()


def weelky_news_job():
    for Category in Category.objects.all():
        mailing_dict = {}
        cat_name = Category.name
        postsForWeek = Post.objects.filter(category=Category, dateCreation__gte=timezone.now() - timedelta(weeks=1))
        if not postsForWeek:
            continue
        for subscriber in Category.subscribers.all():
            if subscriber not in mailing_dict:
                mailing_dict[
                    subscriber] = {}
            if cat_name not in mailing_dict[subscriber]:
                mailing_dict[subscriber][cat_name] = set()  #
            mailing_dict[subscriber][cat_name].update(
                postsForWeek)
        for subscriber, cat_name in mailing_dict.items():
            send_notification(subscriber, cat_name)