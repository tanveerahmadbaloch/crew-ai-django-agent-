from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.contrib.auth import login, authenticate
from django.contrib import messages
import re

from .models import Content
from .services.crewai_service import CrewAIService
from .forms import SignUpForm

def home(request):
    """Home page view"""
    return render(request, 'crewai_app/home.html')

def signup(request):
    """User registration view"""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in after registration
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "Registration successful! Welcome to CrewAI Content Generator.")
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'crewai_app/signup.html', {'form': form})

@login_required
def create_content(request):
    """View to create new content"""
    if request.method == 'POST':
        idea = request.POST.get('idea', '')
        
        # Create a new content object
        content = Content.objects.create(
            title="Processing...",
            content="",
            user=request.user,
            status='processing'
        )
        
        try:
            # Run synchronously
            service = CrewAIService()
            result = service.generate_content(idea)
            
            # Extract title from the result
            title = extract_title_from_result(result)
            
            # Update content
            content.content = result
            content.title = title
            content.status = 'completed'
            content.save()
            
        except Exception as e:
            content.status = 'failed'
            content.content = f"Error: {str(e)}"
            content.save()
        
        # Redirect to the content detail page
        return redirect('content_detail', content_id=content.id)
    
    return render(request, 'crewai_app/create_content.html')

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

@login_required
def content_detail(request, content_id):
    """View to display content details"""
    content = get_object_or_404(Content, id=content_id)
    
    return render(request, 'crewai_app/content_detail.html', {
        'content': content
    })

@login_required
def content_list(request):
    """View to list all content for the current user"""
    contents = Content.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'crewai_app/content_list.html', {
        'contents': contents
    })

@csrf_exempt
def check_content_status(request, content_id):
    """API endpoint to check content generation status"""
    content = get_object_or_404(Content, id=content_id)
    
    return JsonResponse({
        'status': content.status,
        'title': content.title,
        'content': content.content if content.status == 'completed' else ''
    })
