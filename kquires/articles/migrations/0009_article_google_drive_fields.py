# Generated manually for Google Drive integration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0008_add_missing_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='google_drive_file_id',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Google Drive File ID'),
        ),
        migrations.AddField(
            model_name='article',
            name='google_drive_filename',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Google Drive Filename'),
        ),
        migrations.AddField(
            model_name='article',
            name='google_drive_web_view_link',
            field=models.URLField(blank=True, null=True, verbose_name='Google Drive Web View Link'),
        ),
        migrations.AddField(
            model_name='article',
            name='google_drive_web_content_link',
            field=models.URLField(blank=True, null=True, verbose_name='Google Drive Web Content Link'),
        ),
        migrations.AddField(
            model_name='article',
            name='google_drive_file_size',
            field=models.BigIntegerField(blank=True, null=True, verbose_name='Google Drive File Size'),
        ),
    ]
