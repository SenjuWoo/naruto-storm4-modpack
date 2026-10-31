# Release checksums

`SHA256SUMS.txt` pins the two published v1.0.0 archive volumes. The hashes were
computed from the downloaded release assets on 2026-10-31 and matched GitHub's
recorded asset digests.

Verify a local download:

```text
sha256sum -c SHA256SUMS.txt
```

On Windows PowerShell:

```powershell
Get-FileHash .\Naruto.Shippuden.Ultimate.Ninja.Storm.4.Woomodpack-2.7z.001 -Algorithm SHA256
Get-FileHash .\Naruto.Shippuden.Ultimate.Ninja.Storm.4.Woomodpack-2.7z.002 -Algorithm SHA256
```

Check the live GitHub release metadata without downloading 2.2 GB:

```text
python tools/verify_release.py --tag v1.0.0
```

Add `--download DIR` to download both volumes and hash the bytes locally. The
script exits 0 only when every expected asset exists with the pinned hash.
