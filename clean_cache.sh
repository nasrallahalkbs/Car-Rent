#!/bin/bash

# سكريبت سريع لتنظيف ملفات الكاش
echo "بدء تنظيف ملفات الكاش..."

# حذف جميع مجلدات __pycache__
find . -type d -name "__pycache__" -exec rm -rf {} +
echo "✓ تم حذف مجلدات __pycache__"

# حذف جميع ملفات .pyc
find . -type f -name "*.pyc" -delete
echo "✓ تم حذف ملفات .pyc"

# حذف ملفات الكاش الأخرى
find . -type d -name ".webassets-cache" -exec rm -rf {} +
find ./static -type d -name "CACHE" -exec rm -rf {} +
find ./staticfiles -type d -name "CACHE" -exec rm -rf {} +
echo "✓ تم حذف مجلدات الكاش الأخرى"

# حذف ملفات السجلات
find . -type f -name "*.log" -delete
echo "✓ تم حذف ملفات السجلات"

echo "تم الانتهاء من التنظيف!"