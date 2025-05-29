import unittest
import requests
from backend.app.config import settings
class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.bucket_name = settings.BUCKET_NAME
        self.headers = {
            "apikey": settings.SUPABASE_SERVICE_ROLE_KEY.get_secret_value(),
            "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY.get_secret_value()}",
            "Content-Type": "application/octet-stream"
        }

    def test_upload_file(self):
        file_path = r"D:\WORKSPACE\intern_task\backend\data\dataset\2501.11140v1.pdf"
        db_path = "test.pdf"
        with open(file_path, 'rb') as f:
            file_data = f.read()
        upload_url = f'{settings.SUPABASE_URL}/storage/v1/object/{settings.BUCKET_NAME}/{db_path}'

        response = requests.put(upload_url, headers=self.headers, data=file_data)

        if response.status_code == 200 or response.status_code == 201:
            print("✅ File uploaded or overwritten successfully")
            self.assertTrue(True)
        elif response.status_code == 409:
            print("⚠️ File already exists (conflict)")
            self.assertEqual(409, response.status_code)
        else:
            self.fail(f"Unexpected status code {response.status_code}: {response.text}")



    def test_file_db_bucket(self):
        data = {
            "name": self.bucket_name,
            "public": True
        }
        response = requests.post(
            f"{settings.SUPABASE_URL}/storage/v1/bucket",
            headers=self.headers,
            json=data
        )
        if response.status_code !=200:
           print("already exists")
           self.assertEqual(400,response.status_code)
        elif response.status_code ==200:
            print("created a new bucket")
            self.assertTrue(True)
        else:
            self.fail(response.json())


if __name__ == '__main__':
    unittest.main()
