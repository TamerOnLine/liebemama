# 🔐 Security Policy

Thank you for helping us improve the security of **LiebeMama**.

We take security seriously and appreciate your efforts to disclose vulnerabilities responsibly.

---

## 📥 Reporting a Vulnerability

If you discover a security vulnerability, please report it privately via email:

📧 **info@liebemama.com**

Do **NOT** open a public issue. We will investigate and respond as quickly as possible.

---

## ✅ Supported Versions

We currently support the latest stable version of the project:

| Version | Supported |
|---------|-----------|
| v1.x    | ✅         |
| < v1.0  | ❌         |

---

## 🔒 Security Measures

The LiebeMama project uses the following security practices:

- `Flask-Login` for session-based authentication
- Role-Based Access Control (RBAC) via decorators
- Input sanitization using Cerberus + Bleach
- Secure image upload and deletion with access control
- HTTPS enforced via Cloudflare and Let’s Encrypt
- Error logging with minimal exposure in production

---

## 📅 Response Timeline

We aim to respond to valid vulnerability reports within **72 hours**.

---

## 🙏 Thank You

Your help in making **LiebeMama** more secure is greatly appreciated!