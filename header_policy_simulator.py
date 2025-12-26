"""
Header Policy Simulator for security-focused browser testing.
Simulates CSP, HSTS, CORS policies and detects site breakage.
"""

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebEngineCore import *
import json
import re
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Set, Optional


class BreakLevel(Enum):
    """Site breakage severity levels"""
    SAFE = "safe"
    PARTIAL_BREAK = "partial"
    CRITICAL_BREAK = "critical"


class PolicyType(Enum):
    """Security policy types"""
    CSP = "csp"
    HSTS = "hsts"
    CORS = "cors"


@dataclass
class PolicyViolation:
    """Represents a policy violation"""
    policy_type: PolicyType
    violation_type: str
    message: str
    url: str
    timestamp: datetime
    severity: str = "medium"


@dataclass
class PolicyConfig:
    """Configuration for a security policy"""
    enabled: bool = False
    mode: str = "basic"  # basic, strict, report-only
    custom_rules: List[str] = None
    
    def __post_init__(self):
        if self.custom_rules is None:
            self.custom_rules = []


class SecurityPolicyEngine:
    """Core engine for security policy simulation"""
    
    def __init__(self):
        self.policies = {
            PolicyType.CSP: PolicyConfig(),
            PolicyType.HSTS: PolicyConfig(),
            PolicyType.CORS: PolicyConfig()
        }
        self.violations: List[PolicyViolation] = []
        self.monitored_requests: Set[str] = set()
        self.blocked_requests: Set[str] = set()
        
        # Predefined policy templates
        self.csp_templates = {
            "basic": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';",
            "strict": "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; font-src 'self'; object-src 'none'; media-src 'self'; frame-src 'none';",
            "report-only": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; report-uri /csp-report"
        }
        
        self.hsts_templates = {
            "basic": "max-age=31536000",
            "strict": "max-age=31536000; includeSubDomains; preload"
        }
    
    def enable_policy(self, policy_type: PolicyType, mode: str = "basic"):
        """Enable a security policy"""
        self.policies[policy_type].enabled = True
        self.policies[policy_type].mode = mode
    
    def disable_policy(self, policy_type: PolicyType):
        """Disable a security policy"""
        self.policies[policy_type].enabled = False
    
    def get_csp_header(self) -> Optional[str]:
        """Generate CSP header based on current configuration"""
        if not self.policies[PolicyType.CSP].enabled:
            return None
        
        mode = self.policies[PolicyType.CSP].mode
        if mode in self.csp_templates:
            return self.csp_templates[mode]
        return self.csp_templates["basic"]
    
    def get_hsts_header(self) -> Optional[str]:
        """Generate HSTS header based on current configuration"""
        if not self.policies[PolicyType.HSTS].enabled:
            return None
        
        mode = self.policies[PolicyType.HSTS].mode
        if mode in self.hsts_templates:
            return self.hsts_templates[mode]
        return self.hsts_templates["basic"]
    
    def simulate_csp_violation(self, url: str, directive: str, blocked_uri: str):
        """Simulate a CSP violation"""
        violation = PolicyViolation(
            policy_type=PolicyType.CSP,
            violation_type="csp-violation",
            message=f"CSP violation: {directive} blocked {blocked_uri}",
            url=url,
            timestamp=datetime.now(),
            severity="high" if "script-src" in directive else "medium"
        )
        self.violations.append(violation)
        self.blocked_requests.add(blocked_uri)
    
    def simulate_cors_violation(self, url: str, origin: str):
        """Simulate a CORS violation"""
        violation = PolicyViolation(
            policy_type=PolicyType.CORS,
            violation_type="cors-blocked",
            message=f"CORS blocked request from {origin}",
            url=url,
            timestamp=datetime.now(),
            severity="medium"
        )
        self.violations.append(violation)
        self.blocked_requests.add(url)
    
    def simulate_mixed_content_violation(self, url: str, resource_url: str):
        """Simulate mixed content violation"""
        violation = PolicyViolation(
            policy_type=PolicyType.HSTS,
            violation_type="mixed-content",
            message=f"Mixed content blocked: {resource_url}",
            url=url,
            timestamp=datetime.now(),
            severity="high"
        )
        self.violations.append(violation)
        self.blocked_requests.add(resource_url)
    
    def analyze_breakage_level(self) -> BreakLevel:
        """Analyze current breakage level based on violations"""
        if not self.violations:
            return BreakLevel.SAFE
        
        critical_violations = sum(1 for v in self.violations if v.severity == "high")
        total_violations = len(self.violations)
        
        if critical_violations >= 3 or total_violations >= 10:
            return BreakLevel.CRITICAL_BREAK
        elif critical_violations >= 1 or total_violations >= 3:
            return BreakLevel.PARTIAL_BREAK
        else:
            return BreakLevel.SAFE
    
    def get_violation_summary(self) -> Dict[str, int]:
        """Get summary of violations by type"""
        summary = {}
        for violation in self.violations:
            key = f"{violation.policy_type.value}_{violation.violation_type}"
            summary[key] = summary.get(key, 0) + 1
        return summary
    
    def reset_violations(self):
        """Reset all violations and blocked requests"""
        self.violations.clear()
        self.blocked_requests.clear()
        self.monitored_requests.clear()


