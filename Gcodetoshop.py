#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 12:34:43 2024

@author: kommuchandravenkatasaibhagavan
"""

1.	from flask import Flask, request, render_template, send_file
2.	import os
3.	import re
4.	
5.	app = Flask(__name__)
6.	
7.	@app.route('/')
8.	def index():
9.	    return render_template('index.html')
10.	
11.	@app.route('/upload', methods=['POST'])
12.	def upload_file():
13.	    if 'file' not in request.files:
14.	        return 'No file part'
15.	    file = request.files['file']
16.	    if file.filename == '':
17.	        return 'No selected file'
18.	    if file:
19.	        filepath = os.path.join('uploads', file.filename)
20.	        file.save(filepath)
21.	        converted_filepath = convert_gcode(filepath)
22.	        return send_file(converted_filepath, as_attachment=True)
23.	
24.	def convert_gcode(filepath):
25.	    with open(filepath, 'r') as file:
26.	        lines = file.readlines()
27.	    
28.	    converted_lines = []
29.	    layer_lines = []
30.	    layer_index = 1
31.	
32.	    for line in lines:
33.	        if 'layer' in line.lower():
34.	            if layer_lines:
35.	                converted_lines.extend(convert_layer(layer_lines, layer_index))
36.	                layer_lines = []
37.	                layer_index += 1
38.	        layer_lines.append(line)
39.	
40.	    if layer_lines:
41.	        converted_lines.extend(convert_layer(layer_lines, layer_index))
42.	
43.	    converted_filepath = filepath.replace('.gcode', '_converted.txt')
44.	    with open(converted_filepath, 'w') as file:
45.	        file.writelines(converted_lines)
46.	
47.	    return converted_filepath
48.	
49.	def convert_layer(lines, layer_index):
50.	    converted_lines = [f"'Layer {layer_index}'\n"]
51.	    converted_lines.append("\t\tJS .15,1\n")
52.	    converted_lines.append("\t\tJZ 3\n")
53.	    converted_lines.append("\t\tZ2\n")
54.	    converted_lines.append("\t\tJ2 -.6\n")
55.	    
56.	    z_height = 0.035 * layer_index
57.	    converted_lines.append(f"\t\tJZ {z_height:.4f}\n")
58.	    converted_lines.append("\t\tSO,5,1\n")
59.	    converted_lines.append("\t\tJS .05\n")
60.	    
61.	    for line in lines:
62.	        converted_line = convert_line(line)
63.	        if converted_line:
64.	            converted_lines.append(f"\t\t{converted_line}\n")
65.	    
66.	    converted_lines.append("\t\tSO,5,0\n")
67.	    converted_lines.append("\t\tJZ 5\n")
68.	    converted_lines.append("\tPAUSE 20\n")
69.	    converted_lines.append("'''''''''''''''''''''''''''''''''''''''''''''\n")
70.	    
71.	    return converted_lines
72.	
73.	def convert_line(line):
74.	    # Convert coordinates from mm to inches
75.	    def scale(match):
76.	        return f"{float(match.group(1)) * 0.0393701:.4f}"
77.	    
78.	    line = re.sub(r'X([-+]?\d*\.\d+|\d+)', lambda m: 'J2 X' + scale(m), line)
79.	    line = re.sub(r'Y([-+]?\d*\.\d+|\d+)', lambda m: 'Y' + scale(m), line)
80.	    line = re.sub(r'Z([-+]?\d*\.\d+|\d+)', lambda m: 'Z' + scale(m), line)
81.	    
82.	    if 'G1' in line or 'G0' in line:
83.	        line = line.replace('G1', '').replace('G0', '')
84.	    return line.strip()
85.	
86.	if __name__ == '__main__':
87.	    os.makedirs('uploads', exist_ok=True)
88.	    app.run(debug=True)
