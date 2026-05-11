# VNCubing

Organise competitions for Vietnamese cubing community

## Getting started

Requirements: Python 3.11 and MySQL.

1. Clone this repo and cd into it
```cmd
git clone https://github.com/hkgkhanh/vncubing.git
cd vncubing
```

2. Setup database

Make sure MySQL is running, then execute the [schema file](data/db_schema.sql).
```cmd
mysql -u <your_username> -p < data/db_schema.sql
```
<!-- Optionally, you can add pre-built data to the database. (COMING SOON) -->

3. Run backend server
```cmd
cd backend
pip install -r requirements.txt
uvicorn main:app --port 8000 --host localhost --reload
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Licence
This project is licensed under the [MIT License](LICENSE).