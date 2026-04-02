-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Apr 02, 2026 at 12:35 PM
-- Server version: 10.4.28-MariaDB
-- PHP Version: 8.0.28

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `pashucare`
--

-- --------------------------------------------------------

--
-- Table structure for table `ai_predictions`
--

CREATE TABLE `ai_predictions` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `animal_id` int(11) DEFAULT NULL,
  `disease_name` varchar(255) NOT NULL,
  `confidence` varchar(50) NOT NULL,
  `status` varchar(50) NOT NULL,
  `symptoms_json` text DEFAULT NULL,
  `precautions_json` text DEFAULT NULL,
  `image_path` varchar(512) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `ai_predictions`
--

INSERT INTO `ai_predictions` (`id`, `user_id`, `animal_id`, `disease_name`, `confidence`, `status`, `symptoms_json`, `precautions_json`, `image_path`, `created_at`) VALUES
(1, 20, 37, 'Healthy', '98%', 'Normal', '[\"No symptoms detected\"]', '[\"Continue regular health checks\", \"Maintain vaccination schedule\"]', '/uploads/ai_images/911e5581-de8d-4881-8d13-d18944cd5c2e.jpg', '2026-04-02 10:31:55');

-- --------------------------------------------------------

--
-- Table structure for table `animals`
--

CREATE TABLE `animals` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `tag` varchar(100) NOT NULL,
  `breed` varchar(100) NOT NULL DEFAULT '',
  `age` varchar(100) DEFAULT '',
  `weight` varchar(100) DEFAULT '',
  `gender` varchar(100) DEFAULT 'Female',
  `status` enum('Healthy','Sick','Under Treatment') NOT NULL DEFAULT 'Healthy',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `animals`
--

INSERT INTO `animals` (`id`, `user_id`, `name`, `tag`, `breed`, `age`, `weight`, `gender`, `status`, `created_at`) VALUES
(36, 20, 'Bella', 'Cow-0123', 'Holstein', '4', '450', 'Female', 'Healthy', '2026-04-02 10:27:56'),
(37, 20, 'Hella', 'Cow000', 'Jersey', '5', '550', 'Male', 'Healthy', '2026-04-02 10:31:35');

-- --------------------------------------------------------

--
-- Table structure for table `calving_records`
--

CREATE TABLE `calving_records` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `animal_name` varchar(255) NOT NULL,
  `breeding_date` date NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `calving_records`
--

INSERT INTO `calving_records` (`id`, `user_id`, `animal_name`, `breeding_date`, `created_at`) VALUES
(13, 20, 'Yamuna', '2026-03-01', '2026-04-02 10:30:37');

-- --------------------------------------------------------

--
-- Table structure for table `farm_logs`
--

CREATE TABLE `farm_logs` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `type` varchar(20) NOT NULL,
  `date` date NOT NULL,
  `description` text NOT NULL,
  `animal_id` varchar(20) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `feeding_schedules`
--

CREATE TABLE `feeding_schedules` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `time` varchar(20) NOT NULL,
  `title` varchar(255) NOT NULL,
  `items_json` text NOT NULL,
  `is_completed` tinyint(1) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `feeding_schedules`
--

INSERT INTO `feeding_schedules` (`id`, `user_id`, `time`, `title`, `items_json`, `is_completed`, `created_at`) VALUES
(14, 20, '10:59', 'Morning', '[\"Concentrate\"]', 0, '2026-04-02 10:30:13');

-- --------------------------------------------------------

--
-- Table structure for table `feed_activity`
--

CREATE TABLE `feed_activity` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `item_name` varchar(255) NOT NULL,
  `amount_added` decimal(10,2) NOT NULL,
  `date` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `feed_activity`
--

INSERT INTO `feed_activity` (`id`, `user_id`, `item_name`, `amount_added`, `date`) VALUES
(35, 20, 'Concentrate', 500.00, '2026-04-02 10:29:45');

-- --------------------------------------------------------

--
-- Table structure for table `feed_entries`
--

CREATE TABLE `feed_entries` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `date` date NOT NULL,
  `feed_time` varchar(50) DEFAULT '',
  `feed_type` varchar(100) DEFAULT '',
  `target_group` varchar(100) DEFAULT '',
  `quantity` double DEFAULT 0,
  `notes` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `feed_entries`
--

INSERT INTO `feed_entries` (`id`, `user_id`, `date`, `feed_time`, `feed_type`, `target_group`, `quantity`, `notes`, `created_at`) VALUES
(28, 20, '2026-04-02', 'Afternoon', 'Concentrate', 'Buffalo', 100, '', '2026-04-02 10:29:55');

-- --------------------------------------------------------

--
-- Table structure for table `feed_stock`
--

CREATE TABLE `feed_stock` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `quantity` decimal(10,2) NOT NULL DEFAULT 0.00,
  `status` enum('Good','Medium','Low') NOT NULL DEFAULT 'Good',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `feed_stock`
--

INSERT INTO `feed_stock` (`id`, `user_id`, `name`, `quantity`, `status`, `created_at`) VALUES
(18, 20, 'Concentrate', 400.00, 'Medium', '2026-04-02 10:29:45');

