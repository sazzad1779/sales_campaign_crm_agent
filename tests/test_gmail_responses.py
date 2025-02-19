from tools.gmail_tool import GmailTool

def test_gmail_responses():
    gmail = GmailTool()
    responses = gmail.fetch_email_responses()

    for email, (response_text, full_message) in responses.items():
        print(f"📧 Response from {email}:")
        print(f"   📜 Classified as: {response_text}")
        print(f"   📝 Full Message:\n{full_message}")
        print("-" * 50)

if __name__ == "__main__":
    test_gmail_responses()
