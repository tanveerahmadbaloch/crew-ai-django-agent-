from celery import shared_task
import os
import re

from .services.crewai_service import CrewAIService
from .models import Content

@shared_task
def generate_content_task(content_id, idea):
    """
    Celery task to generate content using CrewAI
    """
    try:
        # Get the content object
        content_obj = Content.objects.get(id=content_id)
        
        # Update status to processing
        content_obj.status = 'processing'
        content_obj.save()
        
        # Generate content
        service = CrewAIService()
        result = service.generate_content(idea)
        
        # Extract title from the result or from the file path
        title = extract_title_from_result(result)
        
        # Update content object
        content_obj.title = title
        content_obj.content = result
        content_obj.status = 'completed'
        content_obj.save()
        
        return {
            'status': 'success',
            'content_id': content_id,
            'title': title
        }
    except Exception as e:
        # Update content object with error
        content_obj = Content.objects.get(id=content_id)
        content_obj.status = 'failed'
        content_obj.save()
        
        return {
            'status': 'error',
            'content_id': content_id,
            'error': str(e)
        }

def extract_title_from_result(result):
    """
    Extract title from the result or from the file path
    """
    # Try to find a title in the result
    title_match = re.search(r'# (.*?)(\n|$)', result)
    if title_match:
        return title_match.group(1)
    
    # Try to find a file path in the result
    file_path_match = re.search(r'File written to \./lore/(.*?)\.txt', result)
    if file_path_match:
        return file_path_match.group(1)
    
    # Default title
    return "Generated Content"

