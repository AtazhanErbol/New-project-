from django.contrib import admin, messages
from django.db.models import Q
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from .models import Service, TimeSlot, Booking, Master, Client, MasterTimeOff, generate_slots_for_master
from django.http import HttpResponse
import datetime
import csv


@admin.register(Master)
class MasterAdmin(ModelAdmin):
    list_display = ['photo_preview', 'name', 'email', 'specialization', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'email']
    list_display_links = ['name']
    list_editable = ['is_active']

    def photo_preview(self, obj):
        if obj.photo:
            return mark_safe(f'<img src="{obj.photo.url}" style="width:40px;height:40px;border-radius:50%;object-fit:cover">')
        return mark_safe('<div style="width:40px;height:40px;border-radius:50%;background:#EBC8CE;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700">' + obj.name[0] + '</div>')
    photo_preview.short_description = 'Фото'


@admin.register(MasterTimeOff)
class MasterTimeOffAdmin(ModelAdmin):
    list_display = ['master', 'date_from', 'date_to', 'reason', 'comment']
    list_filter = ['reason', 'master']
    date_hierarchy = 'date_from'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        conflicts = Booking.objects.filter(
            slot__master=obj.master,
            slot__date__gte=obj.date_from,
            slot__date__lte=obj.date_to,
        ).exclude(status='cancelled').count()
        if conflicts:
            self.message_user(
                request,
                f'Внимание: у мастера «{obj.master.name}» в этот период уже есть активных записей: {conflicts}. '
                f'Свяжитесь с клиентами для переноса.',
                level=messages.WARNING,
            )


@admin.register(Service)
class ServiceAdmin(ModelAdmin):
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
class TimeSlotAdmin(ModelAdmin):
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
class BookingAdmin(ModelAdmin):
    list_display = ['id', 'status_label', 'client_info', 'service_name', 'master_name', 'slot_info', 'created_short', 'email_label']
    list_filter = ['status', 'service__category', 'master', 'slot__date']
    search_fields = ['client_name', 'client_phone', 'client_email']
    list_display_links = ['id']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_per_page = 25
    readonly_fields = ['cancel_token', 'created_at', 'email_sent', 'whatsapp_confirm']
    actions = ['mark_confirmed', 'mark_cancelled', 'export_to_csv']

    # --- Кабинет мастера: мастер видит только свои записи ---
    def _is_master(self, request):
        if not request.user.is_authenticated:
            return False
        return Master.objects.filter(user=request.user).exists()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        m = None
        if request.user.is_authenticated:
            m = Master.objects.filter(user=request.user).first()
        if m:
            return qs.filter(Q(master=m) | Q(slot__master=m)).distinct()
        return qs.none()

    def has_module_permission(self, request):
        return request.user.is_superuser or self._is_master(request)

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or self._is_master(request)

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or self._is_master(request)

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_readonly_fields(self, request, obj=None):
        ro = list(super().get_readonly_fields(request, obj))
        if not request.user.is_superuser:
            ro += ['service', 'master', 'slot', 'client', 'client_name',
                   'client_phone', 'client_email', 'consent_given_at']
        return ro

    def whatsapp_confirm(self, obj):
        url = obj.client_whatsapp_url()
        if not url:
            return '-'
        return mark_safe(
            f'<a href="{url}" target="_blank" rel="noopener" '
            f'style="display:inline-block;background:#25D366;color:#fff;padding:8px 16px;'
            f'border-radius:8px;font-weight:600;text-decoration:none">Написать клиенту в WhatsApp</a>'
        )
    whatsapp_confirm.short_description = 'WhatsApp клиенту'

    @display(description='Статус', label={
        'Ожидает': 'warning', 'Подтверждена': 'success',
        'Отменена': 'danger', 'Завершена': 'info',
    })
    def status_label(self, obj):
        return obj.get_status_display()

    def client_info(self, obj):
        return mark_safe(f'<div><strong>{obj.client_name}</strong><br><span style="opacity:.6;font-size:11px">{obj.client_phone}</span></div>')
    client_info.short_description = 'Клиент'
    client_info.allow_tags = True

    def service_name(self, obj):
        return obj.service.name if obj.service else '-'
    service_name.short_description = 'Услуга'

    def master_name(self, obj):
        if obj.master:
            return mark_safe(f'<span style="color:#B76E79;font-weight:600">{obj.master.name}</span>')
        return '-'
    master_name.short_description = 'Мастер'
    master_name.allow_tags = True

    def slot_info(self, obj):
        if obj.slot:
            return mark_safe(f'<div><strong>{obj.slot.date.strftime("%d.%m.%Y")}</strong><br><span style="color:#B76E79;font-weight:600">{obj.slot.time.strftime("%H:%M")}</span></div>')
        return '-'
    slot_info.short_description = 'Дата и время'
    slot_info.allow_tags = True

    def created_short(self, obj):
        from django.utils import timezone
        return timezone.localtime(obj.created_at).strftime('%d.%m %H:%M')
    created_short.short_description = 'Создано'

    @display(description='Email', label={'Отправлено': 'success', 'Не отправлено': 'danger'})
    def email_label(self, obj):
        return 'Отправлено' if obj.email_sent else 'Не отправлено'

    @admin.action(description='Подтвердить выбранные (+ письмо клиенту)')
    def mark_confirmed(self, request, queryset):
        from .views import send_client_confirmation_email
        sent = 0
        total = 0
        for b in queryset:
            b.status = 'confirmed'
            b.save(update_fields=['status'])
            total += 1
            if send_client_confirmation_email(b):
                sent += 1
        self.message_user(request, f'Подтверждено записей: {total}, писем клиентам отправлено: {sent}')

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


class ClientBookingInline(TabularInline):
    model = Booking
    fk_name = 'client'
    extra = 0
    can_delete = False
    show_change_link = True
    fields = ['created_at', 'service', 'master', 'slot', 'status']
    readonly_fields = ['created_at', 'service', 'master', 'slot', 'status']
    ordering = ['-created_at']
    verbose_name = 'Запись'
    verbose_name_plural = 'История записей'

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Client)
class ClientAdmin(ModelAdmin):
    list_display = ['name', 'phone', 'email', 'visits', 'created_at']
    search_fields = ['name', 'phone', 'email']
    ordering = ['name']
    readonly_fields = ['created_at']
    inlines = [ClientBookingInline]
    actions = ['export_clients_csv']

    def visits(self, obj):
        return obj.visits_count
    visits.short_description = 'Визитов'

    @admin.action(description='Экспорт клиентов в CSV')
    def export_clients_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = 'attachment; filename="clients.csv"'
        response.write('﻿')
        writer = csv.writer(response, delimiter=';')
        writer.writerow(['Имя', 'Телефон', 'Email', 'Визитов', 'Создан', 'Комментарий'])
        for c in queryset:
            writer.writerow([c.name, c.phone, c.email, c.visits_count,
                             c.created_at.strftime('%d.%m.%Y'), c.notes])
        return response
