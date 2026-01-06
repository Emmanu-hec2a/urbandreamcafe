# UrbanFoods Manual Payment Implementation

## Overview
Replace MPESA API integration with manual TILL number display for payments. Customers pay manually via TILL numbers, admin confirms orders after payment.

## Tasks

### 1. Update views.py
- [x] Comment out MPESA STK push logic in place_order function
- [x] Comment out mpesa_callback function
- [x] Comment out mpesa_stk_query function
- [x] Comment out initiate_mpesa_payment function
- [x] Update place_order to set payment_status to 'pending' and status to 'pending' (no payment_pending)
- [x] Remove MPESA-specific fields from order creation

### 2. Update homepage.html
- [ ] Modify checkout modal to display TILL numbers instead of MPESA
- [ ] Show different TILL numbers for Food/Grocery vs Liquor
- [ ] Update payment instructions for manual payment
- [ ] Remove MPESA processing modals

### 3. Update admin_views.py
- [ ] Add manual payment confirmation functionality
- [ ] Update order status after payment confirmation
- [ ] Remove MPESA-specific analytics
- [ ] Update order filtering and display

### 4. Update admin templates
- [ ] Update orders.html to show manual payment confirmation buttons
- [ ] Remove MPESA-specific fields from order details

### 5. Testing
- [ ] Test checkout flow with TILL display
- [ ] Test admin order confirmation
- [ ] Verify order status updates correctly
