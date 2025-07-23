#!/bin/bash
echo "🚀 Mobile Pro Upload Script"
echo "Files to upload to https://github.com/zishas1/cellstore_pro:"
echo ""
find . -type f -not -path './.git/*' -not -name 'upload_to_github.sh' -not -name '*.tar.gz' | head -20
echo ""
echo "Total files: $(find . -type f -not -path './.git/*' -not -name 'upload_to_github.sh' -not -name '*.tar.gz' | wc -l)"
