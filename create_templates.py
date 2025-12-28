import os
from pathlib import Path


def create_all_templates():
    # Get project root directory
    project_root = Path(__file__).parent
    templates_dir = project_root / 'templates'

    print(f"Project root: {project_root}")
    print(f"Templates directory: {templates_dir}")

    # Create templates directory
    templates_dir.mkdir(exist_ok=True)
    print(f"Templates directory created: {templates_dir.exists()}")

    # Template contents
    templates = {
        'login.html': '''<!DOCTYPE html>
<html>
<head>
    <title>Login - Engineering College</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            background: #f5f5f5; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            height: 100vh; 
            margin: 0; 
        }
        .login-container { 
            background: white; 
            padding: 40px; 
            border-radius: 10px; 
            box-shadow: 0 0 20px rgba(0,0,0,0.1); 
            width: 100%; 
            max-width: 400px; 
        }
        h1 { color: #333; text-align: center; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; color: #555; }
        input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        button { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .error { color: red; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>Engineering College Login</h1>

        {% if form.errors %}
        <div class="error">Invalid username or password. Please try again.</div>
        {% endif %}

        <form method="post">
            {% csrf_token %}
            <div class="form-group">
                <label>Username:</label>
                <input type="text" name="username" required>
            </div>
            <div class="form-group">
                <label>Password:</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit">Login</button>
        </form>
    </div>
</body>
</html>''',

        'dashboard.html': '''<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - Engineering College</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        .nav { margin-bottom: 20px; }
        .nav a { margin-right: 10px; text-decoration: none; padding: 10px; background: #007bff; color: white; border-radius: 5px; }
        .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 20px 0; }
        .stat-card { background: #f8f9fa; padding: 20px; border-radius: 5px; text-align: center; }
        .stat-number { font-size: 2em; font-weight: bold; color: #007bff; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/faculty/">Faculty</a>
            <a href="/gallery/">Gallery</a>
            <a href="/logout/">Logout</a>
        </div>
        <h1>Welcome, {{ user.username }}!</h1>
        <p>Engineering College Management System</p>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">1,248</div>
                <div>Students</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">84</div>
                <div>Faculty</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">12</div>
                <div>Departments</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">56</div>
                <div>Courses</div>
            </div>
        </div>
    </div>
</body>
</html>''',

        'gallery.html': '''<!DOCTYPE html>
<html>
<head>
    <title>Gallery - Engineering College</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        .nav { margin-bottom: 20px; }
        .nav a { margin-right: 10px; text-decoration: none; padding: 10px; background: #007bff; color: white; border-radius: 5px; }
        .gallery { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
        .gallery-item { background: #f8f9fa; padding: 20px; border-radius: 5px; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/faculty/">Faculty</a>
            <a href="/logout/">Logout</a>
        </div>
        <h1>College Gallery</h1>
        <div class="gallery">
            {% for item in gallery_items %}
            <div class="gallery-item">
                <h3>{{ item.title }}</h3>
                <p>{{ item.description }}</p>
                <small>Category: {{ item.category }}</small>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>''',

        'test.html': '''<!DOCTYPE html>
<html>
<head>
    <title>Test - Engineering College</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; text-align: center; }
        .success { color: green; font-size: 2em; margin-bottom: 20px; }
        .nav { margin-top: 30px; }
        .nav a { display: inline-block; margin: 0 10px; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="success">✅ Template Test Successful!</div>
        <p><strong>Template system is working correctly.</strong></p>
        <p>This confirms that Django can find and render templates from the templates directory.</p>
        <div class="nav">
            <a href="/debug/">Check Template Debug</a>
            <a href="/login/">Go to Login</a>
            <a href="/">Go to Dashboard</a>
        </div>
    </div>
</body>
</html>'''
    }

    # Additional basic templates
    basic_templates = {
        'faculty_list.html': 'Faculty Management',
        'student.html': 'Student Management',
        'department_list.html': 'Departments',
        'subjects.html': 'Subject Management',
        'exambranch.html': 'Exam Branch',
        'library.html': 'Library Management',
        'faculty_add.html': 'Add Faculty',
        'faculty_edit.html': 'Edit Faculty',
        'faculty_delete.html': 'Delete Faculty',
        '404.html': '404 Not Found',
        '500.html': '500 Server Error'
    }

    for name, title in basic_templates.items():
        templates[name] = f'''<!DOCTYPE html>
<html>
<head>
    <title>{title} - Engineering College</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }}
        .nav {{ margin-bottom: 20px; }}
        .nav a {{ margin-right: 10px; text-decoration: none; padding: 10px; background: #007bff; color: white; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/gallery/">Gallery</a>
            <a href="/logout/">Logout</a>
        </div>
        <h1>{title}</h1>
        <p>{title} page content will be displayed here.</p>
    </div>
</body>
</html>'''

    # Create all template files
    for filename, content in templates.items():
        file_path = templates_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created: {filename}")

    # List created files
    print(f"\\nFiles in templates directory:")
    for file in templates_dir.iterdir():
        print(f"  - {file.name}")


if __name__ == "__main__":
    create_all_templates()