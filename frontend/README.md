# BNPL Platform - Frontend

Next.js frontend for the Buy Now Pay Later (BNPL) platform.

## Tech Stack

- Next.js 14+ (App Router)
- TypeScript
- Tailwind CSS
- React Query (TanStack Query)
- Zustand (state management)
- Axios

## Setup

### Prerequisites

- Node.js 18+ and npm

### Installation

1. **Install dependencies:**

   ```bash
   npm install
   ```

2. **Set up environment variables:**

   Create a `.env.local` file in the `frontend` directory:

   ```env
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   ```

3. **Run the development server:**

   ```bash
   npm run dev
   ```

   The frontend will be available at: http://localhost:3000

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint

## Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── customer/          # Customer area pages
│   ├── retailer/          # Retailer area pages
│   ├── lender/            # Lender area pages
│   ├── login/             # Login page
│   ├── register/          # Registration page
│   ├── layout.tsx         # Root layout
│   └── providers.tsx     # React Query provider
├── components/            # React components
├── lib/
│   ├── api/              # API client functions
│   ├── hooks/            # Custom React hooks
│   ├── store/            # Zustand stores
│   └── apiClient.ts      # Axios instance
└── package.json
```

## Features

- JWT-based authentication
- Role-based routing (CUSTOMER, RETAILER, LENDER)
- Product browsing and BNPL checkout
- Loan management
- Credit profile display
- Responsive design with Tailwind CSS

## API Integration

The frontend communicates with the FastAPI backend using Axios. The API client automatically:

- Adds JWT tokens to requests
- Handles 401 errors (redirects to login)
- Uses the base URL from environment variables

## Authentication

Authentication state is managed using Zustand with localStorage persistence. The auth store provides:

- `login(token, user)` - Store token and user
- `logout()` - Clear auth state
- `isAuthenticated` - Check if user is logged in
- `user` - Current user object with role

## Role-Based Access

Each role area (`/customer`, `/retailer`, `/lender`) has a layout that checks authentication and role before rendering.

## Development Notes

- Uses React Query for data fetching and caching
- All API calls go through the centralized `apiClient`
- Components are client-side by default (use `'use client'` directive)
- Tailwind CSS is configured for custom colors and styling
