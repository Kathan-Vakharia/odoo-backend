User
name string
email string
dept_id string (Foreign Key to Department table)
role enum('employee', 'admin', 'HR')

Department
id string (primary key)
name string

Attachment
id string (Primary Key)
url string
grievance_id (Foreign Key to Grievance Table)
mime_type string

Grievance
id string (Primary Key)
user_id string (Foreign Key to Users table)
grievance_type string
title string
description string
assigned_to string nullable(id of user or department)
assigned_type enum('HR', 'Department')
severity enum(low, medium, high)
status enum(submitted, in_review, resolved)
created_at timestamp
updated_at timestamp
resolved_at timestamp

Log
id string (Primary Key)
module enum('grievance', 'chat', 'user')
action enum('login', 'create', 'update', 'delete')
created_at timestamp
msg string

GrievanceNotification
id string (Primary Key)
user_id (Foreign Key to User table)
grievance_id (Foreign Key to Grievance table)
message string
read boolean
created_at timestamp

Chat  
 id string (Primary Key)  
 to (Foreign Key to User table)  
 recieve_id (Foreign Key to User table)  
 message string  
 attach bbolean  
 attach_pth string
