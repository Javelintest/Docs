from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
import os
import uuid
import shutil
from pathlib import Path

from core.models import DocumentTask
from core.tools import (
    merge_pdfs,
    img_to_pdf,
    pdf_to_word,

    pdf_to_excel,
    edit_pdf
    )
import json

def index(request):
    """Render the main landing page."""
    return render(request, 'core/index.html')

def page_merge(request):
    return render(request, 'core/merge.html')

def page_img2pdf(request):
    return render(request, 'core/img2pdf.html')

def page_pdf2word(request):
    return render(request, 'core/pdf2word.html')

def page_pdf2excel(request):
    return render(request, 'core/pdf2excel.html')

def page_edit_pdf(request):
    return render(request, 'core/edit_pdf.html')

def page_result(request, task_id):
    """Render the result/success page for a given task."""
    try:
        task = DocumentTask.objects.get(pk=task_id)
        
        # Determine restart URL based on task type
        restart_map = {
            'merge': 'merge_page',
            'img2pdf': 'img2pdf_page',
            'pdf2word': 'pdf2word_page',
            'pdf2excel': 'pdf2excel_page',
            'edit_pdf': 'edit_pdf_page'
        }
        
        # Get readable task name
        task_name_map = {
            'merge': 'Merge PDF',
            'img2pdf': 'Image to PDF',
            'pdf2word': 'PDF to Word',
            'pdf2excel': 'PDF to Excel',
            'edit_pdf': 'Edit PDF',
        }
        
        restart_url = '/' + task.task_type # default fallback
        from django.urls import reverse
        try:
             restart_url = reverse(restart_map.get(task.task_type, 'index'))
        except:
             pass
             
        ctx = {
            'task': task,
            'filename': os.path.basename(task.output_file.name),
            'download_url': task.output_file.url,
            'task_name': task_name_map.get(task.task_type, 'Document Tool'),
            'restart_url': restart_url
        }
        return render(request, 'core/result.html', ctx)
    except DocumentTask.DoesNotExist:
        return redirect('index')

