from tools.google_sheets_tool import GoogleSheetsTool
from tools.gmail_tool import GmailTool
import time

from langchain_openai import ChatOpenAI
class AgentB:
    def __init__(self):
        self.sheets = GoogleSheetsTool()
        self.gmail = GmailTool()
        self.llm = ChatOpenAI(model_name="gpt-3.5-turbo-0125", temperature=0.3)

    def send_outreach_emails(self):
        """Sends outreach emails to verified leads and updates response status"""
        leads = self.sheets.read_leads()

        for index, lead in enumerate(leads, start=2):  # Assuming row 1 is header
            email = lead[1].strip() if len(lead) > 1 and lead[1] else ""  # Column 'B'
            email_verified = lead[5].strip() if len(lead) > 5 and lead[5] else ""  # Column 'F'
            response_status = lead[6].strip() if len(lead) > 6 and lead[6] else ""  # Column 'G'

            # Only send emails if F = "Y" (verified) and G is empty (no response yet)
            if email_verified == "Y" and not response_status:
                subject = "Exciting Sales Opportunity!"
                message = f"Hello,\n\nWe have an amazing offer for you. Let’s connect!\n\nBest regards."

                if self.gmail.send_email(email, subject, message):

                    # Update G column with "Sent" after sending email
                    self.sheets.update_lead(row=index, col="G", value="Sent")
                    print(f"📧 Agent B: Email sent to {email} (Row {index})")

                    time.sleep(1)  # Prevent hitting rate limits
    
    def classify_response_with_note(self, email_body):
        """Classify email response using OpenAI LLM and extract a short summary note."""
        prompt = f"""
        You are an AI assistant analyzing email responses.

        1. Categorize the response into one of the following:
           - "Interested" (if the user wants to proceed).
           - "Not Interested" (if the user declines).
           - "Needs Review" (if the response is unclear or needs further action).
           - "No Response" (if the email is empty).
        
        2. Extract a **brief summary** (1-2 sentences) from the response highlighting key points.

        Here is the email response:
        {email_body}

        Output the result in the following format (JSON):
        {{"classification": "<category>", "note": "<short summary>"}}
        """
        result = self.llm.invoke(prompt)

        # Ensure the output is valid JSON-like structure
        try:
            response_data = eval(result)
            classification = response_data.get("classification", "Needs Review")
            note = response_data.get("note", "No additional details.")
        except Exception:
            classification, note = "Needs Review", "Failed to extract summary."

        return classification.strip(), note.strip()


    def update_responses(self):
        """Fetch email replies, classify them, and update Google Sheets"""
        responses = self.gmail.fetch_email_responses()
        leads = self.sheets.read_leads()

        for index, lead in enumerate(leads, start=2):  # Assuming row 1 is header
            email = lead[1].strip() if len(lead) > 1 and lead[1] else ""  # Column 'B' (Email)
            email_verified = lead[5].strip() if len(lead) > 5 and lead[5] else ""  # Column 'F' (Verified)
            response_status = lead[6].strip() if len(lead) > 6 and lead[6] else ""  # Column 'G' (Response)

            # Ensure responses are only checked for emails that were Sent (G) and Verified (F)
            if email in responses and response_status == "Sent" and email_verified == "Y":
                full_message = responses[email].strip()  # Fetch full message from responses

                # Classify response and extract a note using OpenAI
                status, note = self.classify_response_with_note(full_message)

                # Update Google Sheets with classification and note
                self.sheets.update_lead(row=index, col="G", value=status)
                self.sheets.update_lead(row=index, col="H", value=note)

                print(f"✅ Updated row {index}: Status '{status}', Note stored in Column 'H' (Email: {email})")

if __name__ == "__main__":
    agent = AgentB()
    # Step 1: Send Outreach Emails
    agent.send_outreach_emails()
    # Step 2: Wait for responses
    time.sleep(10)
    # Step 3: Process Responses and Update Google Sheets
    agent.update_responses()
