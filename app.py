from flask import Flask, render_template, request, jsonify
import math
import re

app = Flask(__name__)

# جدول کدینگ منطبق بر ساختار پیوست مقاله FI9 (قابل توسعه بر اساس کل جدول ۵۱۲ حالتی)
FI9_CODEBOOK = {
    1: {"dots": [(0,0), (1,1), (2,2)], "desc": "الگوی نقطه ای شماره ۱ (قطری اصلی)"},
    2: {"dots": [(0,2), (1,1), (2,0)], "desc": "الگوی نقطه ای شماره ۲ (قطری فرعی)"},
    3: {"dots": [(0,1), (1,0), (1,2), (2,1)], "desc": "الگوی نقطه ای شماره ۳ (صلیبی)"},
    4: {"dots": [(0,0), (0,2), (2,0), (2,2)], "desc": "الگوی نقطه ای شماره ۴ (چهارگوشه)"},
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_codes():
    data = request.json
    raw_input = data.get('indices', '')
    
    # تفکیک ایندکس ها با کاما، خط فاصله یا فاصله
    tokens = re.split(r'[,\\-\\s]+', raw_input.strip())
    
    indices = []
    for t in tokens:
        if t.isdigit():
            indices.append(int(t))
            
    combined_dots = []
    details = []
    
    for idx in indices:
        if idx in FI9_CODEBOOK:
            item = FI9_CODEBOOK[idx]
            combined_dots.extend(item["dots"])
            details.append({"index": idx, "dots": item["dots"], "desc": item["desc"]})
        else:
            details.append({"index": idx, "error": "ایندکس در جدول کدینگ یافت نشد"})
            
    # محاسبه حجم بیت و بایت و مقایسه با سیستم باینری سنتی
    total_indices = len(indices)
    bits_fi9 = total_indices * 9 
    bytes_fi9 = bits_fi9 / 8.0
    
    bits_binary = total_indices * 8
    bytes_binary = total_indices * 1.0

    return jsonify({
        "success": True,
        "details": details,
        "combined_dots": combined_dots,
        "metrics": {
            "fi9_bits": bits_fi9,
            "fi9_bytes": round(bytes_fi9, 2),
            "binary_bits": bits_binary,
            "binary_bytes": bytes_binary
        }
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
