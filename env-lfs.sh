#!/bin/bash
# env-lfs.sh - Configura o ambiente para compilar o LFS

# Diretório raiz do LFS
export LFS=/mnt/lfs

# PATH: prioriza o toolchain temporário do LFS
export PATH="$LFS/tools/bin:/bin:/usr/bin"

# Bibliotecas compartilhadas
export LD_LIBRARY_PATH="$LFS/tools/lib"
export LDFLAGS="-L$LFS/tools/lib"
export CPPFLAGS="-I$LFS/tools/include"

# pkg-config
export PKG_CONFIG_PATH="$LFS/tools/lib/pkgconfig"

# Manuais e info
export MANPATH="$LFS/tools/share/man:$MANPATH"
export INFOPATH="$LFS/tools/share/info:$INFOPATH"

# Prompt customizado para identificar o shell do LFS
export PS1="(LFS) \u:\w\$ "

# Opcional: otimizações de compilação
export CFLAGS="-O2 -g"
export CXXFLAGS="-O2 -g"

# Função de confirmação rápida
echo "Ambiente LFS carregado. PATH, LD_LIBRARY_PATH e variáveis essenciais configuradas."
