Project Requirements Document: ONEP E-Commerce Website

Project Overview
The ONEP website is a modern, feature-rich e-commerce platform designed to provide a seamless shopping experience for both buyers and sellers. With an emphasis on user-friendly navigation, sleek design, and scalability, ONEP aims to deliver an engaging online shopping experience. The website will be optimized for both desktop and mobile use, and will incorporate advanced technologies for performance, security, and ease of use.

Detailed Functional Requirements
The table below outlines the functional requirements for the ONEP e-commerce website:

| **Requirement ID** | **Description**                    | **User Story**                                                                                             | **Expected Behavior/Outcome**                                                                                                                                                                                               |
| ------------------ | ---------------------------------- | ---------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **FR001**          | **Creating a New User Account**    | As a user, I want to easily create an account to start shopping and track my orders.                       | The registration page should have a clean and modern design with fields for email, username, and password. It should also offer social media login options for quick registration.                                          |
| **FR002**          | **User Login**                     | As a user, I want to be able to log in using my account credentials or social media accounts.              | The login page should allow users to log in via email/password or social media accounts, with a smooth transition between light and dark modes.                                                                             |
| **FR003**          | **Product Browsing**               | As a user, I want to browse products across categories with high-quality images and product descriptions.  | The product listing page should display product images, descriptions, prices, and category filters. Smooth transitions between pages and hover effects should enhance the browsing experience.                              |
| **FR004**          | **Product Search**                 | As a user, I want to search for products using a search bar that provides instant suggestions and filters. | The search bar should offer suggestions as the user types, with the ability to filter products by price, rating, and category.                                                                                              |
| **FR005**          | **Product Details**                | As a user, I want to view detailed information about a product before making a purchase.                   | The product detail page should display a product image, description, price, and availability. It should also allow users to view reviews and add the product to the cart.                                                   |
| **FR006**          | **Adding Products to Cart**        | As a user, I want to be able to add products to my cart easily and view them later.                        | The "Add to Cart" button should visually confirm the action, and the cart icon should dynamically update. Users should be able to view items in their cart, including prices and quantities.                                |
| **FR007**          | **Viewing the Cart**               | As a user, I want to see the items in my cart and adjust quantities or remove products before checkout.    | The cart page should show a list of added products with options to modify quantity or remove items. Real-time price updates should be displayed as users adjust quantities.                                                 |
| **FR008**          | **Checkout Process**               | As a user, I want to complete my purchase quickly and securely through an easy checkout process.           | The checkout page should collect shipping information and allow users to choose payment options (e.g., bank transfer). The system should show a temporary message indicating that payment integration is under development. |
| **FR009**          | **Order Confirmation**             | As a user, I want to receive an order confirmation after completing my purchase.                           | After completing the checkout process, the system should display a confirmation page with order details, tracking information, and a summary of the transaction.                                                            |
| **FR010**          | **Order History**                  | As a user, I want to view my previous orders and track their statuses.                                     | The user profile should include an order history page that lists all previous orders, with detailed status and the option to track shipments.                                                                               |
| **FR011**          | **Product Reviews and Ratings**    | As a user, I want to rate and review the products I have purchased.                                        | The product page should allow users to submit star ratings and written reviews. Reviews will influence the visibility of products.                                                                                          |
| **FR012**          | **Wishlist Functionality**         | As a user, I want to be able to add products to my wishlist for future purchase.                           | The system should allow users to add products to their wishlist and view them later. The wishlist should be visible in the user profile.                                                                                    |
| **FR013**          | **Admin Panel**                    | As an admin, I want to manage products, users, and orders efficiently through a dynamic admin panel.       | The admin panel should feature live updates of orders, product stock, and user activity logs. It should also allow admins to delete or update user accounts and product details.                                            |
| **FR014**          | **Product Management by Seller**   | As a seller, I want to add, edit, or delete products and manage orders.                                    | Sellers should have access to a dashboard to manage their product listings, including descriptions, prices, stock quantities, and images.                                                                                   |
| **FR015**          | **Secure Payment System**          | As a user, I want to ensure my payment details are securely processed during checkout.                     | The checkout page should provide a secure payment system with visual feedback showing encryption and supported payment methods (bank transfer, future integrations with payment gateways).                                  |
| **FR016**          | **Product Filtering and Sorting**  | As a user, I want to filter and sort products by attributes like price, rating, and category.              | The product list page should have a filtering system with multi-attribute options and sorting by price, popularity, and rating.                                                                                             |
| **FR017**          | **Push Notifications for Updates** | As a user, I want to receive notifications about order status, discounts, and new products.                | The system should send push notifications for order updates, promotional offers, and new arrivals in the store.                                                                                                             |
| **FR018**          | **Discounts and Coupons**          | As a user, I want to apply discount codes to my purchases.                                                 | The checkout page should allow users to enter discount codes, and the system should provide real-time validation and feedback about code applicability.                                                                     |
| **FR019**          | **Shipping and Tracking**          | As a user, I want to track my orders after they have been shipped.                                         | The user profile should include a tracking page showing the current status of the order, with real-time updates fetched from shipping providers.                                                                            |
| **FR020**          | **Admin User Management**          | As an admin, I want to manage user roles and deactivate accounts if necessary.                             | The admin panel should allow admins to view, update, and deactivate user accounts, with role-based permissions for users.                                                                                                   |



