from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    
    # API endpoints
    path('api/merge', views.merge_pdfs_view, name='merge_pdfs'),
    path('api/img2pdf', views.img2pdf_view, name='img2pdf'),
    path('api/pdf2word', views.pdf2word_view, name='pdf2word'),
    path('api/pdf2excel', views.pdf2excel_view, name='pdf2excel'),
    path('api/edit-pdf', views.edit_pdf_view, name='edit_pdf'),
    
    # Legacy download route support
    path('download/<str:filename>', views.download_redirect, name='download'),
    
    # Render partials (if needed, but index works via tabs. JS calls plain redirects mostly)
    # The original app had routes for /merge etc returning same template mostly? No, they had specific templates.
    # But existing index.html switchTab() just toggles visibility. It doesn't navigate.
    # The navbar links (/merge, /img2pdf) in base.html suggest standard navigation.
    # Let's add them to index view to handle navigation or rendering specific tab.
    path('merge', views.page_merge, name='merge_page'),
    path('img2pdf', views.page_img2pdf, name='img2pdf_page'),
    path('pdf2word', views.page_pdf2word, name='pdf2word_page'),
    path('pdf2excel', views.page_pdf2excel, name='pdf2excel_page'),
    path('edit-pdf', views.page_edit_pdf, name='edit_pdf_page'),
    path('result/<int:task_id>', views.page_result, name='result_page'),
]
