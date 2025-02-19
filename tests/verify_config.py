# verify_config.py
import config

def main():
    print(f"GOOGLE_API_KEY: {config.GOOGLE_API_KEY}")
    print(f"GOOGLE_CREDENTIALS_FILE: {config.GOOGLE_CREDENTIALS_FILE}")
    print(f"TOKEN_FILE: {config.TOKEN_FILE}")
    print(f"SHEET_ID: {config.SHEET_ID}")
    print(f"GMAIL_USER_EMAIL: {config.GMAIL_USER_EMAIL}")
    print(f"HUNTER_API_KEY: {config.HUNTER_API_KEY}")
    print(f"CHECK_INTERVAL: {config.CHECK_INTERVAL}")

if __name__ == "__main__":
    main()
