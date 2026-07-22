from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class LenientManifestStaticFilesStorage(ManifestStaticFilesStorage):
    """Хэширование имён (сброс кэша) без сжатия и без падений.

    - НЕ сжимает файлы (в отличие от WhiteNoise) — collectstatic не виснет
      на сотнях файлов admin-темы на слабом CPU PythonAnywhere.
    - manifest_strict = False: если admin-тема ссылается на статику, которой
      нет в манифесте, возвращается обычное имя вместо ValueError → страница
      не падает с 500.
    """
    manifest_strict = False
