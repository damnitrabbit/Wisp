/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ['@wisp/shared'],
  poweredByHeader: false,
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          { key: 'Referrer-Policy', value: 'no-referrer' },
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'Permissions-Policy', value: 'microphone=(self), camera=(), geolocation=()' }
        ]
      }
    ];
  }
};
export default nextConfig;
