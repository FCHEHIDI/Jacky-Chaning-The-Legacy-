-- state.sql — Project Jacky state dump
-- Generated: 2026-07-01T12:08:33
-- Source of truth: state.db  (excluded from git via .gitignore)
-- Restore with: python scripts/state.py import sql
-- Or:           make state-restore

PRAGMA foreign_keys=OFF;

-- phases (7 rows)
DELETE FROM phases;
INSERT INTO phases (id, name, status, started_at, completed_at) VALUES ('1', 'survey', 'completed', '2026-06-20T15:45:31.206029', '2026-06-20T15:47:47.249020');
INSERT INTO phases (id, name, status, started_at, completed_at) VALUES ('2', 'map', 'completed', NULL, '2026-06-21T11:50:43.929449');
INSERT INTO phases (id, name, status, started_at, completed_at) VALUES ('3', 'audit', 'completed', NULL, '2026-06-26T11:51:53.750868');
INSERT INTO phases (id, name, status, started_at, completed_at) VALUES ('4', 'draft', 'completed', NULL, '2026-07-01T12:08:32.795019');
INSERT INTO phases (id, name, status, started_at, completed_at) VALUES ('5', 'stabilize', 'not_started', NULL, NULL);
INSERT INTO phases (id, name, status, started_at, completed_at) VALUES ('6', 'derive', 'not_started', NULL, NULL);
INSERT INTO phases (id, name, status, started_at, completed_at) VALUES ('7', 'extend', 'not_started', NULL, NULL);

-- decisions (0 rows)
DELETE FROM decisions;

-- smells (22 rows)
DELETE FROM smells;
INSERT INTO smells (id, name, location, severity, status, fixed_in, fixed_at, created_at) VALUES ('1', 'SQL injection', 'get_tasks query builder', 'critical', 'open', NULL, NULL, '2026-06-20 11:43:10');
INSERT INTO smells (id, name, location, severity, status, fixed_in, fixed_at, created_at) VALUES ('2', 'MD5 password', 'register route', 'critical', 'open', NULL, NULL, '2026-06-20 11:43:11');
INSERT INTO smells (id, name, location, severity, status, fixed_in, fixed_at, created_at) VALUES ('3', 'Global DB connection', 'module level conn', 'critical', 'open', NULL, NULL, '2026-06-20 11:43:11');
INSERT INTO smells (id, name, location, severity, status, fixed_in, fixed_at, created_at) VALUES ('4', 'Hardcoded secret key', 'app.secret_key', 'critical', 'open', NULL, NULL, '2026-06-20 11:43:11');
INSERT INTO smells (id, name, location, severity, status, fixed_in, fixed_at, created_at) VALUES ('5', 'Admin routes no auth', '/admin/users /admin/reset', 'critical', 'open', NULL, NULL, '2026-06-20 11:43:12');
INSERT INTO smells (id, name, location, severity, status, fixed_in, fixed_at, created_at) VALUES ('6', 'SQL Injection - register/login', 'register() l.74, login() l.88', 'critical', 'open', NULL, NULL, '2026-06-20 15:45:55');
INSERT INTO smells (id, name, location, severity, status, fixed_in, fixed_at, created_at) VALUES ('7', 'SQL Injection - projects CRUD', 'create_project() l.135/138, delete_project() l.150/151', 'critical', 'open', NULL, NULL, '2026-06-20 15:45:55');
INSERT INTO smells (id, name, location, severity, status, fixed_in, fixed_at, created_at) VALUES ('8', 'SQL Injection - tasks CRUD', 'get_tasks() l.167-173, create_task() l.210/214, update_task() l.231-245, delete_task() l.255', 'critical', 'open', NULL, NULL, '2026-06-20 15:45:55');
INSERT INTO smells (id, name, location, severity, status, fixed_in, fixed_at, created_at) VALUES ('9', 'SQL Injection - comments/search', 'get_comments() l.265, add_comment() l.277, search() l.318-322', 'critical', 'open', NULL, NULL, '2026-06-20 15:45:56');
INSERT INTO smells (id, name, location, severity, status, fixed_in, fixed_at, created_at) VALUES ('10', 'Hardcoded secret key', 'app.secret_key l.14', 'critical', 'open', NULL, NULL, '2026-06-20 15:45:56');
INSERT INTO smells (id, name, location, severity, status, fixed_in, fixed_at, created_at) VALUES ('11', 'MD5 password hashing', 'register() l.70, login() l.86', 'critical', 'open', NULL, NULL, '2026-06-20 15:45:56');
INSERT INTO smells (id, name, location, severity, status, fixed_in, fixed_at, created_at) VALUES ('12', 'Admin routes without auth', '/admin/users l.329, /admin/reset l.338', 'critical', 'open', NULL, NULL, '2026-06-20 15:45:56');
INSERT INTO smells (id, name, location, severity, status, fixed_in, fixed_at, created_at) VALUES ('13', 'Global DB connection check_same_thread=False', 'module level l.20', 'critical', 'open', NULL, NULL, '2026-06-20 15:45:56');
INSERT INTO smells (id, name, location, severity, status, fixed_in, fixed_at, created_at) VALUES ('14', 'Comments GET without auth', 'get_comments() l.264', 'high', 'open', NULL, NULL, '2026-06-20 15:45:57');
INSERT INTO smells (id, name, location, severity, status, fixed_in, fixed_at, created_at) VALUES ('15', 'Bare except clauses', 'register() l.77, get_tasks() l.182', 'high', 'open', NULL, NULL, '2026-06-20 15:45:57');
INSERT INTO smells (id, name, location, severity, status, fixed_in, fixed_at, created_at) VALUES ('16', 'print() used as logging', 'init_db() l.59, create_task() l.221', 'medium', 'open', NULL, NULL, '2026-06-20 15:45:57');
INSERT INTO smells (id, name, location, severity, status, fixed_in, fixed_at, created_at) VALUES ('17', 'No input validation', 'all POST/PUT routes', 'high', 'open', NULL, NULL, '2026-06-20 15:45:57');
INSERT INTO smells (id, name, location, severity, status, fixed_in, fixed_at, created_at) VALUES ('18', 'God module - monolithic app.py', 'entire file l.1-368', 'high', 'open', NULL, NULL, '2026-06-20 15:45:58');
INSERT INTO smells (id, name, location, severity, status, fixed_in, fixed_at, created_at) VALUES ('19', 'Raw SQL column index access', 'all SELECT handlers', 'high', 'open', NULL, NULL, '2026-06-20 15:45:58');
INSERT INTO smells (id, name, location, severity, status, fixed_in, fixed_at, created_at) VALUES ('20', 'File write without path sanitization in export', 'export_data() l.360', 'medium', 'open', NULL, NULL, '2026-06-20 15:45:58');
INSERT INTO smells (id, name, location, severity, status, fixed_in, fixed_at, created_at) VALUES ('21', 'reset_db wipes all data with no confirmation', '/admin/reset l.337-344', 'critical', 'open', NULL, NULL, '2026-06-20 15:45:58');
INSERT INTO smells (id, name, location, severity, status, fixed_in, fixed_at, created_at) VALUES ('22', 'No soft delete / no audit trail', 'delete_project() l.143, delete_task() l.251', 'medium', 'open', NULL, NULL, '2026-06-20 15:45:58');

