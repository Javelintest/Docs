from django.urls import path
from . import views

urlpatterns = [
    # Pages - Redirect to Editor
    path('', views.index, name='index'),
    path('merge', views.editor_entry_view, {'tool': 'merge'}, name='merge_page'),
    path('img2pdf', views.editor_entry_view, {'tool': 'img2pdf'}, name='img2pdf_page'),
    path('pdf2word', views.editor_entry_view, {'tool': 'pdf2word'}, name='pdf2word_page'),
    path('pdf2excel', views.editor_entry_view, {'tool': 'pdf2excel'}, name='pdf2excel_page'),
    path('edit-pdf', views.editor_entry_view, {'tool': 'edit_pdf'}, name='edit_pdf_page'),
    path('compress', views.editor_entry_view, {'tool': 'compress'}, name='compress_page'),
    path('result/<int:task_id>', views.page_result, name='result_page'),

    # APIs
    path('api/merge', views.merge_pdfs_view, name='merge_pdfs_api'),
    path('api/img2pdf', views.img2pdf_view, name='img2pdf_api'),
    path('api/pdf2word', views.pdf2word_view, name='pdf2word_api'),
    path('api/pdf2excel', views.pdf2excel_view, name='pdf2excel_api'),
    path('api/edit-pdf', views.edit_pdf_view, name='edit_pdf_api'),
    path('api/compress', views.compress_pdf_view, name='compress_pdf_api'),

    # Editor Studio
    path('api/upload-session', views.api_upload_session, name='api_upload_session'),
    path('api/process-session/<str:tool>/<str:session_id>', views.api_process_session, name='api_process_session'),
    path('editor/<str:tool>/<str:session_id>', views.editor_view, name='editor_view'),

    # Downloads
    path('download/<path:filename>', views.download_redirect, name='download_file'),
]
