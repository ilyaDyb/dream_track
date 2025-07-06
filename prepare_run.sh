#!/bin/bash

# Aply migrations
echo "Applying migrations..."
python manage.py migrate

# Load fixtures in specific order
echo "Loading fixtures..."

python manage.py loaddata fixtures/base_shop_items.json
python manage.py loaddata fixtures/avatar_items.json
python manage.py loaddata fixtures/icon_items.json
python manage.py loaddata fixtures/background_items.json
python manage.py loaddata fixtures/boost_items.json
python manage.py loaddata fixtures/achievements.json
