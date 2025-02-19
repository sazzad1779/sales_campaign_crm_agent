import time
import json
from langchain_openai import ChatOpenAI
# from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from tools.google_sheets_tool import GoogleSheetsTool
from tools.gmail_tool import GmailTool


class AgentB:
    def __init__(self):
        """Initialize Agent with LLM, Google Sheets, and Gmail APIs."""
        self.sheets = GoogleSheetsTool()
        self.gmail = GmailTool()
        self.llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.3)

        # Define LangChain Tool for Response Classification
        # self.classification_tool = Tool(
        #     name="Email Response Classifier",
        #     func=self.classify_response_with_note,
        #     description="Classifies an email response into categories (Interested, Not Interested, No Response) and provides a summary."
        # )

        # # Initialize LangChain Agent with Tool
        # self.agent_executor = initialize_agent(
        #     tools=[self.classification_tool],  # Register classification tool
        #     llm=self.llm,
        #     max_iterations=3,
        #     agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,  # Agent follows reasoning
        #     verbose=True,
        #     early_stopping_method='generate',

        # )

    def send_outreach_emails(self):
        """Sends outreach emails to verified leads and updates response status in Google Sheets.
        Returns a summary of sent emails.
        """
        leads = self.sheets.read_leads()
        summary = []  # Store results

        for index, lead in enumerate(leads, start=2):  # Assuming row 1 is header
            email = lead[1].strip() if len(lead) > 1 and lead[1] else ""  # Column 'B'
            email_verified = lead[5].strip() if len(lead) > 5 and lead[5] else ""  # Column 'F'
            response_status = lead[6].strip() if len(lead) > 6 and lead[6] else ""  # Column 'G'

            # Only send emails if the email is verified (F = "Y") and no response exists yet
            if email_verified == "Y" and not response_status:
                subject = "Exciting Sales Opportunity!"
                message = f"Hello,\n\nWe have an amazing offer for you. Let’s connect!\n\nBest regards.\nMd Sazzad Hossain"

                if self.gmail.send_email(email, subject, message):
                    # Update Column G with "Sent"
                    self.sheets.update_lead(row=index, col="G", value="Sent")
                    result = f"📧 Email sent to {email} (Row {index})"
                else:
                    result = f"❌ Email sending failed for {email} (Row {index})"

                summary.append(result)
                # print(result)
                time.sleep(1)  # Prevent hitting rate limits

        # If no emails were sent
        if not summary:
            summary.append("ℹ️ No recipients found to send email.")

        return "\n".join(summary)  # Return summary as a formatted string
    
    def classify_response_with_note(self, email_body: str):
        """Uses LangChain Agent to classify email responses into categories and generate a short summary."""
        prompt = f"""
        You are an AI assistant analyzing email responses. Email response can be anything, Make the answer in categorize and note.and compete it in short and precise. 

        1. Categorize the response into one of the following:
           - "Interested" (if the user wants to proceed).
           - "Not Interested" (if the user declines).
           - "No Response" (if the email is empty or (not among interested/ Not interested classes)).
        
        2. Extract a **brief summary** (1-2 sentences) from the response highlighting key points.

        Here is the email response:
        {email_body}

        Output the result in the following format (JSON):
        {{"classification": "<category>", "note": "<short summary>"}}
        """

        # Use the LangChain Agent to classify responses dynamically
        response = self.llm.invoke(prompt)
        response = response.content
        # Ensure JSON-like structure
        try:
            response_data = json.loads(response)
            classification = response_data.get("classification", "Needs Review")
            note = response_data.get("note", "No additional details.")
        except json.JSONDecodeError:
            classification, note = "Needs Review", "Failed to extract summary."

        return classification.strip(), note.strip()

    def update_responses(self):
        """Fetches email replies, classifies them using an Agent, and updates Google Sheets."""
        responses = self.gmail.fetch_email_responses()
        leads = self.sheets.read_leads()
    
        summary = []
        for index, lead in enumerate(leads, start=2):  # Assuming row 1 is header
            email = lead[1].strip() if len(lead) > 1 and lead[1] else ""  # Column 'B'
            email_verified = lead[5].strip() if len(lead) > 5 and lead[5] else ""  # Column 'F'
            response_status = lead[6].strip() if len(lead) > 6 and lead[6] else ""  # Column 'G'

            # Ensure responses are only checked for Sent emails that were Verified
            if email in responses and response_status == "Sent" and email_verified == "Y":
                full_message = responses[email].strip()
                print(f" Processing response from: {email}")

                # Use LangChain Tool to classify the response
                status, note = self.classify_response_with_note(full_message)
                
                # Update Google Sheets
                self.sheets.update_lead(row=index, col="G", value=status)
                self.sheets.update_lead(row=index, col="H", value=note)

                # print(f"✅ Updated row {index}: Status '{status}', Note stored in Column 'H' (Email: {email})")
                # stats+=1
                # return f"✅ Updated row {index}: Status '{status}', Note stored in Column 'H' (Email: {email})"
                summary.append(f"📩 Row {index}: Email from '{email}' classified as '{status}'. Note: {note}.")

                
        return "\n".join(summary) if summary else "No email responses received." 
       
    # def get_response(self):
    #     """Fetches email replies, classifies them using an Agent, and updates Google Sheets."""
    #     responses = self.gmail.fetch_email_responses()
    #     leads = self.sheets.read_leads()
    #     stats=0
    #     for index, lead in enumerate(leads, start=2):  # Assuming row 1 is header
    #         email = lead[1].strip() if len(lead) > 1 and lead[1] else ""  # Column 'B'
    #         email_verified = lead[5].strip() if len(lead) > 5 and lead[5] else ""  # Column 'F'
    #         response_status = lead[6].strip() if len(lead) > 6 and lead[6] else ""  # Column 'G'

    #         # Ensure responses are only checked for Sent emails that were Verified
    #         if email in responses and response_status == "Sent" and email_verified == "Y":
    #             full_message = responses[email].strip()
    #             print(f" Processing response from: {email}")

    #             # Use LangChain Tool to classify the response
    #             return self.classify_response_prompt(full_message)

                
        
    #     return f"getting  {stats} email and updated {stats} rows in sheet."


if __name__ == "__main__":
    agent = AgentB()
    
    # Step 1: Send Outreach Emails
    print("\n🚀 Sending Outreach Emails...\n")
    agent.send_outreach_emails()
    
    # Step 2: Wait for Responses
    print("\n⏳ Waiting for Responses...\n")
    time.sleep(10)
    
    # Step 3: Process Responses using Agent
    print("\n Updating Responses in Google Sheets...\n")
    agent.update_responses()