def save_uploaded_file(uploaded_file):
    """Save an uploaded file to a temporary location and return the path."""
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    filename = f"{uuid.uuid4()}_{uploaded_file.name}"
    file_path = os.path.join(temp_dir, filename)
    with open(file_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
    return file_path

def merge_pdfs_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        files = request.FILES.getlist('files[]')
        if not files:
            return JsonResponse({'error': 'No files provided'}, status=400)
            
        # Save input files
        input_paths = []
        original_names = []
        for f in files:
            path = save_uploaded_file(f)
            input_paths.append(path)
            original_names.append(f.name)
            
        # Prepare output path
        output_filename = f"merged_{uuid.uuid4()}.pdf"
        output_dir = os.path.join(settings.MEDIA_ROOT, 'outputs')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_filename)
        
        # Helper to ensure keys exist in tools (they might rely on some context)
        # Assuming tools are pure functions as seen in review
        success = merge_pdfs(input_paths, output_path)
        
        # Cleanup input files
        for p in input_paths:
            try:
                os.remove(p)
            except:
                pass
                
        if success:
            # Create Task Record
            task = DocumentTask.objects.create(
                task_type='merge',
                status='success',
                original_filenames=','.join(original_names),
                output_file=f"outputs/{output_filename}"
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Successfully merged {len(files)} PDF(s)',
                'filename': output_filename,
                'url': task.output_file.url,
                'task_id': task.id
            })
        else:
            DocumentTask.objects.create(
                task_type='merge',
                status='failed',
                original_filenames=','.join(original_names),
                error_message="Merge operation failed"
            )
            return JsonResponse({'error': 'Failed to merge PDFs'}, status=500)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def img2pdf_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    try:
        files = request.FILES.getlist('files[]')
        separate = request.POST.get('separate') == 'true'
        
        if not files:
            return JsonResponse({'error': 'No files provided'}, status=400)
            
        input_paths = []
        original_names = []
        for f in files:
            path = save_uploaded_file(f)
            input_paths.append(path)
            original_names.append(f.name)
            
        output_dir = os.path.join(settings.MEDIA_ROOT, 'outputs')
        os.makedirs(output_dir, exist_ok=True)
        
        if separate:
            output_files = []
            output_urls = []
            
            # For separate files, we call logic for each or rely on tool?
            # The tool `img_to_pdf` handles `single_pdf_per_image=True`
            # But it returns boolean. We need to know the output filenames.
            # The tool generates filenames based on input.
            # Let's check tool logic again. 
            # It saves to `output_file` (or directory if separate=True).
            
            # To be safe and trackable, let's call it per file if separate
            
            success_count = 0
            for i, input_path in enumerate(input_paths):
                base_name = os.path.splitext(files[i].name)[0]
                out_name = f"{base_name}_{uuid.uuid4()}.pdf"
                out_path = os.path.join(output_dir, out_name)
                
                if img_to_pdf([input_path], out_path, single_pdf_per_image=False):
                    task = DocumentTask.objects.create(
                        task_type='img2pdf',
                        status='success',
                        original_filenames=files[i].name,
                        output_file=f"outputs/{out_name}"
                    )
                    output_files.append(out_name)
                    output_urls.append(task.output_file.url)
                    success_count += 1
            
            # For separate files, we don't have a single "Result Page" easily unless we show a list.
            # Current result page is designed for single file. 
            # We will just stay on page for separate files or redirect to a list page?
            # User request: "add next page or popup window to download there output"
            # For multiple files, maybe we zip them? Or just list links. 
            # For now, let's keep separate files behavior as is (stay on page) OR
            # create a "batch result" page. Let's just create a dummy task for the batch or
            # use the last task ID? 
            # Actually, `img2pdf` with separate=True is an edge case. 
            # Let's return task_id: null to indicate "stay here" or handle specifically.
            pass
            
            # Cleanup
            for p in input_paths:
                try: os.remove(p)
                except: pass
                
            return JsonResponse({
                'success': True,
                'message': f'Successfully converted {success_count} images',
                'files': output_files,
                # 'urls': output_urls # JS expects files list or filename
            })
            
        else:
            # Single PDF
            output_filename = f"images_{uuid.uuid4()}.pdf"
            output_path = os.path.join(output_dir, output_filename)
            
            success = img_to_pdf(input_paths, output_path, single_pdf_per_image=False)
            
            # Cleanup
            for p in input_paths:
                try: os.remove(p)
                except: pass
                
            if success:
                task = DocumentTask.objects.create(
                    task_type='img2pdf',
                    status='success',
                    original_filenames=','.join(original_names),
                    output_file=f"outputs/{output_filename}"
                )
                return JsonResponse({
                    'success': True,
                    'message': f'Successfully converted {len(files)} images',
                    'filename': output_filename,
                    'url': task.output_file.url,
                    'task_id': task.id
                })
            else:
                return JsonResponse({'error': 'Failed to convert images'}, status=500)
                
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def pdf2word_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file provided'}, status=400)
            
        f = request.FILES['file']
        input_path = save_uploaded_file(f)
        
        output_filename = f"{os.path.splitext(f.name)[0]}_{uuid.uuid4()}.docx"
        output_dir = os.path.join(settings.MEDIA_ROOT, 'outputs')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_filename)
        
        success = pdf_to_word(input_path, output_path)
        
        try: os.remove(input_path)
        except: pass
        
        if success:
            task = DocumentTask.objects.create(
                task_type='pdf2word',
                status='success',
                original_filenames=f.name,
                output_file=f"outputs/{output_filename}"
            )
            return JsonResponse({
                'success': True,
                'message': 'Successfully converted to Word',
                'filename': output_filename,
                'url': task.output_file.url,
                'task_id': task.id
            })
        else:
            return JsonResponse({'error': 'Failed to convert'}, status=500)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def pdf2excel_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file provided'}, status=400)
            
        f = request.FILES['file']
        input_path = save_uploaded_file(f)
        
        output_filename = f"{os.path.splitext(f.name)[0]}_{uuid.uuid4()}.xlsx"
        output_dir = os.path.join(settings.MEDIA_ROOT, 'outputs')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_filename)
        
        success = pdf_to_excel(input_path, output_path)
        
        try: os.remove(input_path)
        except: pass
        
        if success:
            task = DocumentTask.objects.create(
                task_type='pdf2excel',
                status='success',
                original_filenames=f.name,
                output_file=f"outputs/{output_filename}"
            )
            return JsonResponse({
                'success': True,
                'message': 'Successfully converted to Excel',
                'filename': output_filename,
                'url': task.output_file.url,
                'task_id': task.id
            })
        else:
            return JsonResponse({'error': 'Failed to convert'}, status=500)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def edit_pdf_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    try:
        # Check if we have a file upload or a JSON body (for reordering/operations)
        # But for the initial approach, we likely upload a file, getting back page info?
        # Actually, the user flow is: Upload -> UI shows pages -> User edits -> Click Save -> Send Config
        # Or: Upload -> Save file temp -> Return Page Count/Preview -> User edits -> Send Config + File ID
        
        # Simpler "all in one" or session based?
        # Let's support a flow where we upload the file first to get info?
        # OR: The standard tool flow: Upload file + Config in one POST request (if possible)
        # Reordering locally in JS using pdf.js to show previews is best.
        # But we need to send the ORIGINAL file + operations to backend.
        
        if 'file' not in request.FILES:
             return JsonResponse({'error': 'No file provided'}, status=400)
             
        f = request.FILES['file']
        pages_config_str = request.POST.get('pages_config', '[]')
        try:
            pages_config = json.loads(pages_config_str)
        except:
            return JsonResponse({'error': 'Invalid pages configuration'}, status=400)
            
        input_path = save_uploaded_file(f)
        
        output_filename = f"edited_{os.path.splitext(f.name)[0]}_{uuid.uuid4()}.pdf"
        output_dir = os.path.join(settings.MEDIA_ROOT, 'outputs')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_filename)
        
        start_page = int(request.POST.get('start_page', 1))
        
        success = edit_pdf(input_path, output_path, pages_config)
        
        try: os.remove(input_path)
        except: pass
        
        if success:
             task = DocumentTask.objects.create(
                task_type='edit_pdf',
                status='success',
                original_filenames=f.name,
                output_file=f"outputs/{output_filename}"
            )
             return JsonResponse({
                'success': True,
                'message': 'Successfully edited PDF',
                'filename': output_filename,
                'url': task.output_file.url,
                'task_id': task.id
            })
        else:
            return JsonResponse({'error': 'Failed to edit PDF'}, status=500)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

