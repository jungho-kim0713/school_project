import os
import django
from io import BytesIO

# 1. Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def verify_bulk_upload():
    print("🚀 Bulk Upload Verification Start")
    
    # 2. Create Superuser for login
    admin_user, created = User.objects.get_or_create(username='admin_test', email='admin_test@example.com')
    if created:
        admin_user.set_password('admin123')
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.save()
        print("✅ Created test admin user")
    
    client = Client()
    client.force_login(admin_user)
    
    # 3. Prepare CSV Data
    csv_content = b"""email,name
    test_student_1@school.com, \xed\x95\x99\xec\x83\x9d1
    test_teacher_1@school.com, \xec\x84\xa0\xec\x83\x9d1
    """
    csv_file = BytesIO(csv_content)
    csv_file.name = 'users.csv'
    
    # 4. Cleanup previous test data
    User.objects.filter(email__in=['test_student_1@school.com', 'test_teacher_1@school.com']).delete()
    print("🧹 Cleaned up old test users")

    # 5. Send POST request
    # Note: URL pattern deduced from admin structure: /admin/auth/user/upload-csv/
    # But because we registered User under 'photo.CustomUserAdmin', but it's still 'auth' app label effectively for the model?
    # Actually wait, unregister/register keeps the original app label 'auth'.
    # URL should be /admin/auth/user/upload-csv/
    
    response = client.post('/admin/auth/user/upload-csv/', {'csv_file': csv_file}, follow=True)
    
    if response.status_code == 200:
        print("✅ Request successful (200 OK)")
    else:
        print(f"❌ Request failed: {response.status_code}")
        
    # 6. Verify Users Created
    u1 = User.objects.filter(email='test_student_1@school.com').first()
    u2 = User.objects.filter(email='test_teacher_1@school.com').first()
    
    if u1 and u1.is_active:
        print(f"✅ User 1 Created: {u1.email} (Active: {u1.is_active})")
    else:
        print("❌ User 1 Creation Failed")

    if u2 and u2.is_active:
        print(f"✅ User 2 Created: {u2.email} (Active: {u2.is_active})")
    else:
        print("❌ User 2 Creation Failed")

if __name__ == '__main__':
    verify_bulk_upload()
