# Shift Platform - Instant DB Setup Guide

## Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Get your Instant DB App ID:**
   - Visit [https://instant.dev](https://instant.dev)
   - Sign up or log in
   - Create a new app
   - Copy your App ID

3. **Configure environment:**
   Create a `.env.local` file in the `frontend` directory:
   ```env
   NEXT_PUBLIC_INSTANT_APP_ID=your_app_id_here
   ```

4. **Run the app:**
   ```bash
   npm run dev
   ```

   Open [http://localhost:3000](http://localhost:3000)

## Features Implemented

✅ **Authentication System**
- User registration with roles (customer, retailer, lender)
- Login/logout functionality
- Role-based access control

✅ **Customer Features**
- Browse marketplace
- View credit profile (score, tier, limit)
- Request BNPL loans
- View loan status and history
- Checkout flow with installment selection

✅ **Retailer Features**
- Product management dashboard
- Add/edit products
- Manage inventory
- View product status

✅ **Lender Features**
- View pending loan applications
- Approve/reject loans
- Track active loans
- Loan management dashboard

✅ **Real-time Updates**
- All data syncs in real-time using Instant DB
- Multiple users can see updates instantly

## Data Schema

The platform uses the following entities:

- **users**: User accounts with email, phone, role, etc.
- **creditProfiles**: Customer credit scores and BNPL limits
- **products**: Products available for BNPL
- **loans**: BNPL loan applications and status
- **paymentSchedules**: Installment payment schedules

## Testing the Platform

1. **Register as a Customer:**
   - Go to `/register`
   - Create a customer account
   - You'll automatically get a credit profile

2. **Register as a Retailer:**
   - Create a retailer account
   - Add products to the marketplace

3. **Register as a Lender:**
   - Create a lender account
   - Approve/reject loan applications

4. **Test the Flow:**
   - Customer browses products
   - Customer requests a BNPL loan
   - Lender reviews and approves
   - Loan becomes active

## Notes

- This is a simplified version for demonstration
- Password hashing is basic (use bcrypt in production)
- No payment processing integration yet
- Credit scores are auto-generated (600 default)
- All data is stored in Instant DB cloud

## Next Steps for Production

- [ ] Implement proper password hashing (bcrypt)
- [ ] Add email verification
- [ ] Integrate payment processing
- [ ] Add proper credit scoring algorithm
- [ ] Add notifications
- [ ] Add analytics dashboard
- [ ] Implement proper error handling
- [ ] Add input validation
- [ ] Add unit and integration tests

