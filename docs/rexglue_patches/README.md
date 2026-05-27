# ReXGlue Local Patches

These patches record local, ignored ReXGlue SDK edits used during the current The Outfit bring-up. Apply required patches from the ReXGlue SDK checkout root:

```powershell
cd D:\360RexGlue\TheOutFit\tools\rexglue-sdk
git apply ..\..\docs\rexglue_patches\0001-use-manual-switch-tables-during-block-discovery.patch
git apply ..\..\docs\rexglue_patches\0002-tolerate-modifier-only-physical-protection.patch
```

Optional D3D12 TDR diagnostics and experiments:

```powershell
git apply ..\..\docs\rexglue_patches\0003-defer-d3d12-primary-submission-with-pending-uav-work.patch
git apply ..\..\docs\rexglue_patches\0004-diagnose-d3d12-shared-memory-coherency.patch
git apply ..\..\docs\rexglue_patches\0005-diagnose-d3d12-resolve-coherency-loop.patch
git apply ..\..\docs\rexglue_patches\0006-diagnose-d3d12-host-render-target-extent-and-resolve.patch
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
- `0003-defer-d3d12-primary-submission-with-pending-uav-work.patch`: makes D3D12 primary-buffer-end submission conservative when shared memory, scaled resolve, or EDRAM UAV work still appears uncommitted. Current evidence does not prove this patch is required; later comparison runs reproduced `DEVICE_HUNG`, so classify it as optional diagnostic/experimental until a tighter A/B proves otherwise.
- `0004-diagnose-d3d12-shared-memory-coherency.patch`: adds trace diagnostics for D3D12 shared-memory allocation mode, tile mapping, upload ranges, state transitions, and UAV barriers. This patch is for evidence capture only and is not a runtime fix.
- `0005-diagnose-d3d12-resolve-coherency-loop.patch`: adds render-target resolve diagnostics for source/destination format, destination range, dispatch counts, and repeated resolve/coherency batches. It also contains an experimental split after four copied resolve dispatches with pending UAV/coherency work. Evidence from the default run still reproduced `DXGI_ERROR_DEVICE_HUNG`, so this patch is diagnostic evidence, not a permanent fix.
- `0006-diagnose-d3d12-host-render-target-extent-and-resolve.patch`: adds host-render-target resolve diagnostics for destination ranges, repeat counts, direct-resolve preflight, and render-target dump rectangles. This patch is for evidence capture only and is not a runtime fix.

Current classification:

| Patch | Classification | Evidence |
|---|---|---|
| `0001` | Required | Without manual switch-table labels participating in block discovery, the `0x8269AB34` state switch produced wrong generated control flow before first frame. |
| `0002` | Required | The first-frame path needed modifier-only physical allocation protection `0x400` / `X_PAGE_WRITECOMBINE` to be accepted as read/write physical memory. |
| `0003` | Optional diagnostic/experimental | It did not independently prevent the D3D12 TDR, and later default/comparison runs still reproduced `DEVICE_HUNG`. |
| `0004` | Diagnostic-only | Adds shared-memory/tile/UAV breadcrumbs only; no runtime fix is claimed. |
| `0005` | Diagnostic-only with failed experiment | The split-after-four-resolves experiment fired but still reproduced `DEVICE_HUNG`; keep only when resolve-loop breadcrumbs are needed. |
| `0006` | Diagnostic-only | Adds host-render-target extent/direct-resolve breadcrumbs. The first diagnostic run stayed alive until killed after 180s while logging more than 52,000 direct resolve attempts, but this is not a fix claim. |

Evidence is recorded in `docs/regression_log.md` and `docs/address_ledger.md`.
