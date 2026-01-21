def api_upload_session(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    try:
        files = request.FILES.getlist('files[]') # Support multiple files
        if not files and 'file' in request.FILES:
             files = [request.FILES['file']]
             
        if not files:
            return JsonResponse({'error': 'No files provided'}, status=400)
            
        session_id = str(uuid.uuid4())
        session_dir = os.path.join(settings.MEDIA_ROOT, 'sessions', session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        file_info = []
        for f in files:
            # Sanitize filename
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
    """
    Render multiple tools in a single unified editor interface.
    """
    # Verify session exists (basic validity check)
    session_dir = os.path.join(settings.MEDIA_ROOT, 'sessions', session_id)
    if not os.path.exists(session_dir):
        # In a real app we might redirect to upload or show error.
        # For now, let's assume valid or just render empty (client-side will fail to load files)
        pass

    ctx = {
        'tool': tool,
        'session_id': session_id,
        # We can pass initial file list if we want, or let JS fetch it.
        # Let's pass the files present in the dir to avoid an extra RTT
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
