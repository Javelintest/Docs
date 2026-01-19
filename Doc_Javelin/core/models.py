from django.db import models
import os

class DocumentTask(models.Model):
    TASK_CHOICES = [
        ('merge', 'Merge PDFs'),
        ('img2pdf', 'Image to PDF'),
        ('pdf2word', 'PDF to Word'),
        ('pdf2excel', 'PDF to Excel'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    task_type = models.CharField(max_length=20, choices=TASK_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    
    # Store output file
    output_file = models.FileField(upload_to='outputs/', null=True, blank=True)
    
    # Optional: store original filename(s) for reference
    original_filenames = models.TextField(help_text="Comma-separated list of original filenames")
    
    # Error message if failed
    error_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.get_task_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-created_at']

    def delete(self, *args, **kwargs):
        # Delete file from system when model is deleted
        if self.output_file:
            if os.path.isfile(self.output_file.path):
                os.remove(self.output_file.path)
        super().delete(*args, **kwargs)
