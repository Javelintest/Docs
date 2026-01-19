import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import DocumentTask

print("Checking DocumentTask entries...")
for task in DocumentTask.objects.all().order_by('-id')[:20]:
    print(f"ID: {task.id} | Type: {task.task_type} | File: {task.output_file.name}")