Technologies Used
Frontend Technologies:
HTML: For the structure of the website’s content and layout.

CSS (via Bootstrap): For designing responsive and modern user interfaces with mobile-first approaches.

JavaScript (if necessary): To add dynamic functionality, including pop-ups, form validation, and interactive elements.

Backend Technologies:
Django: A powerful and scalable backend framework used for managing users, products, orders, and all backend logic.

Views: For rendering dynamic HTML pages based on data from the database.

Models: For defining and interacting with the PostgreSQL database (products, users, orders, etc.).

Django Auth (Authentication): For secure user management and registration.

Django REST Framework (if required): For creating APIs that can be consumed by frontend JavaScript (e.g., for real-time product updates or search functionality).

Database:
PostgreSQL: A scalable and robust relational database to store products, users, orders, reviews, and other essential data.

Tables: products, orders, users, order_items, reviews, etc.

File Structure and Configuration
Frontend Files:
HTML Files:

signup.html – For user registration.

login.html – For user login.

product_list.html – Displays a list of products.

product_detail.html – Displays detailed information about a single product.

cart.html – Displays the shopping cart and allows quantity adjustments.

checkout.html – Allows the user to enter payment details (temporarily inactive).

order_confirmation.html – Displays the order confirmation page.

order_history.html – Displays the user's past orders.

CSS Files:

style.css – For custom styling.

Bootstrap: Integrated for responsive layouts and common UI components.

JavaScript Files:

main.js – For handling client-side validation, dynamic product filtering, and other interactions.

Backend (Django Files):
views.py:

Functions for rendering the HTML pages (signup_view, login_view, product_list_view, product_detail_view, checkout_view, order_confirmation_view, etc.).

models.py:

Define database tables (Product, Order, User, Review, Cart, etc.).

forms.py:

Define forms for user registration, login, and product filtering.

Database Setup (PostgreSQL):
SQL Tables:

users: Stores user data (handled by Django’s built-in user model).

products: Stores product details (name, description, price, stock).

orders: Stores orders and user connections.

order_items: Stores individual products within an order.

reviews: Stores user reviews for products.

File and Folder Structure
The following is a suggested folder structure for your project:

onep/
├── onep/
│   ├── migrations/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── templates/
│       ├── signup.html
│       ├── login.html
│       ├── product_list.html
│       ├── product_detail.html
│       ├── cart.html
│       ├── checkout.html
│       ├── order_confirmation.html
│       ├── order_history.html
│       └── base.html
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── images/
│       └── product_images/
├── db/
│   └── postgres/
│       └── onep_db.sql
└── manage.py

Conclusion
This detailed requirements document and technology stack outlines the flow of the ONEP e-commerce website, covering both frontend and backend aspects, including database structure and file management. By using Django for the backend, HTML/CSS for the frontend, and PostgreSQL for data storage, this design will create a scalable and modern e-commerce platform. It should be in Turkish Language.