from dotenv import load_dotenv
load_dotenv()  # Load .env FIRST!

from app import create_app

app = create_app()

if __name__ == '__main__':
    print("🚀 Real Estate Office Pro API is running!")
app.run(debug=True, host='0.0.0.0', port=5001)  # Changed to 5001