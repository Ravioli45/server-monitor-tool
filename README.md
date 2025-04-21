# Server Monitor and Diagnostic Tool

Web-based app created to monitor URLs given by the user and alert users when there may be issues with the server. This includes if the server responds with a non 200 OK response code and if the SSL certificate is expired

## Installation

1. Use git clone to get the most recent copy of the [source code]

```sh
git clone https://github.com/Ravioli45/server-monitor-tool.git
cd server-monitor-tool
```
[source code]:https://github.com/Ravioli45/server-monitor-tool/

2. Create and activate python virtual environment
```sh
python -m venv .venv
source .venv/Scripts/activate
```
Note: The command shown above for activating the virtual environment will be different on windows command prompt and powershell

In windows command prompt:
```sh
.venv\Scripts\activate.bat
```
In powershell
```sh
. .\.venv\Scripts\activate.ps1
```
Note: The powershell version won't be able to run if running scripts is disables

3. Install dependencies
```sh
pip install -r requirements.txt
```

4. Set up testing database
```sh
flask db upgrade
```
An sqlite database saved as `app.db` is used when running the app locally for testing. The above command will create tables in the database based on the auto-generated python scripts in the `migrations` directory. The scripts in the migration directory are based on the python classes in `app/models.py`

## Running the App
1. Use Flask to run the app
```sh
flask run
```
Note: If you are running this locally you may want to include the `--debug` flag on the above command so that the server is automatically restarted when changes are detected
