import requests
import config as settings

class EmailVerifierTool:
    def __init__(self):
        """Initialize with Hunter.io API key"""
        self.api_key = settings.HUNTER_API_KEY
        self.base_url = "https://api.hunter.io/v2/email-verifier"

    def verify_email(self, email):
        """Check email validity using Hunter.io API"""
        if not email:
            return False

        params = {
            "email": email,
            "api_key": self.api_key
        }

        response = requests.get(self.base_url, params=params)
        data = response.json()

        # Check if the API request was successful
        if response.status_code == 200 and "data" in data:
            status = data["data"]["status"]
            return status == "valid"  # Return True if valid, False otherwise
        else:
            print(f" Email verification failed: {data.get('errors', 'Unknown error')}")
            return False
