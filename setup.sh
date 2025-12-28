#!/bin/bash
# SAOS Sovereign CLI Forge - Zachary Dakota Hulse
# No money. No cloud. No compromise.

set -e

BRYER_MODE=false
LOCAL_BUILD=false

for arg in "$@"; do
  case $arg in
    --bryer-mode) BRYER_MODE=true ;;
    --local-build) LOCAL_BUILD=true ;;
    --no-telemetry) echo "[SAOS] Telemetry disabled by design." ;;
  esac
done

echo "[SAOS] 🔥 Initializing Sovereign CLI Forge..."

# --- 1. ROOTLESS DOCKER ---
echo "[SAOS] Installing Rootless Docker..."
curl -fsSL https://get.docker.com/rootless | sh

echo 'export PATH=$HOME/bin:$PATH' >> ~/.bashrc
echo 'export DOCKER_HOST=unix://$XDG_RUNTIME_DIR/docker.sock' >> ~/.bashrc
source ~/.bashrc

# --- 2. BUILD NEOVIM FROM SOURCE ---
if [ "$LOCAL_BUILD" = true ]; then
  echo "[SAOS] Building Neovim from source..."
  git clone --depth 1 https://github.com/neovim/neovim ~/.cache/nvim-src
  cd ~/.cache/nvim-src
  make CMAKE_BUILD_TYPE=RelWithDebInfo
  make install PREFIX=$HOME/.local
  cd -
fi

# --- 3. CONFIGURE NVIM ---
mkdir -p ~/.config/nvim

cat > ~/.config/nvim/init.lua << EOF
vim.opt.number = true
vim.opt.mouse = ""
vim.opt.tabstop = 2
vim.opt.shiftwidth = 2
vim.opt.expandtab = true

local ensure_packer = function()
  local fn = vim.fn
  local install_path = fn.stdpath('data')..'/site/pack/packer/start/packer.nvim'
  if fn.empty(fn.glob(install_path)) > 0 then
    fn.system({'git', 'clone', '--depth', '1', 'https://github.com/wbthomason/packer.nvim', install_path})
    vim.cmd('packadd packer.nvim')
    return true
  end
  return false
end

local packer_bootstrap = ensure_packer()

require('packer').startup(function(use)
  use 'wbthomason/packer.nvim'
  use 'neovim/nvim-lspconfig'
  use 'hrsh7th/nvim-cmp'
  use 'hrsh7th/cmp-nvim-lsp'
  use 'hrsh7th/cmp-buffer'
  use 'L3MON4D3/LuaSnip'
end)

if packer_bootstrap then
  require('packer').sync()
end

-- LSP
local lspconfig = require('lspconfig')
lspconfig.pyright.setup{}
lspconfig.bashls.setup{}
lspconfig.jsonls.setup{}
lspconfig.yamlls.setup{}

-- Completion
local cmp = require('cmp')
cmp.setup({
  snippet = { expand = function(args) require('luasnip').lsp_expand(args.body) end },
  mapping = cmp.mapping.preset.insert(),
  sources = cmp.config.sources({{ name = 'nvim_lsp' }}, {{ name = 'buffer' }})
})

EOF

# --- 4. AGE ENCRYPTION (IF INSTALLED) ---
if command -v age &> /dev/null; then
  echo "[SAOS] age detected. Ready for Sovereign_Shield encryption."
else
  echo "[SAOS] Install age for module encryption: https://github.com/FiloSottile/age"
fi

# --- 5. DOCKERFILE TEMPLATE ---
cat > Dockerfile.saos << 'EOF'
# SAOS Sovereign Module - No telemetry. No cloud.
FROM alpine:latest
RUN apk add --no-cache python3 py3-pip
WORKDIR /app
COPY . .
RUN pip3 install --no-cache-dir -r requirements.txt
USER 1000
CMD ["python3", "main.py"]
EOF

echo "[SAOS] 🔥 Forge complete."
echo "[SAOS] Next: nvim ~/.config/nvim/init.lua && docker build -f Dockerfile.saos -t saos:local ."