from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort, current_app
from models.models_definitions import db, Setting
from routes.auth_utils import login_required, admin_only

admin_settings_bp = Blueprint('admin_settings', __name__, url_prefix='/admin/settings')


@admin_settings_bp.before_request
@admin_only
@login_required
def restrict_to_admins():
    """Ensure only admins can access this blueprint."""
    pass


@admin_settings_bp.route('/')
def settings_list():
    """عرض جميع الإعدادات"""
    settings = Setting.query.order_by(Setting.key.asc()).all()
    return render_template('admin/settings/settings_list.html', settings=settings)



@admin_settings_bp.route('/edit/<int:setting_id>', methods=['GET', 'POST'])
def edit_setting(setting_id):
    """تعديل إعداد موجود"""
    setting = Setting.query.get_or_404(setting_id)

    if request.method == 'POST':
        setting.value = request.form.get('value', '').strip()
        db.session.commit()
        flash("✅ تم تحديث الإعداد بنجاح", "success")
        return redirect(url_for('admin_settings.settings_list'))

    return render_template('admin/settings/edit_setting.html', setting=setting)



@admin_settings_bp.route('/add', methods=['GET', 'POST'])
def add_setting():
    """إضافة إعداد جديد"""
    if request.method == 'POST':
        key = request.form.get('key', '').strip()
        value = request.form.get('value', '').strip()

        if not key:
            flash("❌ المفتاح مطلوب", "error")
            return redirect(request.url)

        # منع التكرار
        existing = Setting.query.filter_by(key=key).first()
        if existing:
            flash("⚠️ هذا المفتاح موجود مسبقًا", "warning")
            return redirect(url_for('admin_settings.edit_setting', setting_id=existing.id))

        new_setting = Setting(key=key, value=value)
        db.session.add(new_setting)
        db.session.commit()
        flash("✅ تم إضافة الإعداد بنجاح", "success")
        return redirect(url_for('admin_settings.settings_list'))

    return render_template('admin/settings/add_setting.html')


