import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    externalDir: true,
  },
  async rewrites() {
    const configuredApiUrl = process.env.NEXT_PUBLIC_API_URL?.trim();

    if (!configuredApiUrl || configuredApiUrl.startsWith("/")) {
      return [];
    }

    const normalizedApiUrl = configuredApiUrl.endsWith("/")
      ? configuredApiUrl.slice(0, -1)
      : configuredApiUrl;

    return [
      {
        source: "/api/:path*",
        destination: `${normalizedApiUrl}/:path*`,
      },
    ];
  },
};

export default nextConfig;
