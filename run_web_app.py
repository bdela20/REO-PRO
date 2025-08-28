from dotenv import load_dotenv
load_dotenv()

import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    print("Real Estate Office Pro is running!")
    port = int(os.environ.get('PORT', 5001))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)