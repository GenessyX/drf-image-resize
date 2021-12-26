from rest_framework import serializers
from images.models import Image
import requests

class ImageSerializer(serializers.ModelSerializer):
    file = serializers.ImageField(source="picture", required=False)
    class Meta:
        model = Image
        fields = ['id', 'name', 'file', 'url', 'parent_picture', 'width', 'height']

    width = serializers.SerializerMethodField()
    height = serializers.SerializerMethodField()

    def validate(self, attrs):
        if not attrs.get('picture') and not attrs.get('url'):
            raise serializers.ValidationError({"error": "File or url should be provided."})
        if attrs.get('picture') and attrs.get('url'):
            raise serializers.ValidationError({"__all__": "Two field"})
        if attrs.get('url'):
            response = requests.get(attrs['url'])
            code = response.status_code
            if code != requests.codes.ok:
                raise serializers.ValidationError({"error":"URL returned code {}.".format(code)})
            content_type = response.headers['Content-Type']
            if content_type.split("/")[0] != 'image':
                raise serializers.ValidationError({"error": "URL does not contain image."})
            
        return attrs

    def get_width(self, obj):
        if obj.picture:
            return obj.picture.width

    def get_height(self, obj):
        if obj.picture:
            return obj.picture.height

class SizeSerializer(serializers.Serializer):
    width = serializers.IntegerField(min_value=10, max_value=10000, required=False)
    height = serializers.IntegerField(min_value=10, max_value=10000, required=False)

    def validate(self, attrs):
        if 'width' not in attrs and 'height' not in attrs:
            raise serializers.ValidationError({"error":"Either width or height should be provided."})
        return attrs
        

    