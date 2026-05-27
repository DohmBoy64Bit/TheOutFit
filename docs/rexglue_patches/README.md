# ReXGlue Local Patches

These patches record the local, ignored ReXGlue SDK edits required by the current The Outfit bring-up. Apply them from the ReXGlue SDK checkout root:

```powershell
cd D:\360RexGlue\TheOutFit\tools\rexglue-sdk
git apply ..\..\docs\rexglue_patches\0001-use-manual-switch-tables-during-block-discovery.patch
git apply ..\..\docs\rexglue_patches\0002-tolerate-modifier-only-physical-protection.patch
git apply ..\..\docs\rexglue_patches\0003-defer-d3d12-primary-submission-with-pending-uav-work.patch
```

Optional D3D12 TDR diagnostics:

```powershell
git apply ..\..\docs\rexglue_patches\0004-diagnose-d3d12-shared-memory-coherency.patch
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
- `0003-defer-d3d12-primary-submission-with-pending-uav-work.patch`: makes D3D12 primary-buffer-end submission conservative when shared memory, scaled resolve, or EDRAM UAV work still appears uncommitted. Evidence so far shows this is a useful diagnostic guard but not a complete TDR fix by itself; later comparison runs reproduced `DEVICE_HUNG` even with the earlier flag pair.
- `0004-diagnose-d3d12-shared-memory-coherency.patch`: adds trace diagnostics for D3D12 shared-memory allocation mode, tile mapping, upload ranges, state transitions, and UAV barriers. This patch is for evidence capture only and is not a runtime fix.

Evidence is recorded in `docs/regression_log.md` and `docs/address_ledger.md`.
