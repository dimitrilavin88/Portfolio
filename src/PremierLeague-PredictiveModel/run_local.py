import webbrowser
import time
import subprocess

def main():
    # Start the FastAPI server
    print("Starting the Premier League Predictor...")
    print("This may take a few moments as the model loads...")
    
    # Start the server in a separate process
    server_process = subprocess.Popen(
        ["python", "premierleague_MLModel.py"],
        stdout=subprocess.PIPE
    )
    
    # Wait a few seconds for the server to start
    time.sleep(5)
    
    # Open the browser
    webbrowser.open('http://localhost:8000')
    
    try:
        # Keep the script running
        server_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down the server...")
        server_process.terminate()

if __name__ == "__main__":
    main() 