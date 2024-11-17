from django.core.management.base import BaseCommand
from accounts.models import ProfilePicture

class Command(BaseCommand):
    help = 'Load initial profile pictures'

    def handle(self, *args, **kwargs):
        pictures = [
            {'name': 'Default Avatar 1', 'image': 'profile1.jpg'},
            {'name': 'Default Avatar 2', 'image': 'profile2.jpg'},
            {'name': 'Default Avatar 3', 'image': 'profile3.jpg'},
        ]

        for picture in pictures:
            ProfilePicture.objects.get_or_create(
                name=picture['name'],
                image=picture['image']
            )

        self.stdout.write(self.style.SUCCESS('Successfully loaded profile pictures'))
