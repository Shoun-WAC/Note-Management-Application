from pyclbr import Class
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .serializers import NoteManagementSerializer
from authentication.helpers import success_response, error_response
from rest_framework import status
from .models import *


class NoteCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user_type = request.user.profile.user_type
            if user_type != 'Admin' and user_type != 'Editor':
                return error_response(error_message="Only Admin and Editor can create notes", status=status.HTTP_403_FORBIDDEN)
            
            serializer = NoteManagementSerializer(data=request.data)

            if serializer.is_valid():
                note = serializer.save(created_by=request.user.profile)
                return success_response(data=serializer.data, success_message="Note created successfully", status=status.HTTP_200_OK)
            else:
                return error_response(error_message=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return error_response(error_message=str(e))

    def put(self, request):
        try:
            user_type = request.user.profile.user_type
            if user_type != 'Admin' and user_type != 'Editor':
                return error_response(error_message="Only Admin and Editor can update notes", status=status.HTTP_403_FORBIDDEN)
            
            note_id = request.data.get('note_id')
            if not note_id:
                return error_response(error_message="note_id is required", status=status.HTTP_400_BAD_REQUEST)
            
            note_instance = Notes.objects.filter(id=note_id, deleted=False).first()
            if not note_instance:
                return error_response(error_message="Note not found", status=status.HTTP_404_NOT_FOUND)
            
            serializer = NoteManagementSerializer(note_instance, data=request.data, partial=True, context={'request': request})
            
            if serializer.is_valid():
                serializer.save()

                return success_response(data=serializer.data, success_message="Note updated successfully", status=status.HTTP_200_OK)
            else:
                return error_response(error_message="Invalid data", status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return error_response(error_message=str(e))
        
    def delete(self, request):
        try:
            user_type = request.user.profile.user_type
            if user_type != 'Admin' and user_type != 'Editor':
                return error_response(error_message="Only Admin and Editor can delete notes", status=status.HTTP_403_FORBIDDEN)
            
            note_id = request.data.get('note_id')
            if not note_id:
                return error_response(error_message="note_id is required", status=status.HTTP_400_BAD_REQUEST)
            
            note_instance = Notes.objects.filter(id=note_id, deleted=False).first()

            if not note_instance:
                return error_response(error_message="Note not found", status=status.HTTP_404_NOT_FOUND)
            note_instance.deleted = True
            note_instance.save()

            NoteActivityLog.objects.create(
                note_version=NoteVersion.objects.filter(note=note_instance).order_by('-version_number').first(),
                action="Deleted",
                performed_by=request.user.profile
            )

            return success_response(success_message="Note deleted successfully", status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(error_message=str(e))
        

class ListNotesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            notes = Notes.objects.filter(deleted=False).all()
            serializer = NoteManagementSerializer(notes, many=True)
            return success_response(data=serializer.data, success_message="Notes retrieved successfully", status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(error_message=str(e))
        
        
class ListNoteVersionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:            
            version_data = NoteVersion.objects.filter(note_id=id,note_id__deleted=False).all()
            if not version_data:
                return error_response(error_message="Note not found", status=status.HTTP_404_NOT_FOUND)

            version_data = [{
                'version_number': v.version_number,
                'title': v.title,
                'content': v.content,
                'edited_by': v.edited_by.user.username,
                'edited_at': v.created_at
            } for v in version_data]

            return success_response(data=version_data, success_message="Note versions retrieved successfully", status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(error_message=str(e))
        
        
class NoteTagCreationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user_type = request.user.profile.user_type
            if user_type != 'Admin' and user_type != 'Editor':
                return error_response(error_message="Only Admin or Editors can create tags", status=status.HTTP_403_FORBIDDEN)
            
            tag_name = request.data.get('tag_name')
            if not tag_name:
                return error_response(error_message="tag_name is required", status=status.HTTP_400_BAD_REQUEST)
            
            tag, created = Tag.objects.get_or_create(tag_name=tag_name)

            if created:
                return success_response(data={'tag_id': tag.id, 'tag_name': tag.tag_name}, success_message="Tag created successfully", status=status.HTTP_200_OK)
            else:
                return error_response(error_message="Tag already exists", status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return error_response(error_message=str(e))
        
        
class NoteActivityLogListView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            activity_logs = NoteActivityLog.objects.filter().all()
            if not activity_logs:
                return error_response(error_message="No activity logs found for this note", status=status.HTTP_404_NOT_FOUND)

            log_data = [{
                'note_id': log.note_version.note.id,
                'note_version': log.note_version.version_number,
                'note_title': log.note_version.title,
                'content': log.note_version.content,
                'action': log.action,
                'performed_by': log.performed_by.user.username,
                'timestamp': log.timestamp
            } for log in activity_logs]

            return success_response(data=log_data, success_message="Activity logs retrieved successfully", status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(error_message=str(e))
        