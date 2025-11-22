🍽️ Django Developer Milestone Workflow
======================================
Restaurant Chatbot Backend (Admin + Subadmin + API Integration)

This document defines the milestone-wise workflow for the Django developer who will build the backend of the 
AI-powered Restaurant Chatbot System. The Django side will manage restaurant data, menu items, orders, and role-based 
access (Admin/Subadmin), and provide REST APIs to the FastAPI chatbot.

------------------------------------------------------------------
Milestone 1 – Project Setup & Database Design (6–8 hrs)
------------------------------------------------------------------
Goal: Initialize Django project, configure settings, and design database models.

Tasks:
• Create project and apps (accounts, restaurants, menu, orders)
• Configure database (SQLite/PostgreSQL) and run migrations
• Create models for Restaurant, MenuItem, Order, and custom User (Admin/Subadmin)

Deliverables:
• Django project setup with migrations and superuser created
• Database ready with all base models

------------------------------------------------------------------
Milestone 2 – Role-Based Access Control (6–8 hrs)
------------------------------------------------------------------
Goal: Implement Admin and Subadmin user roles with restricted access.

Tasks:
• Extend Django User model to include 'role' and 'restaurant' fields
• Create login/logout for both Admin and Subadmin panels
• Restrict menu/order visibility based on user role

Deliverables:
• Working role-based access system
• Subadmin linked to one restaurant
• Secure authentication

------------------------------------------------------------------
Milestone 3 – Admin Panel Customization (4–6 hrs)
------------------------------------------------------------------
Goal: Build a clean Admin dashboard for full system management.

Tasks:
• Customize Django admin for Restaurant, Menu, and Orders
• Add filtering, search, and inline editing
• Allow Admin to assign Subadmins to Restaurants

Deliverables:
• Fully functional Admin panel for managing all restaurants and data

------------------------------------------------------------------
Milestone 4 – Subadmin Panel (6–8 hrs)
------------------------------------------------------------------
Goal: Create Subadmin panel for managing their assigned restaurant.

Tasks:
• Create a separate /subadmin/ login and dashboard
• Restrict Subadmin data access to one restaurant
• Allow CRUD for Menu and Order management

Deliverables:
• Dedicated Subadmin panel with limited access

------------------------------------------------------------------
Milestone 5 – REST API for Chatbot Integration (5–7 hrs)
------------------------------------------------------------------
Goal: Create APIs for the FastAPI chatbot to fetch menus and post orders.

Tasks:
• Integrate Django REST Framework (DRF)
• Create serializers and endpoints:
  - GET /api/menu/<restaurant_id>/
  - POST /api/orders/
• Add token authentication (optional)

Deliverables:
• REST APIs working and connected to chatbot

------------------------------------------------------------------
Milestone 6 – Testing, Documentation & Integration (4–6 hrs)
------------------------------------------------------------------
Goal: Test entire backend, document setup, and verify chatbot integration.

Tasks:
• Test both Admin and Subadmin panels
• Test API endpoints with chatbot
• Write setup and API documentation
• Confirm Django ↔ FastAPI data flow

Deliverables:
• Stable, tested Django backend
• Integration verified with FastAPI chatbot
• Documentation ready

------------------------------------------------------------------
Final Summary
------------------------------------------------------------------
The Django developer will build and maintain the backend system responsible for managing restaurants, menus, 
orders, and user roles (Admin/Subadmin). They will develop REST APIs that the FastAPI chatbot uses to fetch menu data 
and post customer orders.

Total Estimated Time: 31–43 hours.









Goal: Build a system where

Super Admin → manages all restaurants & admins

Admin → manages only their own restaurant (menu + orders)

🧱 Step-by-Step Plan (Simple Language)
🟢 Step 1: Create Django Project

Make a new Django project (e.g. restaurant_backend).

Create 3 apps:

accounts → for users (superadmin/admin)

restaurants → for restaurant info

menu and orders → for menu items and orders.

Connect it to a database (SQLite for now).

🟢 Step 2: Create Custom User Model

Use Django’s AbstractUser.

Add a field role → values: superadmin, admin.

Add a field restaurant → links admin to their restaurant.

Example:

role = models.CharField(choices=[('superadmin','Super Admin'),('admin','Admin')])
restaurant = models.ForeignKey(Restaurant, null=True, blank=True)

🟢 Step 3: Create Restaurant Model

A restaurant has name, address, email, etc.

Each restaurant is linked to one admin.

admin = models.OneToOneField(User, limit_choices_to={'role': 'admin'})

🟢 Step 4: Create Menu and Orders Models

MenuItem → name, description, price, image, restaurant.

Order → restaurant, customer info, list of items, total price, status.

Both link to Restaurant.

🟢 Step 5: Add Role-Based Access

Super Admin: can see and manage everything.

Admin: can see/edit only their restaurant’s data.

Example in views:

if request.user.role == 'admin':
    queryset = MenuItem.objects.filter(restaurant=request.user.restaurant)

🟢 Step 6: Create Two Panels

Super Admin Panel (/superadmin/)

Can add/edit/delete restaurants.

Can create new Admin accounts and assign them restaurants.

Can view all orders and menus.

Admin Panel (/adminpanel/)

Can edit their restaurant details.

Can add/edit/delete menu items.

Can view and update order status.

(You can use Django Admin or build custom HTML templates.)

🟢 Step 7: Build APIs for the Chatbot

Use Django REST Framework (DRF).

GET /api/menu/<restaurant_id>/ → returns menu items.

POST /api/orders/ → chatbot sends new order.

Add authentication if needed (token-based).

🟢 Step 8: Connect with FastAPI Chatbot

FastAPI will call Django’s API:

To get menus and show them to users.

To create orders when a customer places one.

Django saves the data, and Admin can see it in their panel.

🟢 Step 9: Test Everything

Create one Super Admin → add 2 restaurants → assign each to an Admin.

Check that:

Admin1 sees only their menu/orders.

Super Admin sees everything.

Test chatbot requests via API.

🟢 Step 10: Document & Finalize

Write simple README:

How to run the project

How to create superadmin & admin

How FastAPI connects via API