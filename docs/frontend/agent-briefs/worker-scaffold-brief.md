# Worker Brief: Issue 1 — Vite + React + TypeScript + Tailwind Scaffold

## Your Mission

Bootstrap the `frontend/` directory at `/workspace/frontend/` as a Vite React + TypeScript project. Install and configure Tailwind CSS v3. Establish the required source directory structure with placeholder/index files. Verify the dev server starts and the production build compiles cleanly.

This is the foundation issue — all subsequent workers depend on this structure existing.

## What to Build

### 1. Create the Vite project

From `/workspace`, run:

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
```

### 2. Install Tailwind CSS v3 (not v4)

```bash
npm install -D tailwindcss@3 postcss autoprefixer
npx tailwindcss init -p
```

Configure `tailwind.config.js` to scan the right files:

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

In `src/index.css`, replace the existing contents with the Tailwind directives:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

Ensure `src/main.tsx` imports `./index.css`.

### 3. Install test dependencies

```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom @vitejs/plugin-react
npm install -D @playwright/test
```

Configure Vitest in `vite.config.ts`:

```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
  },
})
```

Create `tests/setup.ts`:

```ts
import '@testing-library/jest-dom'
```

Add to `tsconfig.app.json` (or `tsconfig.json`) the types for vitest globals and jest-dom:
```json
{
  "compilerOptions": {
    "types": ["vitest/globals", "@testing-library/jest-dom"]
  }
}
```

### 4. Install uuid package for session ID generation

```bash
npm install uuid
npm install -D @types/uuid
```

### 5. Create the required directory structure

Create these directories and placeholder files:

```
frontend/src/api/           → create index.ts (empty export placeholder)
frontend/src/types/         → create index.ts (empty export placeholder)
frontend/src/hooks/         → create index.ts (empty export placeholder)
frontend/src/components/    → create index.ts (empty export placeholder)
frontend/src/utils/         → create index.ts (empty export placeholder)
frontend/tests/unit/        → create .gitkeep
frontend/tests/e2e/         → create .gitkeep
```

### 6. Update App.tsx with a Tailwind test element

Replace the default App.tsx content with a minimal component that proves Tailwind works:

```tsx
// App.tsx — placeholder replaced in Issue 9 with full layout

function App() {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <h1 className="text-2xl font-bold text-gray-800">docuFetch</h1>
    </div>
  )
}

export default App
```

### 7. Add npm scripts

Ensure `package.json` has:
```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "test": "vitest run",
    "test:watch": "vitest",
    "test:e2e": "playwright test"
  }
}
```

### 8. Create Playwright config

Create `playwright.config.ts` at `frontend/`:

```ts
import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  use: {
    baseURL: 'http://localhost:5173',
  },
})
```

## Coding Guidelines (from CLAUDE.md)

- Every function must have a docstring
- Every code file must have a description comment at the top
- Simplicity first — minimum code that solves the problem
- No speculative features

## Acceptance Criteria (from issues.md Issue 1)

- [ ] `npm run dev` starts the Vite dev server at `http://localhost:5173` with no console errors
- [ ] `npm run build` produces a production build with no TypeScript or Tailwind compilation errors
- [ ] Tailwind utility classes in `App.tsx` are applied (visible from build output — no need to open browser)
- [ ] Directory structure (`src/api/`, `src/types/`, `src/hooks/`, `src/components/`, `src/utils/`, `tests/unit/`, `tests/e2e/`) exists

## Verification Steps

1. Run `npm run build` from `/workspace/frontend/` — must succeed with no errors
2. Check that all required directories exist with `ls -la src/ tests/`
3. Run `npm run test` — should run with 0 tests (no test files yet) without errors

## What to Write in Your Report

Write your completion report to `/workspace/docs/frontend/agent-reports/worker-scaffold-report.md` with:
- Status: DONE or FAILED
- List of files created
- Output of `npm run build` (last few lines)
- Any deviations from this brief and why
- Blockers for subsequent workers (if any)
