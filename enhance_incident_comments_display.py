import os
import sys
import django

# Add the project path to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from pathlib import Path
import re

def enhance_incident_detail_template():
    """
    Updates the incident_detail.html template to include a dedicated comments section
    """
    template_path = Path(__file__).parent / 'dashboard' / 'templates' / 'dashboard' / 'checklist' / 'incident_detail.html'
    
    if not template_path.exists():
        print(f"Error: {template_path} not found.")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Check if we already have a comments section
    if '<!-- Lista de Comentarios -->' in content:
        print("Comments section already exists in the template")
        return False
    
    # Find the comment form
    comment_form_section = '''            <!-- Agregar Comentario -->
            <div class="card shadow">
                <div class="card-header py-3">
                    <h6 class="m-0 font-weight-bold text-primary">Añadir Comentario</h6>
                </div>
                <div class="card-body">
                    <form id="addCommentForm">
                        {% csrf_token %}
                        <div class="mb-3">
                            <textarea class="form-control" id="commentText" name="comment" rows="3" placeholder="Escribe un comentario sobre este incidente..."></textarea>
                        </div>
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-comment"></i> Publicar Comentario
                        </button>
                    </form>
                </div>
            </div>'''
    
    # Create a new section for comments list
    comments_list_section = '''            <!-- Lista de Comentarios -->
            <div class="card shadow mb-4">
                <div class="card-header py-3">
                    <h6 class="m-0 font-weight-bold text-primary">Comentarios</h6>
                </div>
                <div class="card-body">
                    {% if incident.comments.exists %}
                    <div class="comments-list">
                        {% for comment in incident.comments.all %}
                        <div class="comment-item mb-3 p-3 {% if forloop.first %}border-start border-4 border-primary{% else %}border-start border-4 border-light{% endif %} bg-light rounded">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <div class="comment-author">
                                    <strong class="text-primary">{{ comment.user.get_full_name }}</strong>
                                    {% if comment.user == incident.reported_by %}
                                    <span class="badge bg-info text-white ms-2">Reportante</span>
                                    {% endif %}
                                    {% if comment.user == incident.assigned_to %}
                                    <span class="badge bg-success text-white ms-2">Asignado</span>
                                    {% endif %}
                                </div>
                                <small class="text-muted">{{ comment.created_at|date:"d/m/Y H:i" }}</small>
                            </div>
                            <p class="comment-text mb-0">{{ comment.text|linebreaks }}</p>
                        </div>
                        {% endfor %}
                    </div>
                    {% else %}
                    <div class="text-center py-3">
                        <p class="text-muted">No hay comentarios todavía</p>
                    </div>
                    {% endif %}
                </div>
            </div>
            
''' + comment_form_section
    
    # Replace the old comment form with the new section that includes comments list
    updated_content = content.replace(comment_form_section, comments_list_section)
    
    # Add CSS for comments
    css_section = '''    /* Estilos para comentarios */
    .comments-list {
        max-height: 500px;
        overflow-y: auto;
    }
    .comment-item {
        transition: background-color 0.2s;
    }
    .comment-item:hover {
        background-color: #f8f9fa !important;
    }
    .comment-author {
        display: flex;
        align-items: center;
    }
'''
    
    # Add CSS to the style section
    style_tag_end = '</style>'
    if style_tag_end in updated_content:
        updated_content = updated_content.replace(style_tag_end, css_section + style_tag_end)
    
    with open(template_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print("Successfully updated the incident_detail.html template with a comments section")
    return True

def update_incident_detail_view():
    """
    Updates the incident_detail view to include comments in the context
    """
    views_path = Path(__file__).parent / 'dashboard' / 'views' / 'checklist_views.py'
    
    if not views_path.exists():
        print(f"Error: {views_path} not found.")
        return False
    
    with open(views_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Check if we need to update the import
    if 'from dashboard.models_checklist import IncidentComment' not in content:
        # Add import if needed
        import_statement = 'from dashboard.models_checklist import IncidentReport, IncidentHistory'
        if import_statement in content:
            updated_import = 'from dashboard.models_checklist import IncidentReport, IncidentHistory, IncidentComment'
            content = content.replace(import_statement, updated_import)
    
    # The incident_detail view already includes the comments through the incident object
    # Since we've defined a related_name='comments' in the IncidentComment model,
    # Django will automatically make the comments available via incident.comments.all()
    
    # No changes needed for the context, but we'll make sure the comments are ordered correctly
    if '.order_by(\'-created_at\')' not in content:
        # Find the incident_detail view
        incident_detail_pattern = re.compile(r'def incident_detail\(request, incident_id\):.*?return render\(.*?\)', re.DOTALL)
        incident_detail_match = incident_detail_pattern.search(content)
        
        if incident_detail_match:
            incident_detail_view = incident_detail_match.group(0)
            # Add ordering to the context
            updated_view = incident_detail_view.replace(
                "incident_history = IncidentHistory.objects.filter(incident=incident).order_by('-timestamp')",
                "incident_history = IncidentHistory.objects.filter(incident=incident).order_by('-timestamp')\n    \n    # Get comments\n    comments = incident.comments.all().order_by('-created_at')"
            )
            
            updated_view = updated_view.replace(
                "context = {",
                "context = {\n        'comments': comments,"
            )
            
            # Replace the view in the content
            content = content.replace(incident_detail_view, updated_view)
    
    with open(views_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print("Successfully updated incident_detail view to include comments in the context")
    return True

def main():
    template_updated = enhance_incident_detail_template()
    view_updated = update_incident_detail_view()
    
    if template_updated or view_updated:
        print("\nEnhancements completed successfully!")
        print("\nNext steps:")
        print("1. Restart your Django server if it's running")
        print("2. Visit an incident detail page to see the comments section")
        print("3. Test adding new comments and verify they appear in both the comments section and history timeline")
    else:
        print("\nNo changes were needed - your incident system already has comment functionality")

if __name__ == "__main__":
    main()
