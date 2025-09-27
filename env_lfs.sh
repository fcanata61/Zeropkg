#!/bin/bash
# env-lfs.sh - Configura automaticamente o ambiente LFS conforme a fase

# Diretório raiz do LFS
export LFS=/mnt/lfs

# Detecta a fase do LFS
# Se existir o diretório tools, estamos na fase do toolchain temporário
if [ -d "$LFS/tools" ]; then
    LFS_PHASE="toolchain"
else
    LFS_PHASE="final"
fi

# Configuração para a fase do toolchain temporário
if [ "$LFS_PHASE" = "toolchain" ]; then
    export PATH="$LFS/tools/bin:/bin:/usr/bin"
    export LD_LIBRARY_PATH="$LFS/tools/lib"
    export LDFLAGS="-L$LFS/tools/lib"
    export CPPFLAGS="-I$LFS/tools/include"
    export PKG_CONFIG_PATH="$LFS/tools/lib/pkgconfig"
    export MANPATH="$LFS/tools/share/man:$MANPATH"
    export INFOPATH="$LFS/tools/share/info:$INFOPATH"
    export PS1="(LFS-toolchain) \u:\w\$ "
    echo "Ambiente LFS: Toolchain temporário carregado."

# Configuração para a fase final do LFS
else
    export PATH="$LFS/bin:$LFS/sbin:/bin:/usr/bin"
    export LD_LIBRARY_PATH="$LFS/lib:$LFS/usr/lib"
    export LDFLAGS="-L$LFS/lib -L$LFS/usr/lib"
    export CPPFLAGS="-I$LFS/include -I$LFS/usr/include"
    export PKG_CONFIG_PATH="$LFS/lib/pkgconfig:$LFS/usr/lib/pkgconfig"
    export MANPATH="$LFS/usr/share/man:$LFS/usr/share/man/man1:$MANPATH"
    export INFOPATH="$LFS/usr/share/info:$INFOPATH"
    export PS1="(LFS-final) \u:\w\$ "
    echo "Ambiente LFS: Sistema final carregado."
fi

# Otimizações de compilação padrão
export CFLAGS="-O2 -g"
export CXXFLAGS="-O2 -g"
