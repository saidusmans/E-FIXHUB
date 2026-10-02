<?php
// Database configuration
$host = 'localhost';
$db_name = 'efixhub';
$username = 'root';
$password = '';

try {
    $pdo = new PDO("mysql:host=$host;dbname=$db_name", $username, $password);
    // Set the PDO error mode to exception
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
} catch(PDOException $e) {
    die("ERROR: Could not connect. " . $e->getMessage());
}

// Global utility functions
function log_activity($user_id, $action) {
    global $pdo;
    $stmt = $pdo->prepare("INSERT INTO activity_logs (user_id, action) VALUES (?, ?)");
    $stmt->execute([$user_id, $action]);
}

function is_logged_in() {
    return isset($_SESSION['user_id']);
}

function check_role($roles) {
    if (!isset($_SESSION['role']) || !in_array($_SESSION['role'], (array)$roles)) {
        header("Location: ../auth/login.php?error=unauthorized");
        exit;
    }
}
?>
