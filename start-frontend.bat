@echo off
rem 本文件必须保存为 GBK/ANSI 编码，不要存成 UTF-8，否则中文乱码会导致脚本无法运行
rem 启动本地前端，不使用 Docker

cd /d "%~dp0frontend"

echo ========================================
echo   启动前端  Vite
echo ========================================
echo.

rem 首次运行自动装依赖
if not exist "node_modules" (
    echo 首次运行，正在安装依赖，可能要等一两分钟...
    call npm install
    if errorlevel 1 goto fail
    echo.
)

echo 博客首页   http://localhost:5173
echo 管理后台   http://localhost:5173/#/admin
echo 按 Ctrl+C 停止
echo.
echo 提示：后端没启动的话页面会显示"加载失败"，两个脚本需要同时开着
echo.

rem 必须用 call，否则 npm 结束后整个脚本就退出了
call npm run dev
goto end

:fail
echo.
echo [错误] 安装依赖失败，请确认已安装 Node.js 并加入 PATH
pause
exit /b 1

:end
pause
