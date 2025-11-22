# # chatbot/services.py
# from django.db import transaction
# from django.shortcuts import get_object_or_404

# from restaurants.models import Restaurant
# from menu.models import MenuItem
# from orders.models import Order, OrderItem
# from .engine import ChatbotResult


# def get_or_create_open_order(restaurant: Restaurant, session_id: str) -> Order:
#     order, _ = Order.objects.get_or_create(
#         restaurant=restaurant,
#         status=Order.OrderStatus.PENDING,
#         session_id=session_id,
#         defaults={
#             "order_type": Order.OrderType.TAKEAWAY,
#             "source": "chatbot",
#         },
#     )
#     return order


# def apply_intent(restaurant: Restaurant, session_id: str, result: ChatbotResult):
#     """
#     Takes ChatbotResult, performs DB actions, and returns (reply_text, order).
#     """
#     order = get_or_create_open_order(restaurant, session_id)

#     # 🔹 SHOW_CART (no DB changes, just read)
#     if result.intent == "SHOW_CART":
#         if not order.items.exists():
#             return "Your cart is empty.", order

#         lines = []
#         for item in order.items.select_related("menu_item"):
#             lines.append(f"{item.quantity} × {item.name} – ₹{item.total_price}")

#         reply = "Here is your cart:\n" + "\n".join(lines) + f"\nTotal: ₹{order.total}"
#         return reply, order

#     # 🔹 SHOW_MENU (read menu from DB)
#     if result.intent == "SHOW_MENU":
#         qs = MenuItem.objects.filter(restaurant=restaurant).order_by("category", "name")[:10]
#         if not qs:
#             return "This restaurant has no menu items yet.", order

#         lines = []
#         for m in qs:
#             lines.append(f"{m.id}) {m.name} – ₹{m.price}")

#         reply = (
#             "Here are some items on the menu:\n"
#             + "\n".join(lines)
#             + "\n\nUse 'add <id>' or 'add <id> x 2' to add to your cart."
#         )
#         return reply, order

#     # 🔹 HELP: no DB change
#     if result.intent == "HELP":
#         return result.reply, order

#     # 🔹 CLEAR_CART
#     if result.intent == "CLEAR_CART":
#         order.items.all().delete()
#         order.recalc_totals()
#         return result.reply + " Your cart is now empty.", order

#     # 🔹 CONFIRM_ORDER
#     if result.intent == "CONFIRM_ORDER":
#         if not order.items.exists():
#             return "Your cart is empty. Add some items before confirming.", order
#         order.status = Order.OrderStatus.CONFIRMED
#         order.save(update_fields=["status"])
#         return f"✅ Order #{order.id} confirmed! Total: ₹{order.total}", order

#     # 🔹 ADD_ITEM
#         # 🔹 ADD_ITEM (by id OR by name)
#     if result.intent == "ADD_ITEM":
#         # Decide how to find the menu item
#         if result.item_id is not None:
#             # Old behavior: by ID
#             menu_item = get_object_or_404(
#                 MenuItem,
#                 id=result.item_id,
#                 restaurant=restaurant,
#             )
#         elif result.item_name:
#             # NEW: by name
#             name_query = result.item_name.strip()
#             # Try exact match first
#             qs = MenuItem.objects.filter(
#                 restaurant=restaurant,
#                 name__iexact=name_query,
#             )
#             if not qs.exists():
#                 # Fallback: partial match
#                 qs = MenuItem.objects.filter(
#                     restaurant=restaurant,
#                     name__icontains=name_query,
#                 )

#             if not qs.exists():
#                 return (
#                     f"I couldn't find any dish matching '{name_query}'. "
#                     f"Try 'menu' to see available items.",
#                     order,
#                 )

#             # For now, just pick the first match
#             menu_item = qs.first()
#         else:
#             return (
#                 "I couldn't figure out which item to add. "
#                 "Try 'add 6 x 2' or 'add butter naan x 2'.",
#                 order,
#             )

