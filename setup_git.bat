@echo off
echo Creating .gitignore file...

(
echo # Python
echo __pycache__/
echo *.py[cod]
echo *$py.class
echo *.so
echo .Python
echo *.egg-info/
echo dist/
echo build/
echo.
echo # Virtual Environment
echo venv/
echo vvv/
echo env/
echo ENV/
echo.
echo # Environment Variables
echo .env
echo .env.local
echo.
echo # Folders to ignore
echo uploads/
echo reports/
echo.
echo # IDEs
echo .vscode/
echo .idea/
echo *.swp
echo *.swo
echo *~
echo.
echo # OS
echo .DS_Store
echo Thumbs.db
echo.
echo # Flask
echo instance/
echo .webassets-cache
echo.
echo # Logs
echo *.log
) > .gitignore

echo Initializing git repository...
git init

echo Adding all files...
git add .

echo Creating initial commit...
git commit -m "Initial commit: Inspectify - Data Validation Tool"

echo Renaming branch to main...
git branch -M main

echo Adding remote repository...
git remote add origin https://github.com/Coded-by-Sam/Inspectify-The-Data-Validation-Tool-.git

echo Pushing to GitHub...
git push -u origin main

echo Done!
pause