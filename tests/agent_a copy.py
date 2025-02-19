from tools.google_sheets_tool import GoogleSheetsTool
from tools.email_verifier_tool import EmailVerifierTool

class AgentA:
    def __init__(self):
        """Initialize Agent A for email verification."""
        self.sheets = GoogleSheetsTool()
        self.verifier = EmailVerifierTool()

    def verify_emails(self):
        """Reads leads from Google Sheets, verifies emails, and updates the status."""
        leads = self.sheets.read_leads()

        for index, lead in enumerate(leads, start=2):  # Row 1 is the header
            email = lead[1].strip() if len(lead) > 1 and lead[1] else ""  # Column 'B'
            email_verified = lead[5].strip() if len(lead) > 5 and lead[5] else ""  # Column 'F'

            # Verify email only if Column 'F' is empty and Column 'B' has an email
            if not email_verified and email:
                is_valid = self.verifier.verify_email(email)

                # Update Column 'F' based on verification result
                status = "Y" if is_valid else "N"
                self.sheets.update_lead(row=index, col="F", value=status)

                print(f"✅ Updated row {index}: Email '{email}' → Verified: '{status}'")

if __name__ == "__main__":
    agent = AgentA()
    agent.verify_emails()
