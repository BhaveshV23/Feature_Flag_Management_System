# Feature Flag Management System - Database Schema

## Overview

This database schema is designed for a Feature Flag Management and Release Control System. It supports multiple environments, feature flag versioning, targeting rules, user group memberships, and audit logging.

---

# Database Tables

1. environments
2. flags
3. flag_versions
4. targeting_rules
5. user_group_memberships
6. audit_log

---

# 1. environments

## Purpose

Stores all deployment environments such as Development, Testing, Staging, and Production.

### Columns

| Column | Type | Description |
|---------|------|-------------|
| id | Integer | Primary Key |
| name | String | Environment name |
| description | Text | Description of the environment |
| is_active | Boolean | Indicates whether the environment is active |
| created_at | Timestamp | Record creation timestamp |
| updated_at | Timestamp | Last updated timestamp |

### Primary Key

- id

### Foreign Keys

- None

### Relationships

- One Environment can have many Flags.
- One Environment can have many Audit Logs.

### Suggested Indexes

- PRIMARY KEY(id)
- INDEX(name)
- INDEX(is_active)

---

# 2. flags

## Purpose

Stores all feature flags available in different environments.

### Columns

| Column | Type | Description |
|---------|------|-------------|
| id | Integer | Primary Key |
| environment_id | Integer | Foreign Key referencing environments.id |
| key | String | Unique identifier used in application code |
| name | String | Display name of the feature |
| description | Text | Feature description |
| enabled | Boolean | Current status of the feature |
| created_at | Timestamp | Record creation timestamp |
| updated_at | Timestamp | Last updated timestamp |

### Primary Key

- id

### Foreign Keys

- environment_id → environments.id

### Relationships

- Many Flags belong to one Environment.
- One Flag can have many Flag Versions.
- One Flag can have many Targeting Rules.
- One Flag can have many Audit Logs.

### Suggested Indexes

- PRIMARY KEY(id)
- UNIQUE(key)
- INDEX(environment_id)
- INDEX(enabled)

---

# 3. flag_versions

## Purpose

Maintains the version history of each feature flag and supports rollback.

### Columns

| Column | Type | Description |
|---------|------|-------------|
| id | Integer | Primary Key |
| flag_id | Integer | Foreign Key referencing flags.id |
| version | Integer | Version number |
| enabled | Boolean | Feature status for this version |
| config | JSON | Configuration data |
| created_at | Timestamp | Version creation timestamp |

### Primary Key

- id

### Foreign Keys

- flag_id → flags.id

### Relationships

- Many Flag Versions belong to one Flag.

### Suggested Indexes

- PRIMARY KEY(id)
- INDEX(flag_id)
- INDEX(version)

---

# 4. targeting_rules

## Purpose

Defines which users receive a particular feature flag.

### Columns

| Column | Type | Description |
|---------|------|-------------|
| id | Integer | Primary Key |
| flag_id | Integer | Foreign Key referencing flags.id |
| priority | Integer | Rule execution priority |
| rule_type | String | Targeting type (user, group, country, percentage, etc.) |
| operator | String | Comparison operator (equals, contains, >, <) |
| value | String | Value to compare against |
| percentage | Integer | Percentage rollout value |
| enabled | Boolean | Indicates whether the rule is active |
| created_at | Timestamp | Rule creation timestamp |

### Primary Key

- id

### Foreign Keys

- flag_id → flags.id

### Relationships

- Many Targeting Rules belong to one Flag.

### Suggested Indexes

- PRIMARY KEY(id)
- INDEX(flag_id)
- INDEX(priority)
- INDEX(enabled)

---

# 5. user_group_memberships

## Purpose

Stores user-to-group mappings used for feature targeting.

### Columns

| Column | Type | Description |
|---------|------|-------------|
| id | Integer | Primary Key |
| user_id | Integer | User identifier |
| group_name | String | Name of the user group |
| created_at | Timestamp | Membership creation timestamp |

### Primary Key

- id

### Foreign Keys

- None

### Relationships

- Used by Targeting Rules to target feature flags to specific user groups.

### Suggested Indexes

- PRIMARY KEY(id)
- INDEX(user_id)
- INDEX(group_name)

---

# 6. audit_log

## Purpose

Maintains a complete history of all changes made to feature flags.

### Columns

| Column | Type | Description |
|---------|------|-------------|
| id | Integer | Primary Key |
| flag_id | Integer | Foreign Key referencing flags.id |
| environment_id | Integer | Foreign Key referencing environments.id |
| actor | String | User who performed the action |
| action | String | Action performed (CREATE, UPDATE, ENABLE, DISABLE, DELETE) |
| old_state | JSON | Previous state before change |
| new_state | JSON | Updated state after change |
| created_at | Timestamp | Action timestamp |

### Primary Key

- id

### Foreign Keys

- flag_id → flags.id
- environment_id → environments.id

### Relationships

- Many Audit Logs belong to one Flag.
- Many Audit Logs belong to one Environment.

### Suggested Indexes

- PRIMARY KEY(id)
- INDEX(flag_id)
- INDEX(environment_id)
- INDEX(created_at)

---

# Entity Relationships

```text
environments
      │
      │ 1
      │
      │ *
flags
 ├───────────────┐
 │               │
 │               │
 ▼               ▼
flag_versions   targeting_rules
 │
 │
 ▼
audit_log

environments
      │
      ▼
audit_log

user_group_memberships
      │
      ▼
Referenced by Targeting Rules
```

---

# Relationship Summary

| Parent Table | Child Table | Relationship |
|--------------|-------------|--------------|
| environments | flags | One-to-Many |
| environments | audit_log | One-to-Many |
| flags | flag_versions | One-to-Many |
| flags | targeting_rules | One-to-Many |
| flags | audit_log | One-to-Many |

---

# Index Summary

| Table | Indexes |
|-------|---------|
| environments | PRIMARY KEY(id), INDEX(name), INDEX(is_active) |
| flags | PRIMARY KEY(id), UNIQUE(key), INDEX(environment_id), INDEX(enabled) |
| flag_versions | PRIMARY KEY(id), INDEX(flag_id), INDEX(version) |
| targeting_rules | PRIMARY KEY(id), INDEX(flag_id), INDEX(priority), INDEX(enabled) |
| user_group_memberships | PRIMARY KEY(id), INDEX(user_id), INDEX(group_name) |
| audit_log | PRIMARY KEY(id), INDEX(flag_id), INDEX(environment_id), INDEX(created_at) |