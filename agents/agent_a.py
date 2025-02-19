from tools.google_sheets_tool import GoogleSheetsTool
from tools.email_verifier_tool import EmailVerifierTool
from duckduckgo_search import DDGS


class AgentA:
    def __init__(self):
        """Initialize Agent A for lead data verification (excluding and then including email)."""
        self.sheets = GoogleSheetsTool()
        self.verifier = EmailVerifierTool()

    def search_duckduckgo(self, query):
        """Search DuckDuckGo and return True if there are relevant results."""
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            print(results)
            return len(results) > 0  # Returns True if search results exist

    def verify_lead_details(self, lead_name, company, industry):
        """Validates lead details using DuckDuckGo search."""
        validation_results = {
            "lead_name": self.search_duckduckgo(f"{lead_name}"),
            "company": self.search_duckduckgo(f"{company}"),
            "industry": self.search_duckduckgo(f"{industry} industry")
        }

        # Determine overall validity
        if all(validation_results.values()):
            return "Y", "✅ Lead Validated"
        else:
            invalid_fields = [key for key, valid in validation_results.items() if not valid]
            return "N", f"❌ Check: {', '.join(invalid_fields)}"

    def verify_emails_and_leads(self):
        """Reads leads from Google Sheets, verifies lead details first, then verifies emails.
        Only performs verification if Column 'F' is empty. Returns a summary of the verification process.
        """
        leads = self.sheets.read_leads()
        summary = []  # List to accumulate result statements

        for index, lead in enumerate(leads, start=2):  # Row 1 is the header
            email = lead[1].strip() if len(lead) > 1 and lead[1] else ""  # Column 'B'
            email_verified = lead[5].strip() if len(lead) > 5 and lead[5] else ""  # Column 'F'
            lead_name = lead[0].strip() if len(lead) > 0 and lead[0] else ""  # Column 'A'
            company = lead[3].strip() if len(lead) > 3 and lead[3] else ""  # Column 'D'
            industry = lead[4].strip() if len(lead) > 4 and lead[4] else ""  # Column 'E'

            # Check if Column 'F' is empty before performing verification
            if not email_verified:
                print(f" Row {index}: No verification found in Column 'F'. Proceeding with validation & email check.")

                # Step 1: Validate Lead Name, Company, and Industry
                lead_validation_status, lead_note = self.verify_lead_details(lead_name, company, industry)
                # validation_result = f"✅ Row {index}: Lead '{lead_name}' validated as {lead_validation_status}. Email '{email}' verified as {email_status}."
                # summary.append(validation_result)
                # Step 2: If email exists, perform Email Verification
                if email:
                    is_valid = self.verifier.verify_email(email)
                    email_status = "Y" if is_valid else "N"

                    # Update Column 'F' with final result (email validation takes priority)
                    self.sheets.update_lead(row=index, col="F", value=email_status)
                    validation_result = f"✅ Row {index}: Lead '{lead_name}' validated as {lead_validation_status}. Email '{email}' verified as {email_status}."
                else:
                    # If no email, update with lead validation result only
                    self.sheets.update_lead(row=index, col="F", value=lead_validation_status)
                    validation_result = f"✅ Row {index}: Lead '{lead_name}' validated as {lead_validation_status}. No email to verify."

                # Add results to summary
                summary.append(validation_result)
                print(validation_result)

        # If no validations were performed
        if not summary:
            summary.append("ℹ️ No new leads required verification.")

        return "\n".join(summary)  # Return a formatted summary string


if __name__ == "__main__":
    agent = AgentA()
    agent.verify_emails_and_leads()
