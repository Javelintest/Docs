def page_compress(request):
    return render(request, 'core/compress.html')

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
