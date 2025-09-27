#!/bin/bash
# env-lfs.sh - Ambiente automático e avançado para o LFS

# Diretório raiz do LFS
export LFS=/mnt/lfs

# Detecta número de núcleos para paralelizar builds
if command -v nproc >/dev/null 2>&1; then
    export MAKEFLAGS="-j$(nproc)"
else
    export MAKEFLAGS="-j2"
fi

# Localização e idioma
export LC_ALL=POSIX
export LANG=C

# Evita pegar libs do host em configure
export CONFIG_SITE=$LFS/usr/share/config.site

# Detecta fase
if [ -d "$LFS/tools" ]; then
    LFS_PHASE="toolchain"
else
    LFS_PHASE="final"
fi

# ===============================
# FASE 1: TOOLCHAIN TEMPORÁRIO
# ===============================
if [ "$LFS_PHASE" = "toolchain" ]; then
    export PATH="$LFS/tools/bin:/bin:/usr/bin"
    export LD_LIBRARY_PATH="$LFS/tools/lib"
    export LDFLAGS="-L$LFS/tools/lib"
    export CPPFLAGS="-I$LFS/tools/include"
    export PKG_CONFIG_PATH="$LFS/tools/lib/pkgconfig"
    export MANPATH="$LFS/tools/share/man:$MANPATH"
    export INFOPATH="$LFS/tools/share/info:$INFOPATH"
    export PS1="(LFS-toolchain) \u:\w\$ "
    echo ">> Ambiente LFS: Toolchain temporário carregado."

# ===============================
# FASE 2: SISTEMA FINAL
# ===============================
else
    export PATH="$LFS/bin:$LFS/sbin:$LFS/usr/bin:$LFS/usr/sbin:/bin:/usr/bin"
    export LD_LIBRARY_PATH="$LFS/lib:$LFS/usr/lib"
    export LDFLAGS="-L$LFS/lib -L$LFS/usr/lib"
    export CPPFLAGS="-I$LFS/include -I$LFS/usr/include"
    export PKG_CONFIG_PATH="$LFS/lib/pkgconfig:$LFS/usr/lib/pkgconfig"
    export MANPATH="$LFS/usr/share/man:$MANPATH"
    export INFOPATH="$LFS/usr/share/info:$INFOPATH"
    export PS1="(LFS-final) \u:\w\$ "
    echo ">> Ambiente LFS: Sistema final carregado."
fi

# ===============================
# AJUSTES ADICIONAIS
# ===============================

# DESTDIR pode ser usado para instalar pacotes em um diretório alternativo
export DESTDIR=$LFS/tmp/pkg-install

# Flags padrão de compilação
export CFLAGS="-O2 -g"
export CXXFLAGS="-O2 -g"