class PolicyInterceptor(QWebEngineUrlRequestInterceptor):
    """Intercepts web requests to simulate policy enforcement"""
    
    def __init__(self, policy_engine: SecurityPolicyEngine):
        super().__init__()
        self.policy_engine = policy_engine
        self.page_url = ""
    
    def set_page_url(self, url: str):
        """Set the current page URL for context"""
        self.page_url = url
    
    def interceptRequest(self, info):
        """Intercept and analyze requests"""
        url = info.requestUrl().toString()
        method = info.requestMethod()
        
        # Track all requests
        self.policy_engine.monitored_requests.add(url)
        
        # Simulate HSTS enforcement
        if self.policy_engine.policies[PolicyType.HSTS].enabled:
            self._check_hsts_violations(info, url)
        
        # Simulate CORS enforcement
        if self.policy_engine.policies[PolicyType.CORS].enabled:
            self._check_cors_violations(info, url)
        
        # Simulate CSP enforcement
        if self.policy_engine.policies[PolicyType.CSP].enabled:
            self._check_csp_violations(info, url)
    
    def _check_hsts_violations(self, info, url: str):
        """Check for HSTS violations"""
        if url.startswith("http://") and not url.startswith("https://"):
            # Mixed content detection
            if self.page_url.startswith("https://"):
                self.policy_engine.simulate_mixed_content_violation(self.page_url, url)
                if self.policy_engine.policies[PolicyType.HSTS].mode == "strict":
                    info.block(True)  # Block the request
    
    def _check_cors_violations(self, info, url: str):
        """Check for CORS violations"""
        request_url = QUrl(url)
        page_url = QUrl(self.page_url)
        
        # Simulate strict CORS policy
        if (request_url.host() != page_url.host() and 
            self.policy_engine.policies[PolicyType.CORS].mode == "strict"):
            
            # Allow common CDNs and safe resources
            allowed_hosts = ["fonts.googleapis.com", "cdnjs.cloudflare.com", "ajax.googleapis.com"]
            if not any(host in request_url.host() for host in allowed_hosts):
                self.policy_engine.simulate_cors_violation(self.page_url, url)
                if self.policy_engine.policies[PolicyType.CORS].mode == "strict":
                    info.block(True)
    
    def _check_csp_violations(self, info, url: str):
        """Check for CSP violations"""
        resource_type = info.resourceType()
        
        # Simulate CSP script-src violations
        if resource_type == QWebEngineUrlRequestInfo.ResourceTypeScript:
            if self._violates_script_src(url):
                self.policy_engine.simulate_csp_violation(
                    self.page_url, "script-src", url
                )
                if self.policy_engine.policies[PolicyType.CSP].mode == "strict":
                    info.block(True)
        
        # Simulate CSP style-src violations
        elif resource_type == QWebEngineUrlRequestInfo.ResourceTypeStylesheet:
            if self._violates_style_src(url):
                self.policy_engine.simulate_csp_violation(
                    self.page_url, "style-src", url
                )
                if self.policy_engine.policies[PolicyType.CSP].mode == "strict":
                    info.block(True)
    
    def _violates_script_src(self, url: str) -> bool:
        """Check if script URL violates CSP script-src"""
        csp_mode = self.policy_engine.policies[PolicyType.CSP].mode
        
        if csp_mode == "strict":
            # Strict mode: only allow same-origin scripts
            page_host = QUrl(self.page_url).host()
            script_host = QUrl(url).host()
            return page_host != script_host
        
        return False
    
    def _violates_style_src(self, url: str) -> bool:
        """Check if style URL violates CSP style-src"""
        csp_mode = self.policy_engine.policies[PolicyType.CSP].mode
        
        if csp_mode == "strict":
            # Strict mode: only allow same-origin styles
            page_host = QUrl(self.page_url).host()
            style_host = QUrl(url).host()
            return page_host != style_host
        
        return False


