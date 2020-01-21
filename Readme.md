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

Run the web server
```bash
export FLASK_ENV=production
python app.py
```


For development, set:
```bash
export FLASK_ENV=dev
```
