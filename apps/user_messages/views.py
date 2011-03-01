# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.contrib import messages as system_messages
from django.http import Http404
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic.simple import direct_to_template

from mongoengine.django.shortcuts import get_document_or_404
from mongoengine.queryset import Q

from .forms import MessageTextForm

from .documents import Message
from apps.social.documents import User
from apps.utils.paginator import paginate


def send_message(request, user_id):
    
    from apps.social.documents import User

    recipient = get_document_or_404(User, id=user_id)

    if recipient.id == request.user.id:
        raise Http404()

    msgform = MessageTextForm(request.POST or None)

    if msgform.is_valid():
        text = msgform.data['text']
        Message.send(request.user, recipient, text)
        system_messages.add_message(request, system_messages.SUCCESS, _('Message sent'))
        return redirect('user_messages:view_sent')
    else:
        #@todo: use separate form and screen to handle each situation
        return direct_to_template(request, 'user_messages/write_message.html',
                              { 'page_user': recipient, 'msgform': msgform })


def view_message_by_user(request, user_id, action=''):
    by_user = get_document_or_404(User, id=user_id)
    owner  = request.user
    template = 'by_user.html'
    
    if action == 'sent':
        messages = Message.objects(sender=owner,
                               recipient=by_user,
                               sender_delete=None)
        template = 'by_user_sent.html'

    elif action == 'inbox':
        messages = Message.objects(recipient=request.user,
                               sender=by_user,
                               recipient_delete=None)
        template = 'by_user_inbox.html'

    else:
        messages = Message.objects(
                            Q(sender=owner, recipient=by_user, sender_delete=None) |
                            Q(sender=by_user, recipient=owner, recipient_delete=None),
                               )
    objects = paginate(request,
                       messages,
                       messages.count(),
                       10)
    return direct_to_template(request, 'user_messages/%s' % template,
                              { 'objects': objects,
                                'by_user': by_user,
                                'action': action,
                                })



def view_inbox(request):
    objects = paginate(request,
                       request.user.messages.incoming,
                       request.user.messages.incoming.count(),
                       10)
    return direct_to_template(request, 'user_messages/inbox.html',
                              { 'objects': objects })


def view_sent(request):
    objects = paginate(request,
                       request.user.messages.sent,
                       request.user.messages.sent.count(),
                       10)
    return direct_to_template(request, 'user_messages/sent.html',
                              { 'objects': objects })


def _message_acl_check(message, user):
    if not message.is_sender(user) and not message.is_recipient(user):
        raise Http404()


def view_message(request, message_id):
    message = get_document_or_404(Message, id=message_id)
    user = request.user
    _message_acl_check(message, user)


    if message.recipient.id == request.user.id and not message.is_read:
        message.set_readed()

    return direct_to_template(request, 'user_messages/message.html',
                              { 'msg': message })


def delete_message(request, message_id):
    message = get_document_or_404(Message, id=message_id)
    user = request.user
    _message_acl_check(message, user)

    message.set_user_delete(request.user)
    system_messages.add_message(request, system_messages.SUCCESS, _('Message deleted'))
    if message.is_sender(user):
        return redirect('user_messages:view_sent')
    elif message.is_recipient(user):
        return redirect('user_messages:view_inbox')


def multiple_delete(request):
    view = request.POST.get('view', 'inbox')
    user = request.user

    ids = [ x[4:] for x in request.POST.keys() if x.startswith('del_') ]

    for id in ids:
        message = get_document_or_404(Message, id=id)
        _message_acl_check(message, user)
        message.set_user_delete(user)

    if ids:
        system_messages.add_message(request, system_messages.SUCCESS,
                                    _('Messages deleted: %d') % len(ids) )

    if view == 'inbox':
        return redirect('user_messages:view_inbox')

    return redirect('user_messages:view_sent')
