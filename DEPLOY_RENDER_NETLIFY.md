# Netlify + Render + PostgreSQL deploy qo'llanma

Bu loyiha Render backend va Netlify frontend uchun moslangan.
Ma'lumotlar o'chib ketmasligi uchun backendni SQLite bilan emas, alohida PostgreSQL bilan ishlating.
Bepul start uchun Neon PostgreSQL yoki Render PostgreSQL ishlatish mumkin.

## 1) Database tayyorlash

PostgreSQL yarating va `DATABASE_URL` oling.
Neon ishlatsangiz URL oxirida `?sslmode=require` bo'lishi yaxshi.

## 2) Backendni Renderga qo'yish

Renderda New Web Service yarating va GitHub repo ulang.

Sozlamalar:

- Root Directory: `backend`
- Build Command: `./build.sh`
- Start Command: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`

Environment Variables:

```text
DEBUG=False
SECRET_KEY=strong-random-secret-key
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DB_NAME?sslmode=require
ALLOWED_HOSTS=your-backend.onrender.com
CORS_ALLOWED_ORIGINS=https://your-site.netlify.app
CSRF_TRUSTED_ORIGINS=https://your-site.netlify.app,https://your-backend.onrender.com
```

Deploy tugagandan keyin backend URL shunaqa bo'ladi:

```text
https://your-backend.onrender.com
```

Admin panel:

```text
https://your-backend.onrender.com/admin/
```

Agar superuser kerak bo'lsa Render Shell ichida:

```bash
python manage.py createsuperuser
```

## 3) Frontendni Netlifyga qo'yish

Netlifyda New site from Git qiling.

Sozlamalar:

- Base directory: `frontend`
- Build command: `npm run build`
- Publish directory: `frontend/dist` yoki Base directory `frontend` bo'lsa `dist`

Environment Variables:

```text
VITE_API_URL=https://your-backend.onrender.com/api
```

Deploydan keyin Netlify URLni Render envga qo'shing:

```text
CORS_ALLOWED_ORIGINS=https://your-site.netlify.app
CSRF_TRUSTED_ORIGINS=https://your-site.netlify.app,https://your-backend.onrender.com
```

Keyin Render backendni redeploy qiling.

## Muhim

- Frontend yoki backend yangilanganda ma'lumotlar o'chmaydi, chunki ma'lumotlar PostgreSQL bazada turadi.
- Ma'lumot o'chib ketmasligi uchun `python manage.py flush` ishlatmang.
- Modeldan ustun o'chirishdan oldin backup oling.
- Render free uxlab qolishi mumkin, birinchi ochilganda sekinroq bo'ladi.