#         with transaction.atomic():
#             oi, created = OrderItem.objects.get_or_create(
#                 order=order,
#                 menu_item=menu_item,
#                 defaults={
#                     "name": menu_item.name,
#                     "quantity": result.quantity,
#                     "unit_price": menu_item.price,
#                     "total_price": menu_item.price * result.quantity,
#                 },
#             )
#             if not created:
#                 oi.quantity += result.quantity
#                 oi.total_price = oi.unit_price * oi.quantity
#                 oi.save(update_fields=["quantity", "total_price"])

#             order.recalc_totals()

#         # Nice reply using actual name + total
#         reply = (
#             f"✅ Added {result.quantity} × {menu_item.name} to your cart.\n"
#             f"Current total: ₹{order.total}"
#         )
#         return reply, order

#         # 🔹 REMOVE_ITEM
#     if result.intent == "REMOVE_ITEM":
#         # If cart is empty already
#         if not order.items.exists():
#             return "Your cart is already empty.", order

#         try:
#             oi = OrderItem.objects.get(
#                 order=order,
#                 menu_item__id=result.item_id,
#             )
#         except OrderItem.DoesNotExist:
#             return "That item is not in your cart.", order

#         # Decide how much to remove
#         qty_to_remove = result.quantity

#         if qty_to_remove >= oi.quantity:
#             oi.delete()
#             msg = "Removed that item from your cart."
#         else:
#             oi.quantity -= qty_to_remove
#             oi.total_price = oi.unit_price * oi.quantity
#             oi.save(update_fields=["quantity", "total_price"])
#             msg = f"Removed {qty_to_remove} × {oi.name} from your cart."

#         order.recalc_totals()
#         msg += f" Current total: ₹{order.total}"
#         return msg, order


#     # 🔹 Fallback
#     return "I didn't understand what to do.", order
# chatbot/services.py (AI-powered version)
from django.db import transaction
from django.shortcuts import get_object_or_404

from restaurants.models import Restaurant
from menu.models import MenuItem
from orders.models import Order, OrderItem
from .engine import ChatbotResult


def get_or_create_open_order(restaurant: Restaurant, session_id: str) -> Order:
    """Get or create a pending order for this session."""
    order, _ = Order.objects.get_or_create(
        restaurant=restaurant,
        status=Order.OrderStatus.PENDING,
        session_id=session_id,
        defaults={
            "order_type": Order.OrderType.TAKEAWAY,
            "source": "chatbot",
        },
    )
    return order


def find_menu_item_by_name(restaurant: Restaurant, item_name: str) -> MenuItem:
    """
    Find MenuItem by name using fuzzy matching.
    Raises MenuItem.DoesNotExist if not found.
    """
    # Try exact match first
    try:
        return MenuItem.objects.get(
            restaurant=restaurant,
            name__iexact=item_name
        )
    except MenuItem.DoesNotExist:
        pass
    
    # Try contains match
    qs = MenuItem.objects.filter(
        restaurant=restaurant,
        name__icontains=item_name
    )
    
    if qs.exists():
        return qs.first()
    
    raise MenuItem.DoesNotExist(f"No menu item found matching: {item_name}")


