/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
      {
        protocol: 'http',
        hostname: '**',
      },
    ],
  },
  // Enable experimental features for better performance
  experimental: {
    optimizePackageImports: ['@tanstack/react-query', 'date-fns'],
  },
  // Optional: Enable standalone output for smaller Docker images
  // Uncomment the line below if using Docker and want optimized builds
  // output: 'standalone',
};

module.exports = nextConfig;

