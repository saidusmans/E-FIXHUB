-- E-Fix Hub Database Schema
CREATE DATABASE IF NOT EXISTS efixhub;
USE efixhub;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('Admin', 'Customer', 'Agent', 'Mechanic') NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Profiles for different roles
CREATE TABLE IF NOT EXISTS customer_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS agent_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    qualification VARCHAR(255),
    experience INT DEFAULT 0,
    verification_status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
    is_available BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mechanic_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    specialization VARCHAR(100),
    qualification VARCHAR(255),
    workshop_address TEXT,
    verification_status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Damaged Products (submitted by customers)
CREATE TABLE IF NOT EXISTS damaged_products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uploaded_by INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    image_path VARCHAR(255),
    condition_description TEXT,
    status ENUM(
        'uploaded',
        'inspection_pending',
        'agent_assigned',
        'collected',
        'mechanic_assigned',
        'repairing',
        'repair_completed',
        'awaiting_admin_approval',
        'published_in_store',
        'ordered',
        'delivery_assigned',
        'delivered'
    ) DEFAULT 'uploaded',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE CASCADE
);

-- Product Assignments (tracking which agent/mechanic is handling what)
CREATE TABLE IF NOT EXISTS product_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    agent_id INT, -- For collection
    mechanic_id INT, -- For repair
    collection_agent_id INT, -- Redundant but explicit
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES damaged_products(id) ON DELETE CASCADE,
    FOREIGN KEY (agent_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (mechanic_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Repair Reports (Technical details)
CREATE TABLE IF NOT EXISTS repair_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    mechanic_id INT NOT NULL,
    repair_notes TEXT,
    repair_progress INT DEFAULT 0, -- 0 to 100
    cost DECIMAL(10, 2) DEFAULT 0.00,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (product_id) REFERENCES damaged_products(id) ON DELETE CASCADE,
    FOREIGN KEY (mechanic_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Refurbished Products (Marketplace ready)
CREATE TABLE IF NOT EXISTS refurbished_products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    condition_rating TINYINT DEFAULT 5, -- 1-5 scale
    description TEXT,
    is_published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES damaged_products(id) ON DELETE CASCADE
);

-- Orders
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    buyer_id INT NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    status ENUM('ordered', 'delivery_assigned', 'shipped', 'delivered', 'cancelled') DEFAULT 'ordered',
    payment_method VARCHAR(50) DEFAULT 'Online',
    shipping_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES refurbished_products(id) ON DELETE CASCADE,
    FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Delivery Tasks
CREATE TABLE IF NOT EXISTS delivery_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    agent_id INT NOT NULL,
    status ENUM('assigned', 'picked_up', 'out_for_delivery', 'delivered') DEFAULT 'assigned',
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivered_at TIMESTAMP NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (agent_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Activity Logs
CREATE TABLE IF NOT EXISTS activity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);
