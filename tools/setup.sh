#!/usr/bin/env bash
# Fetch fonts next to render.py (GitHub is reachable from the Claude sandbox).
cd "$(dirname "$0")"
curl -sL -o sg.zip https://github.com/floriankarsten/space-grotesk/releases/download/2.0.0/SpaceGrotesk-2.0.0.zip
unzip -o -q -j sg.zip "SpaceGrotesk-2.0.0/ttf/SpaceGrotesk[wght].ttf" -d . && mv "SpaceGrotesk[wght].ttf" SpaceGrotesk.ttf && rm sg.zip
curl -sL -o JetBrainsMono.ttf "https://raw.githubusercontent.com/JetBrains/JetBrainsMono/master/fonts/variable/JetBrainsMono%5Bwght%5D.ttf"
pip install playwright --break-system-packages -q 2>/dev/null; python3 -m playwright install chromium -q 2>/dev/null
echo "ready"
