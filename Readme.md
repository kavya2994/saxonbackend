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
# for Windows:
BACKEND_ENV=development FLASK_ENV=development  flask run

# for Unix:
BACKEND_ENV=dev-unix FLASK_ENV=development  flask run
```

http://localhost:5000/v1/my-ip
