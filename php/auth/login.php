<?php
session_start();
require_once '../config/db.php';

$error = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['username'];
    $password = $_POST['password'];

    $stmt = $pdo->prepare("SELECT * FROM users WHERE username = ?");
    $stmt->execute([$username]);
    $user = $stmt->fetch();

    if ($user && password_verify($password, $user['password'])) {
        $_SESSION['user_id'] = $user['id'];
        $_SESSION['username'] = $user['username'];
        $_SESSION['role'] = $user['role'];
        
        log_activity($user['id'], "User logged in successfully");
        
        header("Location: ../dashboards/" . strtolower($user['role']) . ".php");
        exit;
    } else {
        $error = "Invalid credentials";
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Login | E-Fix Hub</title>
    <style>
        body { background: #020617; color: white; display: flex; justify-content: center; align-items: center; height: 100vh; font-family: sans-serif; }
        .login-card { background: #1e293b; padding: 3rem; border-radius: 1.5rem; border: 1px solid #334155; width: 100%; max-width: 400px; text-align: center; }
        h2 { color: #10b981; margin-bottom: 2rem; }
        input { width: 100%; padding: 1rem; margin-bottom: 1rem; border-radius: 0.5rem; border: 1px solid #334155; background: #0f172a; color: white; }
        button { background: #10b981; color: #020617; width: 100%; padding: 1rem; border-radius: 0.5rem; border: none; font-weight: 700; cursor: pointer; }
        .error { color: #ef4444; margin-bottom: 1rem; font-size: 0.9rem; }
    </style>
</head>
<body>
    <div class="login-card">
        <h2>LOGIN</h2>
        <?php if($error): ?><div class="error"><?php echo $error; ?></div><?php endif; ?>
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Access Hub</button>
        </form>
        <p style="margin-top: 2rem; color: #94a3b8; font-size: 0.8rem;">Don't have an account? <a href="register.php" style="color: #10b981;">Register here</a></p>
    </div>
</body>
</html>
