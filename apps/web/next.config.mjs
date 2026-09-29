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
          { key: 'Permissions-Policy', value: 'microphone=(self), camera=(), geolocation=()' },
          // Nobody can frame NoTrace inside their own site (clickjacking), and browsers stick to HTTPS.
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'Content-Security-Policy', value: "frame-ancestors 'none'" },
          { key: 'Strict-Transport-Security', value: 'max-age=63072000; includeSubDomains' }
        ]
      }
    ];
  }
};
export default nextConfig;