-- metrics (4 rows)
DELETE FROM metrics;
INSERT INTO metrics (id, phase, key, value, unit, recorded_at) VALUES ('1', 'unknown', 'snapshot_smells_open', '22.0', NULL, '2026-06-21T11:49:29.218613');
INSERT INTO metrics (id, phase, key, value, unit, recorded_at) VALUES ('2', 'unknown', 'snapshot_smells_fixed', '0.0', NULL, '2026-06-21T11:49:29.218613');
INSERT INTO metrics (id, phase, key, value, unit, recorded_at) VALUES ('3', 'unknown', 'snapshot_smells_open', '22.0', NULL, '2026-06-21T11:49:38.158138');
INSERT INTO metrics (id, phase, key, value, unit, recorded_at) VALUES ('4', 'unknown', 'snapshot_smells_fixed', '0.0', NULL, '2026-06-21T11:49:38.158138');

-- session_log (39 rows)
DELETE FROM session_log;
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('1', 'RISK', 'Smell catalogued: SQL injection @ get_tasks query builder (critical)', 'survey', '2026-06-20 11:43:10');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('2', 'RISK', 'Smell catalogued: MD5 password @ register route (critical)', 'survey', '2026-06-20 11:43:11');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('3', 'RISK', 'Smell catalogued: Global DB connection @ module level conn (critical)', 'survey', '2026-06-20 11:43:11');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('4', 'RISK', 'Smell catalogued: Hardcoded secret key @ app.secret_key (critical)', 'survey', '2026-06-20 11:43:11');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('5', 'RISK', 'Smell catalogued: Admin routes no auth @ /admin/users /admin/reset (critical)', 'survey', '2026-06-20 11:43:12');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('6', 'INFO', 'Phase ''survey'' → in_progress', 'survey', '2026-06-20 15:44:57');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('7', 'INFO', 'Phase ''survey'' → in_progress', 'survey', '2026-06-20 15:45:31');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('8', 'RISK', 'Smell catalogued: SQL Injection - register/login @ register() l.74, login() l.88 (critical)', 'survey', '2026-06-20 15:45:55');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('9', 'RISK', 'Smell catalogued: SQL Injection - projects CRUD @ create_project() l.135/138, delete_project() l.150/151 (critical)', 'survey', '2026-06-20 15:45:55');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('10', 'RISK', 'Smell catalogued: SQL Injection - tasks CRUD @ get_tasks() l.167-173, create_task() l.210/214, update_task() l.231-245, delete_task() l.255 (critical)', 'survey', '2026-06-20 15:45:55');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('11', 'RISK', 'Smell catalogued: SQL Injection - comments/search @ get_comments() l.265, add_comment() l.277, search() l.318-322 (critical)', 'survey', '2026-06-20 15:45:56');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('12', 'RISK', 'Smell catalogued: Hardcoded secret key @ app.secret_key l.14 (critical)', 'survey', '2026-06-20 15:45:56');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('13', 'RISK', 'Smell catalogued: MD5 password hashing @ register() l.70, login() l.86 (critical)', 'survey', '2026-06-20 15:45:56');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('14', 'RISK', 'Smell catalogued: Admin routes without auth @ /admin/users l.329, /admin/reset l.338 (critical)', 'survey', '2026-06-20 15:45:56');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('15', 'RISK', 'Smell catalogued: Global DB connection check_same_thread=False @ module level l.20 (critical)', 'survey', '2026-06-20 15:45:56');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('16', 'RISK', 'Smell catalogued: Comments GET without auth @ get_comments() l.264 (high)', 'survey', '2026-06-20 15:45:57');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('17', 'RISK', 'Smell catalogued: Bare except clauses @ register() l.77, get_tasks() l.182 (high)', 'survey', '2026-06-20 15:45:57');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('18', 'RISK', 'Smell catalogued: print() used as logging @ init_db() l.59, create_task() l.221 (medium)', 'survey', '2026-06-20 15:45:57');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('19', 'RISK', 'Smell catalogued: No input validation @ all POST/PUT routes (high)', 'survey', '2026-06-20 15:45:57');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('20', 'RISK', 'Smell catalogued: God module - monolithic app.py @ entire file l.1-368 (high)', 'survey', '2026-06-20 15:45:58');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('21', 'RISK', 'Smell catalogued: Raw SQL column index access @ all SELECT handlers (high)', 'survey', '2026-06-20 15:45:58');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('22', 'RISK', 'Smell catalogued: File write without path sanitization in export @ export_data() l.360 (medium)', 'survey', '2026-06-20 15:45:58');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('23', 'RISK', 'Smell catalogued: reset_db wipes all data with no confirmation @ /admin/reset l.337-344 (critical)', 'survey', '2026-06-20 15:45:58');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('24', 'RISK', 'Smell catalogued: No soft delete / no audit trail @ delete_project() l.143, delete_task() l.251 (medium)', 'survey', '2026-06-20 15:45:58');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('25', 'RISK', 'SQL injection sur /login permet bypass auth et dump complet de la DB', 'survey', '2026-06-20 15:46:14');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('26', 'RISK', 'SQL injection sur /tasks?status= et /search?q= permet exfiltration de donnees sans restriction', 'survey', '2026-06-20 15:46:14');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('27', 'RISK', '/admin/reset accessible sans auth - efface toutes les taches et projets en production', 'survey', '2026-06-20 15:46:15');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('28', 'RISK', '/admin/users retourne tous les utilisateurs (username, role) sans auth', 'survey', '2026-06-20 15:46:15');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('29', 'RISK', 'Connexion DB globale check_same_thread=False provoque corruption de donnees sous charge concurrente', 'survey', '2026-06-20 15:46:15');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('30', 'RISK', 'MD5 password - toute la base users est compromettable par rainbow tables', 'survey', '2026-06-20 15:46:15');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('31', 'RISK', 'Hardcoded secret_key - les sessions Flask sont forgeables par qui connait le secret', 'survey', '2026-06-20 15:46:15');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('32', 'RISK', 'export_data() ecrit un fichier JSON non protege sur le serveur, accessible par chemin connu', 'survey', '2026-06-20 15:46:16');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('33', 'RISK', 'Suppression en cascade (delete_project supprime tasks) sans transaction atomique', 'survey', '2026-06-20 15:46:16');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('34', 'INFO', 'Phase ''survey'' → completed', 'survey', '2026-06-20 15:47:47');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('35', 'INFO', 'Metrics snapshot recorded (0 series + smells)', 'unknown', '2026-06-21 11:49:29');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('36', 'INFO', 'Metrics snapshot recorded (0 series + smells)', 'unknown', '2026-06-21 11:49:38');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('37', 'INFO', 'Phase ''map'' → completed', 'map', '2026-06-21 11:50:43');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('38', 'INFO', 'Phase ''audit'' → completed', 'audit', '2026-06-26 11:51:53');
INSERT INTO session_log (id, level, message, phase, created_at) VALUES ('39', 'INFO', 'Phase ''draft'' → completed', 'draft', '2026-07-01 12:08:32');

-- files_touched (0 rows)
DELETE FROM files_touched;

PRAGMA foreign_keys=ON;
