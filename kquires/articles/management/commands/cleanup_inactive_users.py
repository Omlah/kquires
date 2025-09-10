"""
Management command to cleanup inactive users
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from kquires.users.models import User
from kquires.articles.tasks import cleanup_inactive_users


class Command(BaseCommand):
    help = 'Cleanup inactive users and notify admins'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Number of days to consider a user inactive (default: 90)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually doing it'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        self.stdout.write(f"Starting cleanup of users inactive for {days} days...")
        
        if dry_run:
            self.stdout.write("DRY RUN MODE - No changes will be made")
        
        # Calculate cutoff date
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Find inactive users
        inactive_users = User.objects.filter(
            last_login__lt=cutoff_date,
            is_admin=False,
            is_active=True
        )
        
        count = inactive_users.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS(f"No inactive users found (inactive for {days} days)")
            )
            return
        
        self.stdout.write(f"Found {count} inactive users:")
        
        for user in inactive_users:
            self.stdout.write(
                f"  - {user.name} ({user.email}) - Last login: {user.last_login}"
            )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f"DRY RUN: Would deactivate {count} users")
            )
            return
        
        # Confirm before proceeding
        confirm = input(f"\nDeactivate {count} inactive users? (y/N): ")
        if confirm.lower() != 'y':
            self.stdout.write("Operation cancelled.")
            return
        
        # Run the cleanup task
        try:
            result = cleanup_inactive_users.delay()
            self.stdout.write(
                self.style.SUCCESS(f"Cleanup task started with ID: {result.id}")
            )
            self.stdout.write("Check the task status or wait for email notifications.")
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error starting cleanup task: {str(e)}")
            )
