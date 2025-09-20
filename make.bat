@echo off
SET CMD=%1

IF /i "%CMD%"=="test" (
	echo Executando testes...
	poetry run pytest --cov=mtcli_risco --cov-report=html
	goto :EOF
)

IF "%CMD%"=="format" (
	echo Formatando o codigo com black...
	poetry run black .
    goto :EOF
)

IF /i "%CMD%"=="check" (
	echo Verificando o codigo com black...
	poetry run black --check .
	goto :EOF
)

echo Comando invalido: %CMD%
echo Uso: make [test] [format] [check]
