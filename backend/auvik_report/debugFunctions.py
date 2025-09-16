import json
import requests

def response_csv(response) -> None:
    """
    Takes a JSON and outputs it into its own file

    Args:
        JSON: Response from the API before response.json()
    
    Returns:
        None
    """
    if response.status_code == 200:
        data = response.json()
        with open("output.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print("JSON data saved to output.json")
    else:
        print(f"Request failed with status code {response.status_code}")

def error_output(response) -> None:
    """
    Takes a response from the API that is causing errors and outputs the errors into a CSV file.

    Args:
        response: Response object from the requests library.

    Returns:
        None
    """
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        print(f"[ERROR] HTTP {response.status_code} Error: {http_err}")
        try:
            error_details = response.json().get("errors", [])
            print("[INFO] Error details from API:")
            for err in error_details:
                print(f" - {err.get('title', 'No Title')}: {err.get('detail', 'No Details')}")
        except json.JSONDecodeError:
            print("[WARNING] Response did not contain valid JSON.")

        # Optionally, write to a log file:
        with open("errors.log", "a") as f:
            f.write(f"\n[HTTP {response.status_code}] {response.url}\n")
            f.write(response.text + "\n")

        raise  # Re-raise the HTTPError to stop execution if needed