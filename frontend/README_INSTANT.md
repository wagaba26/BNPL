# Shift Platform - Instant DB Version

This is a fullstack rebuild of the Shift BNPL platform using Instant DB and Next.js.

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Set up Instant DB:**
   - Go to [https://instant.dev](https://instant.dev) and create an account
   - Create a new app and get your App ID
   - Create a `.env.local` file in the `frontend` directory:
   ```env
   NEXT_PUBLIC_INSTANT_APP_ID=your_app_id_here
   ```

3. **Run the development server:**
   ```bash
   npm run dev
   ```

   The app will be available at http://localhost:3000

## Features

### User Roles
- **Customer**: Browse products, request BNPL loans, view loan status
- **Retailer**: List products, manage inventory
- **Lender**: View loans, approve/reject loan applications

### Core Functionality
1. **Authentication**: Simple auth with role-based access
2. **Credit Profile**: Automatic credit score and BNPL limit for customers
3. **Product Management**: Retailers can list BNPL-eligible products
4. **BNPL Requests**: Customers can request loans for products
5. **Loan Management**: Lenders can approve/reject loans
6. **Real-time Updates**: All data updates in real-time using Instant DB

## Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── customer/          # Customer area pages
│   ├── retailer/          # Retailer area pages
│   ├── lender/            # Lender area pages
│   ├── login/             # Login page
│   ├── register/          # Registration page
│   └── page.tsx           # Home/Marketplace page
├── components/            # React components
├── lib/
│   ├── instant.ts         # Instant DB schema and helpers
│   ├── auth.ts            # Auth utilities
│   └── contexts/          # React contexts
│       └── AuthContext.tsx
└── package.json
```

## Instant DB Schema

The schema includes:
- `users`: User accounts with roles
- `creditProfiles`: Customer credit scores and limits
- `products`: Products available for BNPL
- `loans`: BNPL loan applications
- `paymentSchedules`: Installment payment schedules

## Notes

- This is a simplified version for demonstration. In production, you should:
  - Use proper password hashing (bcrypt)
  - Implement proper authentication with Instant DB's auth features
  - Add proper error handling
  - Add validation
  - Add payment processing integration
  - Add proper security measures

