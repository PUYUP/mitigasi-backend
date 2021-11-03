from core.loading import is_model_registered
from simple_history.models import HistoricalRecords

from .base import *
from .generic import *
from .report import *

__all__ = list()


if not is_model_registered('contribution', 'Activity'):
    class Activity(AbstractActivity):
        class Meta(AbstractActivity.Meta):
            pass

    __all__.append('Activity')


if not is_model_registered('contribution', 'Report'):
    class Report(AbstractReport):
        class Meta(AbstractReport.Meta):
            pass

    __all__.append('Report')


if not is_model_registered('contribution', 'ReportLocation'):
    class ReportLocation(AbstractReportLocation):
        class Meta(AbstractReportLocation.Meta):
            pass

    __all__.append('ReportLocation')


if not is_model_registered('contribution', 'Confirmation'):
    class Confirmation(AbstractConfirmation):
        class Meta(AbstractConfirmation.Meta):
            pass

    __all__.append('Confirmation')


if not is_model_registered('contribution', 'Reaction'):
    class Reaction(AbstractReaction):
        class Meta(AbstractReaction.Meta):
            pass

    __all__.append('Reaction')


if not is_model_registered('contribution', 'Comment'):
    class Comment(AbstractComment):
        class Meta(AbstractComment.Meta):
            pass

    __all__.append('Comment')


if not is_model_registered('contribution', 'CommentTree'):
    class CommentTree(AbstractCommentTree):
        class Meta(AbstractCommentTree.Meta):
            pass

    __all__.append('CommentTree')


if not is_model_registered('contribution', 'Attachment'):
    class Attachment(AbstractAttachment):
        class Meta(AbstractAttachment.Meta):
            pass

    __all__.append('Attachment')
