#!/bin/bash
# zeropkg_test_all.sh - executa testes para todos os pacotes instalados/compilados

FROOT=${FROOT:-/var/tmp/zeropkg/build/sandbox}
LOG_FILE="$FROOT/var/log/zeropkg/test_results.log"
mkdir -p "$(dirname $LOG_FILE)"

echo "=== Iniciando testes de todos os pacotes ===" | tee -a $LOG_FILE

all_ok=true

# Função de teste genérico
test_package() {
    local pkg_name="$1"
    local pkg_dir="$2"
    echo "Testando pacote: $pkg_name" | tee -a $LOG_FILE

    # 1. Testes upstream
    if [ -f "$pkg_dir/Makefile" ]; then
        (cd "$pkg_dir" && make check) &>> $LOG_FILE || all_ok=false
    elif [ -f "$pkg_dir/CMakeLists.txt" ]; then
        (cd "$pkg_dir" && ctest --output-on-failure) &>> $LOG_FILE || all_ok=false
    elif [ -f "$pkg_dir/Cargo.toml" ]; then
        (cd "$pkg_dir" && cargo test) &>> $LOG_FILE || all_ok=false
    elif [ -f "$pkg_dir/setup.py" ]; then
        (cd "$pkg_dir" && python3 setup.py test) &>> $LOG_FILE || all_ok=false
    fi

    # 2. Script genérico de sanity check
    BIN=$(find "$FROOT/usr/bin" -maxdepth 1 -type f -executable -name "$pkg_name*")
    if [ -n "$BIN" ]; then
        echo "Executando sanity check para $pkg_name..." | tee -a $LOG_FILE
        "$BIN" --version &>> $LOG_FILE || all_ok=false
    else
        echo "[WARNING] Binário de $pkg_name não encontrado no sandbox" | tee -a $LOG_FILE
    fi
}

# Percorre todos os pacotes no sandbox
for pkg_dir in $FROOT/src/*; do
    pkg_name=$(basename "$pkg_dir")
    test_package "$pkg_name" "$pkg_dir"
done

echo "=== Resultados finais dos testes ===" | tee -a $LOG_FILE
if [ "$all_ok" = true ]; then
    echo "Todos os pacotes passaram nos testes!" | tee -a $LOG_FILE
    exit 0
else
    echo "Alguns pacotes falharam. Verifique o log em $LOG_FILE" | tee -a $LOG_FILE
    exit 1
fi
