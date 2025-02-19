import json

def save_result_to_json(result, filename="supervisor_report.json"):
    """Converts result to a JSON-serializable format and saves it to a file."""
    
    def convert_message(msg):
        """Converts LangGraph messages into a serializable dictionary."""
        return {
            "role": msg.get("name", "Unknown"),
            "content": msg.get("content", ""),
            "metadata": msg.get("response_metadata", {})
        }

    # Step 1: Extract only serializable content from messages
    result_dict = {
        "messages": [convert_message(msg) for msg in result.get("messages", [])]
    }

    # Step 2: Save as JSON file
    with open(filename, "w", encoding="utf-8") as json_file:
        json.dump(result_dict, json_file, indent=4, ensure_ascii=False)

    print(f"✅ Supervisor report saved as '{filename}'")


