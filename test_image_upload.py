#!/usr/bin/env python
"""
Test script to verify image upload functionality in Django models.
"""

import os
import sys
import django
from django.conf import settings

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coderr_backend.settings')
django.setup()

from users.models import UserProfile
from offers.models import Offer
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

def test_image_uploads():
    """Test image upload functionality for offers and user profiles."""
    
    print("🔍 Testing Image Upload Functionality")
    print("=" * 50)
    
    # Create a test image in memory
    img = Image.new('RGB', (100, 100), color='red')
    img_io = io.BytesIO()
    img.save(img_io, format='JPEG')
    img_io.seek(0)
    
    # Create uploaded file object
    test_image = SimpleUploadedFile(
        name='test.jpg',
        content=img_io.getvalue(),
        content_type='image/jpeg'
    )
    
    try:
        # Test 1: Create user with profile image
        print("📝 Test 1: User Profile Image Upload")
        user = User.objects.create_user(
            username='testuser_img',
            email='test@example.com',
            password='testpass123'
        )
        
        profile = UserProfile.objects.create(
            user=user,
            type='business',
            first_name='Test',
            last_name='User',
            file=test_image
        )
        
        print(f"✅ User profile created with ID: {profile.id}")
        print(f"📁 Profile image path: {profile.file.name if profile.file else 'No image'}")
        
        # Test 2: Create offer with image
        print("\n📝 Test 2: Offer Image Upload")
        
        # Reset image for second test
        img_io.seek(0)
        offer_image = SimpleUploadedFile(
            name='offer.jpg',
            content=img_io.getvalue(),
            content_type='image/jpeg'
        )
        
        offer = Offer.objects.create(
            user=user,
            title='Test Offer with Image',
            description='This is a test offer with an image',
            image=offer_image
        )
        
        print(f"✅ Offer created with ID: {offer.id}")
        print(f"📁 Offer image path: {offer.image.name if offer.image else 'No image'}")
        
        # Test 3: Check if media files are properly configured
        print("\n📝 Test 3: Media Configuration Check")
        print(f"📂 MEDIA_ROOT: {settings.MEDIA_ROOT}")
        print(f"🌐 MEDIA_URL: {settings.MEDIA_URL}")
        
        # Test 4: Check file system
        print("\n📝 Test 4: File System Check")
        if profile.file:
            file_path = profile.file.path
            print(f"🔍 Profile image file exists: {os.path.exists(file_path)}")
            print(f"📍 Full path: {file_path}")
        
        if offer.image:
            file_path = offer.image.path
            print(f"🔍 Offer image file exists: {os.path.exists(file_path)}")
            print(f"📍 Full path: {file_path}")
        
        print("\n✅ All image upload tests completed successfully!")
        
        # Clean up
        print("\n🧹 Cleaning up test data...")
        offer.delete()
        profile.delete()
        user.delete()
        print("✅ Cleanup completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_image_uploads()
