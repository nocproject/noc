#!/bin/bash
set -e

echo "🚀 Starting NOC DevContainer..."

install_node_deps() {
    if [ -f "ui/package.json" ]; then
        echo "📦 Installing Node.js dependencies..."
        
        cd ui
        echo "📥 Installing packages with pnpm..."
        pnpm install
        cd .. 
        echo "✅ Node.js dependencies installed successfully"
    else
        echo "⚠️  No ui/package.json found, skipping Node.js dependencies installation"
    fi
}

install_node_deps

if [ $# -gt 0 ]; then
    exec "$@"
else
    exec /bin/bash
fi