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
import json

# Try to import tools, handle potential import errors gracefully during dev
try:
    from core.models import DocumentTask
    from core.tools import (
        merge_pdfs,
        img_to_pdf,
        pdf_to_word,
        pdf_to_excel,
        edit_pdf,
        compress_pdf
    )
except ImportError:
    # Fallback for dev if models/tools aren't perfectly synced yet
    pass

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

def page_compress(request):
    return render(request, 'core/compress.html')

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
            'edit_pdf': 'edit_pdf_page',
            'compress': 'compress_page'
        }
        
        # Get readable task name
        task_name_map = {
            'merge': 'Merge PDF',
            'img2pdf': 'Image to PDF',
            'pdf2word': 'PDF to Word',
            'pdf2excel': 'PDF to Excel',
            'edit_pdf': 'Edit PDF',
            'compress': 'Compress PDF',
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

# --- API VIEWS ---

def merge_pdfs_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        files = request.FILES.getlist('files[]')
        if not files:
            return JsonResponse({'error': 'No files provided'}, status=400)
            
        input_paths = []
        original_names = []
        for f in files:
            path = save_uploaded_file(f)
            input_paths.append(path)
            original_names.append(f.name)
            
        output_filename = f"merged_{uuid.uuid4()}.pdf"
        output_dir = os.path.join(settings.MEDIA_ROOT, 'outputs')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_filename)
        
        success = merge_pdfs(input_paths, output_path)
        
        for p in input_paths:
            try: os.remove(p)
            except: pass
                
        if success:
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
                    success_count += 1
            
            for p in input_paths:
                try: os.remove(p)
                except: pass
                
            return JsonResponse({
                'success': True,
                'message': f'Successfully converted {success_count} images',
                'files': output_files,
            })
        else:
            output_filename = f"images_{uuid.uuid4()}.pdf"
            output_path = os.path.join(output_dir, output_filename)
            
            success = img_to_pdf(input_paths, output_path, single_pdf_per_image=False)
            
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

