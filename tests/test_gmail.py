from tools.gmail_tool import GmailTool
def test_gmail():
    gmail = GmailTool()

    # Test sending an email
    gmail.send_email(
        recipient="sazzad1779@gmail.com",
        subject="Test Email",
        message="This is a test email from the Gmail API."
    )