def apply_intent(restaurant: Restaurant, session_id: str, result: ChatbotResult):
    """
    Takes ChatbotResult from AI engine, performs DB actions, returns (reply_text, order).
    """
    order = get_or_create_open_order(restaurant, session_id)

    # ============================================
    # SHOW_CART
    # ============================================
    if result.intent == "SHOW_CART":
        if not order.items.exists():
            return "Your cart is empty.", order

        lines = []
        for item in order.items.select_related("menu_item"):
            lines.append(f"{item.quantity} × {item.name} — ₹{item.total_price}")

        reply = "Here is your cart:\n" + "\n".join(lines) + f"\nTotal: ₹{order.total}"
        return reply, order

    # ============================================
    # SHOW_MENU
    # ============================================
    if result.intent == "SHOW_MENU":
        qs = MenuItem.objects.filter(
            restaurant=restaurant,
            available=True
        ).order_by("category", "name")[:15]
        
        if not qs:
            return "This restaurant has no menu items yet.", order

        lines = []
        current_category = None
        
        for m in qs:
            # Group by category
            if m.category != current_category:
                current_category = m.category
                lines.append(f"\n**{current_category}**")
            lines.append(f"• {m.name} — ₹{m.price}")

        reply = "Here's our menu:\n" + "\n".join(lines) + "\n\nJust tell me what you'd like to add!"
        return reply, order

    # ============================================
    # HELP
    # ============================================
    if result.intent == "HELP":
        return result.reply, order

    # ============================================
    # CLEAR_CART
    # ============================================
    if result.intent == "CLEAR_CART":
        order.items.all().delete()
        order.recalc_totals()
        return "✅ Your cart has been cleared.", order

    # ============================================
    # CONFIRM_ORDER
    # ============================================
    if result.intent == "CONFIRM_ORDER":
        if not order.items.exists():
            return "Your cart is empty. Add some items before confirming.", order
        
        order.status = Order.OrderStatus.CONFIRMED
        order.save(update_fields=["status"])
        
        return f"✅ Order #{order.id} confirmed! Total: ₹{order.total}\n\nThank you for your order!", order
    
    # ============================================
    # SEARCH_ITEM (semantic-only; reply already built in engine)
    # ============================================
    if result.intent == "SEARCH_ITEM":
        # No DB changes; just return the AI-built reply
        return result.reply, order

    # ============================================
    # ADD_ITEM (AI-powered with semantic search)
    # ============================================
    if result.intent == "ADD_ITEM":
        # result.item_name comes from semantic search in engine.py
        if not result.item_name:
            return "I couldn't figure out what to add. Try 'add butter naan' or 'menu'.", order
        
        try:
            # Find the actual MenuItem in the database
            menu_item = find_menu_item_by_name(restaurant, result.item_name)
        except MenuItem.DoesNotExist:
            # Suggest alternatives
            similar_items = MenuItem.objects.filter(
                restaurant=restaurant,
                name__icontains=result.item_name.split()[0]  # first word
            )[:3]
            
            if similar_items:
                suggestions = ", ".join([item.name for item in similar_items])
                return f"I couldn't find '{result.item_name}'. Did you mean: {suggestions}?", order
            else:
                return f"Sorry, '{result.item_name}' is not on our menu. Type 'menu' to see options.", order
        
        # Add to cart
        with transaction.atomic():
            oi, created = OrderItem.objects.get_or_create(
                order=order,
                menu_item=menu_item,
                defaults={
                    "name": menu_item.name,
                    "quantity": result.quantity,
                    "unit_price": menu_item.price,
                    "total_price": menu_item.price * result.quantity,
                },
            )
            
            if not created:
                oi.quantity += result.quantity
                oi.total_price = oi.unit_price * oi.quantity
                oi.save(update_fields=["quantity", "total_price"])

            order.recalc_totals()

        # Confidence-based reply
        confidence_emoji = "✅" if result.confidence > 0.7 else "👍"
        reply = (
            f"{confidence_emoji} Added {result.quantity} × {menu_item.name} to your cart.\n"
            f"Current total: ₹{order.total}"
        )
        return reply, order

    # ============================================
    # REMOVE_ITEM (AI-powered)
    # ============================================
    if result.intent == "REMOVE_ITEM":
        if not order.items.exists():
            return "Your cart is already empty.", order
        
        if not result.item_name:
            return "Which item would you like to remove?", order
        
        try:
            # Find menu item by name
            menu_item = find_menu_item_by_name(restaurant, result.item_name)
            
            # Find in current cart
            oi = OrderItem.objects.get(
                order=order,
                menu_item=menu_item,
            )
        except (MenuItem.DoesNotExist, OrderItem.DoesNotExist):
            return f"'{result.item_name}' is not in your cart.", order

        # Remove quantity
        qty_to_remove = result.quantity

        if qty_to_remove >= oi.quantity:
            oi.delete()
            msg = f"Removed {oi.name} from your cart."
        else:
            oi.quantity -= qty_to_remove
            oi.total_price = oi.unit_price * oi.quantity
            oi.save(update_fields=["quantity", "total_price"])
            msg = f"Removed {qty_to_remove} × {oi.name} from your cart."

        order.recalc_totals()
        msg += f" Current total: ₹{order.total}"
        return msg, order

    # ============================================
    # Fallback
    # ============================================
    return "I'm not sure what to do. Try 'menu', 'cart', 'add [item]', or 'confirm'.", order
