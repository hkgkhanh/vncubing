# VNCubing

Organise competitions for Vietnamese cubing community

## Install and run the project

Requirements: Python 3.11 and MySQL.

1. Clone this repo and cd into it
```cmd
git clone https://github.com/hkgkhanh/vncubing.git
cd vncubing
```

2. Run backend server
```cmd
cd backend
pip install -r requirements.txt
uvicorn main:app --port 8000 --host localhost --reload
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Licence
This project is licensed under the [MIT License](LICENSE).