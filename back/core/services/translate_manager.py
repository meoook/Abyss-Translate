import logging
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

from django.core import management

from core.tasks import upload_translated
from core.serializers import TranslatesSerializer
from core.models import Files, Translated, FileMarks, Translates

logger = logging.getLogger('django')


class TranslateManager:
    """ Create or update translates. Update translate progress. If finished - create translate file. """

    def __init__(self, file_id, mark_id, lang_id, translator_id, text, md5sum=None):

        if not file_id or not mark_id or not lang_id:
            return Response({'err': 'request params error'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            file_obj = Files.objects.get(pk=file_id)
        except ObjectDoesNotExist:
            return Response({'err': 'file not found'}, status=status.HTTP_404_NOT_FOUND)
        # Check lang_translate in list of need translate languages
        if lang_id not in file_obj.translated_set.values_list('id', flat=True):
            return Response({'err': "no need translate to this language"}, status=status.HTTP_400_BAD_REQUEST)
        # Can't change original text
        if lang_id == file_obj.lang_orig.id:
            # TODO: permisions check - mb owner can change
            return Response({'err': "can't change original text"}, status=status.HTTP_404_NOT_FOUND)

        # Get or create translate(s)
        if md5sum:  # multi update
            # Check if translates exist with same md5
            translates = Translates.objects.filter(mark__file=file_obj, language=lang_id, mark__md5sum=md5sum)
            control_marks = file_obj.filemarks_set.filter(md5sum=md5sum)
        else:
            translates = Translates.objects.filter(mark__file=file_obj, language=lang_id, mark__id=mark_id)
            control_marks = file_obj.filemarks_set.filter(id=mark_id)
        # TODO: check text language and other
        translates.update(text=text)
        # Add new translates if mark(marks for md5) have no translates
        if translates.count() != control_marks.count():
            def_obj = {'translator': request.user, 'text': text, 'language_id': lang_id}
            objs = [Translates(**def_obj, mark=mark) for mark in control_marks if mark.id not in translates.values_list('mark', flat=True)]
            Translates.objects.bulk_create(objs)

        return_trans = translates.get(mark_id=mark_id)
        serializer = TranslatesSerializer(return_trans, many=False)
        # Get file progress for language
        try:
            progress = Translated.objects.get(file=file_obj, language=lang_id)
        except ObjectDoesNotExist:
            logger.error(f"For file {file_obj.id} related translated object not found: language {lang_id}")
            return Response({'err': 'related translated object not found'}, status=status.HTTP_404_NOT_FOUND)
        how_much_translated = self.get_queryset()\
            .filter(Q(translates__language=lang_id), Q(file=file_obj), ~Q(translates__text__exact='')).count()
        if file_obj.items == how_much_translated:
            progress.finished = True
        elif file_obj.items < how_much_translated:
            logging.error(f'For file {file_obj.id} translates items more then file have')
            progress.finished = True    # But it's error
        elif progress.finished:
            progress.finished = False
        progress.items = how_much_translated
        progress.save()
        if progress.finished:
            management.call_command('file_create_translated', file_obj.id, lang_id)
        return Response(serializer.data, status=status.HTTP_200_OK)