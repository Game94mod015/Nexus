# Nexus Railway Panel — Python starter

این پروژه یک اسکلت امن و قابل توسعه برای پنل مدیریت Railway با Python/FastAPI است.

## اجرا

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export ADMIN_TOKEN="یک-توکن-طولانی-تصادفی"
uvicorn app:app --host 0.0.0.0 --port 8000
```

## Railway

- Repository را به Railway متصل کنید.
- `ADMIN_TOKEN` را در Railway Variables قرار دهید.
- پورت را دستی hard-code نکنید؛ برنامه از `$PORT` استفاده می‌کند.
- Health check: `/health`

## نکته امنیتی

مسیر مدیریتی بدون احراز هویت مثل `/adminadmin` در این نسخه عمداً ساخته نشده است؛
یک URL مخفی به‌تنهایی احراز هویت نیست. API مدیریتی با Bearer token محافظت شده است.

## وضعیت این نسخه

این فایل نسخه starter است، نه پنل production نهایی. Database، migration،
Xray/sing-box integration، RBAC، 2FA، metrics واقعی و persistence باید قبل از
استفاده عملیاتی اضافه شوند.
