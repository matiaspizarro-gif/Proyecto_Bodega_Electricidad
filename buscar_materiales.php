<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

require_once 'conexion.php';

$busqueda = isset($_GET['q']) ? trim($_GET['q']) : '';

if (strlen($busqueda) < 2) {
    echo json_encode([]);
    exit;
}

try {
    // Consulta a la tabla articulos vinculada con inventario_stock y ubicaciones
    $sql = "SELECT 
                a.id, 
                a.sku AS codigo, 
                a.nombre, 
                i.stock_disponible AS stock, 
                u.nombre AS ubicacion
            FROM articulos a
            LEFT JOIN inventario_stock i ON a.id = i.articulo_id
            LEFT JOIN ubicaciones u ON i.ubicacion_id = u.id
            WHERE (a.nombre LIKE :patron OR a.sku LIKE :patron)
            LIMIT 10";

    $stmt = $pdo->prepare($sql);
    $stmt->execute(['patron' => '%' . $busqueda . '%']);
    $materiales = $stmt->fetchAll();

    echo json_encode($materiales);
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['error' => $e->getMessage()]);
}
?>