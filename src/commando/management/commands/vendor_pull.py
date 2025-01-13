from django.core.management.base import BaseCommand
from helper.downloader import download_to_local
from django.conf import settings

STATICFILES_VENDORS_DIR = getattr(settings, 'STATICFILES_VENDORS_DIR')

VENDOR_STATICFILES = {
    # "saas-theme.min.css": "https://raw.githubusercontent.com/codingforentrepreneurs/SaaS-Foundations/main/src/staticfiles/theme/saas-theme.min.css",
    "flowbite.min.css": "https://cdnjs.cloudflare.com/ajax/libs/flowbite/2.3.0/flowbite.min.css",
    "flowbite.min.js": "https://cdnjs.cloudflare.com/ajax/libs/flowbite/2.3.0/flowbite.min.js",
    "flowbite.min.js.map": "https://cdnjs.cloudflare.com/ajax/libs/flowbite/2.3.0/flowbite.min.js.map"
}

class Command(BaseCommand):
    def handle(self, *args, **options):
        
        completed_urls = []
        for name, url in VENDOR_STATICFILES.items():
            out_path = STATICFILES_VENDORS_DIR / name
            # print(name,url,out_path)

            dl_success = download_to_local(url,out_path)

            if dl_success:
                completed_urls.append(url)
            else:
                self.stdout.write(
                    self.style.ERROR(f'{url} failed to download')
                )
        if set(completed_urls) == set(VENDOR_STATICFILES.values()):
            self.stdout.write(
                self.style.SUCCESS('Successfully updated all vendor static files.')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Some files were not updated.')
            )        
