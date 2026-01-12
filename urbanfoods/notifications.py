# urbanfoods/notifications.py
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

def send_admin_order_notification(order):
    """Send email notification to admin when a new order is received"""
    subject = f'🔔 New Order: {order.order_number}'
    
    # Get order items
    items_list = "\n".join([
        f"  - {item.food_item.name} x{item.quantity} @ KES {item.price_at_order}"
        for item in order.items.all()
    ])
    
    # Plain text version
    message = f'''
New Order Received!

Order Details:
--------------
Order Number: {order.order_number}
Store Type: {order.store_type.upper()}
Status: {order.status.upper()}

Customer Information:
--------------------
Name: {order.user.get_full_name() or order.user.username}
Email: {order.user.email}
Phone: {order.phone_number}

Delivery Details:
----------------
Hostel: {order.hostel}
Room Number: {order.room_number}
Delivery Notes: {order.delivery_notes or 'None'}

Order Summary:
-------------
{items_list}

Subtotal: KES {order.subtotal}
Delivery Fee: KES {order.delivery_fee}
Total Amount: KES {order.total}

Payment:
--------
Payment Method: {order.payment_method.upper()}
Payment Type: {order.payment_type.upper()}
Payment Status: {order.payment_status.upper()}

Estimated Delivery: {order.estimated_delivery.strftime('%I:%M %p')}

View order details at:
https://urbandreamcafe.up.railway.app/admin-panel/orders/

---
UrbanDreams Cafe Admin System
    '''
    
    # HTML version
    items_html = "".join([
        f'''
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{item.food_item.name}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: center;">{item.quantity}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: right;">KES {item.price_at_order}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: right; font-weight: bold;">KES {item.quantity * item.price_at_order}</td>
        </tr>
        '''
        for item in order.items.all()
    ])
    
    html_message = f'''
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 650px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px 10px 0 0;">
                <h2 style="color: white; margin: 0;">🔔 New Order Received!</h2>
            </div>
            
            <div style="background: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="background-color: #f0f4ff; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <h3 style="color: #667eea; margin: 0 0 10px 0;">Order #{order.order_number}</h3>
                    <p style="margin: 5px 0;"><strong>Store:</strong> {order.store_type.upper()}</p>
                    <p style="margin: 5px 0;"><strong>Status:</strong> <span style="color: #f59e0b; font-weight: bold;">{order.status.upper()}</span></p>
                </div>

                <h3 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px;">Customer Information</h3>
                <table style="width: 100%; margin-bottom: 20px;">
                    <tr>
                        <td style="padding: 8px 0;"><strong>Name:</strong></td>
                        <td style="padding: 8px 0;">{order.user.get_full_name() or order.user.username}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0;"><strong>Email:</strong></td>
                        <td style="padding: 8px 0;">{order.user.email}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0;"><strong>Phone:</strong></td>
                        <td style="padding: 8px 0;">{order.phone_number}</td>
                    </tr>
                </table>

                <h3 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px;">Delivery Details</h3>
                <table style="width: 100%; margin-bottom: 20px;">
                    <tr>
                        <td style="padding: 8px 0;"><strong>Hostel:</strong></td>
                        <td style="padding: 8px 0;">{order.hostel}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0;"><strong>Room Number:</strong></td>
                        <td style="padding: 8px 0;">{order.room_number}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0;"><strong>Notes:</strong></td>
                        <td style="padding: 8px 0;">{order.delivery_notes or 'None'}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0;"><strong>Estimated Delivery:</strong></td>
                        <td style="padding: 8px 0; color: #22c55e; font-weight: bold;">{order.estimated_delivery.strftime('%I:%M %p')}</td>
                    </tr>
                </table>

                <h3 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px;">Order Items</h3>
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                    <thead>
                        <tr style="background-color: #f8f9fa;">
                            <th style="padding: 10px; text-align: left; border-bottom: 2px solid #667eea;">Item</th>
                            <th style="padding: 10px; text-align: center; border-bottom: 2px solid #667eea;">Qty</th>
                            <th style="padding: 10px; text-align: right; border-bottom: 2px solid #667eea;">Price</th>
                            <th style="padding: 10px; text-align: right; border-bottom: 2px solid #667eea;">Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                        <tr style="background-color: #f8f9fa; font-weight: bold;">
                            <td colspan="3" style="padding: 10px; text-align: right; border-top: 2px solid #667eea;">Subtotal:</td>
                            <td style="padding: 10px; text-align: right; border-top: 2px solid #667eea;">KES {order.subtotal}</td>
                        </tr>
                        <tr style="background-color: #f8f9fa;">
                            <td colspan="3" style="padding: 10px; text-align: right;">Delivery Fee:</td>
                            <td style="padding: 10px; text-align: right;">KES {order.delivery_fee}</td>
                        </tr>
                        <tr style="background-color: #667eea; color: white; font-size: 1.1em;">
                            <td colspan="3" style="padding: 12px; text-align: right;"><strong>TOTAL:</strong></td>
                            <td style="padding: 12px; text-align: right;"><strong>KES {order.total}</strong></td>
                        </tr>
                    </tbody>
                </table>

                <h3 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px;">Payment Information</h3>
                <table style="width: 100%; margin-bottom: 20px;">
                    <tr>
                        <td style="padding: 8px 0;"><strong>Payment Method:</strong></td>
                        <td style="padding: 8px 0;">{order.payment_method.upper()}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0;"><strong>Payment Type:</strong></td>
                        <td style="padding: 8px 0;">{order.payment_type.upper()}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0;"><strong>Payment Status:</strong></td>
                        <td style="padding: 8px 0;"><span style="color: #f59e0b; font-weight: bold;">{order.payment_status.upper()}</span></td>
                    </tr>
                </table>
                
                <div style="margin-top: 30px; text-align: center;">
                    <a href="https://urbandreamcafe.up.railway.app/admin-panel/orders/" 
                       style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                              color: white; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 1.1em;">
                        View All Orders →
                    </a>
                </div>
                
                <p style="margin-top: 30px; color: #718096; font-size: 12px; text-align: center; border-top: 1px solid #e2e8f0; padding-top: 20px;">
                    This is an automated notification from UrbanDreams Cafe Admin System<br>
                    Sent at {timezone.now().strftime('%B %d, %Y at %I:%M %p')}
                </p>
            </div>
        </div>
    </body>
    </html>
    '''
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_NOTIFICATION_EMAIL],
            fail_silently=False,
            html_message=html_message,
        )
        return True
    except Exception as e:
        print(f"Failed to send admin notification email: {e}")
        return False