class HeaderPolicySimulatorDialog(QDialog):
    """Main dialog for Header Policy Simulator"""
    
    def __init__(self, web_view: QWebEngineView, parent=None):
        super().__init__(parent)
        self.web_view = web_view
        self.policy_engine = SecurityPolicyEngine()
        self.interceptor = PolicyInterceptor(self.policy_engine)
        
        # Install interceptor
        profile = self.web_view.page().profile()
        profile.setUrlRequestInterceptor(self.interceptor)
        
        self.setWindowTitle("🛡️ Header Policy Simulator")
        self.setMinimumSize(600, 700)
        self.resize(700, 800)
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(1000)  # Update every second
        
        self.setup_ui()
        self.update_current_url()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("🛡️ Header Policy Simulator")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2196F3; padding: 10px;")
        layout.addWidget(header_label)
        
        # Current URL display
        url_group = QGroupBox("🌐 Current Page")
        url_layout = QVBoxLayout(url_group)
        
        self.url_label = QLabel("No page loaded")
        self.url_label.setStyleSheet("font-family: monospace; padding: 5px; background-color: #f5f5f5; border-radius: 3px;")
        self.url_label.setWordWrap(True)
        url_layout.addWidget(self.url_label)
        
        layout.addWidget(url_group)
        
        # Policy Controls
        policies_group = QGroupBox("🔧 Security Policies")
        policies_layout = QVBoxLayout(policies_group)
        
        # CSP Controls
        csp_frame = self.create_policy_frame("Content Security Policy (CSP)", PolicyType.CSP, [
            ("Basic", "basic", "Allow inline scripts/styles"),
            ("Strict", "strict", "Block all external resources"),
            ("Report-Only", "report-only", "Monitor violations only")
        ])
        policies_layout.addWidget(csp_frame)
        
        # HSTS Controls
        hsts_frame = self.create_policy_frame("HTTP Strict Transport Security (HSTS)", PolicyType.HSTS, [
            ("Basic", "basic", "Force HTTPS for 1 year"),
            ("Strict", "strict", "Force HTTPS + subdomains + preload")
        ])
        policies_layout.addWidget(hsts_frame)
        
        # CORS Controls
        cors_frame = self.create_policy_frame("Cross-Origin Resource Sharing (CORS)", PolicyType.CORS, [
            ("Basic", "basic", "Allow common CDNs"),
            ("Strict", "strict", "Block all cross-origin requests")
        ])
        policies_layout.addWidget(cors_frame)
        
        layout.addWidget(policies_group)
        
        # Status Panel
        status_group = QGroupBox("📊 Security Status")
        status_layout = QVBoxLayout(status_group)
        
        # Break level indicator
        self.break_level_label = QLabel("🟢 SAFE - No policy violations detected")
        self.break_level_label.setStyleSheet("font-weight: bold; padding: 8px; border-radius: 4px; background-color: #d4edda; color: #155724;")
        status_layout.addWidget(self.break_level_label)
        
        # Violation counts
        self.violation_stats = QLabel("Violations: 0 CSP, 0 CORS, 0 Mixed Content")
        self.violation_stats.setStyleSheet("font-family: monospace; padding: 5px;")
        status_layout.addWidget(self.violation_stats)
        
        # Active policies
        self.active_policies = QLabel("Active Policies: None")
        self.active_policies.setStyleSheet("font-family: monospace; padding: 5px;")
        status_layout.addWidget(self.active_policies)
        
        layout.addWidget(status_group)
        
        # Violations Log
        log_group = QGroupBox("📋 Violations Log")
        log_layout = QVBoxLayout(log_group)
        
        self.violations_list = QTextEdit()
        self.violations_list.setMaximumHeight(150)
        self.violations_list.setReadOnly(True)
        self.violations_list.setFont(QFont("Consolas", 9))
        self.violations_list.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
        """)
        log_layout.addWidget(self.violations_list)
        
        layout.addWidget(log_group)
        
        # Control Buttons
        button_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("🔄 Refresh Page")
        self.refresh_btn.clicked.connect(self.refresh_page)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        button_layout.addWidget(self.refresh_btn)
        
        self.reset_btn = QPushButton("🔄 Reset Policies")
        self.reset_btn.clicked.connect(self.reset_policies)
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: #212529;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
        """)
        button_layout.addWidget(self.reset_btn)
        
        self.export_btn = QPushButton("💾 Export Report")
        self.export_btn.clicked.connect(self.export_report)
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        button_layout.addWidget(self.export_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("❌ Close")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def create_policy_frame(self, title: str, policy_type: PolicyType, modes: List[tuple]) -> QGroupBox:
        """Create a policy control frame"""
        frame = QGroupBox(title)
        layout = QVBoxLayout(frame)
        
        # Enable/Disable checkbox
        enable_cb = QCheckBox(f"Enable {title}")
        enable_cb.stateChanged.connect(lambda state, pt=policy_type: self.toggle_policy(pt, state == Qt.Checked))
        layout.addWidget(enable_cb)
        
        # Store reference to checkbox
        setattr(self, f"{policy_type.value}_enable_cb", enable_cb)
        
        # Mode selection
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Mode:"))
        
        mode_group = QButtonGroup(self)
        for i, (name, value, description) in enumerate(modes):
            radio = QRadioButton(name)
            radio.setToolTip(description)
            if i == 0:  # Select first option by default
                radio.setChecked(True)
            radio.toggled.connect(lambda checked, pt=policy_type, val=value: 
                                self.set_policy_mode(pt, val) if checked else None)
            mode_group.addButton(radio)
            mode_layout.addWidget(radio)
        
        layout.addLayout(mode_layout)
        
        return frame
    
    def toggle_policy(self, policy_type: PolicyType, enabled: bool):
        """Toggle a security policy"""
        if enabled:
            # Get current mode from radio buttons
            mode = "basic"  # Default mode
            self.policy_engine.enable_policy(policy_type, mode)
        else:
            self.policy_engine.disable_policy(policy_type)
        
        self.update_status()
    
    def set_policy_mode(self, policy_type: PolicyType, mode: str):
        """Set policy mode"""
        if self.policy_engine.policies[policy_type].enabled:
            self.policy_engine.policies[policy_type].mode = mode
            self.update_status()
    
    def update_current_url(self):
        """Update current URL display"""
        if self.web_view and self.web_view.url().isValid():
            url = self.web_view.url().toString()
            self.url_label.setText(url)
            self.interceptor.set_page_url(url)
        else:
            self.url_label.setText("No page loaded")
    
    def update_status(self):
        """Update status panel"""
        # Update URL
        self.update_current_url()
        
        # Update break level
        break_level = self.policy_engine.analyze_breakage_level()
        
        if break_level == BreakLevel.SAFE:
            self.break_level_label.setText("🟢 SAFE - No critical policy violations")
            self.break_level_label.setStyleSheet("font-weight: bold; padding: 8px; border-radius: 4px; background-color: #d4edda; color: #155724;")
        elif break_level == BreakLevel.PARTIAL_BREAK:
            self.break_level_label.setText("🟡 PARTIAL BREAK - Some functionality may be affected")
            self.break_level_label.setStyleSheet("font-weight: bold; padding: 8px; border-radius: 4px; background-color: #fff3cd; color: #856404;")
        else:  # CRITICAL_BREAK
            self.break_level_label.setText("🔴 CRITICAL BREAK - Site functionality severely impacted")
            self.break_level_label.setStyleSheet("font-weight: bold; padding: 8px; border-radius: 4px; background-color: #f8d7da; color: #721c24;")
        
        # Update violation stats
        summary = self.policy_engine.get_violation_summary()
        csp_count = sum(v for k, v in summary.items() if k.startswith("csp"))
        cors_count = sum(v for k, v in summary.items() if k.startswith("cors"))
        hsts_count = sum(v for k, v in summary.items() if k.startswith("hsts"))
        
        self.violation_stats.setText(f"Violations: {csp_count} CSP, {cors_count} CORS, {hsts_count} Mixed Content")
        
        # Update active policies
        active = []
        for policy_type, config in self.policy_engine.policies.items():
            if config.enabled:
                active.append(f"{policy_type.value.upper()}({config.mode})")
        
        if active:
            self.active_policies.setText(f"Active Policies: {', '.join(active)}")
        else:
            self.active_policies.setText("Active Policies: None")
        
        # Update violations log
        self.update_violations_log()
    
    def update_violations_log(self):
        """Update violations log display"""
        if not self.policy_engine.violations:
            return
        
        # Show only recent violations (last 10)
        recent_violations = self.policy_engine.violations[-10:]
        
        log_text = ""
        for violation in recent_violations:
            timestamp = violation.timestamp.strftime("%H:%M:%S")
            severity_icon = "🔴" if violation.severity == "high" else "🟡"
            log_text += f"{timestamp} {severity_icon} {violation.message}\n"
        
        self.violations_list.setPlainText(log_text)
        
        # Auto-scroll to bottom
        cursor = self.violations_list.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.violations_list.setTextCursor(cursor)
    
    def refresh_page(self):
        """Refresh the current page"""
        if self.web_view:
            self.policy_engine.reset_violations()
            self.violations_list.clear()
            self.web_view.reload()
    
    def reset_policies(self):
        """Reset all policies to default"""
        # Disable all policies
        for policy_type in PolicyType:
            self.policy_engine.disable_policy(policy_type)
        
        # Reset UI checkboxes
        for policy_type in PolicyType:
            checkbox = getattr(self, f"{policy_type.value}_enable_cb", None)
            if checkbox:
                checkbox.setChecked(False)
        
        # Reset violations
        self.policy_engine.reset_violations()
        self.violations_list.clear()
        
        self.update_status()
    
    def export_report(self):
        """Export security report"""
        if not self.policy_engine.violations:
            QMessageBox.information(self, "No Data", "No violations to export.")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Security Report",
            f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("Header Policy Simulator Report\n")
                    f.write("=" * 40 + "\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"URL: {self.url_label.text()}\n\n")
                    
                    # Active policies
                    f.write("Active Policies:\n")
                    for policy_type, config in self.policy_engine.policies.items():
                        if config.enabled:
                            f.write(f"  - {policy_type.value.upper()}: {config.mode}\n")
                    f.write("\n")
                    
                    # Break level
                    break_level = self.policy_engine.analyze_breakage_level()
                    f.write(f"Break Level: {break_level.value.upper()}\n\n")
                    
                    # Violations
                    f.write("Violations:\n")
                    for violation in self.policy_engine.violations:
                        f.write(f"  {violation.timestamp.strftime('%H:%M:%S')} [{violation.severity.upper()}] {violation.message}\n")
                
                QMessageBox.information(self, "Export Successful", f"Report exported to:\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Failed to export report:\n{str(e)}")
    
    def closeEvent(self, event):
        """Handle dialog close"""
        # Remove interceptor
        if self.web_view:
            profile = self.web_view.page().profile()
            profile.setUrlRequestInterceptor(None)
        
        self.update_timer.stop()
        event.accept()


def show_header_policy_simulator(web_view: QWebEngineView, parent=None):
    """Show Header Policy Simulator dialog"""
    dialog = HeaderPolicySimulatorDialog(web_view, parent)
    dialog.show()
    return dialog