from app import create_app

app = create_app()

# List all registered routes
print("\n=== CALENDAR ROUTES ===")
with app.app_context():
    for rule in app.url_map.iter_rules():
        if 'calendar' in str(rule):
            print(f"{rule.methods} - {rule}")
            
print("\n=== ALL API ROUTES ===")
with app.app_context():
    for rule in app.url_map.iter_rules():
        if '/api/' in str(rule):
            print(f"{rule.methods} - {rule}")
