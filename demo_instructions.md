# Script Scanner Demo Instructions

## 🚀 How to Test the Enhanced Script Scanner

### Prerequisites
1. Run the browser application: `py main.py`
2. Navigate to the `test_scripts.html` file (or any webpage with JavaScript)

### Testing Basic Script Scanner

1. **Right-click** anywhere on the webpage
2. Select **"📜 Scan Scripts (Inline & External)"**
3. Explore the results:
   - **External Scripts Tab**: Shows all external JavaScript files
   - **Inline Scripts Tab**: Shows all inline JavaScript code
   - **Detailed Report Tab**: Comprehensive analysis summary

### Testing View Full Content Feature

#### For External Scripts:
1. In the External Scripts tab, **double-click** any script row
2. OR click the **"👁️ View Source"** button
3. Watch as the script content is fetched and displayed
4. Features available:
   - **Save Script**: Export the external script as a .js file
   - **Stop Loading**: Cancel slow downloads
   - **Metadata Display**: See script attributes and security info

#### For Inline Scripts:
1. In the Inline Scripts tab, **double-click** any script row
2. OR click the **"👁️ View Full Script"** button
3. Features available:
   - **Line Numbers**: Toggle on/off for better readability
   - **Word Wrap**: Toggle for long lines
   - **Copy to Clipboard**: Copy the entire script
   - **Save Script**: Export with metadata headers
   - **Security Analysis**: See detected vulnerabilities

### Testing Advanced Script Analysis

1. **Right-click** anywhere on the webpage
2. Select **"🔍 Advanced Script Analysis"**
3. Explore the comprehensive analysis:

#### Security Tab:
- **CSP Status**: Content Security Policy detection
- **SRI Usage**: Subresource Integrity statistics
- **Nonce Usage**: CSP nonce implementation
- **Vulnerability Tree**: Color-coded security issues by severity

#### Performance Tab:
- **Loading Analysis**: Blocking vs Async vs Defer scripts
- **Performance Impact**: How scripts affect page load
- **Recommendations**: Optimization suggestions

#### Dependencies Tab:
- **Library Detection**: Automatically detected frameworks (jQuery, React, etc.)
- **API Usage**: What browser APIs are being used
- **DOM Manipulation**: How scripts interact with the page

### Test Cases in test_scripts.html

The test file includes:

#### External Scripts:
- ✅ **jQuery with SRI**: Secure external script with integrity check
- ✅ **Bootstrap with SRI**: Another secure script
- ⚠️ **Axios without SRI**: Security risk - no integrity check
- 🔄 **Deferred Script**: Performance optimized loading
- ⚡ **Async Script**: Non-blocking Google Analytics
- 🔐 **Nonce Script**: CSP compliant with nonce attribute

#### Inline Scripts:
- 🟢 **Safe Script**: Basic DOM manipulation
- 🟡 **Medium Risk**: Uses innerHTML and localStorage
- 🔴 **High Risk**: Contains eval(), document.write(), setTimeout with strings
- 📊 **API Heavy**: Uses fetch, geolocation, WebSocket, IndexedDB
- 🎯 **Library Detection**: Contains patterns for React, Vue, Angular detection

### Expected Results

#### Security Analysis Should Detect:
- **High Severity**: eval() usage, Function constructor, JavaScript protocols
- **Medium Severity**: document.write(), innerHTML manipulation, setTimeout with strings
- **Low Severity**: window.open(), location manipulation

#### Performance Analysis Should Show:
- Script loading distribution (blocking/async/defer)
- Performance recommendations
- Loading impact assessment

#### Dependencies Should Detect:
- jQuery, Bootstrap, Axios, D3.js, Moment.js
- API usage patterns (fetch, localStorage, geolocation)
- DOM manipulation methods

### Export Features

Both scanners support exporting:
- **Text Reports**: Comprehensive analysis in readable format
- **Script Files**: Individual scripts with metadata
- **Timestamps**: All exports include date/time information

### Tips for Testing

1. **Try Different Websites**: Test on various sites to see different script patterns
2. **Check Security**: Look for sites with/without CSP headers
3. **Performance Comparison**: Compare sites with different script loading strategies
4. **Library Detection**: Visit sites using popular frameworks

### Troubleshooting

- **Slow External Script Loading**: Use the "Stop Loading" button
- **Large Inline Scripts**: Use line numbers and word wrap for better viewing
- **Export Issues**: Check file permissions in the selected directory
- **No Scripts Found**: Ensure JavaScript is enabled and the page has loaded completely

## 🎯 Key Features Demonstrated

✅ **Comprehensive Script Analysis**
✅ **Security Vulnerability Detection**  
✅ **Performance Impact Assessment**
✅ **Library/Framework Detection**
✅ **Full Content Viewing**
✅ **Export Capabilities**
✅ **Real-time Analysis**
✅ **User-friendly Interface**

Happy testing! 🚀