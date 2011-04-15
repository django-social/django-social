from datetime import datetime
from mongoengine import *


class Note(Document):
    title = StringField(max_length=128, required=True)
    text = StringField(required=True)
    author = ReferenceField('User')
    timestamp = DateTimeField()
    is_public = BooleanField(default=True)

    meta = {
        'indexes': ['-timestamp', 'author'],
        'ordering': ['-timestamp'],
    }

    def __init__(self, *args, **kwargs):
        super(Note, self).__init__(*args, **kwargs)
        self.timestamp = self.timestamp or datetime.now()

    def comments(self, user=None):
        objects = Comment.objects(note=self)
        if user:
            objects = [setattr(i, 'can_manage', i.can_manage(user)) or i for i in objects]
        return objects

    def delete(self, *args, **kwargs):
        Comment.objects(note=self).delete()
        super(Note, self).delete(*args, **kwargs)


class Comment(Document):
    sender = ReferenceField('User')
    note = ReferenceField('Note')
    text = StringField(required=True)

    timestamp = DateTimeField()

    meta = {
        'indexes': [
                'timestamp',
                'sender',
        ],

        'ordering': [
                'timestamp',
        ]

    }

    def __init__(self, *args, **kwargs):
        super(Comment, self).__init__(*args, **kwargs)
        self.timestamp = self.timestamp or datetime.now()

    def is_sender(self, user):
        return self.sender.id == user.id

    def can_manage(self, user):
        return user.is_superuser or self.is_sender(user) or self.note.author == user