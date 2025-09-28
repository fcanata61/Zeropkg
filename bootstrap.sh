## colocar em /etc/profile.d/bootstrap.sh
# =============================
# LFS BOOTSTRAP ENVIRONMENT
# =============================

# Caminho raiz do LFS
export LFS=/mnt/lfs

# PATH: prioriza o toolchain temporário
export PATH="$LFS/tools/bin:/bin:/usr/bin"

# Bibliotecas e includes
export LD_LIBRARY_PATH="$LFS/tools/lib"
export LDFLAGS="-L$LFS/tools/lib"
export CPPFLAGS="-I$LFS/tools/include"

# pkg-config
export PKG_CONFIG_PATH="$LFS/tools/lib/pkgconfig"

# Documentação
export MANPATH="$LFS/tools/share/man:$MANPATH"
export INFOPATH="$LFS/tools/share/info:$INFOPATH"

# Locale: fixo pra evitar bugs em configure/make
export LC_ALL=POSIX
export LANG=C

# Evita pegar configs do host
export CONFIG_SITE=$LFS/usr/share/config.site

# Paralelismo de compilação
if command -v nproc >/dev/null 2>&1; then
    export MAKEFLAGS="-j$(nproc)"
else
    export MAKEFLAGS="-j2"
fi

# Flags padrão
export CFLAGS="-O2 -g"
export CXXFLAGS="-O2 -g"

# Prompt visível
export PS1="(LFS-bootstrap) \u:\w\$ "

echo ">> Ambiente LFS bootstrap carregado."
