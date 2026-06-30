/** @type {import('next').NextConfig} */
const nextConfig = {
  // Static export — Lectern is a pre-baked workbench (the wrootpress static-site
  // pattern). Every occasion + year page is generated at build from data/build/.
  output: "export",
  trailingSlash: true,
  images: { unoptimized: true },
};

export default nextConfig;
