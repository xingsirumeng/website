@echo off
rem 本文件必须保存为 GBK/ANSI 编码，不要存成 UTF-8，否则中文乱码会导致脚本无法运行
rem 启动本地后端，不使用 Docker

cd /d "%~dp0backend"

echo ========================================
echo   启动后端  FastAPI
echo ========================================
echo.

rem 首次运行自动建虚拟环境并装依赖
if not exist "venv\Scripts\python.exe" (
    echo 首次运行，正在创建虚拟环境...
    python -m venv venv
    if errorlevel 1 goto fail_venv
    echo 正在安装依赖，可能要等一两分钟...
    venv\Scripts\python.exe -m pip install -r requirements.txt
    if errorlevel 1 goto fail_deps
    echo.
)

rem .env 不在 git 里，新克隆的仓库没有，从模板生成一份
if not exist ".env" (
    echo 未找到 backend\.env，已从 .env.example 生成一份
    copy /y ".env.example" ".env" >nul
    echo.
    echo   注意：请先打开 backend\.env 把 ADMIN_PASSWORD 改成你自己的密码
    echo         改完重新运行本脚本，否则后台无法登录
    echo.
    pause
    exit /b 0
)

echo 后端地址   http://127.0.0.1:8000
echo 接口文档   http://127.0.0.1:8000/docs
echo 按 Ctrl+C 停止
echo.

rem 只监听本机。想用局域网设备访问，把 127.0.0.1 改成 0.0.0.0
venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
goto end

:fail_venv
echo.
echo [错误] 创建虚拟环境失败，请确认已安装 Python 并加入 PATH
pause
exit /b 1

:fail_deps
echo.
echo [错误] 安装依赖失败，请检查网络
pause
exit /b 1

:end
pause
