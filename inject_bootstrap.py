with open('rezervace/templates/rezervace/base.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add Bootstrap CSS to the head
if 'bootstrap.min.css' not in content:
    replacement = """<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
:root {
  --bs-success: #154b2a;
  --bs-success-rgb: 21, 75, 42;
  --bs-primary: #154b2a;
  --bs-primary-rgb: 21, 75, 42;
}
.bg-success {
  background-color: #154b2a !important;
}
.text-success {
  color: #154b2a !important;
}
.btn-success {
  background-color: #154b2a !important; border-color: #154b2a !important;
}
.btn-success:hover {
  background-color: #0e331c !important; border-color: #0e331c !important; color: white !important;
}
.btn-outline-success {
  color: #154b2a !important; border-color: #154b2a !important;
}
.btn-outline-success:hover {
  background-color: #154b2a !important; color: white !important;
}

/* Fix any bootstrap overrides breaking Návsí header */
.gcm-header a { text-decoration: none; }
.gcm-header ul { padding-left: 0; }
</style>
</head>"""
    content = content.replace('</head>', replacement)

with open('rezervace/templates/rezervace/base.html', 'w', encoding='utf-8') as f:
    f.write(content)
