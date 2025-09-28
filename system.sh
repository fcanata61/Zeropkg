## Colocar em /etc/profile.d/system.sh
# =============================
# LFS SYSTEM ENVIRONMENT
# =============================

# Caminho raiz do LFS
export LFS=/mnt/lfs

# PATH: agora usa o sistema final
export PATH="/bin:/usr/bin:/sbin:/usr/sbin:/usr/local/bin:/usr/local/sbin"

# Bibliotecas
export LD_LIBRARY_PATH="/lib:/usr/lib:/usr/local/lib"
export LDFLAGS="-L/lib -L/usr/lib -L/usr/local/lib"
export CPPFLAGS="-I/include -I/usr/include -I/usr/local/include"

# pkg-config
export PKG_CONFIG_PATH="/usr/lib/pkgconfig:/usr/local/lib/pkgconfig"

# Documentação
export MANPATH="/usr/share/man:/usr/local/share/man:$MANPATH"
export INFOPATH="/usr/share/info:/usr/local/share/info:$INFOPATH"

# Locale
export LANG=C.UTF-8
export LC_ALL=C.UTF-8

# Paralelismo de compilação
if command -v nproc >/dev/null 2>&1; then
    export MAKEFLAGS="-j$(nproc)"
else
    export MAKEFLAGS="-j2"
fi

# Flags padrão
export CFLAGS="-O2 -pipe"
export CXXFLAGS="-O2 -pipe"

# Prompt visível
export PS1="(LFS-system) \u:\w\$ "

echo ">> Ambiente LFS system carregado."