-- --------------------------------------------------------

--
-- Table structure for table `health_records`
--

CREATE TABLE `health_records` (
  `id` int(11) NOT NULL,
  `animal_id` int(11) NOT NULL,
  `date` date NOT NULL,
  `title` varchar(255) NOT NULL,
  `status` varchar(100) NOT NULL DEFAULT 'Completed',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `doctor` varchar(255) DEFAULT NULL,
  `treatment` text DEFAULT NULL,
  `cost` decimal(10,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `milk_entries`
--

CREATE TABLE `milk_entries` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `milk_type` enum('Bulk Milk','Individual Milk') NOT NULL DEFAULT 'Bulk Milk',
  `date` date NOT NULL,
  `cattle_tag` varchar(100) DEFAULT '',
  `am` decimal(8,2) NOT NULL DEFAULT 0.00,
  `noon` decimal(8,2) NOT NULL DEFAULT 0.00,
  `pm` decimal(8,2) NOT NULL DEFAULT 0.00,
  `total_used` decimal(8,2) NOT NULL DEFAULT 0.00,
  `cow_milked_number` int(11) NOT NULL DEFAULT 0,
  `note` text DEFAULT '',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `milk_entries`
--

INSERT INTO `milk_entries` (`id`, `user_id`, `milk_type`, `date`, `cattle_tag`, `am`, `noon`, `pm`, `total_used`, `cow_milked_number`, `note`, `created_at`) VALUES
(29, 20, 'Bulk Milk', '2026-04-02', 'Cow-0123', 5.00, 2.00, 9.00, 5.00, 0, '', '2026-04-02 10:28:25'),
(30, 20, 'Individual Milk', '2026-04-02', 'Cow000', 6.00, 0.00, 5.00, 3.00, 0, '', '2026-04-02 10:33:47');

-- --------------------------------------------------------

--
-- Table structure for table `otp_codes`
--

CREATE TABLE `otp_codes` (
  `id` int(11) NOT NULL,
  `email_or_phone` varchar(255) NOT NULL,
  `otp_code` varchar(100) DEFAULT NULL,
  `context` varchar(50) NOT NULL,
  `expires_at` datetime NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `sanitation_scores`
--

CREATE TABLE `sanitation_scores` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `score` int(11) NOT NULL,
  `tasks_json` text DEFAULT NULL,
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `sanitation_scores`
--

INSERT INTO `sanitation_scores` (`id`, `user_id`, `score`, `tasks_json`, `updated_at`, `created_at`) VALUES
(23, 20, 100, '{\"Feeding Area\": true, \"Equipment Wash\": true, \"Water Troughs\": true, \"Shed Cleaning\": true, \"Footbath\": true, \"Waste Disposal\": true}', '2026-04-02 10:29:07', '2026-04-02 10:29:07');

-- --------------------------------------------------------

--
-- Table structure for table `transactions`
--

CREATE TABLE `transactions` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `category` enum('Income','Expense') NOT NULL,
  `date` date NOT NULL,
  `type` varchar(100) NOT NULL,
  `amount` decimal(12,2) NOT NULL,
  `receipt_no` varchar(100) DEFAULT '',
  `note` text DEFAULT '',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `transactions`
--

INSERT INTO `transactions` (`id`, `user_id`, `category`, `date`, `type`, `amount`, `receipt_no`, `note`, `created_at`) VALUES
(28, 20, 'Income', '2026-04-02', 'Category Income', 400000.00, 'Tab-123', '', '2026-04-02 10:30:56'),
(29, 20, 'Expense', '2026-04-02', 'Labour', 50000.00, 'Sen-09', '', '2026-04-02 10:31:11');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `full_name` varchar(255) NOT NULL,
  `email_or_phone` varchar(255) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `farm_name` varchar(255) NOT NULL DEFAULT '',
  `password_hash` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `full_name`, `email_or_phone`, `phone`, `farm_name`, `password_hash`, `created_at`) VALUES
(20, 'Tharun', 'tharunyadav973@gmail.com', '9876543210', 'green house farm', 'scrypt:32768:8:1$JBf4OL6XE8pgoVlK$84c19d5bf4f30db4fda172a5649667fa93106180981537162867905aaa2ff89b43facbdc2d9c5101400b9f4a9ddd4ad104e16f539b0f8bc9e45564d571befdd3', '2026-04-02 10:20:30');

-- --------------------------------------------------------

--
-- Table structure for table `vaccinations`
--

CREATE TABLE `vaccinations` (
  `id` int(11) NOT NULL,
  `animal_id` int(11) NOT NULL,
  `vaccine_name` varchar(255) NOT NULL,
  `date_given` date NOT NULL,
  `next_due_date` date DEFAULT NULL,
  `batch_number` varchar(100) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `visitors`
--

CREATE TABLE `visitors` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `purpose` varchar(255) DEFAULT '',
  `date` date NOT NULL,
  `entry_time` datetime NOT NULL,
  `outgoing_time` datetime NOT NULL,
  `person_to_meet` varchar(255) DEFAULT '',
  `vehicle_number` varchar(50) DEFAULT '',
  `notes` text DEFAULT '',
  `status` enum('Pending','Approved','Rejected','Checked In','Checked Out') NOT NULL DEFAULT 'Pending',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `visitors`
--

INSERT INTO `visitors` (`id`, `user_id`, `name`, `phone`, `purpose`, `date`, `entry_time`, `outgoing_time`, `person_to_meet`, `vehicle_number`, `notes`, `status`, `created_at`) VALUES
(15, 20, 'Dhanush', '9999999999', 'Milk collection', '2026-04-02', '2026-04-02 10:28:29', '2026-04-02 11:28:29', '', '', '', 'Pending', '2026-04-02 10:28:54'),
(16, 20, 'Tharun', '9876543210', 'Milk collection', '2026-04-02', '2026-04-02 10:34:22', '2026-04-02 10:34:22', '', '', '', 'Approved', '2026-04-02 10:34:13');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `ai_predictions`
--
ALTER TABLE `ai_predictions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `animal_id` (`animal_id`);

--
-- Indexes for table `animals`
--
ALTER TABLE `animals`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `calving_records`
--
ALTER TABLE `calving_records`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `farm_logs`
--
ALTER TABLE `farm_logs`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `feeding_schedules`
--
ALTER TABLE `feeding_schedules`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `feed_activity`
--
ALTER TABLE `feed_activity`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `feed_entries`
--
ALTER TABLE `feed_entries`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `feed_stock`
--
ALTER TABLE `feed_stock`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `health_records`
--
ALTER TABLE `health_records`
  ADD PRIMARY KEY (`id`),
  ADD KEY `animal_id` (`animal_id`);

--
-- Indexes for table `milk_entries`
--
ALTER TABLE `milk_entries`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `otp_codes`
--
ALTER TABLE `otp_codes`
  ADD PRIMARY KEY (`id`),
  ADD KEY `email_or_phone` (`email_or_phone`);

--
-- Indexes for table `sanitation_scores`
--
ALTER TABLE `sanitation_scores`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `transactions`
--
ALTER TABLE `transactions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email_or_phone` (`email_or_phone`);

--
-- Indexes for table `vaccinations`
--
ALTER TABLE `vaccinations`
  ADD PRIMARY KEY (`id`),
  ADD KEY `animal_id` (`animal_id`);

--
-- Indexes for table `visitors`
--
ALTER TABLE `visitors`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `ai_predictions`
--
ALTER TABLE `ai_predictions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `animals`
--
ALTER TABLE `animals`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=38;

--
-- AUTO_INCREMENT for table `calving_records`
--
ALTER TABLE `calving_records`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `farm_logs`
--
ALTER TABLE `farm_logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `feeding_schedules`
--
ALTER TABLE `feeding_schedules`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT for table `feed_activity`
--
ALTER TABLE `feed_activity`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=36;

--
-- AUTO_INCREMENT for table `feed_entries`
--
ALTER TABLE `feed_entries`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

--
-- AUTO_INCREMENT for table `feed_stock`
--
ALTER TABLE `feed_stock`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- AUTO_INCREMENT for table `health_records`
--
ALTER TABLE `health_records`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `milk_entries`
--
ALTER TABLE `milk_entries`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;

--
-- AUTO_INCREMENT for table `otp_codes`
--
ALTER TABLE `otp_codes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=82;

--
-- AUTO_INCREMENT for table `sanitation_scores`
--
ALTER TABLE `sanitation_scores`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24;

--
-- AUTO_INCREMENT for table `transactions`
--
ALTER TABLE `transactions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=30;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT for table `vaccinations`
--
ALTER TABLE `vaccinations`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `visitors`
--
ALTER TABLE `visitors`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `ai_predictions`
--
ALTER TABLE `ai_predictions`
  ADD CONSTRAINT `ai_predictions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `ai_predictions_ibfk_2` FOREIGN KEY (`animal_id`) REFERENCES `animals` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `animals`
--
ALTER TABLE `animals`
  ADD CONSTRAINT `animals_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `calving_records`
--
ALTER TABLE `calving_records`
  ADD CONSTRAINT `calving_records_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `feeding_schedules`
--
ALTER TABLE `feeding_schedules`
  ADD CONSTRAINT `feeding_schedules_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `feed_activity`
--
ALTER TABLE `feed_activity`
  ADD CONSTRAINT `feed_activity_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `feed_stock`
--
ALTER TABLE `feed_stock`
  ADD CONSTRAINT `feed_stock_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `health_records`
--
ALTER TABLE `health_records`
  ADD CONSTRAINT `health_records_ibfk_1` FOREIGN KEY (`animal_id`) REFERENCES `animals` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `milk_entries`
--
ALTER TABLE `milk_entries`
  ADD CONSTRAINT `milk_entries_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `transactions`
--
ALTER TABLE `transactions`
  ADD CONSTRAINT `transactions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `vaccinations`
--
ALTER TABLE `vaccinations`
  ADD CONSTRAINT `vaccinations_ibfk_1` FOREIGN KEY (`animal_id`) REFERENCES `animals` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `visitors`
--
ALTER TABLE `visitors`
  ADD CONSTRAINT `visitors_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
