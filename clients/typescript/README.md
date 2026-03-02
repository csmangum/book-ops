# BookOps TypeScript API Client

Typed client generated from the OpenAPI 3.1 contract:

- Spec: `openapi/bookops-api.openapi.yaml`
- Generated schema types: `src/generated/schema.ts`
- Convenience wrapper: `src/client.ts`

## Install dependencies

```bash
npm install
```

## Generate schema types from OpenAPI

```bash
npm run generate
```

## Typecheck

```bash
npm run typecheck
```

## Usage

```ts
import { BookOpsApiClient } from "@bookops/api-client";

const api = BookOpsApiClient.create("/api");

const version = await api.getVersion();
if (version.data?.ok) {
  console.log(version.data.data.bookops_version);
}

const analyze = await api.analyzeChapter({
  chapter_id: 1,
  checks: ["repetition", "motifs"],
});
```
