from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Service, TimeSlot, Booking, Master, generate_slots_for_master
from django.http import HttpResponse
import datetime
import csv


@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ['photo_preview', 'name', 'specialization', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    list_display_links = ['name']
    list_editable = ['is_active']

    def photo_preview(self, obj):
        if obj.photo:
            return mark_safe(f'<img src="{obj.photo.url}" style="width:40px;height:40px;border-radius:50%;object-fit:cover">')
        return mark_safe('<div style="width:40px;height:40px;border-radius:50%;background:#F5C6D0;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700">' + obj.name[0] + '</div>')
    photo_preview.short_description = 'Фото'


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['thumbnail', 'name', 'category', 'duration_minutes', 'price_from', 'is_active', 'order']
    list_filter = ['category', 'is_active']
    search_fields = ['name']
    list_editable = ['is_active', 'order']
    list_display_links = ['name']
    filter_horizontal = ['masters']

    def thumbnail(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="width:48px;height:48px;border-radius:8px;object-fit:cover">')
        return '-'
    thumbnail.short_description = 'Фото'


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'time', 'master', 'is_booked']
    list_filter = ['date', 'is_booked', 'master']
    list_display_links = ['id']
    actions = ['generate_slots']

    @admin.action(description='Сгенерировать слоты на 2 недели')
    def generate_slots(self, request, queryset):
        masters = Master.objects.filter(is_active=True)
        count = 0
        for master in masters:
            count += generate_slots_for_master(master)
        self.message_user(request, f'Создано {count} новых слотов')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'colored_status', 'client_info', 'service_name', 'master_name', 'slot_info', 'created_short', 'email_badge']
    list_filter = ['status', 'service__category', 'master', 'slot__date']
    search_fields = ['client_name', 'client_phone', 'client_email']
    list_display_links = ['id']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_per_page = 25
    readonly_fields = ['cancel_token', 'created_at', 'email_sent']
    actions = ['mark_confirmed', 'mark_cancelled', 'export_to_csv']

    def colored_status(self, obj):
        colors = {
            'pending': ('#FFF3CD', '#856404', 'Ожидает'),
            'confirmed': ('#D4EDDA', '#155724', 'Подтверждена'),
            'cancelled': ('#F8D7DA', '#721C24', 'Отменена'),
            'completed': ('#E2E3E5', '#383D41', 'Завершена'),
        }
        bg, fg, label = colors.get(obj.status, ('#FFF', '#000', obj.status))
        return mark_safe(f'<span style="background:{bg};color:{fg};padding:4px 12px;border-radius:12px;font-size:12px;font-weight:600;white-space:nowrap">{label}</span>')
    colored_status.short_description = 'Статус'
    colored_status.allow_tags = True

    def client_info(self, obj):
        return mark_safe(f'<div><strong>{obj.client_name}</strong><br><span style="color:#888;font-size:11px">{obj.client_phone}</span></div>')
    client_info.short_description = 'Клиент'
    client_info.allow_tags = True

    def service_name(self, obj):
        return obj.service.name if obj.service else '-'
    service_name.short_description = 'Услуга'

    def master_name(self, obj):
        if obj.master:
            return mark_safe(f'<span style="color:#C9A96E;font-weight:600">{obj.master.name}</span>')
        return '-'
    master_name.short_description = 'Мастер'
    master_name.allow_tags = True

    def slot_info(self, obj):
        if obj.slot:
            return mark_safe(f'<div><strong>{obj.slot.date.strftime("%d.%m.%Y")}</strong><br><span style="color:#C9A96E;font-weight:600">{obj.slot.time.strftime("%H:%M")}</span></div>')
        return '-'
    slot_info.short_description = 'Дата и время'
    slot_info.allow_tags = True

    def created_short(self, obj):
        return obj.created_at.strftime('%d.%m %H:%M')
    created_short.short_description = 'Создано'

    def email_badge(self, obj):
        if obj.email_sent:
            return mark_safe('<span style="background:#D4EDDA;color:#155724;padding:2px 8px;border-radius:8px;font-size:11px">Отправлено</span>')
        return mark_safe('<span style="background:#F8D7DA;color:#721C24;padding:2px 8px;border-radius:8px;font-size:11px">Не отправлено</span>')
    email_badge.short_description = 'Email'
    email_badge.allow_tags = True

    @admin.action(description='Подтвердить выбранные')
    def mark_confirmed(self, request, queryset):
        queryset.update(status='confirmed')

    @admin.action(description='Отменить выбранные')
    def mark_cancelled(self, request, queryset):
        for b in queryset:
            b.status = 'cancelled'
            b.save()
            if b.slot:
                b.release_slots()

    @admin.action(description='Экспорт в CSV')
    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = 'attachment; filename="bookings.csv"'
        response.write('\ufeff')
        writer = csv.writer(response, delimiter=';')
        writer.writerow(['ID', 'Клиент', 'Телефон', 'Email', 'Услуга', 'Мастер', 'Дата', 'Время', 'Статус', 'Создано', 'Email отправлен'])
        for b in queryset:
            writer.writerow([
                b.id, b.client_name, b.client_phone, b.client_email,
                b.service.name, b.master.name if b.master else '-',
                str(b.slot.date), b.slot.time.strftime('%H:%M'),
                b.get_status_display(),
                b.created_at.strftime('%d.%m.%Y %H:%M'),
                'Да' if b.email_sent else 'Нет'
            ])
        return response
