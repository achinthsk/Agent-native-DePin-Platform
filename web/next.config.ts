import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export",
  images: { unoptimized: true },
  // Trailing slash helps StaticFiles hosting under FastAPI.
  trailingSlash: true,
};

export default nextConfig;
