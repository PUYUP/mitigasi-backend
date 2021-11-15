from core.loading import is_model_registered

from .activity import *
from .location import *
from .attachment import *
from .comment import *
from .confirmation import *
from .reaction import *
from .impact import *
from .safetycheck import *

__all__ = list()


if not is_model_registered('generic', 'Activity'):
    class Activity(AbstractActivity):
        class Meta(AbstractActivity.Meta):
            pass

    __all__.append('Activity')


if not is_model_registered('generic', 'Location'):
    class Location(AbstractLocation):
        class Meta(AbstractLocation.Meta):
            pass

    __all__.append('Location')


if not is_model_registered('generic', 'Attachment'):
    class Attachment(AbstractAttachment):
        class Meta(AbstractAttachment.Meta):
            pass

    __all__.append('Attachment')


if not is_model_registered('generic', 'Comment'):
    class Comment(AbstractComment):
        class Meta(AbstractComment.Meta):
            pass

    __all__.append('Comment')


if not is_model_registered('generic', 'CommentTree'):
    class CommentTree(AbstractCommentTree):
        class Meta(AbstractCommentTree.Meta):
            pass

    __all__.append('CommentTree')


if not is_model_registered('generic', 'Confirmation'):
    class Confirmation(AbstractConfirmation):
        class Meta(AbstractConfirmation.Meta):
            pass

    __all__.append('Confirmation')


if not is_model_registered('generic', 'Reaction'):
    class Reaction(AbstractReaction):
        class Meta(AbstractReaction.Meta):
            pass

    __all__.append('Reaction')


if not is_model_registered('generic', 'Impact'):
    class Impact(AbstractImpact):
        class Meta(AbstractImpact.Meta):
            pass

    __all__.append('Impact')


if not is_model_registered('generic', 'SafetyCheck'):
    class SafetyCheck(AbstractSafetyCheck):
        class Meta(AbstractSafetyCheck.Meta):
            pass

    __all__.append('SafetyCheck')
