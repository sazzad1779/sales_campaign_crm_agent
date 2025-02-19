from tools.google_sheets_tool import GoogleSheetsTool
from tools.email_verifier_tool import EmailVerifierTool

def test_google_sheet():
    sheets = GoogleSheetsTool()
    verifier = EmailVerifierTool()

    # Read all leads from Google Sheets
    leads = sheets.read_leads()
    print("Leads Data:", leads)

    # Loop through each row and check conditions
    for index, lead in enumerate(leads, start=2):  # Assuming row 1 is the header
        email = lead[1].strip() if len(lead) > 1 and lead[1] else ""  # Column 'B' (Index 1) is Email
        email_verified = lead[5].strip() if len(lead) > 5 and lead[5] else ""  # Column 'F' (Index 5) is Email Verified

        # Check if 'F' column is empty and 'B' column has a valid email
        if not email_verified and email:
            is_valid = verifier.verify_email(email)

            if is_valid:
                sheets.update_lead(row=index, col="F", value="Y")
                print(f" Updated row {index}, Column 'F' with 'Y' (Valid Email: {email})")
            else:
                sheets.update_lead(row=index, col="F", value="N")
                print(f" Updated row {index}, Column 'F' with 'N' (Invalid Email: {email})")

if __name__ == "__main__":
    test_google_sheet()
