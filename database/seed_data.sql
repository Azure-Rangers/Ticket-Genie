-- ==========================================================
-- TicketGenie Initial Seed Data (SQL)
-- ==========================================================

-- Seed Standard Departments
INSERT INTO departments (id, name, queue_name, description, createdAt)
SELECT 'dept-it-001', 'IT Team', 'IT - Service Desk', 'IT Support and hardware/software service desk queue', '2026-08-16T12:00:00'
WHERE NOT EXISTS (SELECT 1 FROM departments WHERE id = 'dept-it-001' OR name = 'IT Team');

INSERT INTO departments (id, name, queue_name, description, createdAt)
SELECT 'dept-hr-002', 'HR Team', 'HR - Employee Relations', 'Human resources, benefits, and employee relations queue', '2026-08-16T12:00:00'
WHERE NOT EXISTS (SELECT 1 FROM departments WHERE id = 'dept-hr-002' OR name = 'HR Team');

INSERT INTO departments (id, name, queue_name, description, createdAt)
SELECT 'dept-acc-003', 'Accounting Team', 'Accounting - Payroll', 'Finance, accounts payable, and payroll queue', '2026-08-16T12:00:00'
WHERE NOT EXISTS (SELECT 1 FROM departments WHERE id = 'dept-acc-003' OR name = 'Accounting Team');

INSERT INTO departments (id, name, queue_name, description, createdAt)
SELECT 'dept-exec-004', 'Upper Executive Management', 'Upper Management - Leave Approval', 'Executive leadership and leave approval escalations', '2026-08-16T12:00:00'
WHERE NOT EXISTS (SELECT 1 FROM departments WHERE id = 'dept-exec-004' OR name = 'Upper Executive Management');

INSERT INTO departments (id, name, queue_name, description, createdAt)
SELECT 'dept-wop-005', 'Workplace Operations Team', 'Workplace Operations - Facilities', 'Workplace operations, facilities, and logistics queue', '2026-08-16T12:00:00'
WHERE NOT EXISTS (SELECT 1 FROM departments WHERE id = 'dept-wop-005' OR name = 'Workplace Operations Team');

-- Seed Initial Admin in Department Users
INSERT INTO department_users (id, department_name, azure_object_id, role, user_email, createdAt)
SELECT 'uobj-admin-dc3b56e9', 'Upper Executive Management', 'dc3b56e9-9280-40dc-8d73-98bfd81fdd6a', 'Admin', 'Admin1@vigneshquadrantoutlook.onmicrosoft.com', '2026-08-16T12:00:00'
WHERE NOT EXISTS (SELECT 1 FROM department_users WHERE id = 'uobj-admin-dc3b56e9');

-- Seed Initial Admin in User Profiles
INSERT INTO user_profiles (id, name, email, role, department, phone, avatar, azure_object_id)
SELECT 'usr-admin-dc3b56e9', 'Greg Davis', 'Admin1@vigneshquadrantoutlook.onmicrosoft.com', 'Admin', 'Upper Executive Management', '+1 (555) 019-9999', 'GD', 'dc3b56e9-9280-40dc-8d73-98bfd81fdd6a'
WHERE NOT EXISTS (SELECT 1 FROM user_profiles WHERE id = 'usr-admin-dc3b56e9');

-- Seed Initial Ticket Created by User (usr-admin-dc3b56e9 / dc3b56e9-9280-40dc-8d73-98bfd81fdd6a)
INSERT INTO tickets (id, title, department, queue, category, priority, status, description, date, createdAt, is_anonymous, auto_resolved, is_synthetic, requester_id, classification_status, classification_confidence, classification_reason, needs_human_review, model_deployment)
SELECT 'HD-2001', 'VPN Connection Issue for Admin User', 'IT Team', 'IT - Service Desk', 'IT Support', 'High', 'Open', 'Unable to connect to internal VPN network from remote office.', '2026-08-16', '2026-08-16T23:06:00', 0, 0, 0, 'usr-admin-dc3b56e9', 'Classified', '0.95', 'IT Support request regarding VPN', 0, 'gpt-5.2'
WHERE NOT EXISTS (SELECT 1 FROM tickets WHERE id = 'HD-2001');

-- Seed Initial Ticket Created by Another User (other-employee-7890)
INSERT INTO tickets (id, title, department, queue, category, priority, status, description, date, createdAt, is_anonymous, auto_resolved, is_synthetic, requester_id, classification_status, classification_confidence, classification_reason, needs_human_review, model_deployment)
SELECT 'HD-2002', 'Payroll Discrepancy Inquiry', 'HR Team', 'HR - Employee Relations', 'Payroll', 'Medium', 'Open', 'Overtime pay was not reflected on recent paystub.', '2026-08-16', '2026-08-16T23:06:30', 0, 0, 0, 'other-employee-7890', 'Classified', '0.90', 'HR Payroll request', 0, 'gpt-5.2'
WHERE NOT EXISTS (SELECT 1 FROM tickets WHERE id = 'HD-2002');