from django.http import FileResponse
import mimetypes

from django.views.decorators.clickjacking import xframe_options_sameorigin

@xframe_options_sameorigin
def download_redirect(request, filename):
    """Serve file with optional renaming."""
    # Security check: prevent directory traversal
    filename = os.path.basename(filename)
    output_dir = os.path.join(settings.MEDIA_ROOT, 'outputs')
    file_path = os.path.join(output_dir, filename)
    
    print(f"DEBUG: Download request for {filename}")
    
    # 1. Resolve File Path (Exact or Fuzzy)
    real_filename = filename
    if not os.path.exists(file_path):
        print(f"DEBUG: Not found at {file_path}. Fuzzy searching...")
        found = False
        # Heuristic: UUIDs are long, look for files containing this string
        if len(filename) > 20: 
             for f in os.listdir(output_dir):
                 if filename in f:
                     file_path = os.path.join(output_dir, f)
                     real_filename = f
                     found = True
                     print(f"DEBUG: Fuzzy match found: {real_filename}")
                     break
        
        if not found:
            print("DEBUG: No match found.")
            return HttpResponse('File not found', status=404)
    else:
        real_filename = filename

    # 2. Determine Correct Extension from Real File
    _, real_ext = os.path.splitext(real_filename)
    if not real_ext:
        # Fallback if disk file has no extension (rare)
        is_pdf = False
        try:
            with open(file_path, 'rb') as f:
                if f.read(4).startswith(b'%PDF'):
                    is_pdf = True
        except: pass
        real_ext = '.pdf' if is_pdf else '.bin'

    # 3. Determine Output Filename
    custom_name = request.GET.get('name')
    if custom_name:
        custom_name = custom_name.strip()
    else:
        custom_name = real_filename

    # ALWAYS Enforce the REAL extension on the custom name
    # Verify we aren't duplicating extension (e.g. file.pdf.pdf)
    if not custom_name.lower().endswith(real_ext.lower()):
        custom_name += real_ext

    # 4. MIME Type
    if real_ext.lower() == '.pdf':
        content_type = 'application/pdf'
    elif real_ext.lower() == '.docx':
        content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    elif real_ext.lower() == '.xlsx':
        content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    else:
        content_type, _ = mimetypes.guess_type(file_path)
        if not content_type:
            content_type = 'application/octet-stream'

    log_msg = f"REQ: {filename} | REAL: {real_filename} | EXT: {real_ext} | FINAL: {custom_name} | TYPE: {content_type}\n"
    print(f"DEBUG: {log_msg.strip()}")
    try:
        with open('debug_download.log', 'a') as logf:
            logf.write(log_msg)
    except: pass

    response = FileResponse(open(file_path, 'rb'), content_type=content_type)
    
    # Check for preview mode
    disposition = 'attachment'
    if request.GET.get('preview') == 'true':
        disposition = 'inline'
        
    response['Content-Disposition'] = f'{disposition}; filename="{custom_name}"'
    return response
