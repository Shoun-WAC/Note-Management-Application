from rest_framework import serializers
from .models import *

class NoteManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = ['id', 'title', 'content', 'note_tag', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, attrs):
        title = attrs.get('title')
        content = attrs.get('content')

        qs = Notes.objects.filter(title=title, content=content)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)

        if qs.exists():
            raise serializers.ValidationError("A note with the same title and content already exists.")
        return attrs

    def log_activity(self, version, action, performed_by):
        NoteActivityLog.objects.create(
            note_version=version,
            action=action,
            performed_by=performed_by
        )

    def create(self, validated_data):
        tags = validated_data.pop('note_tag', [])
        created_by = validated_data.pop('created_by')

        note = Notes.objects.create(created_by=created_by, **validated_data)
        note.note_tag.set(tags)
        
        version = NoteVersion.objects.create(
            note=note,
            title=note.title,
            content=note.content,
            version_number=1,
            edited_by=created_by
        )

    
        self.log_activity(note, version, "Created", created_by)

        return note

    def update(self, instance, validated_data):
        edited_by = self.context['request'].user.profile

        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)

        if 'note_tag' in validated_data:
            instance.note_tag.set(validated_data.pop('note_tag'))

        instance.save()

        
        latest_version = instance.versions.order_by('-version_number').first()
        new_version_num = latest_version.version_number + 1 if latest_version else 1

        version = NoteVersion.objects.create(
            note=instance,
            title=instance.title,
            content=instance.content,
            version_number=new_version_num,
            edited_by=edited_by
        )

        self.log_activity(instance, version, "Edited", edited_by)

        return instance


