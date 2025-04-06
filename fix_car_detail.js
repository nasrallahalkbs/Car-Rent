// Try to fix the car detail JS
const fs = require('fs');
const path = require('path');

// Read the file
const filePath = path.join(__dirname, 'templates', 'car_detail_django.html');
let content = fs.readFileSync(filePath, 'utf8');

// Fix the JS by replacing the problematic part
let fixed = content.replace(
  /unavailableDatesContainer\.innerHTML = "<p class="text-danger mb-0 text-center py-4"><i class="fas fa-exclamation-circle ms-2"><\/i>حدث خطأ أثناء تحميل التواريخ المحجوزة<\/p>";/g,
  'unavailableDatesContainer.innerHTML = \'<p class="text-danger mb-0 text-center py-4"><i class="fas fa-exclamation-circle ms-2"></i>حدث خطأ أثناء تحميل التواريخ المحجوزة</p>\';'
);

// Write the file back
fs.writeFileSync(filePath, fixed, 'utf8');
console.log('File fixed successfully');
