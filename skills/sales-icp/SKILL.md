# Ideal Customer Profile Builder (alias)

## Metadata
- **Title:** Ideal Customer Profile Builder
- **Invocation:** `/sales icp [description]` — back-compat alias
- **Output:** `./.sales/icp.md`

---

This skill is a back-compatibility alias retained so that `/sales icp <description>` from prior documentation continues to work.

**Behavior:** Delegate to `/sales init icp [description]` and stop. Do not produce a standalone `IDEAL-CUSTOMER-PROFILE.md` in the working directory — the canonical location is now `./.sales/icp.md`.

If `./.sales/` does not exist, `/sales init icp` will create it (along with the `.sales/icp.md` file). No other files are touched.

For full setup of the seller config, point the user at `/sales init`.
