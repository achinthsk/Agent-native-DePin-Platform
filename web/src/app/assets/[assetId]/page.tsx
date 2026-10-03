import { promises as fs } from "fs";
import path from "path";
import { AssetDetailPage } from "@/components/tokn/asset-detail-page";
import { LIVE_API_FALLBACK } from "@/lib/api";

async function listAssetIds(): Promise<string[]> {
  const ids = new Set<string>();

  // Prefer committed storage directories so static export works offline.
  try {
    const storageRoot = path.join(process.cwd(), "..", "storage");
    const entries = await fs.readdir(storageRoot, { withFileTypes: true });
    for (const ent of entries) {
      if (ent.isDirectory()) ids.add(ent.name);
    }
  } catch {
    // ignore
  }

  try {
    const res = await fetch(
      `${LIVE_API_FALLBACK}/v1/assets?latest_only=true&limit=50`,
      { headers: { Accept: "application/json" }, cache: "no-store" },
    );
    if (res.ok) {
      const data = (await res.json()) as {
        assets?: { asset_id?: string }[];
      };
      for (const a of data.assets || []) {
        if (a.asset_id) ids.add(a.asset_id);
      }
    }
  } catch {
    // ignore — storage list is enough for known assets
  }

  if (ids.size === 0) {
    ids.add("glow-farm-1");
  }

  return [...ids].sort();
}

export async function generateStaticParams() {
  const ids = await listAssetIds();
  return ids.map((assetId) => ({ assetId }));
}

export default async function Page({
  params,
}: {
  params: Promise<{ assetId: string }>;
}) {
  const { assetId } = await params;
  return <AssetDetailPage assetId={decodeURIComponent(assetId)} />;
}
