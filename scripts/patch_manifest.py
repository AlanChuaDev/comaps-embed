#!/usr/bin/env python3
"""Patch a decoded (apktool) CoMaps AndroidManifest.xml so it can be embedded.
Usage: patch_manifest.py <decoded_dir>   Prints a log of what it changed/found."""
import re, sys, pathlib

p = pathlib.Path(sys.argv[1]) / "AndroidManifest.xml"
s = p.read_text(encoding="utf-8")

# 1) allowUntrustedActivityEmbedding on <application>
m = re.search(r"<application\b[^>]*>", s, re.S)
if not m:
    sys.exit("ERROR: no <application> tag found")
tag = m.group(0)
if "allowUntrustedActivityEmbedding" in tag:
    new = re.sub(r'android:allowUntrustedActivityEmbedding="[^"]*"',
                 'android:allowUntrustedActivityEmbedding="true"', tag)
    print("allowUntrustedActivityEmbedding: already present, forced to true")
else:
    new = tag[:-1] + ' android:allowUntrustedActivityEmbedding="true">'
    print("allowUntrustedActivityEmbedding: ADDED on <application>")
s = s.replace(tag, new, 1)

# 2) resizeableActivity=false -> true
n = len(re.findall(r'android:resizeableActivity="false"', s))
s = s.replace('android:resizeableActivity="false"', 'android:resizeableActivity="true"')
print(f"resizeableActivity=false fixed: {n}")

# 3) forced portrait orientations -> unspecified
portrait = r'(portrait|sensorPortrait|reversePortrait|userPortrait)'
hits = re.findall(r'android:screenOrientation="' + portrait + '"', s)
s = re.sub(r'android:screenOrientation="' + portrait + '"',
           'android:screenOrientation="unspecified"', s)
print(f"portrait-forced screenOrientation fixed: {len(hits)}")

# 4) things that can break split-screen: just report
for pat in (r'android:maxAspectRatio="[^"]*"', r'android:minAspectRatio="[^"]*"',
            r'android:screenOrientation="[^"]*"', r'android:resizeableActivity="[^"]*"',
            r'android:supportsPictureInPicture="[^"]*"'):
    found = sorted(set(re.findall(pat, s)))
    if found:
        print("INFO remaining:", ", ".join(found))

p.write_text(s, encoding="utf-8")