def send_customer_order_confirmation(order):
    """Send order confirmation email to customer"""
    subject = f'Order Confirmation - {order.order_number}'
    
    # Get order items
    items_list = "\n".join([
        f"  - {item.food_item.name} x{item.quantity} @ KES {item.price_at_order}"
        for item in order.items.all()
    ])
    
    payment_instructions = ""
    if order.payment_method == 'cash':
        if order.store_type == 'liquor':
            payment_instructions = f'''
Payment Instructions:
--------------------
Please complete payment using M-PESA Paybill:
Business Number: 8330098 - NETWIX
Account Number: {order.order_number}
Amount: KES {order.total}

Your order will be processed once payment is confirmed.
please ignore this if already paid.
'''
        else:
            payment_instructions = f'''
Payment Instructions:
--------------------
Please complete payment using M-PESA Till Number:
Till Number: 6960814 - MOSES ONKUNDI ATINDA
Amount: KES {order.total}

Your order will be processed once payment is confirmed.
please ignore this if already paid.
'''
    
    # Plain text version
    message = f'''
Thank you for your order!

Hi {order.user.get_full_name() or order.user.username},

Your order has been received and is being processed.

Order Details:
--------------
Order Number: {order.order_number}
Order Date: {order.created_at.strftime('%B %d, %Y at %I:%M %p')}

Delivery Information:
--------------------
Hostel: {order.hostel}
Room Number: {order.room_number}
Phone: {order.phone_number}
Estimated Delivery: {order.estimated_delivery.strftime('%I:%M %p')}

Order Summary:
-------------
{items_list}

Subtotal: KES {order.subtotal}
Delivery Fee: KES {order.delivery_fee}
Total Amount: KES {order.total}

Payment Method: {order.payment_method.upper()}
{payment_instructions}

You can track your order status at:
https://urbandreamcafe.up.railway.app/orders/

If you have any questions, please contact us | Call 0743486638/.

Thank you for choosing UrbanDreams Cafe!

---
UrbanDreams Cafe
    '''
    
    # HTML version
    items_html = "".join([
        f'''
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{item.food_item.name}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: center;">{item.quantity}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: right;">KES {item.price_at_order}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: right; font-weight: bold;">KES {item.quantity * item.price_at_order}</td>
        </tr>
        '''
        for item in order.items.all()
    ])
    
    payment_html = ""
    if order.payment_method == 'cash':
        payment_type = "Till" if order.store_type == 'liquor' else "Till Number"
        payment_number = "8330098 - NETWIX" if order.store_type == 'liquor' else "6960814 - MOSES ONKUNDI ATINDA"
        payment_html = f'''
        <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 5px;">
            <h3 style="color: #856404; margin-top: 0;">⚠️ Payment Required</h3>
            <p style="margin: 10px 0;"><strong>Please complete payment using M-PESA {payment_type}:</strong></p>
            <p style="margin: 5px 0; font-size: 1.1em;"><strong>{payment_type}:</strong> <span style="color: #667eea; font-size: 1.3em; font-weight: bold;">{payment_number}</span></p>
            {"<p style='margin: 5px 0;'><strong>Account Number:</strong> " + order.order_number + "</p>" if order.store_type == 'liquor' else ""}
            <p style="margin: 5px 0;"><strong>Amount:</strong> <span style="color: #22c55e; font-size: 1.2em; font-weight: bold;">KES {order.total}</span></p>
            <p style="margin: 10px 0 0 0; font-size: 0.9em; color: #856404;">Your order will be processed once payment is confirmed by our team.</p>
        </div>
        '''
    
    html_message = f'''
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 650px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 10px 10px 0 0; text-align: center;">
                <h1 style="color: white; margin: 0;">✅ Order Confirmed!</h1>
                <p style="color: white; margin: 10px 0 0 0; font-size: 1.1em;">Thank you for your order</p>
            </div>
            
            <div style="background: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <p style="font-size: 1.1em; margin-top: 0;">Hi <strong>{order.user.get_full_name() or order.user.username}</strong>,</p>
                <p>Your order has been received and is being processed. Here are your order details:</p>

                <div style="background-color: #f0f4ff; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #667eea; margin: 0 0 10px 0;">Order #{order.order_number}</h3>
                    <p style="margin: 5px 0;"><strong>Order Date:</strong> {order.created_at.strftime('%B %d, %Y at %I:%M %p')}</p>
                    <p style="margin: 5px 0;"><strong>Status:</strong> <span style="color: #f59e0b; font-weight: bold;">{order.status.upper()}</span></p>
                </div>

                {payment_html}

                <h3 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px;">Delivery Information</h3>
                <table style="width: 100%; margin-bottom: 20px;">
                    <tr>
                        <td style="padding: 8px 0;"><strong>Hostel:</strong></td>
                        <td style="padding: 8px 0;">{order.hostel}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0;"><strong>Room Number:</strong></td>
                        <td style="padding: 8px 0;">{order.room_number}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0;"><strong>Phone:</strong></td>
                        <td style="padding: 8px 0;">{order.phone_number}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0;"><strong>Estimated Delivery:</strong></td>
                        <td style="padding: 8px 0; color: #22c55e; font-weight: bold; font-size: 1.1em;">{order.estimated_delivery.strftime('%I:%M %p')}</td>
                    </tr>
                </table>

                <h3 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px;">Order Summary</h3>
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                    <thead>
                        <tr style="background-color: #f8f9fa;">
                            <th style="padding: 10px; text-align: left; border-bottom: 2px solid #667eea;">Item</th>
                            <th style="padding: 10px; text-align: center; border-bottom: 2px solid #667eea;">Qty</th>
                            <th style="padding: 10px; text-align: right; border-bottom: 2px solid #667eea;">Price</th>
                            <th style="padding: 10px; text-align: right; border-bottom: 2px solid #667eea;">Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                        <tr style="background-color: #f8f9fa; font-weight: bold;">
                            <td colspan="3" style="padding: 10px; text-align: right; border-top: 2px solid #667eea;">Subtotal:</td>
                            <td style="padding: 10px; text-align: right; border-top: 2px solid #667eea;">KES {order.subtotal}</td>
                        </tr>
                        <tr style="background-color: #f8f9fa;">
                            <td colspan="3" style="padding: 10px; text-align: right;">Delivery Fee:</td>
                            <td style="padding: 10px; text-align: right;">KES {order.delivery_fee}</td>
                        </tr>
                        <tr style="background-color: #667eea; color: white; font-size: 1.1em;">
                            <td colspan="3" style="padding: 12px; text-align: right;"><strong>TOTAL:</strong></td>
                            <td style="padding: 12px; text-align: right;"><strong>KES {order.total}</strong></td>
                        </tr>
                    </tbody>
                </table>

                <p style="margin: 20px 0;"><strong>Payment Method:</strong> {order.payment_method.upper()}</p>
                
                <div style="margin: 30px 0; text-align: center;">
                    <a href="https://urbandreamcafe.up.railway.app/orders/" 
                       style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                              color: white; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 1.1em;">
                        Track Your Order →
                    </a>
                </div>

                <div style="background-color: #f0f9ff; border-left: 4px solid #3b82f6; padding: 15px; margin-top: 20px; border-radius: 5px;">
                    <p style="margin: 0; color: #1e40af;"><strong>💡 Need Help?</strong></p>
                    <p style="margin: 5px 0 0 0; color: #1e40af;">If you have any questions about your order, please contact our support team. | Call 0743486638</p>
                </div>
                
                <p style="margin-top: 30px; color: #718096; font-size: 12px; text-align: center; border-top: 1px solid #e2e8f0; padding-top: 20px;">
                    Thank you for choosing Urban Dreams Cafe!<br>
                    This email was sent to {order.user.email}<br>
                    Sent at {timezone.now().strftime('%B %d, %Y at %I:%M %p')}
                </p>
            </div>
        </div>
    </body>
    </html>
    '''
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.user.email],
            fail_silently=False,
            html_message=html_message,
        )
        return True
    except Exception as e:
        print(f"Failed to send customer confirmation email: {e}")
        return False