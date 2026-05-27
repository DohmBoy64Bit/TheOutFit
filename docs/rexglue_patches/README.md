# ReXGlue Local Patches

These patches record the local, ignored ReXGlue SDK edits required by the current The Outfit bring-up. Apply them from the ReXGlue SDK checkout root:

```powershell
cd D:\360RexGlue\TheOutFit\tools\rexglue-sdk
git apply ..\..\docs\rexglue_patches\0001-use-manual-switch-tables-during-block-discovery.patch
git apply ..\..\docs\rexglue_patches\0002-tolerate-modifier-only-physical-protection.patch
```

After applying, rebuild and install the SDK, then rebuild the port:

```powershell
cmake --build --preset win-amd64-relwithdebinfo --target install
cd D:\360RexGlue\TheOutFit\TheOutFit_Port
cmake --build --preset win-amd64-relwithdebinfo
```

Patch summary:

- `0001-use-manual-switch-tables-during-block-discovery.patch`: makes ReXGlue manual `[[switch_tables]]` entries participate in block discovery, not only emission. This is required for the `0x8269AB34` bctr state switch.
- `0002-tolerate-modifier-only-physical-protection.patch`: treats modifier-only physical-memory protection such as `X_PAGE_WRITECOMBINE` (`0x400`) as read/write physical memory, matching the successful first-frame runtime evidence.

Evidence is recorded in `docs/regression_log.md` and `docs/address_ledger.md`.
