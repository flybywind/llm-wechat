import sys

def process_clipboard_content(content):
    # Process the content here
    processed = f"Processed: {content.upper()}"
    print(processed, flush=True)  # flush=True ensures the output is sent immediately
    # Add your custom processing logic here

if __name__ == "__main__":
    for line in sys.stdin:
        process_clipboard_content(line.strip())