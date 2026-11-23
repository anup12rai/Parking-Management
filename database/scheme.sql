
CREATE DATABASE IF NOT EXISTS parking_management
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE parking_management;

-- 1. Admin and staff accounts
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'staff') DEFAULT 'admin',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Registered vehicles
CREATE TABLE vehicles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_number VARCHAR(30) NOT NULL UNIQUE,
    owner_name VARCHAR(120) NOT NULL,
    vehicle_type ENUM('bike', 'car', 'truck', 'other') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Parking slots
CREATE TABLE parking_slots (
    id INT AUTO_INCREMENT PRIMARY KEY,
    slot_number VARCHAR(20) NOT NULL UNIQUE,
    allowed_vehicle_type ENUM(
        'any', 'bike', 'car', 'truck', 'other'
    ) DEFAULT 'any',
    status ENUM(
        'available', 'occupied', 'maintenance'
    ) DEFAULT 'available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Parking entry and exit records
CREATE TABLE parking_records (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT NOT NULL,
    slot_id INT NOT NULL,
    entry_time DATETIME NOT NULL,
    exit_time DATETIME NULL,
    duration_minutes INT NULL,
    total_amount DECIMAL(10,2) NULL,
    status ENUM('active', 'completed') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
    FOREIGN KEY (slot_id) REFERENCES parking_slots(id),

    INDEX idx_record_status (status),
    INDEX idx_record_entry (entry_time)
);

-- 5. Parking prices
CREATE TABLE pricing (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_type ENUM(
        'bike', 'car', 'truck', 'other'
    ) NOT NULL UNIQUE,
    hourly_rate DECIMAL(10,2) NOT NULL
);

-- 6. Payment records
CREATE TABLE payments (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    record_id BIGINT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_method ENUM(
        'cash', 'card', 'online'
    ) DEFAULT 'cash',
    payment_status ENUM(
        'paid', 'pending', 'refunded'
    ) DEFAULT 'paid',
    paid_at DATETIME NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (record_id) REFERENCES parking_records(id)
);

-- Default hourly parking rates (NPR)
INSERT IGNORE INTO pricing (vehicle_type, hourly_rate)
VALUES
('bike', 20.00),
('car', 50.00),
('truck', 100.00),
('other', 30.00);

-- Initial parking slots
INSERT IGNORE INTO parking_slots
(slot_number, allowed_vehicle_type)
VALUES
('B-01', 'bike'),
('B-02', 'bike'),
('B-03', 'bike'),
('C-01', 'car'),
('C-02', 'car'),
('C-03', 'car'),
('A-01', 'any'),
('A-02', 'any');
