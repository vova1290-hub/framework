-- Запросы к data/offers.sqlite.
-- В сайте значения от пользователя передаются через знак ?, не через склейку текста.

-- 1. Список клиентов.
SELECT id, name
FROM clients
ORDER BY name;

-- 2. Список менеджеров.
SELECT id, name
FROM managers
ORDER BY name;

-- 3. Согласованные предложения.
SELECT id, number, status
FROM proposals
WHERE status = 'Согласовано';

-- 4. Отменённые предложения.
SELECT id, number, status
FROM proposals
WHERE status = 'Отменено';

-- 5. Предложение и название клиента.
SELECT
    proposals.number,
    clients.name AS client_name
FROM proposals
JOIN clients ON proposals.client_id = clients.id;

-- 6. Предложение, клиент и менеджер.
SELECT
    proposals.number,
    clients.name AS client_name,
    managers.name AS manager_name
FROM proposals
JOIN clients ON proposals.client_id = clients.id
JOIN managers ON proposals.manager_id = managers.id;

-- 7. Сколько всего предложений.
SELECT COUNT(*) AS proposals_count
FROM proposals;

-- 8. Сколько действующих предложений. Отменённые не считаются.
SELECT COUNT(*) AS active_count
FROM proposals
WHERE status != 'Отменено';

-- 9. Сколько предложений у каждого клиента. Клиент без предложений тоже виден.
SELECT
    clients.name AS client_name,
    COUNT(proposals.id) AS proposals_count
FROM clients
LEFT JOIN proposals ON proposals.client_id = clients.id
GROUP BY clients.id, clients.name
ORDER BY proposals_count DESC;

-- 10. Сколько предложений каждого статуса.
SELECT
    status,
    COUNT(*) AS proposals_count
FROM proposals
GROUP BY status;

-- 11. Менеджеры, у которых больше одного предложения.
SELECT
    managers.name AS manager_name,
    COUNT(proposals.id) AS proposals_count
FROM managers
JOIN proposals ON proposals.manager_id = managers.id
GROUP BY managers.id, managers.name
HAVING COUNT(proposals.id) > 1;

-- 12. Клиенты, у которых сумма предложений больше 100000.
SELECT
    clients.name AS client_name,
    SUM(proposals.amount) AS total_amount
FROM clients
JOIN proposals ON proposals.client_id = clients.id
GROUP BY clients.id, clients.name
HAVING SUM(proposals.amount) > 100000;

-- 13. Предложения, в срок которых входит дата 2026-09-27.
SELECT
    proposals.number,
    clients.name AS client_name,
    proposals.created_date
FROM proposals
JOIN clients ON proposals.client_id = clients.id
WHERE date('2026-09-27') >= date(proposals.created_date)
    AND date('2026-09-27') <= date(
        proposals.created_date,
        '+' || proposals.validity_days || ' days'
    )
ORDER BY proposals.id;
