-- ==========================================================
-- TicketGenie Seed Data
-- Default Roles
-- ==========================================================

INSERT INTO dbo.Roles (role_name, description)
VALUES
    ('EMPLOYEE', 'Can create tickets and view their own ticket history'),
    ('SUPPORT_AGENT', 'Can manage HR or IT tickets and use the internal chatbot'),
    ('ADMIN', 'Can manage users and access all system features');
GO

-- ==========================================================
-- Synthetic Demo Users
-- ==========================================================

INSERT INTO dbo.Users (
    username,
    email,
    password_hash,
    first_name,
    last_name,
    role_id,
    department
)
VALUES
    (
        'employee.demo',
        'employee.demo@ticketgenie.test',
        'REPLACE_WITH_REAL_HASH',
        'Maya',
        'Patel',
        (SELECT role_id FROM dbo.Roles WHERE role_name = 'EMPLOYEE'),
        NULL
    ),
    (
        'hr.agent',
        'hr.agent@ticketgenie.test',
        'REPLACE_WITH_REAL_HASH',
        'Olivia',
        'Chen',
        (SELECT role_id FROM dbo.Roles WHERE role_name = 'SUPPORT_AGENT'),
        'HR'
    ),
    (
        'it.agent',
        'it.agent@ticketgenie.test',
        'REPLACE_WITH_REAL_HASH',
        'Ethan',
        'Brooks',
        (SELECT role_id FROM dbo.Roles WHERE role_name = 'SUPPORT_AGENT'),
        'IT'
    ),
    (
        'admin.demo',
        'admin.demo@ticketgenie.test',
        'REPLACE_WITH_REAL_HASH',
        'Noah',
        'Williams',
        (SELECT role_id FROM dbo.Roles WHERE role_name = 'ADMIN'),
        NULL
    );
GO