def compress_pdf_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file provided'}, status=400)
        f = request.FILES['file']
        input_path = save_uploaded_file(f)
        output_filename = f"compressed_{os.path.splitext(f.name)[0]}_{uuid.uuid4()}.pdf"
        output_dir = os.path.join(settings.MEDIA_ROOT, 'outputs')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_filename)
        
        success = compress_pdf(input_path, output_path)
        try: os.remove(input_path)
        except: pass
        
        if success:
            task = DocumentTask.objects.create(
                task_type='compress',
                status='success',
                original_filenames=f.name,
                output_file=f"outputs/{output_filename}"
            )
            return JsonResponse({
                'success': True,
                'message': 'Successfully compressed PDF',
                'filename': output_filename,
                'url': task.output_file.url,
                'task_id': task.id
            })
        else:
            return JsonResponse({'error': 'Failed to compress PDF'}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# --- EDITOR STUDIO VIEWS ---

def api_upload_session(request):
    """Handle session-based file uploads for the Editor Studio."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        files = request.FILES.getlist('files[]')
        if not files and 'file' in request.FILES:
             files = [request.FILES['file']]
        if not files:
            return JsonResponse({'error': 'No files provided'}, status=400)
            
        session_id = request.POST.get('session_id') or str(uuid.uuid4())
        session_dir = os.path.join(settings.MEDIA_ROOT, 'sessions', session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        file_info = []
        for f in files:
            clean_name = os.path.basename(f.name)
            file_path = os.path.join(session_dir, clean_name)
            with open(file_path, 'wb+') as dest:
                for chunk in f.chunks():
                    dest.write(chunk)
            file_info.append({
                'name': clean_name,
                'size': f.size,
                'url': f"{settings.MEDIA_URL}sessions/{session_id}/{clean_name}"
            })
        return JsonResponse({
            'success': True,
            'session_id': session_id,
            'files': file_info
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def editor_view(request, tool, session_id):
    """Render the unified editor studio."""
    session_dir = os.path.join(settings.MEDIA_ROOT, 'sessions', session_id)
    ctx = {
        'tool': tool,
        'session_id': session_id,
        'initial_files': []
    }
    
    if os.path.exists(session_dir):
        for fname in os.listdir(session_dir):
            fpath = os.path.join(session_dir, fname)
            if os.path.isfile(fpath):
                ctx['initial_files'].append({
                    'name': fname,
                    'size': os.path.getsize(fpath),
                    'url': f"{settings.MEDIA_URL}sessions/{session_id}/{fname}"
                })
    return render(request, 'core/editor.html', ctx)

from django.views.decorators.clickjacking import xframe_options_sameorigin

@xframe_options_sameorigin
def download_redirect(request, filename):
    """Serve file with optional renaming."""
    from django.http import FileResponse
    import mimetypes
    
    filename = os.path.basename(filename)
    output_dir = os.path.join(settings.MEDIA_ROOT, 'outputs')
    file_path = os.path.join(output_dir, filename)
    
    if not os.path.exists(file_path):
        # Fuzzy search
        found = False
        if len(filename) > 20: 
             for f in os.listdir(output_dir):
                 if filename in f:
                     file_path = os.path.join(output_dir, f)
                     filename = f # Update real filename
                     found = True
                     break
        if not found:
            return HttpResponse('File not found', status=404)

    # Determine Correct Extension
    _, real_ext = os.path.splitext(filename)
    if not real_ext:
        is_pdf = False
        try:
            with open(file_path, 'rb') as f:
                if f.read(4).startswith(b'%PDF'): is_pdf = True
        except: pass
        real_ext = '.pdf' if is_pdf else '.bin'

    custom_name = request.GET.get('name', filename).strip()
    if not custom_name.lower().endswith(real_ext.lower()):
        custom_name += real_ext

    # MIME Type
    if real_ext.lower() == '.pdf': content_type = 'application/pdf'
    elif real_ext.lower() == '.docx': content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    elif real_ext.lower() == '.xlsx': content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    else:
        content_type, _ = mimetypes.guess_type(file_path)
        if not content_type: content_type = 'application/octet-stream'

    response = FileResponse(open(file_path, 'rb'), content_type=content_type)
    disposition = 'inline' if request.GET.get('preview') == 'true' else 'attachment'
    response['Content-Disposition'] = f'{disposition}; filename="{custom_name}"'
    return response

def editor_entry_view(request, tool):
    """EntryPoint for tools to land directly on the editor."""
    # We use 'new' as session_id to indicate a fresh start
    return editor_view(request, tool, 'new')

def api_process_session(request, tool, session_id):
    """Unified endpoint to call tools on session files."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        session_dir = os.path.join(settings.MEDIA_ROOT, 'sessions', session_id)
        if not os.path.exists(session_dir):
            return JsonResponse({'error': 'Session expired or invalid'}, status=404)

        output_dir = os.path.join(settings.MEDIA_ROOT, 'outputs')
        os.makedirs(output_dir, exist_ok=True)
        task_output_file = None
        task_original_names = []

        if tool == 'merge':
            # Expect data['files'] as ordered list of filenames
            ordered_files = data.get('files', [])
            
            input_paths = []
            if ordered_files:
                for fname in ordered_files:
                     fpath = os.path.join(session_dir, fname)
                     if os.path.exists(fpath):
                         input_paths.append(fpath)
                         task_original_names.append(fname)
            else:
                # Fallback: all files
                for fname in os.listdir(session_dir):
                    fpath = os.path.join(session_dir, fname)
                    if os.path.isfile(fpath):
                        input_paths.append(fpath)
                        task_original_names.append(fname)

            if not input_paths:
                 return JsonResponse({'error': 'No files to merge'}, status=400)

            out_name = f"merged_{uuid.uuid4()}.pdf"
            out_path = os.path.join(output_dir, out_name)
            
            success = merge_pdfs(input_paths, out_path)
            if success:
                task_output_file = f"outputs/{out_name}"

        elif tool == 'compress':
            files = [f for f in os.listdir(session_dir) if os.path.isfile(os.path.join(session_dir, f))]
            if not files: return JsonResponse({'error': 'No file'}, status=400)
            
            fname = files[0] # Compress first file only for now
            input_path = os.path.join(session_dir, fname)
            out_name = f"compressed_{uuid.uuid4()}.pdf"
            out_path = os.path.join(output_dir, out_name)
            
            success = compress_pdf(input_path, out_path)
            if success:
                 task_output_file = f"outputs/{out_name}"
                 task_original_names.append(fname)

        elif tool == 'edit_pdf':
            files = [f for f in os.listdir(session_dir) if os.path.isfile(os.path.join(session_dir, f))]
            if not files: return JsonResponse({'error': 'No file'}, status=400)
            
            fname = files[0]
            input_path = os.path.join(session_dir, fname)
            out_name = f"edited_{uuid.uuid4()}.pdf"
            out_path = os.path.join(output_dir, out_name)
            
            # data['pages_config'] should be the list of operations
            pages_config = data.get('pages_config', [])
            success = edit_pdf(input_path, out_path, pages_config)
            if success:
                 task_output_file = f"outputs/{out_name}"
                 task_original_names.append(fname)
        
        elif tool == 'pdf2word':
             files = [f for f in os.listdir(session_dir) if os.path.isfile(os.path.join(session_dir, f))]
             fname = files[0]
             input_path = os.path.join(session_dir, fname)
             out_name = f"{os.path.splitext(fname)[0]}_{uuid.uuid4()}.docx"
             out_path = os.path.join(output_dir, out_name)
             
             success = pdf_to_word(input_path, out_path)
             if success:
                 task_output_file = f"outputs/{out_name}"
                 task_original_names.append(fname)

        elif tool == 'pdf2excel':
             files = [f for f in os.listdir(session_dir) if os.path.isfile(os.path.join(session_dir, f))]
             fname = files[0]
             input_path = os.path.join(session_dir, fname)
             out_name = f"{os.path.splitext(fname)[0]}_{uuid.uuid4()}.xlsx"
             out_path = os.path.join(output_dir, out_name)
             
             success = pdf_to_excel(input_path, out_path)
             if success:
                 task_output_file = f"outputs/{out_name}"
                 task_original_names.append(fname)
                 
        elif tool == 'img2pdf':
             # Similar to merge but with img_to_pdf
             input_paths = []
             for fname in os.listdir(session_dir):
                 input_paths.append(os.path.join(session_dir, fname))
                 task_original_names.append(fname)
             
             out_name = f"images_{uuid.uuid4()}.pdf"
             out_path = os.path.join(output_dir, out_name)
             success = img_to_pdf(input_paths, out_path, False)
             if success:
                 task_output_file = f"outputs/{out_name}"


        if task_output_file:
             task = DocumentTask.objects.create(
                task_type=tool,
                status='success',
                original_filenames=','.join(task_original_names),
                output_file=task_output_file
            )
             return JsonResponse({
                'success': True,
                'redirect_url': f"/result/{task.id}"
            })
        else:
             return JsonResponse({'error': 'Processing failed'}, status=500)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_editor_apply(request, session_id):
    """
    Apply annotation layers to a PDF and generate final output.
    Expects POST with JSON body: { layers: [...] }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        from core.tools.pdf_flattener import flatten_pdf_with_layers
        
        data = json.loads(request.body)
        layers = data.get('layers', [])
        
        session_dir = os.path.join(settings.MEDIA_ROOT, 'sessions', session_id)
        if not os.path.exists(session_dir):
            return JsonResponse({'error': 'Session not found'}, status=404)
        
        # Get the first PDF in session
        pdf_files = [f for f in os.listdir(session_dir) if f.lower().endswith('.pdf')]
        if not pdf_files:
            return JsonResponse({'error': 'No PDF found in session'}, status=400)
        
        input_pdf = os.path.join(session_dir, pdf_files[0])
        
        # Generate output path
        output_dir = os.path.join(settings.MEDIA_ROOT, 'outputs')
        os.makedirs(output_dir, exist_ok=True)
        output_name = f"edited_{uuid.uuid4()}.pdf"
        output_path = os.path.join(output_dir, output_name)
        
        # Flatten layers
        success = flatten_pdf_with_layers(input_pdf, layers, output_path)
        
        if success:
            # Create task record
            task = DocumentTask.objects.create(
                task_type='edit_pdf',
                status='success',
                original_filenames=pdf_files[0],
                output_file=f"outputs/{output_name}"
            )
            return JsonResponse({
                'success': True,
                'redirect_url': f"/result/{task.id}"
            })
        else:
            return JsonResponse({'error': 'Failed to flatten PDF'}, status=500)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def api_analyze_pdf(request, session_id, page_num):
    """
    Analyze text on a specific PDF page for Inspector Mode.
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    try:
        from core.tools.pdf_analyzer import analyze_pdf_text
        
        session_dir = os.path.join(settings.MEDIA_ROOT, 'sessions', session_id)
        if not os.path.exists(session_dir):
            return JsonResponse({'error': 'Session not found'}, status=404)
            
        # Get the first PDF in session
        pdf_files = [f for f in os.listdir(session_dir) if f.lower().endswith('.pdf')]
        if not pdf_files:
            return JsonResponse({'error': 'No PDF found in session'}, status=400)
            
        input_pdf = os.path.join(session_dir, pdf_files[0])
        
        # Analyze
        text_data = analyze_pdf_text(input_pdf, int(page_num))
        
        if text_data is None:
             return JsonResponse({'error': 'Failed to analyze text'}, status=500)
             
        return JsonResponse({
            'success': True,
            'page': page_num,
            'text_blocks': text_data
        })
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)