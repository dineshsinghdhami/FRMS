# # Family Record Management System

![License](https://img.shields.io/badge/license-Proprietary-red)
![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-green)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue)
![Bootstrap](https://img.shields.io/badge/UI-Bootstrap-purple)

**Family Record Management System (FRMS)** is a web-based application developed using **Python, Flask, PostgreSQL, Bootstrap, and Jinja2**.

It is designed to digitally record, organize, manage, and preserve important family information in one centralized system.

> FRMS was created by **Dinesh Singh Dhami** as a system for maintaining family members, relationships, personal records, activities, events, documents, photos, and family history.

---

## # Features

- Admin and Member login
- Role-based access control
- Family member management
- Family relationships and family tree
- Personal timeline
- Activities and events
- Announcements
- Gallery
- Document management
- Family history
- Invite-based member registration
- User account management
- Admin dashboard
- Mobile responsive design

---

## # User Roles

### # Admin

Admin can manage family members, user accounts, relationships, invitations, activities, events, announcements, gallery, documents, family history, and system status.

### # Member

Members can manage their profile, timeline, activities, events, announcements, gallery, documents, family history, and view family members and the family tree.

---

## # Invitation Registration

```text
Admin Creates Family Member
        ↓
Generates Invitation
        ↓
Member Opens Link
        ↓
Creates Account
        ↓
Account Automatically Linked
        ↓
Member Can Log In
```

Invitation links are unique, one-time use, expirable, and can be revoked by the Admin.

---

## # Tech Stack

- **Python**
- **Flask**
- **PostgreSQL**
- **SQLAlchemy**
- **Flask-Login**
- **Flask-WTF**
- **Bootstrap**
- **HTML / CSS**
- **Jinja2**
- **Gunicorn**
- **Render**

---

## # Project Structure

```text
family-record-management/
│
├── app/
│   ├── forms/
│   ├── models/
│   ├── routes/
│   ├── templates/
│   └── uploads/
│
├── migrations/
├── config.py
├── requirements.txt
├── render-build.sh
├── Procfile
├── .python-version
├── .gitignore
└── README.md
```

---

## # Note

> **Family Record Management System (FRMS)** was designed and developed by **Dinesh Singh Dhami** to digitally record, organize, manage, and preserve family details and important family records.

---

## # Author

**Dinesh Singh Dhami**

- Website: https://dineshsinghdhami.com.np
- GitHub: https://github.com/dineshsinghdhami
- Email: dineshdhamidn@gmail.com

---

## # License

This project is proprietary software created by **Dinesh Singh Dhami**.

Unauthorized copying, distribution, modification, or commercial use without permission is prohibited.
