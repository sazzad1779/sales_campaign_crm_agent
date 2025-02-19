from langchain_openai import ChatOpenAI
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from typing import Annotated
from agents.agent_b import AgentB
from agents.agent_a import AgentA
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

## load model
model = ChatOpenAI(model="gpt-3.5-turbo")


@tool
def validate_leads(
    query: Annotated[str, "query to start validating using leads information"],

) -> str:
    """when new input comes in the sheet, validate leads based on sheet information and make validate status in the sheet. make a summary as a return."""
    # Email configuration
    
    agent_a =AgentA()
    # verify function calls
    result = agent_a.verify_emails_and_leads()
    return result

@tool
def send_email(
    query: Annotated[str, "query to start sending email"],

) -> str:
    """Send email  based on the sales campaign sheet."""
    # Email configuration
    
    agent = AgentB()
    # #Step 1: Send Outreach Emails
    msg =agent.send_outreach_emails()
    return msg

@tool
def check_email_update_status(
    query: Annotated[str, "query to check unread email and update sheet"],
) -> str:
    """Check Unread email if any reply come agains the sales campaign offer then analysis and fill the status field in sheet."""
    # Email configuration
    agent = AgentB()
    # #Step 2: check Emails for response.
    msg =agent.update_responses()
    return msg

# tool for sending summary
@tool
def send_summary_email(
    query: Annotated[str, "query to send the final summary via email"],
    final_summary: Annotated[str, "final_summary from the all agents"]
) -> str:
    """Sends the final summary of the sales campaign workflow via email.final_summary value will be the supervisor's agent response."""
    from tools.gmail_tool import GmailTool
    # Assuming AgentB can send emails
    gmail = GmailTool()

    # Define email details
    subject = "Sales Campaign - Execution Report"
    recipient = "mdsazzad1779@gmail.com"  # Modify this as needed

    if gmail.send_email(recipient, subject, final_summary):
        return f"📩 Final summary sent to {recipient} successfully."
    else:
        return f"❌ Failed to send final summary to {recipient}."


# Create validation specialized agents
agent_a = create_react_agent(
    model=model,
    tools=[validate_leads],
    name="validate_expert",
    prompt="""You are a lead validation expert. Your responsibility is to validate leads by checking their Name, Company, and Industry based on the sales campaign sheet.
    
    **How you should work:**
    - Read the lead information from the campaign sheet.
    - Verify the validity of the lead details.
    - Update the validation status in the sheet as 'Y' (Valid) or 'N' (Invalid).
    - If a lead is invalid, provide a short note explaining why.
    - Return a structured summary with the total leads validated and any issues encountered.

    Use the 'validate_leads' tool whenever a validation request is received."""
)

# Create outreach specialized agents
agent_b = create_react_agent(
    model=model,
    tools=[send_email, check_email_update_status],
    name="Outreach_expert",
    prompt="""You are an outreach expert responsible for sending sales campaign emails and processing responses.
    
    **Your responsibilities include:**
    
    **Step 1: Send Outreach Emails**
    - Send emails based on the sales campaign details.
    - Ensure emails are only sent to validated leads.
    - Update the campaign sheet after successfully sending an email.
    - If an email fails, log the issue.

    **Step 2: Check Email Responses**
    - Check unread emails to see if any leads responded to the campaign.
    - Classify responses into:
      - 'Interested' → If the lead is interested in the offer.
      - 'Not Interested' → If the lead declines.
      - 'No Response' → If no response is received.
    - Update the campaign sheet with the classification and any relevant notes.

    **Step 3: Generate Summary**
    - Summarize the total emails sent and their success/failure rates.
    - Summarize response classifications and their count.
    - Provide any issues encountered.

    Use the 'send_email' tool to send outreach emails and the 'check_email_update_status' tool to check email responses and update the sheet."""
)


# Create supervisor workflow
supervisor = create_supervisor(
    agents=[agent_a, agent_b],
    model=model,
    tools=[send_summary_email],
    prompt="""You are a supervisor responsible for managing the validation and outreach agents to automate the sales campaign workflow.

    **Your Responsibilities:**
    
    **Step 1: Validate Leads**
    - Assign the 'validate_expert' agent to validate all new leads.
    - Ensure leads are checked for Name, Company, and Industry.
    - Update the campaign sheet accordingly.
    - Collect and store the validation summary.

    **Step 2: Send Outreach Emails**
    - Once leads are validated, assign the 'Outreach_expert' agent to send emails to all verified leads.
    - Ensure no duplicate emails are sent.
    - Track the number of emails successfully sent.
    
    **Step 3: Check Email Responses**
    - Assign the 'Outreach_expert' agent to check unread email responses.
    - Categorize responses as 'Interested', 'Not Interested', or 'No Response'.
    - Update the campaign sheet with classifications.
    
    **Step 4: Generate and Send Final Summary**
    - Collect summaries from all previous steps.
    - Use 'send_summary_email' to send the final execution report via email
    - Provide a structured summary including:
      - ✅ Number of leads validated.
      - 📧 Number of outreach emails sent.
      - 📩 Number of responses received and their classifications.
      - ℹ️ Any issues or notes encountered during execution.
      
    
    Always ensure tasks are assigned in the correct order and avoid re-executing completed tasks. Provide a clear and structured summary after completion.""",
    output_mode="last_message"
)

# Compile the workflow
app = supervisor.compile()

# Example user message to send an email
user_message = {
    "messages": [
        # {"role": "user", "content": "Please validate the leads as if new information comes."},
        # {"role": "user", "content": "Please send an email based on the sales campaign sheet."},
        # {"role": "user", "content": "Please check email responses the sales campaign offer."}
        
        {
        "role": "user",
        "content": """You are responsible for automating the sales campaign workflow by coordinating specialized agents. Execute the following steps in the correct order, utilizing the appropriate agents and tools:
        
        **Step 1: Validate Leads**
        - Use the 'validate_expert' agent to validate all new leads.
        - Ensure Lead Name, Company, and Industry are correctly verified.
        - Update the validation status in the sales campaign sheet.
        - Summarize the number of leads validated and any issues found.

        **Step 2: Send Outreach Emails**
        - Use the 'Outreach_expert' agent to send emails to all verified leads.
        - Emails should be based on the sales campaign details in the sheet.
        - Track the number of emails successfully sent and any failures.

        **Step 3: Check Email Responses**
        - Use the 'Outreach_expert' agent to check for unread emails related to the sales campaign.
        - Classify email responses into categories: 'Interested', 'Not Interested', or 'No Response'.
        - Update the campaign sheet with the appropriate status.

        **Step 4: Generate a Comprehensive Summary**
        - Summarize the total number of leads validated.
        - Summarize the number of outreach emails sent.
        - Summarize the number of email responses received and their classifications.
        - Note any challenges or issues encountered during execution.

        Ensure all steps are executed in the correct sequence using the appropriate tools. Provide a final structured report detailing the results of each step.
    """}
 ]
}

# Function to invoke the supervisor workflow
def run_supervisor_workflow():
    print(" Running Scheduled Sales Campaign Automation...")
    
    # Invoke the app with the user message
    result = app.invoke(user_message)

    # Print the summary
    print("\n Sales Campaign Execution Completed. Summary:")
    print(result)

if __name__ == "__main__":
    run_supervisor_workflow()