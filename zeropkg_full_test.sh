#!/bin/bash
# zeropkg_full_test.sh
# Script completo de validação do Zeropkg no sandbox

FROOT=${FROOT:-/var/tmp/zeropkg/build/sandbox}
LOG_FILE="$FROOT/var/log/zeropkg/test_results.log"
mkdir -p "$(dirname $LOG_FILE)"

RED="\e[31m"
GREEN="\e[32m"
YELLOW="\e[33m"
RESET="\e[0m"

echo -e "${YELLOW}=== Iniciando testes completos Zeropkg ===${RESET}" | tee -a $LOG_FILE

all_ok=true
results=()

# Função para validar dependências de binário
check_deps() {
    local bin="$1"
    missing=$(ldd "$bin" 2>/dev/null | grep "not found")
    if [ -n "$missing" ]; then
        echo -e "${RED}[FAIL] Dependências faltando para $bin: $missing${RESET}" | tee -a $LOG_FILE
        return 1
    fi
    return 0
}

# Função de teste genérico de pacote
test_package() {
    local pkg_name="$1"
    local pkg_dir="$2"
    local pkg_ok=true

    echo -e "${YELLOW}Testando pacote: $pkg_name${RESET}" | tee -a $LOG_FILE

    # 1. Testes upstream
    if [ -f "$pkg_dir/Makefile" ]; then
        (cd "$pkg_dir" && make check) &>> $LOG_FILE || pkg_ok=false
    elif [ -f "$pkg_dir/CMakeLists.txt" ]; then
        (cd "$pkg_dir" && ctest --output-on-failure) &>> $LOG_FILE || pkg_ok=false
    elif [ -f "$pkg_dir/Cargo.toml" ]; then
        (cd "$pkg_dir" && cargo test) &>> $LOG_FILE || pkg_ok=false
    elif [ -f "$pkg_dir/setup.py" ]; then
        (cd "$pkg_dir" && python3 setup.py test) &>> $LOG_FILE || pkg_ok=false
    elif [ -f "$pkg_dir/go.mod" ]; then
        (cd "$pkg_dir" && go test ./...) &>> $LOG_FILE || pkg_ok=false
    fi

    # 2. Sanity check do binário
    BIN=$(find "$FROOT/usr/bin" -maxdepth 1 -type f -executable -name "$pkg_name*" | head -n1)
    if [ -n "$BIN" ]; then
        "$BIN" --version &>> $LOG_FILE || pkg_ok=false
        check_deps "$BIN" || pkg_ok=false
    else
        echo -e "${YELLOW}[WARN] Binário de $pkg_name não encontrado${RESET}" | tee -a $LOG_FILE
    fi

    # 3. Verificação de permissões
    if [ -n "$BIN" ]; then
        perms=$(stat -c "%a" "$BIN")
        if [[ $perms -lt 755 ]]; then
            echo -e "${RED}[WARN] Permissões incorretas para $BIN ($perms)${RESET}" | tee -a $LOG_FILE
            pkg_ok=false
        fi
    fi

    # Resultado
    if [ "$pkg_ok" = true ]; then
        echo -e "${GREEN}[OK] Pacote $pkg_name passou nos testes${RESET}" | tee -a $LOG_FILE
        results+=("$pkg_name: OK")
    else
        echo -e "${RED}[FAIL] Pacote $pkg_name falhou nos testes${RESET}" | tee -a $LOG_FILE
        results+=("$pkg_name: FAIL")
        all_ok=false
        notify-send "Zeropkg Test Failed" "Pacote $pkg_name falhou nos testes."
    fi
}

export -f test_package
export -f check_deps
export FROOT LOG_FILE RED GREEN YELLOW RESET

# 4. Executa todos os pacotes em paralelo
find "$FROOT/src/" -mindepth 1 -maxdepth 1 -type d | \
xargs -n1 -P4 -I{} bash -c 'test_package "$(basename {})" "{}"'

# 5. Resumo final
echo -e "${YELLOW}=== Resumo final dos testes ===${RESET}" | tee -a $LOG_FILE
for r in "${results[@]}"; do
    if [[ $r == *OK ]]; then
        echo -e "${GREEN}$r${RESET}" | tee -a $LOG_FILE
    else
        echo -e "${RED}$r${RESET}" | tee -a $LOG_FILE
    fi
done

if [ "$all_ok" = true ]; then
    echo -e "${GREEN}Todos os pacotes passaram nos testes!${RESET}" | tee -a $LOG_FILE
    exit 0
else
    echo -e "${RED}Alguns pacotes falharam. Verifique o log em $LOG_FILE${RESET}" | tee -a $LOG_FILE
    exit 1
fi
