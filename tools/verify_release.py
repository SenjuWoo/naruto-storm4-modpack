# Verify the published Woo Modpack release assets against the pinned checksums.
# It reads release/SHA256SUMS.txt and the GitHub release metadata; --download
# hashes the actual bytes instead of trusting the API digest.
# No third-party packages are required. Logs go to stdout; the exit code is the result.
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.request
from pathlib import Path

DEFAULT_REPO = "SenjuWoo/naruto-storm4-modpack"
DEFAULT_TAG = "v1.0.0"
DEFAULT_SUMS = Path(__file__).resolve().parents[1] / "release" / "SHA256SUMS.txt"


# Read the standard sha256sum format: "<64 hex>  <name>" or "<64 hex> *<name>".
def parse_sums(text):
    expected = {}
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            raise ValueError(f"line {number}: expected '<hash>  <name>'")
        digest, name = parts
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest.lower()):
            raise ValueError(f"line {number}: not a SHA-256 digest")
        name = name.lstrip("*").strip()
        if not name:
            raise ValueError(f"line {number}: missing asset name")
        if name in expected:
            raise ValueError(f"line {number}: duplicate asset {name}")
        expected[name] = digest.lower()
    if not expected:
        raise ValueError("checksum file is empty")
    return expected


# Compare the pinned names and hashes with the release API asset rows.
# Extra release assets are allowed; a checksum file may be added beside them.
def compare_assets(expected, assets):
    errors = []
    by_name = {asset.get("name"): asset for asset in assets}
    for name, digest in expected.items():
        asset = by_name.get(name)
        if asset is None:
            errors.append(f"missing release asset: {name}")
            continue
        actual = (asset.get("digest") or "").lower()
        if actual.startswith("sha256:"):
            actual = actual[len("sha256:"):]
        if not actual:
            errors.append(f"release asset has no digest: {name}")
        elif actual != digest:
            errors.append(f"hash mismatch: {name}: expected {digest}, got {actual}")
    return errors


# Fetch one release's metadata. A token is optional but avoids the 60/hour limit.
def fetch_release(repo, tag, token=None):
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/releases/tags/{tag}",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "woo-release-verifier"},
    )
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


# Download one asset and return its SHA-256 without keeping the whole file in memory.
def download_asset(url, destination):
    digest = hashlib.sha256()
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=60) as response, destination.open("wb") as output:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
            output.write(chunk)
    return digest.hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser(description="Verify published Woo Modpack release assets against release/SHA256SUMS.txt.")
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--tag", default=DEFAULT_TAG)
    parser.add_argument("--sums", type=Path, default=DEFAULT_SUMS)
    parser.add_argument("--download", type=Path, help="download assets here and hash the bytes")
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"))
    args = parser.parse_args(argv)

    expected = parse_sums(args.sums.read_text(encoding="utf-8"))
    release = fetch_release(args.repo, args.tag, args.token)
    assets = release.get("assets") or []
    errors = compare_assets(expected, assets)

    if args.download:
        by_name = {asset.get("name"): asset for asset in assets}
        for name, digest in expected.items():
            asset = by_name.get(name)
            if asset is None:
                continue
            actual = download_asset(asset["browser_download_url"], args.download / name)
            if actual != digest:
                errors.append(f"downloaded hash mismatch: {name}: expected {digest}, got {actual}")
            else:
                print(f"downloaded ok  {name}")

    if errors:
        for error in errors:
            print(f"FAIL {error}", file=sys.stderr)
        return 1
    print(f"OK {args.repo} {args.tag}: {len(expected)} asset(s) match {args.sums.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
