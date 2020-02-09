## How To Run

Create virtual environment:
```bash
virtualenv venv -p "$(which python3)"
source venv/bin/activate
```

Install required packages
```bash
pip install -r requirements.txt
```

For development:
```bash
FLASK_ENV=development flask run
```

http://localhost:5000/v1/my-ip
