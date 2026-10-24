<?php

// ===== KẾT NỐI DATABASE =====
$conn = new mysqli("localhost", "root", "", "tool_keys");

if ($conn->connect_error) {
    die("db_error");
}


// ===== ANTI SPAM API =====
$ip = $_SERVER['REMOTE_ADDR'];

$check = $conn->prepare("SELECT * FROM api_log WHERE ip=? AND time > (NOW() - INTERVAL 2 SECOND)");
$check->bind_param("s", $ip);
$check->execute();

if ($check->get_result()->num_rows > 0) {
    echo "spam";
    exit;
}

$conn->query("INSERT INTO api_log(ip) VALUES('$ip')");


// ===== LẤY KEY TỪ REQUEST =====
$key = $_GET['key'] ?? '';

if ($key == "") {
    echo "no_key";
    exit;
}


// ===== TÌM KEY =====
$stmt = $conn->prepare("SELECT * FROM license_keys WHERE license_key = ?");
$stmt->bind_param("s", $key);
$stmt->execute();

$result = $stmt->get_result();

if ($result->num_rows == 0) {
    echo "invalid";
    exit;
}

$row = $result->fetch_assoc();


// ===== KIỂM TRA LOCK =====
if ($row['status'] == 'locked') {
    echo "locked";
    exit;
}


// ===== KIỂM TRA HẾT HẠN =====
if (!$row['is_permanent']) {

    if ($row['expire_at'] != NULL) {

        if (strtotime($row['expire_at']) < time()) {

            $update = $conn->prepare("UPDATE license_keys SET status='expired' WHERE id=?");
            $update->bind_param("i", $row['id']);
            $update->execute();

            echo "expired";
            exit;
        }

    }

}


// ===== KIỂM TRA SỐ THIẾT BỊ =====
$key_id = $row['id'];

$device = $conn->prepare("SELECT COUNT(*) as total FROM key_devices WHERE key_id=?");
$device->bind_param("i", $key_id);
$device->execute();

$count = $device->get_result()->fetch_assoc()['total'];

if ($count >= $row['max_devices']) {
    echo "device_full";
    exit;
}


// ===== KEY HỢP LỆ =====
echo "valid";

?>