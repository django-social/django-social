from django.shortcuts import redirect
from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.core.urlresolvers import reverse
from django.contrib import messages as system_messages
from django.utils.translation import ugettext_lazy as _
from apps.notes.documents import Comment
from apps.notes.forms import CommentTextForm
from apps.utils.paginator import paginate
from mongoengine.django.shortcuts import get_document_or_404

from .documents import Note

from .forms import NoteForm


def note_list(request, id=None):
    if id:
        notes = Note.objects(author=id, is_public=True)
    else:
        notes = Note.objects.filter(author=request.user)
    return direct_to_template(request, 'notes/note_list.html',
                              { 'notes': notes,
                                'is_public': id is not None })



def note_edit(request, note_id=None):
    fields = ('title', 'text', 'is_public')

    if note_id:
        note = get_document_or_404(Note, id=note_id, author=request.user)

        initial = {}

        for field in fields:
            initial[field] = getattr(note, field)

    else:
        note = None
        initial = {}

    form = NoteForm(request.POST or None, initial=initial)

    if form.is_valid():
        note = note or Note(author=request.user)

        for field in fields:
            setattr(note, field, form.cleaned_data[field])

        note.save()
        return HttpResponseRedirect(reverse('notes:note_list'))

    return direct_to_template(request, 'notes/note_edit.html',
                              { 'form': form, 'create': not note })


def comment_delete(request, comment_id):
    comment = get_document_or_404(Comment, id=comment_id)

    if not comment.can_manage(request.user):
        return HttpResponseNotFound()

    note_id = comment.note.id
    comment.delete()
    system_messages.add_message(request, system_messages.SUCCESS, _('Comment deleted'))
    return redirect(reverse('notes:note_view', args=[note_id]))


def note_view(request, note_id):
    notes = Note.objects(id=note_id, author=request.user)[:] or \
        Note.objects(id=note_id, is_public=True)[:]
    if not notes:
        return HttpResponseNotFound()
    note = notes[0]

    form = CommentTextForm(request.POST or None)
    if form.is_valid():
        text = form.data['text']
        Comment(sender=request.user, note=note, text=text).save()
        system_messages.add_message(request, system_messages.SUCCESS, _('Comment sent'))

    objects = paginate(request,
                       note.comments(user=request.user),
                       note.comments().count(),
                       10)
    return direct_to_template(request, 'notes/note_view.html',
                              { 'note': note,
                                'objects': objects,
                                'msgform': form })



def note_delete(request, note_id):
    note = Note.objects(id=note_id, author=request.user)
    if not note:
        return HttpResponseNotFound()
    note.delete()
    return HttpResponseRedirect(reverse('notes:note_list'))


def multiple_delete(request):
    ids = [ x[4:] for x in request.POST.keys() if x.startswith('del_') ]
    deleted = 0
    for id in ids:
        note = Note.objects(id=id, author=request.user)
        if note:
            note.delete()
            deleted += 1
    if deleted:
        system_messages.add_message(request, system_messages.SUCCESS,
                                    _('Notes deleted: %d') % deleted )
    return HttpResponseRedirect(reverse('notes:note_list'))