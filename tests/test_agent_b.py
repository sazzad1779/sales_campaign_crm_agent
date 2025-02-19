from agents.agent_b import AgentB
import time
def test_agent_b():
    agent = AgentB()
    
    # #Step 1: Send Outreach Emails
    print(agent.send_outreach_emails())
    
    # # # Step 2: Wait for responses
    time.sleep(30)
    
    # # Step 3: Process Responses and Update Google Sheets
    print(agent.update_responses())