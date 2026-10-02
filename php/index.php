<?php
session_start();
require_once 'config/db.php';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-Fix Hub | Refurbishment Marketplace</title>
    <style>
        :root {
            --primary: #0f172a;
            --accent: #10b981;
            --text-light: #f8fafc;
            --bg-dark: #020617;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', system-ui, sans-serif; }
        body { background: var(--bg-dark); color: var(--text-light); overflow-x: hidden; }
        .hero {
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            background: radial-gradient(circle at center, #1e293b 0%, var(--bg-dark) 100%);
            padding: 2rem;
        }
        h1 { font-size: 4rem; font-weight: 800; letter-spacing: -0.05em; margin-bottom: 1rem; color: var(--accent); }
        p { font-size: 1.25rem; max-width: 600px; color: #94a3b8; line-height: 1.6; margin-bottom: 2rem; }
        .nav { position: fixed; top: 0; width: 100%; padding: 1.5rem 2rem; display: flex; justify-content: space-between; align-items: center; z-index: 100; backdrop-filter: blur(10px); }
        .logo { font-size: 1.5rem; font-weight: 700; color: var(--accent); text-decoration: none; }
        .nav-links a { color: var(--text-light); text-decoration: none; margin-left: 2rem; font-weight: 500; transition: color 0.3s; }
        .nav-links a:hover { color: var(--accent); }
        .btn {
            background: var(--accent);
            color: var(--bg-dark);
            padding: 0.75rem 2rem;
            border-radius: 9999px;
            text-decoration: none;
            font-weight: 700;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .btn:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(16, 185, 129, 0.2); }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; padding: 4rem 2rem; max-width: 1200px; margin: 0 auto; }
        .card { background: #1e293b; padding: 2rem; border-radius: 1.5rem; border: 1px solid #334155; }
        .card h3 { margin-bottom: 1rem; font-size: 1.5rem; }
        .card p { font-size: 1rem; }
    </style>
</head>
<body>
    <nav class="nav">
        <a href="index.php" class="logo">E-FIX HUB</a>
        <div class="nav-links">
            <a href="#features">Features</a>
            <a href="refurbished_store.php">Store</a>
            <?php if(is_logged_in()): ?>
                <a href="dashboards/<?php echo strtolower($_SESSION['role']); ?>.php" class="btn">Dashboard</a>
            <?php else: ?>
                <a href="auth/login.php">Login</a>
                <a href="auth/register.php" class="btn">Get Started</a>
            <?php endif; ?>
        </div>
    </nav>

    <section class="hero">
        <h1>Transforming E-Waste into Excellence</h1>
        <p>A professional refurbishment marketplace connecting sustainable customers with expert restoration technical hubs.</p>
        <div class="cta">
            <a href="auth/register.php" class="btn">Join the Ecosystem</a>
        </div>
    </section>

    <div id="features" class="grid">
        <div class="card">
            <h3>Precision Logistics</h3>
            <p>Verified agents handle product collection and delivery with real-time status updates and chain-of-custody tracking.</p>
        </div>
        <div class="card">
            <h3>Expert Restoration</h3>
            <p>Certified mechanics utilize advanced engineering protocols to breathe new life into damaged electronic assets.</p>
        </div>
        <div class="card">
            <h3>Certified Store</h3>
            <p>Purchase enterprise-grade refurbished hardware with detailed condition ratings and professional verification.</p>
        </div>
    </div>

    <script>
        console.log("E-Fix Hub - System Initialized");
    </script>
</body>
</html>
