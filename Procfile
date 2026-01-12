cat > Procfile << 'EOF'
web: python manage.py migrate --noinput && python manage.py collectstatic --noinput && python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', '123_123')
    print('✅ Суперпользователь создан')
else:
    print('⚠️ Суперпользователь уже существует')
" && gunicorn hackathon_site.wsgi:application --bind 0.0.0.0:\$PORT
EOF
