"""Fetch a URL to data/raw/<name>.html and print readable text (helper for source capture)."""
import sys, re, html, subprocess, pathlib
url, name = sys.argv[1], sys.argv[2]
out = pathlib.Path(__file__).resolve().parents[1] / "data" / "raw" / f"{name}.html"
subprocess.run(["curl", "-sL", "--max-time", "40", "-A",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/128 Safari/537.36",
                "-o", str(out), url], check=False)
t = out.read_text(errors="ignore")
t = re.sub(r"(?s)<script.*?</script>|<style.*?</style>|<nav.*?</nav>|<footer.*?</footer>", "", t)
t = html.unescape(re.sub(r"<[^>]+>", "\n", t))
t = re.sub(r"\n\s*\n+", "\n", t)
kw = sys.argv[3] if len(sys.argv) > 3 else None
if kw and kw in t:
    i = t.find(kw); t = t[max(0, i - 1500):]
print(t[:int(sys.argv[4]) if len(sys.argv) > 4 else 7000])
