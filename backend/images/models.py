from django.core.files.base import ContentFile
from django.db import models
import requests
import os
from django.core import files
import PIL.Image
from io import BytesIO
import tempfile
from django.db.models.signals import post_delete
from django.dispatch import receiver

# Create your models here.
class Image(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    picture = models.ImageField(upload_to='uploads/', blank=True)
    url = models.URLField(max_length=200, blank=True, null=True)
    parent_picture = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True
    )

    @classmethod
    def create(cls, *args, **kwargs):
        image = cls(**kwargs)
        return image

    # TODO: verify url has image.
    def save(self, *args, **kwargs):
        if self.picture:
            if not self.name:
                self.name = self.picture.url.split("/")[-1]
                
        super(Image, self).save(*args, **kwargs)

        if not self.picture:
            r = requests.get(self.url, stream=True)
            filename = ""
            if not self.name:
                self.name = self.url.split("/")[-1]
            else:
                url_file_extension = self.url.split(".")[-1]
                if self.name.split(".")[-1] != url_file_extension:
                    filename = "{}.{}".format(self.name, url_file_extension)

            lf = tempfile.NamedTemporaryFile() 

            for block in r.iter_content(1024*8):
                if not block:
                    break
                lf.write(block)

            self.picture.save(filename or self.name, files.File(lf))


    def resize(self, width=None, height=None):
        img = PIL.Image.open(self.picture)
        new_img = img.resize((width or img.width, height or img.height))
        buffer = BytesIO()
        new_img.save(fp=buffer, format=img.format)
        new_name = "{}_{}_{}".format(self.name, str(new_img.width), str(new_img.height))
        img_to_save = Image.create(
            name=new_name,
            parent_picture=self
        )
        img_to_save.picture.save("{}.{}".format(new_name, self.name.split(".")[-1]), ContentFile(buffer.getvalue()))
        img_to_save.save()
        return img_to_save

    def __str__(self):
        return self.name

@receiver(post_delete, sender=Image)
def image_delete_handler(sender, instance, **kwargs):
    try:
        os.remove(instance.picture.path)
    except:
        pass