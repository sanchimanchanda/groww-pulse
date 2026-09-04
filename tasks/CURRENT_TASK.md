# CURRENT TASK

> This file contains ONLY the first P0 task that is ready to implement.
> Update this file when the task is complete: replace with the next unblocked P0 task.

---

## TASK-001

**Title:** Initialize monorepo project structure

**Epic:** Project Foundation

**Priority:** P0

**Status:** 🟡 READY TO IMPLEMENT

**Dependencies:** None

---

### Description

Create the top-level monorepo directory layout for backend, frontend, worker, and shared packages. Establish the project skeleton that all subsequent tasks build into.

---

### Directory Structure to Create

```
groww/
├── backend/                  # Fastify API server
│   ├── src/
│   │   └── index.ts          # (placeholder)
│   ├── package.json
│   └── tsconfig.json
│
├── worker/                   # Market data pipeline process
│   ├── src/
│   │   └── index.ts          # (placeholder)
│   ├── package.json
│   └── tsconfig.json
│
├── frontend/                 # React + TypeScript UI
│   ├── src/
│   │   └── main.tsx          # (placeholder)
│   ├── index.html
│   ├── package.json
│   └── tsconfig.json
│
├── shared/                   # Shared TypeScript types & utilities
│   ├── src/
│   │   └── index.ts          # (placeholder)
│   ├── package.json
│   └── tsconfig.json
│
├── docs/                     # Already exists (DESIGN.md)
├── tasks/                    # Already exists (this file)
│
├── .gitignore
├── README.md                 # (stub)
└── package.json              # Root npm workspace config
```

---

### Implementation Notes

1. Use **npm workspaces** at the root to link packages:
   ```json
   // package.json (root)
   {
     "name": "groww-watchlist",
     "private": true,
     "workspaces": ["backend", "worker", "frontend", "shared"],
     "scripts": {
       "dev:backend":  "npm -w backend run dev",
       "dev:worker":   "npm -w worker run dev",
       "dev:frontend": "npm -w frontend run dev"
     }
   }
   ```

2. The `shared` package must be installed as a dependency in `backend` and `worker`:
   ```json
   // backend/package.json
   {
     "dependencies": {
       "@groww/shared": "*"
     }
   }
   ```

3. `.gitignore` must exclude:
   - `node_modules/`
   - `.env` (all packages)
   - `dist/`
   - `build/`
   - `*.local`
   - `.DS_Store`

4. Each package's `package.json` should have:
   - `"name"`: e.g. `@groww/backend`, `@groww/worker`, `@groww/frontend`, `@groww/shared`
   - `"version"`: `"1.0.0"`
   - `"private"`: `true`
   - A placeholder `"main"` entry

---

### Acceptance Criteria

- [ ] Root `package.json` has `workspaces` correctly set to all 4 packages.
- [ ] `npm install` at the project root completes with exit code 0.
- [ ] All 4 package directories exist with `package.json` and a `src/` folder.
- [ ] `.gitignore` is present at root and covers all required exclusions.
- [ ] `README.md` stub exists at root.
- [ ] `npm run dev:backend` can be run from root without error (even if it just exits — placeholder script).

---

### Testing

```bash
# Verify workspace links
npm install
ls node_modules/@groww/

# Verify directory structure
tree -L 3 --gitignore

# Verify .gitignore excludes node_modules
git check-ignore node_modules/
```

---

### Next Task After Completion

→ **TASK-002**: Environment variable strategy and `.env.example` files.
→ **TASK-004**: Shared TypeScript configuration and linting.

Both are unblocked once TASK-001 is complete. They can proceed in parallel.
