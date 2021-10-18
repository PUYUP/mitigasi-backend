from core.loading import is_model_registered
from simple_history.models import HistoricalRecords

from .base import *
from .generic import *
from .report import *

__all__ = list()


if not is_model_registered('contribution', 'Activity'):
    class Activity(AbstractActivity):
        history = HistoricalRecords(inherit=True)

        class Meta(AbstractActivity.Meta):
            pass

    __all__.append('Activity')


if not is_model_registered('contribution', 'Report'):
    class Report(AbstractReport):
        history = HistoricalRecords(inherit=True)

        class Meta(AbstractReport.Meta):
            pass

    __all__.append('Report')


if not is_model_registered('contribution', 'ReportLocation'):
    class ReportLocation(AbstractReportLocation):
        history = HistoricalRecords(inherit=True)

        class Meta(AbstractReportLocation.Meta):
            pass

    __all__.append('ReportLocation')


if not is_model_registered('contribution', 'Confirmation'):
    class Confirmation(AbstractConfirmation):
        history = HistoricalRecords(inherit=True)

        class Meta(AbstractConfirmation.Meta):
            pass

    __all__.append('Confirmation')


if not is_model_registered('contribution', 'Reaction'):
    class Reaction(AbstractReaction):
        history = HistoricalRecords(inherit=True)

        class Meta(AbstractReaction.Meta):
            pass

    __all__.append('Reaction')


if not is_model_registered('contribution', 'Comment'):
    class Comment(AbstractComment):
        history = HistoricalRecords(inherit=True)

        class Meta(AbstractComment.Meta):
            pass

    __all__.append('Comment')


if not is_model_registered('contribution', 'CommentTree'):
    class CommentTree(AbstractCommentTree):
        history = HistoricalRecords(inherit=True)

        class Meta(AbstractCommentTree.Meta):
            pass

    __all__.append('CommentTree')


if not is_model_registered('contribution', 'Attachment'):
    class Attachment(AbstractAttachment):
        history = HistoricalRecords(inherit=True)

        class Meta(AbstractAttachment.Meta):
            pass

    __all__.append('Attachment')
