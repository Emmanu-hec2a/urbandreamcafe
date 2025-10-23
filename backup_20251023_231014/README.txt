UrbanDream Cafe - Complete Backup
Created: Thu Oct 23 23:10:30 EAST 2025
================================================

Contents:
- full_database.json: Complete database dump
- food_data.json: Food items and categories only
- users.json: User accounts data
- orders.json: Order history
- media/: All uploaded images
- static/: Static files
- db.sqlite3: Complete SQLite database

Restore Instructions:
1. For PostgreSQL: python manage.py loaddata <file>.json
2. For media files: Copy media/ to your project root
3. For SQLite: Copy db.sqlite3 to project root

Notes:
- Passwords are hashed (secure)
- Session data excluded
- Permissions will be recreated automatically
