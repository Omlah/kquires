# Generated manually for AI enhancements

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0001_initial'),  # Update with actual latest migration
        ('users', '0001_initial'),  # Update with actual latest migration
        ('articles', '0002_article_updated_at'),  # Update with actual latest migration
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='language',
            field=models.CharField(choices=[('english', 'English'), ('arabic', 'Arabic')], default='english', max_length=20, verbose_name='Language'),
        ),
        migrations.AddField(
            model_name='article',
            name='original_language',
            field=models.CharField(blank=True, choices=[('english', 'English'), ('arabic', 'Arabic')], max_length=20, null=True, verbose_name='Original Language'),
        ),
        migrations.AddField(
            model_name='article',
            name='ai_analysis',
            field=models.JSONField(blank=True, null=True, verbose_name='AI Analysis'),
        ),
        migrations.AddField(
            model_name='article',
            name='technical_terms',
            field=models.JSONField(blank=True, null=True, verbose_name='Technical Terms'),
        ),
        migrations.AddField(
            model_name='article',
            name='version',
            field=models.CharField(default='1.0', max_length=10, verbose_name='Version'),
        ),
        migrations.AddField(
            model_name='article',
            name='is_ai_generated',
            field=models.BooleanField(default=False, verbose_name='AI Generated'),
        ),
        migrations.AddField(
            model_name='article',
            name='requires_approval',
            field=models.BooleanField(default=False, verbose_name='Requires Approval'),
        ),
        migrations.AddField(
            model_name='article',
            name='translation_preview',
            field=models.TextField(blank=True, null=True, verbose_name='Translation Preview'),
        ),
        migrations.AddField(
            model_name='article',
            name='parent_article',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='articles.article', verbose_name='Parent Article'),
        ),
        migrations.AddField(
            model_name='article',
            name='subcategory',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subcategory_articles', to='categories.category', verbose_name='Subcategory'),
        ),
        migrations.AlterField(
            model_name='article',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('draft', 'Draft'), ('ai_generated', 'AI Generated')], default='pending', max_length=255, verbose_name='Status'),
        ),
        migrations.CreateModel(
            name='ArticleVersion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version_number', models.CharField(max_length=10, verbose_name='Version Number')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('content', models.TextField(verbose_name='Content')),
                ('language', models.CharField(choices=[('english', 'English'), ('arabic', 'Arabic')], max_length=20, verbose_name='Language')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('change_summary', models.TextField(blank=True, null=True, verbose_name='Change Summary')),
                ('is_current', models.BooleanField(default=False, verbose_name='Is Current Version')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='articles.article')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.user', verbose_name='Created By')),
            ],
            options={
                'verbose_name': 'Article Version',
                'verbose_name_plural': 'Article Versions',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='articleversion',
            constraint=models.UniqueConstraint(fields=('article', 'version_number'), name='unique_article_version'),
        ),
    ]
