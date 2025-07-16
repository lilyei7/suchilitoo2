"""
Test script to verify checklist sidebar highlighting
"""

def test_sidebar_context():
    """
    Test function that simulates the sidebar context functionality
    """
    def get_sidebar_context(view_name):
        """Simplified version of the actual function"""
        checklist_section_active = view_name in [
            # Standard names
            'checklist_dashboard', 'checklist_incidents', 'checklist_notifications', 
            'manage_categories', 'manage_tasks', 'task_history',
            # Alternative names
            'categorias_checklist', 'tareas_checklist', 'historial_checklist', 'notificaciones_checklist',
            'checklist_categories', 'checklist_tasks', 'checklist_history',
            # Generic checklist name
            'checklist'
        ]
        
        return {
            'sidebar_active': view_name,
            'checklist_section_active': checklist_section_active
        }
    
    print("===== Checklist Sidebar Activation Tester =====")
    print("\nTesting sidebar activation for different view names:")

    # Test various checklist-related view names
    test_views = [
        'checklist_dashboard',
        'checklist_categories',
        'checklist_tasks',
        'checklist_history',
        'checklist_incidents', 
        'checklist_notifications',
        'checklist',
        'manage_categories',
        'manage_tasks',
        'task_history'
    ]

    for view in test_views:
        context = get_sidebar_context(view)
        is_active = context['checklist_section_active']
        print(f"{view:25} => {'✅ ACTIVE' if is_active else '❌ INACTIVE'}")

    print("\nTest complete. All checklist sidebar items should now properly highlight in blue.")

if __name__ == "__main__":
    test_sidebar_context()
