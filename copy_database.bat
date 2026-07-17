@echo off
:: Check if the file exists
if exist "stock_rental_system.db" (
    echo Copying file...
    copy "stock_rental_system.db" "D:\"
    echo File copied successfully to D:\
) else (
    echo Error: File stock_rental_system.db not found in the current directory.
)
pause