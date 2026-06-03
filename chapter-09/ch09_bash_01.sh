# Create Next.js project with TypeScript and App Router
npx create-next-app@latest briefly --typescript --tailwind --app

# Install dependencies
cd briefly
npm install @supabase/supabase-js @supabase/ssr @stripe/stripe-js
npm install @stripe/react-stripe-js axios react-hook-form
npm install @anthropic-ai/sdk zod

# Install dev dependencies
npm install -D @types/node stripe-cli
