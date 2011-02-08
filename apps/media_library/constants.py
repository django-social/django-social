from django.utils.translation import ugettext_lazy as _

LIBRARY_TYPE_IMAGE = 'image'
LIBRARY_TYPE_AUDIO = 'audio'
LIBRARY_TYPE_VIDEO = 'video'

FILE_TYPE_IMAGE = 'image'
FILE_TYPE_AUDIO = 'audio'
FILE_TYPE_VIDEO = 'video'

LIBRARY_IMAGE_RESIZE_TASK = 'LIBRARY_IMAGE_RESIZE'
LIBRARY_VIDEO_RESIZE_TASK = 'LIBRARY_VIDEO_RESIZE'


REMOVE_MESSAGES = { LIBRARY_TYPE_IMAGE: _('Image successfully removed'),
                    LIBRARY_TYPE_AUDIO: _('Audio successfully removed'),
                    LIBRARY_TYPE_VIDEO: _('Video successfully removed') }