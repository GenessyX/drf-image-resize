from rest_framework.generics import get_object_or_404
from images.models import Image
from images.serializers import ImageSerializer, SizeSerializer
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
# Create your views here.


class ImageViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    @action( detail=True, methods=['POST'])
    def resize(self, request, pk=None):
        img = get_object_or_404(Image, id=pk)
        size_serializer = SizeSerializer(data=request.data)
        if size_serializer.is_valid():
            width, height = size_serializer.data.get('width'), size_serializer.data.get('height')
            new_img = img.resize(width, height)
            img_serializer = ImageSerializer(new_img)
            return Response(img_serializer.data)

        return Response(size_serializer.errors)