import logging
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

from django.core import management

# TODO: Check file_manager and delete this func

from core.serializers import TranslatesSerializer
from core.models import Files, Translated, FileMarks, Translates

logger = logging.getLogger("django")


def mark_create_translate(file_id, mark_id, lang_id, translator_id, text, md5sum=None):
    """ Create or update translates. Update translate progress. If finished - create translate file. """
    # assert(file_id and mark_id and lang_id)
    # assert(file_id >= 0 and mark_id >= 0 and lang_id >= 0)
    if not file_id or not mark_id or not lang_id:
        return Response({"err": "request params error"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        file_obj = Files.objects.get(pk=file_id)
    except ObjectDoesNotExist:
        return Response({"err": "file not found"}, status=status.HTTP_404_NOT_FOUND)
    # Check lang_translate in list of need translate languages
    if lang_id not in file_obj.translated_set.values_list("id", flat=True):
        return Response({"err": "no need translate to this language"}, status=status.HTTP_400_BAD_REQUEST)
    # Can't change original text
    if lang_id == file_obj.lang_orig.id:
        # TODO: permissions check - mb owner can change ?
        return Response({"err": "can't change original text"}, status=status.HTTP_400_BAD_REQUEST)

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
        def_obj = {"translator_id": translator_id, "language_id": lang_id, "text": text}
        objs = [Translates(**def_obj, mark=mark) for mark in control_marks if mark.id not in translates.values_list("mark", flat=True)]
        Translates.objects.bulk_create(objs)
    # Translate for response
    return_trans = translates.get(mark_id=mark_id)
    serializer = TranslatesSerializer(return_trans, many=False)
    # Update file progress for language
    try:
        progress = file_obj.translated_set.get(language=lang_id)
    except ObjectDoesNotExist:
        logger.error(f"For file {file_obj.id} related translated object not found: language {lang_id}")
        return Response({"err": "related translated object not found"}, status=status.HTTP_404_NOT_FOUND)
    how_much_translated = file_obj.filemarks_set.filter(Q(translates__language=lang_id), ~Q(translates__text__exact="")).count()
    progress.items = how_much_translated
    if file_obj.items != how_much_translated:
        progress.finished = False
        if file_obj.items < how_much_translated:
            logger.error(f"For file {file_obj.id} translates items more then file have")
    else:
        # upload_all_translated.delay(file_obj.id, lang_id)
        pass
    progress.save()
    return Response(serializer.data, status=status.HTTP_200_OK)
