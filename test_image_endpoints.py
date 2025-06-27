#!/usr/bin/env python
"""
Test script for image upload functionality in the Coderr API.
Tests offer image uploads and profile picture uploads.
"""

import requests
import json
from PIL import Image
import io
import os

# Server base URL
BASE_URL = "http://127.0.0.1:8000/api"

def create_test_image(filename="test_upload.jpg"):
    """Create a simple test image for uploading."""
    img = Image.new('RGB', (100, 100), color='blue')
    img.save(filename)
    return filename

def test_user_registration():
    """Test user registration to get authentication token."""
    import time
    timestamp = str(int(time.time()))
    
    url = f"{BASE_URL}/registration/"
    data = {
        "username": f"imagetestuser{timestamp}",
        "email": f"imagetest{timestamp}@example.com", 
        "password": "testpass123",
        "repeated_password": "testpass123",
        "type": "business"
    }
    
    print("Testing user registration...")
    try:
        response = requests.post(url, json=data)
        print(f"Registration Status: {response.status_code}")
        if response.status_code == 201:
            result = response.json()
            print(f"✅ User created successfully! Token: {result.get('token')}")
            return result.get('token')
        else:
            print(f"❌ Registration failed: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running on port 8000?")
        return None

def test_offer_image_upload(token):
    """Test creating an offer with an image."""
    if not token:
        print("❌ No token available for offer test")
        return
    
    # Create test image
    image_file = create_test_image("offer_test.jpg")
    
    url = f"{BASE_URL}/offers/"
    headers = {"Authorization": f"Token {token}"}
    
    # Test data for offer creation
    offer_data = {
        "title": "Test Offer with Image",
        "description": "Testing image upload functionality",
        "details": [
            {
                "title": "Basic",
                "revisions": 1,
                "delivery_time_in_days": 3,
                "price": "50.00",
                "features": ["Feature 1"],
                "offer_type": "basic"
            }
        ]
    }
    
    print("\nTesting offer creation with image...")
    try:
        with open(image_file, 'rb') as img:
            files = {'image': img}
            # For multipart form data, we need to send JSON data differently
            data = {
                'title': offer_data['title'], 
                'description': offer_data['description'],
                'details': json.dumps(offer_data['details'])
            }
            
            response = requests.post(url, headers=headers, data=data, files=files)
            print(f"Offer Creation Status: {response.status_code}")
            if response.status_code == 201:
                result = response.json()
                print(f"✅ Offer created successfully! ID: {result.get('id')}")
                if result.get('image'):
                    print(f"✅ Image uploaded: {result.get('image')}")
                else:
                    print("⚠️ Offer created but no image field in response")
                return result.get('id')
            else:
                print(f"❌ Offer creation failed: {response.text}")
                return None
    except FileNotFoundError:
        print(f"❌ Test image file not found: {image_file}")
        return None
    finally:
        # Clean up test image
        if os.path.exists(image_file):
            os.remove(image_file)

def test_profile_image_upload(token):
    """Test updating user profile with image."""
    if not token:
        print("❌ No token available for profile test")
        return
    
    # Create test image
    image_file = create_test_image("profile_test.jpg")
    
    # First get user ID
    headers = {"Authorization": f"Token {token}"}
    
    print("\nTesting profile image upload...")
    try:
        # Get user info from token (we'll need user ID)
        # For now, assume user ID is 1 (adjust as needed)
        user_id = 1  # This might need to be dynamic
        
        url = f"{BASE_URL}/profile/{user_id}/"
        
        with open(image_file, 'rb') as img:
            files = {'file': img}  # 'file' is the field name in UserProfile
            data = {'first_name': 'Test', 'last_name': 'User'}
            
            response = requests.patch(url, headers=headers, data=data, files=files)
            print(f"Profile Update Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Profile updated successfully!")
                if 'file' in result and result['file']:
                    print(f"✅ Profile image uploaded: {result['file']}")
                else:
                    print("⚠️ Profile updated but no image field in response")
            else:
                print(f"❌ Profile update failed: {response.text}")
                
    except FileNotFoundError:
        print(f"❌ Test image file not found: {image_file}")
    finally:
        # Clean up test image
        if os.path.exists(image_file):
            os.remove(image_file)

def main():
    """Run all image upload tests."""
    print("🧪 Testing Image Upload Functionality for Coderr API")
    print("=" * 50)
    
    # Test 1: User Registration
    token = test_user_registration()
    
    if token:
        # Test 2: Offer Image Upload
        test_offer_image_upload(token)
        
        # Test 3: Profile Image Upload
        test_profile_image_upload(token)
    
    print("\n" + "=" * 50)
    print("🏁 Image upload tests completed!")

if __name__ == "__main__":
    main()
